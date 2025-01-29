import { startLocalGame, updateLocalGameState, getLocalGameState } from './localGame.js';

document.getElementById('close-btn').addEventListener('click', function () {
    if (gameStarted) {
        const confirmClose = confirm("The game is ongoing. Are you sure you want to close?");
        if (!confirmClose) {
            return;
        }
    }
    if (socket) {
        socket.close();
        console.log('WebSocket connection closed');
    }
    document.getElementById('pong-container').style.display = 'none';
    window.location.href = '/home';
});

// Global variables
let font;
let player1TextMesh, player2TextMesh;
let effectComposer1, effectComposer2, vaporPlane, vaporPlane2, vaporPlane3;
let keyState = {};
let isAnimating = false;
let direction = 1;
let socket = null;
let isConnecting = false;
let gameStarted = false;
let player;
let scene, camera1, camera2, renderer1, renderer2, ball, paddle1, paddle2;

function createTextMesh(text, size, color, position) {
    const geometry = new THREE.TextGeometry(text, {
        font: font,
        size: size,
        height: 0.1,
    });
    const material = new THREE.MeshBasicMaterial({
        color: color
    });
    const mesh = new THREE.Mesh(geometry, material);
    mesh.position.set(position.x, position.y, position.z);
    return mesh;
}

function gameOver(winner) {
    const gameOverview = document.getElementById('game-overview');
    const gameOverviewTitle = document.getElementById('game-overview-title');
    const gameOverviewResult = document.getElementById('game-overview-result');

    gameOverviewTitle.textContent = 'Game Over';
    if (winner === player) {
        gameOverviewResult.textContent = 'You won!';
    } else {
        gameOverviewResult.textContent = 'You lost!';
    }

    gameOverview.style.display = 'block';

    // Close the WebSocket connection
    if (socket) {
        socket.close();
        console.log('WebSocket connection closed');
    }
}

// WebSocket setup
function createWebSocket() {
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
    socket = new WebSocket(`wss://${document.location.hostname}/game`);

    socket.onopen = () => {
        console.log('Connected to the server');
        isConnecting = false;
    };

    socket.onmessage = (event) => {
        const state = JSON.parse(event.data);
        // console.log('Received state:', state)
        if (state.type === 'gameStarted') {
            updateScene()
            player = state.player;
            console.log('Game started');
            gameStarted = true;
            updateCamera(); // Update the camera position
        }
        if (state.type === 'updateState') {
            if (!gameStarted) {
                gameStarted = true;
                updateScene();
            }
            if (state.paddle1 !== undefined) {
                paddle1.position.x = state.paddle1.x;
            }
            if (state.paddle2 !== undefined) {
                paddle2.position.x = state.paddle2.x;
            }
            if (state.ball !== undefined) {
                ball.position.set(state.ball.x, 0.5, state.ball.z);
            }
            if (state.points !== undefined) {
                updateTextMesh(player1TextMesh, `${state.points.player1}`, camera1);
                updateTextMesh(player2TextMesh, `${state.points.player2}`, camera2);
            }
            if (state.direction !== undefined) {
                direction = state.direction;
            }
        }
        if (state.type === 'gameOver') {
            gameStarted = false;
            console.log('Game Over');
            gameOver(state.winner);
        }
    };

    socket.onclose = (event) => {
        console.log('Disconnected from the server', event);
        isConnecting = false;
        // Attempt to reconnect after 1 second
        setTimeout(() => createWebSocket(), 1000);
    };

    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        isConnecting = false;
    };
}

function updateTextMesh(mesh, text, camera) {
    if (!mesh) {
        console.log("text mesh is null");
        return;
    }
    if (!font) {
        console.log("Font not loaded yet");
        return;
    }
    const geometry = new THREE.TextGeometry(text, {
        font: font,
        size: 1,
        height: 0.1,
    });
    geometry.computeBoundingBox();
    const boundingBox = geometry.boundingBox;
    const textWidth = boundingBox.max.x - boundingBox.min.x;
    mesh.geometry.dispose();
    mesh.geometry = geometry;
    updateTextMeshOrientation(mesh, camera);
}

function updateTextMeshOrientation(textMesh, camera) {
    if (textMesh) {
        const cameraDirection = new THREE.Vector3();
        camera.getWorldDirection(cameraDirection);
        textMesh.rotation.z = camera.rotation.z;
    }
}

