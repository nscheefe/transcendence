let gameStarted = false;
let gameLoopInterval;
const gameState = {
    ball: { x: 0, y: 0, z: 0 },
    ballSpeed: { x: 0.1, z: 0.1 },
    paddle1: { x: 0, y: 0, z: -9 },
    paddle2: { x: 0, y: 0, z: 9 },
    points: { player1: 0, player2: 0 },
    keyState: {}
};

function resetBall() {
    gameState.ball = { x: 0, y: 0, z: 0 };
    const randomAngle = Math.random() * Math.PI * 2;
    const speed = 0.1; // Initial speed
    gameState.ballSpeed = {
        x: speed * Math.cos(randomAngle),
        z: speed * Math.sin(randomAngle)
    };
}

function checkWinner() {
    // Implement winner check logic here
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
}

function startLocalGame() {
    gameStarted = true;
    gameLoopInterval = setInterval(gameLoop, 1000 / 60); // 60 times per second
}

function updateLocalGameState(key, state) {
    gameState.keyState[key] = state;
}

function getLocalGameState() {
    return gameState;
}

export { startLocalGame, updateLocalGameState, getLocalGameState };
