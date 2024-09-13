const express = require('express');
const http = require('http');
const WebSocket = require('ws');

const app = express();
const server = http.createServer(app);


const wss = new WebSocket.Server({ port: 4000 });

let gameState = {
  ball: { x: 0, y: 0, z: 0 },
  paddle1: { x: 0, y: 0, z: -9 },
  paddle2: { x: 0, y: 0, z: 9 },
  ballSpeed: { x: 0.05, z: 0.05 }
};

wss.on('connection', (ws) => {
  console.log('New client connected');
  ws.send(JSON.stringify({ type: 'updateBall', ...gameState.ball }));

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
  });
});

function broadcast(data) {
  wss.clients.forEach((client) => {
    if (client.readyState === WebSocket.OPEN) {
      client.send(JSON.stringify(data));
    }
  });
}

function gameLoop() {
  gameState.ball.x += gameState.ballSpeed.x;
  gameState.ball.z += gameState.ballSpeed.z;

  // Ball collision with walls (left/right)
  if (gameState.ball.x <= -4.5 || gameState.ball.x >= 4.5) {
    gameState.ballSpeed.x = -gameState.ballSpeed.x;
  }

  // Ball collision with paddles
  if (gameState.ball.z <= -8.5 && gameState.ball.x >= gameState.paddle1.x - 1 && gameState.ball.x <= gameState.paddle1.x + 1) {
    gameState.ballSpeed.z = -gameState.ballSpeed.z;
  }
  if (gameState.ball.z >= 8.5 && gameState.ball.x >= gameState.paddle2.x - 1 && gameState.ball.x <= gameState.paddle2.x + 1) {
    gameState.ballSpeed.z = -gameState.ballSpeed.z;
  }

  // Ball out of bounds (reset position)
  if (gameState.ball.z <= -10 || gameState.ball.z >= 10) {
    gameState.ball = { x: 0, y: 0.5, z: 0 };
    gameState.ballSpeed = { x: 0.05, z: 0.05 };
  }

  broadcast({ type: 'updateBall', ...gameState.ball });
}

setInterval(gameLoop, 1000 / 60); // 60 times per second
