const express = require('express');
const http = require('http');
const WebSocket = require('ws');

const app = express();
const server = http.createServer(app);

const wss = new WebSocket.Server({ port: 4000 });

const WINNING_POINTS = 10;
let clients = [];
let gameStarted = false;

let gameState = {
  ball: { x: 0, y: 0, z: 0 },
  paddle1: { x: 0, y: 0, z: -9 },
  paddle2: { x: 0, y: 0, z: 9 },
  ballSpeed: { x: 0.1, z: 0.1 },
  points: { player1: 0, player2: 0 },
  winner: null
};

wss.on('connection', (ws) => {
  console.log('New client connected');
  clients.push(ws);

  if (clients.length === 2) {
    startGame();
  }

  ws.on('message', (message) => {
    const data = JSON.parse(message);
    if (data.type === 'movePaddle') {
      if (data.player === 1) {
        gameState.paddle1.x = data.x;
      } else {
        gameState.paddle2.x = data.x;
      }
      broadcast({ type: 'movePaddle', player: data.player, x: data.x });
    }
  });

  ws.on('close', () => {
    console.log('Client disconnected');
    clients = clients.filter(client => client !== ws);
  });
});

function broadcast(data) {
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(data));
    }
  });
}

function checkWinner() {
  if (gameState.points.player1 >= WINNING_POINTS) {
    gameState.winner = 'Player 1';
  } else if (gameState.points.player2 >= WINNING_POINTS) {
    gameState.winner = 'Player 2';
  }
}

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

function gameLoop() {
  if (!gameStarted) return;

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

//  broadcast({ type: 'updateBall', ...gameState.ball });
  broadcast({ type: 'updateState', ...gameState });
}

function startGame() {
	if (gameStarted) return;
	gameStarted = true;
	setInterval(gameLoop, 1000 / 60); // 60 times per second
}

server.listen(3000, () => {
  console.log('Server is listening on port 3000');
});
