const WebSocket = require('ws');

const wss = new WebSocket.Server({ port: 4000 });

const WINNING_POINTS = 10;

let gameStarted = false;
let gameLoopInterval;
const gameState = {
  ball: { x: 0, y: 0, z: 0 },
  ballSpeed: { x: 0.1 , z: 0.1 },
  paddle1: { x: 0, y: 0, z: -9 },
  paddle2: { x: 0, y: 0, z: 9 },
  points: { player1: 0, player2: 0 },
  keyState: {}
};

function resetBall() {
	// Randomize ball position within a range
	const randomX = (Math.random() - 0.5) * 9; // Random value between -4.5 and 4.5
	const randomZ = 0; // Start in the middle of the field

	gameState.ball = { x: randomX, y: 0.5, z: randomZ };

	// Randomize ball direction with a maximum of 25 degrees variation towards paddles
	const maxAngleVariation = 25 * (Math.PI / 180); // Convert 25 degrees to radians
	const baseAngle = Math.random() < 0.5 ? Math.PI / 2 : -Math.PI / 2; // Either 90 degrees (towards player 2) or -90 degrees (towards player 1)
	const randomAngle = baseAngle + (Math.random() * 2 - 1) * maxAngleVariation; // Random angle within ±25 degrees of baseAngle
	const speed = 0.1; // Initial speed
	gameState.ballSpeed = {
	  x: speed * Math.cos(randomAngle),
	  z: speed * Math.sin(randomAngle)
	};
  }

function checkWinner() {
  if (gameState.points.player1 >= WINNING_POINTS || gameState.points.player2 >= WINNING_POINTS) {
	gameStarted = false;
	clearInterval(gameLoopInterval);
	broadcast({ type: 'gameOver', winner: gameState.points.player1 >= WINNING_POINTS ? 1 : 2 });
	gameState.points.player1 = 0;
	gameState.points.player2 = 0;
  }
}

function updatePaddlePositions() {
  if (gameState.keyState['ArrowLeft'] && gameState.paddle1.x > -4.5) {
    gameState.paddle1.x -= 0.1;
  }
  if (gameState.keyState['ArrowRight'] && gameState.paddle1.x < 4.5) {
    gameState.paddle1.x += 0.1;
  }
  if (gameState.keyState['a'] && gameState.paddle2.x > -4.5) {
    gameState.paddle2.x -= 0.1;
  }
  if (gameState.keyState['d'] && gameState.paddle2.x < 4.5) {
    gameState.paddle2.x += 0.1;
  }
}

function gameLoop() {
  if (!gameStarted) return;

  updatePaddlePositions();

  gameState.ball.x += gameState.ballSpeed.x;
  gameState.ball.z += gameState.ballSpeed.z;

  // Ball collision with walls (left/right)
  if (gameState.ball.x <= -4.5 || gameState.ball.x >= 4.5) {
    gameState.ballSpeed.x = -gameState.ballSpeed.x;
  }

  // Ball collision with paddles
  if (gameState.ball.z <= -8.5 && gameState.ball.z >= -9 && gameState.ball.x >= gameState.paddle1.x - 1 && gameState.ball.x <= gameState.paddle1.x + 1) {
    gameState.ballSpeed.z = -gameState.ballSpeed.z;
    const impactPoint = gameState.ball.x - gameState.paddle1.x;
    gameState.ballSpeed.x += impactPoint * 0.05;
  }
  if (gameState.ball.z >= 8.5 && gameState.ball.z <= 9 && gameState.ball.x >= gameState.paddle2.x - 1 && gameState.ball.x <= gameState.paddle2.x + 1) {
    gameState.ballSpeed.z = -gameState.ballSpeed.z;
    const impactPoint = gameState.ball.x - gameState.paddle2.x;
    gameState.ballSpeed.x += impactPoint * 0.05;
  }

  // Ball out of bounds (reset position and update points)
  if (gameState.ball.z <= -10) {
    gameState.points.player2 += 1;
    resetBall();
    checkWinner();
  } else if (gameState.ball.z >= 10) {
    gameState.points.player1 += 1;
    resetBall();
    checkWinner();
  }

  broadcast({
    type: 'updateState',
    ball: { x: gameState.ball.x, z: gameState.ball.z },
    paddle1: { x: gameState.paddle1.x },
    paddle2: { x: gameState.paddle2.x },
    points: gameState.points
  });
}

function startGame() {
  gameStarted = true;
  gameLoopInterval = setInterval(gameLoop, 1000 / 60); // 60 times per second
}

function broadcast(message) {
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(message));
    }
  });
}

wss.on('connection', (ws) => {
  console.log('Client connected');

  ws.on('message', (message) => {
    const data = JSON.parse(message);
    if (data.type === 'keyState') {
      gameState.keyState[data.key] = data.state;
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected');
  });

  if (!gameStarted) {
    startGame();
  }
});

console.log('WebSocket server is running on ws://localhost:4000');
