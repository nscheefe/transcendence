package game

import (
	"fmt"
	"math"
	"math/rand/v2"
)

func gameLoop(game *Game) {
	game.Mu.Lock()

	if len(game.Clients) != 2 || game.State != GameStateInProgress {
		game.loopInterval.Stop()
		game.Mu.Unlock()
		return
	}

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
		resetBall(game)
		checkWinner(game)
	} else if game.state.Ball.Z >= 10 {
		game.state.Points.Player1++
		resetBall(game)
		checkWinner(game)
	}

	game.Mu.Unlock()

	broadcast(game, map[string]interface{}{
		"type":      "updateState",
		"ball":      game.state.Ball,
		"paddle1":   game.state.Paddle1,
		"paddle2":   game.state.Paddle2,
		"points":    game.state.Points,
		"direction": game.state.Direction,
	})
}

func updatePaddlePositions(game *Game) {
	for _, keyState := range game.state.KeyState {
		if keyState["ArrowLeft"] && game.state.Paddle1.X > -4.5 {
			game.state.Paddle1.X -= 0.1
		}
		if keyState["ArrowRight"] && game.state.Paddle1.X < 4.5 {
			game.state.Paddle1.X += 0.1
		}
		if keyState["a"] && game.state.Paddle2.X > -4.5 {
			game.state.Paddle2.X -= 0.1
		}
		if keyState["d"] && game.state.Paddle2.X < 4.5 {
			game.state.Paddle2.X += 0.1
		}
	}
}

func resetBall(game *Game) {
	randomX := (rand.Float32() - 0.5) * 9
	var randomZ float32 = 0.0

	game.state.Ball = position{X: randomX, Y: 0.5, Z: randomZ}

	baseAngle := math.Pi / 2
	if rand.Float64() < 0.5 {
		baseAngle = -math.Pi / 2
	}
	randomAngle := baseAngle + (rand.Float64()*2-1)*maxAngleVariation
	game.state.BallSpeed = speed{
		X: initialBallSpeed * float32(math.Cos(randomAngle)),
		Z: initialBallSpeed * float32(math.Sin(randomAngle)),
	}
	game.state.Direction = 1
	if game.state.BallSpeed.Z < 0 {
		game.state.Direction = -1
	}
}

func checkWinner(game *Game) {
	if game.state.Points.Player1 >= winningPoints || game.state.Points.Player2 >= winningPoints {
		game.State = GameStateFinished
		game.Mu.Unlock()
		broadcast(game, map[string]interface{}{
			"type":   "gameOver",
			"winner": 1,
		})
		game.Mu.Lock()
		if game.state.Points.Player2 >= winningPoints {
			game.Mu.Unlock()
			broadcast(game, map[string]interface{}{
				"type":   "gameOver",
				"winner": 2,
			})
			game.Mu.Lock()
		}
		fmt.Println("Game over")
	}
}
