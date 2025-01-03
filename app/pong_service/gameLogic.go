package main

import (
	"math"
	"math/rand"
	"time"
)

func resetBall() {
	randomX := (rand.Float32() - 0.5) * 9
	var randomZ float32 = 0.0

	gameState.Ball = Position{X: randomX, Y: 0.5, Z: randomZ}

	baseAngle := math.Pi / 2
	if rand.Float64() < 0.5 {
		baseAngle = -math.Pi / 2
	}
	randomAngle := baseAngle + (rand.Float64()*2-1)*maxAngleVariation
	gameState.BallSpeed = Speed{
		X: initialBallSpeed * float32(math.Cos(randomAngle)),
		Z: initialBallSpeed * float32(math.Sin(randomAngle)),
	}
	gameState.Direction = 1
	if gameState.BallSpeed.Z < 0 {
		gameState.Direction = -1
	}
}

func checkWinner() {
	if gameState.Points.Player1 >= winningPoints || gameState.Points.Player2 >= winningPoints {
		gameStarted = false
		gameLoopInterval.Stop()
		broadcast(map[string]interface{}{
			"type":   "gameOver",
			"winner": 1,
		})
		if gameState.Points.Player2 >= winningPoints {
			broadcast(map[string]interface{}{
				"type":   "gameOver",
				"winner": 2,
			})
		}
		gameState.Points.Player1 = 0
		gameState.Points.Player2 = 0
	}
}

func updatePaddlePositions() {
	mu.Lock()
	defer mu.Unlock()
	for _, client := range clients {
		if client.role == "paddle1" {
			if gameState.KeyState["ArrowLeft"] && gameState.Paddle1.X > -4.5 {
				gameState.Paddle1.X -= 0.1
			}
			if gameState.KeyState["ArrowRight"] && gameState.Paddle1.X < 4.5 {
				gameState.Paddle1.X += 0.1
			}
		} else if client.role == "paddle2" {
			if gameState.KeyState["a"] && gameState.Paddle2.X > -4.5 {
				gameState.Paddle2.X -= 0.1
			}
			if gameState.KeyState["d"] && gameState.Paddle2.X < 4.5 {
				gameState.Paddle2.X += 0.1
			}
		}
	}
}

func gameLoop() {
	if !gameStarted {
		return
	}

	updatePaddlePositions()

	gameState.Ball.X += gameState.BallSpeed.X
	gameState.Ball.Z += gameState.BallSpeed.Z

	if gameState.Ball.X <= -4.5 || gameState.Ball.X >= 4.5 {
		gameState.BallSpeed.X = -gameState.BallSpeed.X
	}

	if gameState.Ball.Z <= -8.5 && gameState.Ball.Z >= -9 && gameState.Ball.X >= gameState.Paddle1.X-1 && gameState.Ball.X <= gameState.Paddle1.X+1 {
		gameState.BallSpeed.Z = -gameState.BallSpeed.Z
		impactPoint := gameState.Ball.X - gameState.Paddle1.X
		gameState.BallSpeed.X += impactPoint * 0.05
		gameState.Direction = 1
		if gameState.BallSpeed.Z < 0 {
			gameState.Direction = -1
		}
	}
	if gameState.Ball.Z >= 8.5 && gameState.Ball.Z <= 9 && gameState.Ball.X >= gameState.Paddle2.X-1 && gameState.Ball.X <= gameState.Paddle2.X+1 {
		gameState.BallSpeed.Z = -gameState.BallSpeed.Z
		impactPoint := gameState.Ball.X - gameState.Paddle2.X
		gameState.BallSpeed.X += impactPoint * 0.05
		gameState.Direction = 1
		if gameState.BallSpeed.Z < 0 {
			gameState.Direction = -1
		}
	}

	if gameState.Ball.Z <= -10 {
		gameState.Points.Player2++
		resetBall()
		checkWinner()
	} else if gameState.Ball.Z >= 10 {
		gameState.Points.Player1++
		resetBall()
		checkWinner()
	}

	broadcast(map[string]interface{}{
		"type":      "updateState",
		"ball":      gameState.Ball,
		"paddle1":   gameState.Paddle1,
		"paddle2":   gameState.Paddle2,
		"points":    gameState.Points,
		"direction": gameState.Direction,
	})
}

func startGame() {
	gameStarted = true
	gameLoopInterval = time.NewTicker(time.Second / 60)
	go func() {
		for range gameLoopInterval.C {
			gameLoop()
		}
	}()
	broadcast(map[string]interface{}{
		"type": "gameStart",
	})
}
