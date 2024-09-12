	import * as THREE from 'three';

	function createScene() {
		const scene = new THREE.Scene();
		return scene;
	}

	function createCamera() {
		const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
		camera.position.set(10, 15, 0);
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

	function handleBallMovement(ball, ballSpeed, paddle1, paddle2) {
		ball.position.x += ballSpeed.x;
		ball.position.z += ballSpeed.z;

		// Ball collision with walls (left/right)
		if (ball.position.x <= -4.5 || ball.position.x >= 4.5) {
			ballSpeed.x = -ballSpeed.x;
		}

		// Ball collision with paddles
		if (ball.position.z <= -8.5 && ball.position.x >= paddle1.position.x - 1 && ball.position.x <= paddle1.position.x + 1) {
			ballSpeed.z = -ballSpeed.z;
		}
		if (ball.position.z >= 8.5 && ball.position.x >= paddle2.position.x - 1 && ball.position.x <= paddle2.position.x + 1) {
			ballSpeed.z = -ballSpeed.z;
		}

		// Ball out of bounds (reset position)
		if (ball.position.z <= -10 || ball.position.z >= 10) {
			ball.position.set(0, 0.5, 0);
			ballSpeed.x = 0;
			ballSpeed.z = 0;
		}
	}

	function handlePaddleMovement(event, paddle1, paddle2, ballSpeed) {
		switch (event.key) {
			case 'ArrowLeft':
				if (paddle1.position.x > -4.5) paddle1.position.x -= 0.5;
				break;
			case 'ArrowRight':
				if (paddle1.position.x < 4.5) paddle1.position.x += 0.5;
				break;
			case 'a':
				if (paddle2.position.x > -4.5) paddle2.position.x -= 0.5;
				break;
			case 'd':
				if (paddle2.position.x < 4.5) paddle2.position.x += 0.5;
				break;
			case ' ':
				ballSpeed.x = 0.05;
				ballSpeed.z = 0.05;
				break;
		}
	}

	function animate(renderer, scene, camera, ball, ballSpeed, paddle1, paddle2) {
		function render() {
			requestAnimationFrame(render);
			handleBallMovement(ball, ballSpeed, paddle1, paddle2);
			renderer.render(scene, camera);
		}
		render();
	}

	function main() {
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

		let ballSpeed = { x: 0.05, z: 0.05 };

		window.addEventListener('keydown', (event) => handlePaddleMovement(event, paddle1, paddle2, ballSpeed));

		animate(renderer, scene, camera, ball, ballSpeed, paddle1, paddle2);
	}

	main();