// Constants for vaporwave textures
const TEXTURE_PATH = "https://res.cloudinary.com/dg5nsedzw/image/upload/v1641657168/blog/vaporwave-threejs-textures/grid.png";
const DISPLACEMENT_PATH = "https://res.cloudinary.com/dg5nsedzw/image/upload/v1641657200/blog/vaporwave-threejs-textures/displacement.png";
const METALNESS_PATH = "https://res.cloudinary.com/dg5nsedzw/image/upload/v1641657200/blog/vaporwave-threejs-textures/metalness.png";

// Scene creation functions
function createScene() {
    const scene = new THREE.Scene();
    return scene;
}

function createCamera(player, local = false) {
    const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
    const y = local ? 10 : 5;
    if (player === 1) {
        camera.position.set(0, y, -15);
    } else {
        camera.position.set(0, y, 15);
    }
    camera.lookAt(0, 0, 0);
    return camera;
}

function createRenderer(id, sizes) {
    // Remove any existing canvas elements
    const existingCanvas = document.getElementById(id);
    if (existingCanvas) {
        existingCanvas.remove();
    }

    const renderer = new THREE.WebGLRenderer({
        antialias: true,
        alpha: true,
        canvas: document.createElement('canvas')
    });
    renderer.domElement.id = id;

    // Append the new canvas to the pong-container
    const pongContainer = document.getElementById('pong-container');
    pongContainer.appendChild(renderer.domElement);

    // Set the renderer size to match the parent container
    renderer.setSize(sizes.width, sizes.height);

    renderer.setClearColor(0x000000, 0.5); // Second parameter is the alpha value

    return renderer;
}

function createLights(scene) {
    const ambientLight = new THREE.AmbientLight("#ffffff", 200);
    scene.add(ambientLight);

    const spotlight = new THREE.SpotLight("#d53c3d", 20, 500, Math.PI * 0.1, 5);
    spotlight.position.set(10, 15, 2.2);
    spotlight.target.position.set(-5, 5, 5);
    scene.add(spotlight);
    scene.add(spotlight.target);

    const spotlight2 = new THREE.SpotLight("#d53c3d", 20, 500, Math.PI * 0.1, 5);
    spotlight2.position.set(-10, 15, 2.2);
    spotlight2.target.position.set(5, 5, 5);
    scene.add(spotlight2);
    scene.add(spotlight2.target);
}

function createTable() {
    const tableGeometry = new THREE.PlaneGeometry(10, 20, 1, 2);
    const tableMaterial = new THREE.MeshPhongMaterial({
        color: 0x00ff00,
        transparent: true,
        opacity: 0
    });
    const table = new THREE.Mesh(tableGeometry, tableMaterial);
    table.rotation.x = -Math.PI / 2;
    return table;
}

function createBall() {
    const ballGeometry = new THREE.SphereGeometry(0.5, 32, 32);
    const ballMaterial = new THREE.MeshPhongMaterial({ color: 0xff0000 });
    const ball = new THREE.Mesh(ballGeometry, ballMaterial);
    ball.position.set(0, 0.5, 0);
    return ball;
}

function createPaddle(color, x, z) {
    const paddleGeometry = new THREE.BoxGeometry(2, 0.5, 0.5);
    const paddleMaterial = new THREE.MeshPhongMaterial({
        color: color,
        transparent: true,
        opacity: 0.85
    });
    const paddle = new THREE.Mesh(paddleGeometry, paddleMaterial);
    paddle.position.set(x, 0.25, z);
    return paddle;
}

function createTextOnTable(font, scene, text, offsetY, table) {
    const geometry = new THREE.TextGeometry(text, {
        font: font,
        size: 1,
        height: 0.1,
    });
    const material = new THREE.MeshBasicMaterial({
        color: 0xffffff
    });
    const mesh = new THREE.Mesh(geometry, material);

    geometry.computeBoundingBox();
    const boundingBox = geometry.boundingBox;
    const textWidth = boundingBox.max.x - boundingBox.min.x;

    mesh.position.set(-(textWidth / 2), offsetY, 0);
    table.add(mesh);
    return mesh;
}

