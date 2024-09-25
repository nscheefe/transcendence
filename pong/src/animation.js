import { keyState } from './input';
import { socket } from './websocket';

let isAnimating = false;

export function animate(renderer, scene, camera) {
  if (isAnimating) return; // Prevent multiple animation loops
  isAnimating = true;

  function render() {
    renderer.render(scene, camera);
    requestAnimationFrame(render);
  }
  render();
}

//function updatePaddlePosition(paddle1, paddle2) { //  For Local later
//  if (keyState['ArrowLeft'] && paddle1.position.x > -4.5) {
//    paddle1.position.x -= 0.1;
//    sendPaddlePosition(1, paddle1.position.x);
//  }
//  if (keyState['ArrowRight'] && paddle1.position.x < 4.5) {
//    paddle1.position.x += 0.1;
//    sendPaddlePosition(1, paddle1.position.x);
//  }
//  if (keyState['a'] && paddle2.position.x > -4.5) {
//    paddle2.position.x -= 0.1;
//    sendPaddlePosition(2, paddle2.position.x);
//  }
//  if (keyState['d'] && paddle2.position.x < 4.5) {
//    paddle2.position.x += 0.1;
//    sendPaddlePosition(2, paddle2.position.x);
//  }
//}

export function updatePaddlePositionFromServer(paddle1, paddle2, state) {
	if (state.paddle1 !== undefined) {
	  paddle1.position.x = state.paddle1.x;
	}
	if (state.paddle2 !== undefined) {
	  paddle2.position.x = state.paddle2.x;
	}
  }

function sendPaddlePosition(player, x) {
  if (socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify({ type: 'movePaddle', player, x }));
  }
}
