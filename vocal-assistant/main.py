import os
from fastapi import FastAPI
from pydantic import BaseModel
from ollama import Client as OllamaClient

import registry
import mqtt_control

OLLAMA_HOST = os.getenv("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")

app = FastAPI()
client = OllamaClient(host=OLLAMA_HOST)

TYPE_LABELS = {
    "switch": "prise",
    "light": "ampoule",
    "cover": "volet",
    "lock": "serrure",
    "climate": "climatisation",
}

TYPE_GENDER = {
    "switch": "f",
    "light": "f",
    "cover": "m",
    "lock": "f",
    "climate": "f",
}


@app.on_event("startup")
def startup():
    mqtt_control.connect()


class CommandRequest(BaseModel):
    text: str


class CommandResponse(BaseModel):
    reply: str


def build_tools(devices: dict) -> list[dict]:
    tools = []
    for name, dev in devices.items():
        for action_name in dev["actions"]:
            tools.append({
                "type": "function",
                "function": {
                    "name": f"{name}__{action_name}",
                    "description": f"{action_name} sur {name}",
                    "parameters": {"type": "object", "properties": {}},
                },
            })
    return tools


def build_system_prompt(devices: dict) -> str:
    if devices:
        device_list = "\n".join(
            f"- {name} ({TYPE_LABELS.get(dev.get('device_type', ''), dev.get('device_type', '?'))})"
            for name, dev in devices.items()
        )
    else:
        device_list = "(aucun appareil disponible actuellement)"

    return (
        "Tu es l'assistant vocal d'une maison connectée. Ton seul rôle est "
        "de contrôler les appareils listés ci-dessous, rien d'autre.\n\n"
        "APPAREILS RÉELLEMENT DISPONIBLES (liste exacte et complète) :\n"
        f"{device_list}\n\n"
        "PRINCIPES GÉNÉRAUX (à appliquer à toute demande, même celles non "
        "explicitement prévues ci-dessous) :\n\n"
        "A. Périmètre strict. Tu ne sais faire qu'une seule chose : agir sur "
        "les appareils listés ci-dessus. Toute demande qui n'est pas une "
        "instruction claire de contrôle d'un de ces appareils (météo, "
        "recette, blague, question générale, calcul, conversation, etc.) "
        "est hors de ton périmètre. Dans ce cas, n'utilise aucun outil et "
        "réponds en une phrase naturelle et variée que tu es un assistant "
        "domotique qui contrôle uniquement les appareils connectés de la "
        "maison. Varie la formulation d'une fois à l'autre plutôt que de "
        "répéter toujours la même phrase.\n\n"
        "B. Correspondance stricte. N'utilise un outil que si le nom "
        "d'appareil mentionné par l'utilisateur correspond réellement (marque, "
        "pièce, mots-clés en commun) à un appareil de la liste ci-dessus. Le "
        "fait qu'un seul appareil d'un type donné existe ne justifie jamais "
        "de le choisir par défaut : sans correspondance claire, n'utilise "
        "aucun outil.\n\n"
        "C. Jamais de noms inventés ou hors contexte. Ne mentionne le nom "
        "précis d'un appareil (marque, pièce, nom complet) QUE si tu viens "
        "réellement d'agir dessus via un outil dans cette même réponse. Dans "
        "tous les autres cas (hors périmètre, appareil non trouvé, type "
        "absent, question sans rapport comme la météo, une recette, une "
        "réparation, etc.), reste sur l'expression générique \"appareils "
        "connectés\" — ne cite JAMAIS de type précis (\"une prise\", \"une "
        "lampe\"), de nom précis, de marque ou de pièce. Exemple à ne JAMAIS "
        "faire : si on te demande de l'aide pour réparer une voiture, ne "
        "réponds JAMAIS quelque chose comme \"je peux contrôler la prise de "
        "la chambre Lidl\" ou \"je peux contrôler des prises\" — dis "
        "seulement que tu contrôles les appareils connectés de la maison, "
        "sans aucun détail.\n\n"
        "D. Plusieurs appareils à la fois. Si la demande concerne plusieurs "
        "appareils (\"ferme les volets et éteins tout\", \"la lampe et la "
        "prise\"), appelle un outil séparé pour chaque appareil concerné "
        "dans la même réponse.\n\n"
        "E. Honnêteté. Ne confirme jamais une action que tu n'as pas "
        "réellement exécutée via un outil.\n\n"
        "F. Style. Réponds toujours entièrement en français courant, sans "
        "aucun mot anglais, en une phrase courte et naturelle."
    )


def phrase_action_result(name: str, device_type: str, action_name: str, confirmed: bool) -> str:
    gender = TYPE_GENDER.get(device_type, "f")
    article = "Le" if gender == "m" else "La"

    if not confirmed:
        return f"{article} {name} n'a pas répondu, action impossible."

    participles = {
        "turn_on": "allumé" if gender == "m" else "allumée",
        "turn_off": "éteint" if gender == "m" else "éteinte",
    }
    participle = participles.get(action_name, "modifié" if gender == "m" else "modifiée")
    return f"{article} {name} a été {participle}."


def execute(tool_name: str, devices: dict) -> str:
    name, action_name = tool_name.rsplit("__", 1)
    dev = devices.get(name)
    if not dev:
        return f"Je n'ai pas trouvé d'appareil correspondant à {name}."

    action = dev["actions"][action_name]
    confirmed = mqtt_control.send_and_confirm(
        dev["topic_set"], action["payload"],
        dev["topic_state"], action["expected_field"], action["expected_value"],
    )

    return phrase_action_result(name, dev.get("device_type", ""), action_name, confirmed)


@app.post("/api/voice/command", response_model=CommandResponse)
def command(req: CommandRequest):
    devices = registry.get_devices()
    tools = build_tools(devices)

    response = client.chat(
        model=OLLAMA_MODEL,
        messages=[
            {"role": "system", "content": build_system_prompt(devices)},
            {"role": "user", "content": req.text},
        ],
        tools=tools,
    )
    message = response["message"]
    tool_calls = message.get("tool_calls") or []

    if not tool_calls:
        return CommandResponse(reply=message.get("content", "Action impossible."))

    results = [execute(call["function"]["name"], devices) for call in tool_calls]
    return CommandResponse(reply=" ".join(results))


@app.get("/api/voice/health")
def health():
    return {"status": "ok"}