function initVaporwaveScene(scene, camera, renderer, sizes, local = false) {
    const fog = new THREE.Fog("#000000", 1, 60);
    scene.fog = fog;

    // Load textures
    const textureLoader = new THREE.TextureLoader();
    const gridTexture = textureLoader.load(TEXTURE_PATH);
    const terrainTexture = textureLoader.load(DISPLACEMENT_PATH);
    const metalnessTexture = textureLoader.load(METALNESS_PATH);

    // Create vaporwave planes
    const geometry = new THREE.PlaneGeometry(20, 40, 24, 24);
    const material = new THREE.MeshStandardMaterial({
        map: gridTexture,
        displacementMap: terrainTexture,
        displacementScale: 8,
        metalnessMap: metalnessTexture,
        metalness: 0.96,
        roughness: 0.5,
    });

    vaporPlane = new THREE.Mesh(geometry, material);
    vaporPlane.rotation.x = -Math.PI * 0.5;
    vaporPlane.position.y = 0.0;
    vaporPlane.position.z = 3;

    vaporPlane2 = new THREE.Mesh(geometry, material);
    vaporPlane2.rotation.x = -Math.PI * 0.5;
    vaporPlane2.position.y = 0.0;
    vaporPlane2.position.z = -37;

    vaporPlane3 = new THREE.Mesh(geometry, material);
    vaporPlane3.rotation.x = -Math.PI * 0.5;
    vaporPlane3.position.y = 0.0;
    vaporPlane3.position.z = 43;

    scene.add(vaporPlane);
    scene.add(vaporPlane2);
    scene.add(vaporPlane3);

    // Post Processing for the first renderer
    effectComposer1 = new THREE.EffectComposer(renderer1);
    effectComposer1.setSize(sizes.width, sizes.height);
    effectComposer1.setPixelRatio(Math.min(window.devicePixelRatio, 2));

    const renderPass1 = new THREE.RenderPass(scene, camera1);
    effectComposer1.addPass(renderPass1);

    const rgbShiftPass1 = new THREE.ShaderPass(THREE.RGBShiftShader);
    rgbShiftPass1.uniforms["amount"].value = 0.0015;
    effectComposer1.addPass(rgbShiftPass1);

    const gammaCorrectionPass1 = new THREE.ShaderPass(THREE.GammaCorrectionShader);
    effectComposer1.addPass(gammaCorrectionPass1);
}

function handleKeyState(event) {
    keyState[event.key] = event.type === 'keydown';

    // Update local game state
    updateLocalGameState(event.key, keyState[event.key]);

    // Send key state to server if WebSocket is open
    if (socket && socket.readyState === WebSocket.OPEN) {
        socket.send(JSON.stringify({ type: 'keyState', key: event.key, state: keyState[event.key] }));
    }

    // Handle local paddle movement for preview
    updatePaddlePosition();
}

function updatePaddlePosition() {
    if (player === 1) {
        if (keyState['ArrowLeft'] && paddle1.position.x > -4.5) {
            paddle1.position.x += 0.1;
        }
        if (keyState['ArrowRight'] && paddle1.position.x < 4.5) {
            paddle1.position.x -= 0.1;
        }
        if (keyState['a'] && paddle1.position.x > -4.5) {
            paddle1.position.x += 0.1;
        }
        if (keyState['d'] && paddle1.position.x < 4.5) {
            paddle1.position.x -= 0.1;
        }
    }
    if (player === 2) {
        if (keyState['ArrowLeft'] && paddle2.position.x > -4.5) {
            paddle2.position.x -= 0.1;
        }
        if (keyState['ArrowRight'] && paddle2.position.x < 4.5) {
            paddle2.position.x += 0.1;
        }
        if (keyState['a'] && paddle2.position.x > -4.5) {
            paddle2.position.x -= 0.1;
        }
        if (keyState['d'] && paddle2.position.x < 4.5) {
            paddle2.position.x += 0.1;
        }
    }
}

function animate() {
    if (isAnimating) return;
    const clock = new THREE.Clock();
    isAnimating = true;
    let timer = 0;

    function render() {
        const elapsedTime = clock.getDelta();
        timer += (direction * elapsedTime);

        // Update vaporwave planes
        vaporPlane.position.z = (timer * 3) % 40;
        vaporPlane2.position.z = ((timer * 3) % 40) - 40;
        vaporPlane3.position.z = ((timer * 3) % 40) + 40;

        effectComposer1.render();
        if (effectComposer2) {
            effectComposer2.render();
        }
        renderer1.render(scene, camera1);
        if (renderer2) {
            renderer2.render(scene, camera2);
        }
        requestAnimationFrame(render);
    }
    render();
}

