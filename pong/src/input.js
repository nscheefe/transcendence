
let keyState = {};
import { socket } from './websocket';

export function handleKeyState(event) {
	keyState[event.key] = event.type === 'keydown';
	if (socket && socket.readyState === WebSocket.OPEN) {
	  socket.send(JSON.stringify({ type: 'keyState', key: event.key, state: keyState[event.key] }));
	}
}


export { keyState };
