import * as THREE from 'three';

function createScene() {
	const scene = new THREE.Scene();
	return scene;
}

function createCamera() {
	const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
	camera.position.set(0, 15, 10);
	camera.lookAt(0, 0, 0);
	return camera;
}

function createRenderer() {
	const renderer = new THREE.WebGLRenderer({ antialias: true });
	renderer.setSize(window.innerWidth, window.innerHeight);
	document.body.appendChild(renderer.domElement);
	return renderer;
}

	function createLights(scene) {
	const ambientLight = new THREE.AmbientLight(0xffffff, 0.5);
	scene.add(ambientLight);
	const pointLight = new THREE.PointLight(0xffffff, 0.5);
	pointLight.position.set(0, 50, 50);
	scene.add(pointLight);
}

function createTable(scene) {
	const tableGeometry = new THREE.PlaneGeometry(10, 20);
	const tableMaterial = new THREE.MeshPhongMaterial({ color: 0x00ff00 });
	const table = new THREE.Mesh(tableGeometry, tableMaterial);
	table.rotation.x = -Math.PI / 2;  // Make it horizontal
	scene.add(table);
}

function createPaddle(color, x, z) {
	const paddleGeometry = new THREE.BoxGeometry(2, 0.5, 0.5);
	const paddleMaterial = new THREE.MeshPhongMaterial({ color });
	const paddle = new THREE.Mesh(paddleGeometry, paddleMaterial);
	paddle.position.set(x, 0.25, z);
	return paddle;
}

function createBall() {
	const ballGeometry = new THREE.SphereGeometry(0.5, 32, 32);
	const ballMaterial = new THREE.MeshPhongMaterial({ color: 0xff0000 });
	const ball = new THREE.Mesh(ballGeometry, ballMaterial);
	ball.position.set(0, 0.5, 0);
	return ball;
}

let socket;
let font;
const THROTTLE_INTERVAL = 100;
let player1TextMesh, player2TextMesh;
let isAnimating = false;

function createWebSocket( ball, paddle1, paddle2) {
  if (!socket || socket.readyState === WebSocket.CLOSED) {
    socket = new WebSocket('ws://localhost:4000');

    socket.onopen = () => {
      console.log('Connected to the server');
    };

    socket.onmessage = (event) => {
      const state = JSON.parse(event.data);
      console.log('Received state:', state); // Add logging to debug
	if (state.type === 'updateState') {
		if (state.ball !== undefined) {
			ball.position.set(state.ball.x, state.ball.y, state.ball.z);
		}
		if (state.paddle1 !== undefined) {
			paddle1.position.set(state.paddle1.x, state.paddle1.y, state.paddle1.z);
		}
		if (state.paddle2 !== undefined) {
			paddle2.position.set(state.paddle2.x, state.paddle2.y, state.paddle2.z);
		}
		if (state.points !== undefined) {
			updateTextMesh(player1TextMesh, `Player 1: ${state.points.player1}`);
			updateTextMesh(player2TextMesh, `Player 2: ${state.points.player2}`);
		}
	} else if (state.type === 'updateBall') {
        if (state.x !== undefined && state.y !== undefined && state.z !== undefined) {
          ball.position.set(state.x, state.y, state.z);
        } else {
          console.error('Invalid ball state received:', state);
        }
      } else if (state.type === 'movePaddle') {
        if (state.player === 1 && state.x !== undefined) {
          paddle1.position.x = state.x;
        } else if (state.player === 2 && state.x !== undefined) {
          paddle2.position.x = state.x;
        } else {
          console.error('Invalid paddle state received:', state);
        }
      } else if (state.type === 'updatePoints') {
        if (state.points !== undefined) {
          updateTextMesh(player1TextMesh, `Player 1: ${state.points.player1}`);
          updateTextMesh(player2TextMesh, `Player 2: ${state.points.player2}`);
        }
      }
    };

    socket.onclose = () => {
      console.log('Disconnected from the server');
    };
  }
}

function handlePaddleMovement(event, paddle1, paddle2) {
  let move = false;
  let player = 0;
  let x = 0;
  let lastSentTime = 0;

  switch (event.key) {
    case 'ArrowLeft':
      if (paddle1.position.x > -4.5) {
        paddle1.position.x -= 0.5;
        move = true;
        player = 1;
        x = paddle1.position.x;
      }
      break;
    case 'ArrowRight':
      if (paddle1.position.x < 4.5) {
        paddle1.position.x += 0.5;
        move = true;
        player = 1;
        x = paddle1.position.x;
      }
      break;
    case 'a':
      if (paddle2.position.x > -4.5) {
        paddle2.position.x -= 0.5;
        move = true;
        player = 2;
        x = paddle2.position.x;
      }
      break;
    case 'd':
      if (paddle2.position.x < 4.5) {
        paddle2.position.x += 0.5;
        move = true;
        player = 2;
        x = paddle2.position.x;
      }
      break;
  }

  const currentTime = Date.now();
  if (move && socket.readyState === WebSocket.OPEN && currentTime - lastSentTime > THROTTLE_INTERVAL) {
    socket.send(JSON.stringify({ type: 'movePaddle', player, x }));
    lastSentTime = currentTime;
  }
}

function createTextMesh(text, size, color, position) {
  const geometry = new THREE.TextGeometry(text, {
    font: font,
    size: size,
    height: 0.1,
  });
  const material = new THREE.MeshBasicMaterial({ color: color });
  const mesh = new THREE.Mesh(geometry, material);
  mesh.position.set(position.x, position.y, position.z);
  return mesh;
}

function updateTextMesh(mesh, text) {
  const geometry = new THREE.TextGeometry(text, {
    font: font,
    size: 1,
    height: 0.1,
  });
  mesh.geometry.dispose();
  mesh.geometry = geometry;
}

function animate(renderer, scene, camera) {
	if (isAnimating) return;
	isAnimating = true;
  function render() {
    requestAnimationFrame(render);
    renderer.render(scene, camera);
  }
  render();
}

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
  });

  window.addEventListener('keydown', (event) => handlePaddleMovement(event, paddle1, paddle2));

  createWebSocket(ball, paddle1, paddle2);

  animate(renderer, scene, camera, ball, paddle1, paddle2);
}

main();