function updateCamera() {
    if (player === 1) {
        camera1.position.set(0, 10, -15);
        if (camera2) {
            camera2.position.set(0, 10, 15);
        }
    } else {
        camera1.position.set(0, 10, 15);
        if (camera2) {
            camera2.position.set(0, 10, -15);
        }
    }
    camera1.lookAt(0, 0, 0);
    if (camera2) {
        camera2.lookAt(0, 0, 0);
    }
}

function updateScene(local = false) {
    // Remove waiting-message
    const loadingScreen = document.getElementById('waiting-message');
    if (loadingScreen) {
        loadingScreen.remove();
    }
    const pongContainer = document.getElementById('pong-container');
    const sizes = {
        width: pongContainer.clientWidth,
        height: pongContainer.clientHeight,
    };
    if (local)
        sizes.width /= 2;
    // Scene setup
    scene = createScene();
    camera1 = createCamera(2);
    renderer1 = createRenderer('pong-canvas-1', sizes);
    createLights(scene);
    initVaporwaveScene(scene, camera1, renderer1, sizes, local);

    if (local) {
        camera2 = createCamera(1);
        renderer2 = createRenderer('pong-canvas-2', sizes);
        effectComposer2 = new THREE.EffectComposer(renderer2);
        effectComposer2.setSize(sizes.width, sizes.height);
        effectComposer2.setPixelRatio(Math.min(window.devicePixelRatio, 2));

        const renderPass2 = new THREE.RenderPass(scene, camera2);
        effectComposer2.addPass(renderPass2);

        const rgbShiftPass2 = new THREE.ShaderPass(THREE.RGBShiftShader);
        rgbShiftPass2.uniforms["amount"].value = 0.0015;
        effectComposer2.addPass(rgbShiftPass2);

        const gammaCorrectionPass2 = new THREE.ShaderPass(THREE.GammaCorrectionShader);
        effectComposer2.addPass(gammaCorrectionPass2);
    }

    // Create game objects
    const table = createTable();
    ball = createBall();
    paddle1 = createPaddle(0x00babc, 0, -9);
    paddle2 = createPaddle(0x00babc, 0, 9);

    window.paddle1 = paddle1;
    window.paddle2 = paddle2;

    scene.add(table);
    scene.add(ball);
    scene.add(paddle1);
    scene.add(paddle2);

    // Load font and start game
    const loader = new THREE.FontLoader();
    loader.load('https://threejs.org/examples/fonts/helvetiker_regular.typeface.json', (loadedFont) => {
        font = loadedFont;
        player1TextMesh = createTextOnTable(font, scene, '0', 6, table);
        player2TextMesh = createTextOnTable(font, scene, '0', -6, table);

        window.addEventListener('keydown', handleKeyState);
        window.addEventListener('keyup', handleKeyState);

        animate();
    });
}

console.log("pong.js loaded");

function main(local = false) {
    if (local) {
        console.log("local game");
        updateScene(true);
        startLocalGame();
        setInterval(() => {
            const state = getLocalGameState();
            if (state.paddle1 !== undefined) {
                paddle1.position.x = state.paddle1.x;
            }
            if (state.paddle2 !== undefined) {
                paddle2.position.x = state.paddle2.x;
            }
            if (state.ball !== undefined) {
                ball.position.set(state.ball.x, 0.5, state.ball.z);
            }
            if (state.points !== undefined) {
                updateTextMesh(player1TextMesh, `${state.points.player1}`, camera1);
                updateTextMesh(player2TextMesh, `${state.points.player2}`, camera2);
            }
            if (state.direction !== undefined) {
                direction = state.direction;
            }
            if (state.type === 'gameOver') {
                gameStarted = false;
                console.log('Game Over');
                gameOver(state.winner);
            }
        }, 1000 / 120); // 60 times per second
    }
    else {
        console.log("initPongGame called");
        updateScene(false);
        createWebSocket();
    }
}
// Expose the init function to be called externally
window.initPongGame = main;
console.log("initPongGame defined");
