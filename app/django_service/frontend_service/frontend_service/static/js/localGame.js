let gameStarted = false;
let gameLoopInterval;
const gameState = {
    ball: { x: 0, y: 0, z: 0 },
    ballSpeed: { x: 0.1, z: 0.1 },
    paddle1: { x: 0, y: 0, z: -9 },
    paddle2: { x: 0, y: 0, z: 9 },
    points: { player1: 0, player2: 0 },
    keyState: {},
    direction: 1
};

function resetBall() {
    gameState.ball = { x: 0, y: 0, z: 0 };
    // Limit the angle to avoid steep angles
    const minAngle = Math.PI / 6; // 30 degrees
    const maxAngle = Math.PI / 3; // 60 degrees
    const randomAngle = Math.random() * (maxAngle - minAngle) + minAngle;
    const speed = 0.1; // Initial speed
    // Randomly choose the direction (left or right)
    const direction = Math.random() < 0.5 ? 1 : -1;
    gameState.ballSpeed = {
        x: speed * Math.cos(randomAngle) * direction,
        z: speed * Math.sin(randomAngle)
    };
}

function checkWinner(winningScore = 10) {
    if (gameState.points.player1 >= winningScore || gameState.points.player2 >= winningScore) {
        gameStarted = false;
        gameState.type = 'gameOver';
        clearInterval(gameLoopInterval);
    }
}

function updatePaddlePositions() {
    if (gameState.keyState['ArrowLeft'] && gameState.paddle1.x < 4.5) {
        gameState.paddle1.x += 0.1;
    }
    if (gameState.keyState['ArrowRight'] && gameState.paddle1.x > -4.5) {
        gameState.paddle1.x -= 0.1;
    }
    if (gameState.keyState['a'] && gameState.paddle2.x > -4.5) {
        gameState.paddle2.x -= 0.1;
    }
    if (gameState.keyState['d'] && gameState.paddle2.x < 4.5) {
        gameState.paddle2.x += 0.1;
    }
}

let winningScore = 10;

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
        gameState.direction = gameState.ballSpeed.z > 0 ? -1 : 1; // Update direction
        const impactPoint = gameState.ball.x - gameState.paddle1.x;
        gameState.ballSpeed.x += impactPoint * 0.05;
    }
    if (gameState.ball.z >= 8.5 && gameState.ball.z <= 9 && gameState.ball.x >= gameState.paddle2.x - 1 && gameState.ball.x <= gameState.paddle2.x + 1) {
        gameState.ballSpeed.z = -gameState.ballSpeed.z;
        gameState.direction = gameState.ballSpeed.z > 0 ? -1 : 1; // Update direction
        const impactPoint = gameState.ball.x - gameState.paddle2.x;
        gameState.ballSpeed.x += impactPoint * 0.05;
    }

    // Ball out of bounds (reset position and update points)
    if (gameState.ball.z <= -10) {
        gameState.points.player2 += 1;
        resetBall();
        checkWinner(winningScore);
    } else if (gameState.ball.z >= 10) {
        gameState.points.player1 += 1;
        resetBall();
        checkWinner(winningScore);
    }
}


function startLocalGame(winning_Score) {
    gameStarted = true;
    winningScore = winning_Score;
    gameLoopInterval = setInterval(gameLoop, 1000 / 90); // 60 times per second
}

function updateLocalGameState(key, state) {
    gameState.keyState[key] = state;
}

function getLocalGameState() {
    return gameState;
}

export { startLocalGame, updateLocalGameState, getLocalGameState };
