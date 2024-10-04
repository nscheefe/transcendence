import * as THREE from 'three';
import { createScene, createCamera, createRenderer, createLights, createTable,createTextMesh, createTextOnTable, updateTextMeshOrientation } from './scene';
import { createPaddle } from './paddle';
import { createBall } from './ball';
import { createWebSocket, socket } from './websocket';
import { animate } from './animation';
import { handleKeyState } from './input';

import { effectComposer, initVaporwaveScene } from './vaporwave.js';


let font;
let player1TextMesh, player2TextMesh;

function main() {

	if (socket) {
		socket.close();
	}

	// Sizes
	const sizes = {
		width: window.innerWidth,
		height: window.innerHeight,
	};

	// INITIALIZATION

	//Scene
	let scene = createScene();
	let camera = createCamera();
	let renderer = createRenderer();
	createLights(scene);
	initVaporwaveScene(scene, camera, renderer, sizes);

	// Objects
	const table = createTable();
	const ball = createBall();
	const paddle1 = createPaddle(0x0000ff, 0, -9);
	const paddle2 = createPaddle(0x0000ff, 0, 9);
	scene.add(table);
	scene.add(ball);
	scene.add(paddle1);
	scene.add(paddle2);

	window.addEventListener("resize", () => {
		sizes.width = window.innerWidth;
		sizes.height = window.innerHeight;

		camera.aspect = sizes.width / sizes.height;
		camera.updateProjectionMatrix();

		renderer.setSize(sizes.width, sizes.height);
		renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));

		effectComposer.setSize(sizes.width, sizes.height);
		effectComposer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
	});

	const loader = new THREE.FontLoader();
	loader.load('https://threejs.org/examples/fonts/helvetiker_regular.typeface.json', (loadedFont) => {
		font = loadedFont;
		player1TextMesh = createTextOnTable(font, scene, '0', 6, table);
		player2TextMesh = createTextOnTable(font, scene, '0', -6, table);

		window.addEventListener('keydown', handleKeyState);
		window.addEventListener('keyup', handleKeyState);

		createWebSocket(ball, paddle1, paddle2, player1TextMesh, player2TextMesh, scene, camera);

		animate(renderer, scene, camera, ball, paddle1, paddle2);
	});
}

export {
	socket,
	font
};

main();
