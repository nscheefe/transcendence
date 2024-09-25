import * as THREE from 'three';
import { createScene, createCamera, createRenderer, createLights, createTable,createTextMesh } from './scene';
import { createPaddle } from './paddle';
import { createBall } from './ball';
import { createWebSocket, socket } from './websocket';
import { animate } from './animation';
import { handleKeyState } from './input';

let font;
let player1TextMesh, player2TextMesh;

function main() {
  if (socket) {
    socket.close();
  }

  const scene = createScene();
  const camera = createCamera();
  const renderer = createRenderer();
  createLights(scene);
  createTable(scene);

  const paddle1 = createPaddle(0x0000ff, 0, -9);
  const paddle2 = createPaddle(0x0000ff, 0, 9);
  scene.add(paddle1);
  scene.add(paddle2);

  const ball = createBall();
  scene.add(ball);

  const loader = new THREE.FontLoader();
  loader.load('https://threejs.org/examples/fonts/helvetiker_regular.typeface.json', (loadedFont) => {
    font = loadedFont;
    player1TextMesh = createTextMesh('Player 1: 0', 1, 0xffffff, { x: -5, y: 1, z: -9 });
    player2TextMesh = createTextMesh('Player 2: 0', 1, 0xffffff, { x: -5, y: 1, z: 9 });
    scene.add(player1TextMesh);
    scene.add(player2TextMesh);

	console.log("Player 1 Text Mesh " + player1TextMesh);
	//  window.addEventListener('keydown', (event) => handlePaddleMovement(event, paddle1, paddle2));
	window.addEventListener('keydown', handleKeyState);
	window.addEventListener('keyup', handleKeyState);

	createWebSocket(ball, paddle1, paddle2, player1TextMesh, player2TextMesh);

	animate(renderer, scene, camera, ball, paddle1, paddle2);
	});
}

export { socket, font };

main();
