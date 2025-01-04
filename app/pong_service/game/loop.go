package game

import (
	"math"
	"math/rand/v2"
)

func gameLoop(game *Game) {

	updatePaddlePositions(game)

	game.state.Ball.X += game.state.BallSpeed.X
	game.state.Ball.Z += game.state.BallSpeed.Z

	if game.state.Ball.X <= -4.5 || game.state.Ball.X >= 4.5 {
		game.state.BallSpeed.X = -game.state.BallSpeed.X
	}

	if game.state.Ball.Z <= -8.5 && game.state.Ball.Z >= -9 && game.state.Ball.X >= game.state.Paddle1.X-1 && game.state.Ball.X <= game.state.Paddle1.X+1 {
		game.state.BallSpeed.Z = -game.state.BallSpeed.Z
		impactPoint := game.state.Ball.X - game.state.Paddle1.X
		game.state.BallSpeed.X += impactPoint * 0.05
		game.state.Direction = 1
		if game.state.BallSpeed.Z < 0 {
			game.state.Direction = -1
		}
	}
	if game.state.Ball.Z >= 8.5 && game.state.Ball.Z <= 9 && game.state.Ball.X >= game.state.Paddle2.X-1 && game.state.Ball.X <= game.state.Paddle2.X+1 {
		game.state.BallSpeed.Z = -game.state.BallSpeed.Z
		impactPoint := game.state.Ball.X - game.state.Paddle2.X
		game.state.BallSpeed.X += impactPoint * 0.05
		game.state.Direction = 1
		if game.state.BallSpeed.Z < 0 {
			game.state.Direction = -1
		}
	}

	if game.state.Ball.Z <= -10 {
		game.state.Points.Player2++
		resetBall()
		checkWinner()
	} else if game.state.Ball.Z >= 10 {
		game.state.Points.Player1++
		resetBall()
		checkWinner()
	}

	broadcast(map[string]interface{}{
		"type":      "updateState",
		"ball":      game.state.Ball,
		"paddle1":   game.state.Paddle1,
		"paddle2":   game.state.Paddle2,
		"points":    game.state.Points,
		"direction": game.state.Direction,
	})
}

func updatePaddlePositions(game *Game) {
	game.mu.Lock()
	defer game.mu.Unlock()
	if game.state.KeyState["ArrowLeft"] && game.state.Paddle1.X > -4.5 {
		game.state.Paddle1.X -= 0.1
	}
	if game.state.KeyState["ArrowRight"] && game.state.Paddle1.X < 4.5 {
		game.state.Paddle1.X += 0.1
	}
	if game.state.KeyState["a"] && game.state.Paddle2.X > -4.5 {
		game.state.Paddle2.X -= 0.1
	}
	if game.state.KeyState["d"] && game.state.Paddle2.X < 4.5 {
		game.state.Paddle2.X += 0.1
	}
}

func resetBall() {
	randomX := (rand.Float32() - 0.5) * 9
	var randomZ float32 = 0.0

	game.state.Ball = Position{X: randomX, Y: 0.5, Z: randomZ}

	baseAngle := math.Pi / 2
	if rand.Float64() < 0.5 {
		baseAngle = -math.Pi / 2
	}
	randomAngle := baseAngle + (rand.Float64()*2-1)*maxAngleVariation
	game.state.BallSpeed = Speed{
		X: initialBallSpeed * float32(math.Cos(randomAngle)),
		Z: initialBallSpeed * float32(math.Sin(randomAngle)),
	}
	game.state.Direction = 1
	if game.state.BallSpeed.Z < 0 {
		game.state.Direction = -1
	}
}

func checkWinner() {
	if game.state.Points.Player1 >= winningPoints || game.state.Points.Player2 >= winningPoints {
		gameStarted = false
		gameLoopInterval.Stop()
		broadcast(map[string]interface{}{
			"type":   "gameOver",
			"winner": 1,
		})
		if game.state.Points.Player2 >= winningPoints {
			broadcast(map[string]interface{}{
				"type":   "gameOver",
				"winner": 2,
			})
		}
		game.state.Points.Player1 = 0
		game.state.Points.Player2 = 0
	}
}
