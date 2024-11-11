import { updateTextMesh, gameOver } from './scene';
import { updatePaddlePositionFromServer } from './animation';

let socket;
let direction = 1;
let isConnecting = false;

export function createWebSocket(ball, paddle1, paddle2, player1TextMesh, player2TextMesh, scene, camera) {
    if (socket && socket.readyState !== WebSocket.CLOSED) {
        console.log('WebSocket connection already exists');
        return;
    }

    if (isConnecting) {
        console.log('Already attempting to connect to WebSocket server');
        return;
    }

    console.log('Attempting to connect to WebSocket server...');
    isConnecting = true;
    socket = new WebSocket('ws://localhost:4000');

    socket.onopen = () => {
        console.log('Connected to the server');
        isConnecting = false;
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
                updateTextMesh(player1TextMesh, `${state.points.player1}`, camera);
                updateTextMesh(player2TextMesh, `${state.points.player2}`, camera);
            }
            if (state.direction !== undefined) {
                direction = state.direction;
            }
        }
        if (state.type === 'gameOver') {
            console.log('Game Over');
            scene.add(gameOver(state.winner, camera));
        }
    };

    socket.onclose = (event) => {
        console.log('Disconnected from the server', event);
        isConnecting = false;
        // Optionally, implement reconnection logic
        setTimeout(() => createWebSocket(ball, paddle1, paddle2, player1TextMesh, player2TextMesh, scene, camera), 1000); // Attempt to reconnect after 1 second
    };

    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        isConnecting = false;
    };
}

export {
    socket,
    direction
};
