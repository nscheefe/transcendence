package game

import (
	"time"
)

func initGame(id int) *Game {
	game := &Game{
		id:           id,
		loopInterval: time.NewTicker(time.Second / 20),
		state: state{
			Ball:      position{X: 0, Y: 0, Z: 0},
			BallSpeed: speed{X: initialBallSpeed, Z: initialBallSpeed},
			Paddle1:   position{X: 0, Y: 0, Z: -9},
			Paddle2:   position{X: 0, Y: 0, Z: 9},
			Points:    points{Player1: 0, Player2: 0},
			KeyState:  make(map[int]map[string]bool),
			Direction: 1,
		},
		Clients: make(map[int]Clients, 10),
		State:   GameStatePending,
	}

	go func() {
		for range game.loopInterval.C {
			gameLoop(game)
		}
	}()

	return game
}
