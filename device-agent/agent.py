import asyncio
import queue
import threading
import time

import numpy as np
import requests
import sounddevice as sd

from wyoming.audio import AudioChunk, AudioStart, AudioStop
from wyoming.asr import Transcript
from wyoming.tts import Synthesize
from wyoming.wake import Detect, Detection
from wyoming.event import async_read_event, async_write_event

WHISPER_HOST, WHISPER_PORT = "localhost", 10300
PIPER_HOST, PIPER_PORT = "localhost", 10200
WAKEWORD_HOST, WAKEWORD_PORT = "localhost", 10400
WAKEWORD_MODEL = "alexa"

SERVER_URL = "http://localhost:8090/api/voice/command"

RATE, WIDTH, CHANNELS = 16000, 2, 1
CHUNK = 1280
SILENCE_THRESHOLD = 700
SILENCE_DURATION_S = 1.0
MAX_RECORD_S = 10
GRACE_PERIOD_S = 3
WARMUP_CHUNKS = 50  # ~4s, temps nécessaire à openWakeWord pour remplir sa fenêtre de contexte



async def wait_for_wake_word():
    reader, writer = await asyncio.open_connection(WAKEWORD_HOST, WAKEWORD_PORT)
    await async_write_event(Detect(names=[WAKEWORD_MODEL]).event(), writer)
    await async_write_event(AudioStart(rate=RATE, width=WIDTH, channels=CHANNELS).event(), writer)

    silence_chunk = b"\x00\x00" * CHUNK
    for _ in range(WARMUP_CHUNKS):
        await async_write_event(
            AudioChunk(audio=silence_chunk, rate=RATE, width=WIDTH, channels=CHANNELS).event(), writer
        )

    q = queue.Queue()
    done = {"flag": False}
    stream_ready = threading.Event()

    def callback(indata, frames, t, status):
        q.put(bytes(indata))

    def producer():
        with sd.RawInputStream(samplerate=RATE, blocksize=CHUNK, dtype="int16", channels=CHANNELS, callback=callback):
            time.sleep(0.3)
            stream_ready.set()
            while not done["flag"]:
                time.sleep(0.05)

    threading.Thread(target=producer, daemon=True).start()
    stream_ready.wait()
    print("[Micro actif] En attente du mot de réveil...")

    async def sender():
        while not done["flag"]:
            try:
                chunk = q.get_nowait()
            except queue.Empty:
                await asyncio.sleep(0.02)
                continue
            await async_write_event(AudioChunk(audio=chunk, rate=RATE, width=WIDTH, channels=CHANNELS).event(), writer)

    task = asyncio.create_task(sender())

    while True:
        event = await async_read_event(reader)
        if event is None or Detection.is_type(event.type):
            break

    done["flag"] = True
    task.cancel()
    writer.close()


def record_until_silence() -> bytes:
    frames = []
    recent_amplitudes = []
    silence_start = None
    start_time = time.time()
    q = queue.Queue()

    def callback(indata, f, t, status):
        q.put(bytes(indata))

    with sd.RawInputStream(samplerate=RATE, blocksize=CHUNK, dtype="int16", channels=CHANNELS, callback=callback):
        while True:
            chunk = q.get()
            frames.append(chunk)
            amplitude = np.abs(np.frombuffer(chunk, dtype=np.int16).astype(np.int32)).mean()

            recent_amplitudes.append(amplitude)
            if len(recent_amplitudes) > 3:
                recent_amplitudes.pop(0)
            smoothed = sum(recent_amplitudes) / len(recent_amplitudes)

            elapsed = time.time() - start_time

            if elapsed < GRACE_PERIOD_S:
                pass
            elif smoothed < SILENCE_THRESHOLD:
                if silence_start is None:
                    silence_start = time.time()
                elif time.time() - silence_start > SILENCE_DURATION_S:
                    break
            else:
                silence_start = None

            if elapsed > MAX_RECORD_S:
                break
    return b"".join(frames)


async def transcribe(pcm: bytes) -> str:
    reader, writer = await asyncio.open_connection(WHISPER_HOST, WHISPER_PORT)
    await async_write_event(AudioStart(rate=RATE, width=WIDTH, channels=CHANNELS).event(), writer)
    step = CHUNK * WIDTH
    for i in range(0, len(pcm), step):
        await async_write_event(AudioChunk(audio=pcm[i:i+step], rate=RATE, width=WIDTH, channels=CHANNELS).event(), writer)
    await async_write_event(AudioStop().event(), writer)

    text = ""
    while True:
        event = await async_read_event(reader)
        if event is None:
            break
        if Transcript.is_type(event.type):
            text = Transcript.from_event(event).text
            break
    writer.close()
    return text


async def synthesize(text: str):
    reader, writer = await asyncio.open_connection(PIPER_HOST, PIPER_PORT)
    await async_write_event(Synthesize(text=text).event(), writer)
    chunks = []
    rate, width, channels = RATE, WIDTH, CHANNELS
    while True:
        event = await async_read_event(reader)
        if event is None:
            break
        if AudioStart.is_type(event.type):
            s = AudioStart.from_event(event)
            rate, width, channels = s.rate, s.width, s.channels
        elif AudioChunk.is_type(event.type):
            chunks.append(AudioChunk.from_event(event).audio)
        elif AudioStop.is_type(event.type):
            break
    writer.close()
    return b"".join(chunks), rate, width, channels


def play(pcm: bytes, rate: int, width: int, channels: int):
    audio_np = np.frombuffer(pcm, dtype="int16")
    sd.play(audio_np, samplerate=rate)
    sd.wait()


async def main():
    while True:
        await wait_for_wake_word()
        print("[Ecoute] Parlez...")
        pcm = record_until_silence()
        print("[Ecoute] Terminé, traitement en cours...")

        text = await transcribe(pcm)
        print(f"[STT] -> {text}")
        if not text.strip():
            reply = "Je n'ai pas compris votre demande, parlez plus fort."
            print(f"[Serveur] -> {reply}")
            pcm_out, rate, width, channels = await synthesize(reply)
            play(pcm_out, rate, width, channels)
            continue

        try:
            resp = requests.post(SERVER_URL, json={"text": text}, timeout=60)
            print(f"[debug] raw response: {resp.text}")
            reply = resp.json().get("reply", "Action impossible.")
        except requests.RequestException as e:
            print(f"[Erreur serveur] {e}")
            reply = "Je n'arrive pas à contacter le serveur."
        print(f"[Serveur] -> {reply}")

        pcm_out, rate, width, channels = await synthesize(reply)
        play(pcm_out, rate, width, channels)


if __name__ == "__main__":
    asyncio.run(main())