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

    socket.onopen = () => handleOpen();
    socket.onmessage = handleMessage(ball, paddle1, paddle2, player1TextMesh, player2TextMesh, scene, camera);
    socket.onclose = handleClose(ball, paddle1, paddle2, player1TextMesh, player2TextMesh, scene, camera);
    socket.onerror = handleError;
}

function handleOpen() {
    console.log('Connected to the server');
    isConnecting = false;
    // Send handshake message with a placeholder client ID
    const clientId = 'placeholder-client-id';
    socket.send(JSON.stringify({ type: 'handshake', clientId }));
}

function handleMessage(ball, paddle1, paddle2, player1TextMesh, player2TextMesh, scene, camera) {
    return (event) => {
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
}

function handleClose(ball, paddle1, paddle2, player1TextMesh, player2TextMesh, scene, camera) {
    return (event) => {
        console.log('Disconnected from the server', event);
        isConnecting = false;
        // Optionally, implement reconnection logic
        setTimeout(() => createWebSocket(ball, paddle1, paddle2, player1TextMesh, player2TextMesh, scene, camera), 1000); // Attempt to reconnect after 1 second
    };
}

function handleError(error) {
    console.error('WebSocket error:', error);
    isConnecting = false;
}

export {
    socket,
    direction
};
