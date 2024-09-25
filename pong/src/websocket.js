let socket;
import { updateTextMesh } from './scene';
import { updatePaddlePositionFromServer } from './animation';

export function createWebSocket(ball, paddle1, paddle2, player1TextMesh, player2TextMesh) {
	if (!socket || socket.readyState === WebSocket.CLOSED) {
	  socket = new WebSocket('ws://localhost:4000');

	  socket.onopen = () => {
		console.log('Connected to the server');
	  };

	  socket.onmessage = (event) => {
		const state = JSON.parse(event.data);
		console.log('Received state:', state);
		if (state.type === 'updateState') {
		  updatePaddlePositionFromServer(paddle1, paddle2, state);
		  if (state.ball !== undefined) {
			ball.position.set(state.ball.x, 0, state.ball.z);
		  }
		  if (state.points !== undefined) {
			updateTextMesh(player1TextMesh, `Player 1: ${state.points.player1}`);
			updateTextMesh(player2TextMesh, `Player 2: ${state.points.player2}`);
		  }
		}
	  };

	  socket.onclose = () => {
		console.log('Disconnected from the server');
		// Optionally, implement reconnection logic
		setTimeout(() => createWebSocket(ball, paddle1, paddle2, player1TextMesh, player2TextMesh), 1000); // Attempt to reconnect after 1 second
	  };
	}
}

export { socket };
