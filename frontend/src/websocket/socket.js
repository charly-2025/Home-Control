let socket = null;

export function connect(onMessage) {
  if (
    socket &&
    (socket.readyState === WebSocket.OPEN ||
      socket.readyState === WebSocket.CONNECTING)
  ) {
    return socket;
  }

  const protocol = window.location.protocol === "https:" ? "wss" : "ws";

  const ws = new WebSocket(`${protocol}://${window.location.host}/ws`);
  socket = ws;

  ws.onopen = () => {
    console.log("WebSocket connected");
  };

  ws.onclose = () => {
    console.log("WebSocket disconnected");
    if (socket === ws) {
      socket = null;
    }
  };

  ws.onerror = (error) => {
    console.error(error);
  };

  ws.onmessage = (event) => {
    onMessage(JSON.parse(event.data));
  };

  return ws;
}

export function disconnect() {
  if (!socket) {
    return;
  }

  const ws = socket;
  socket = null;

  ws.onopen = null;
  ws.onclose = null;
  ws.onerror = null;
  ws.onmessage = null;

  if (
    ws.readyState === WebSocket.OPEN ||
    ws.readyState === WebSocket.CONNECTING
  ) {
    ws.close();
  }
}
