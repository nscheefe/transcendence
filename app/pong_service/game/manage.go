package game

import (
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

func InitGame() *Game {
	return &Game{
		Started:      false,
		loopInterval: time.NewTicker(time.Second / 20),
		state: state{
			Ball:      position{X: 0, Y: 0, Z: 0},
			BallSpeed: speed{X: initialBallSpeed, Z: initialBallSpeed},
			Paddle1:   position{X: 0, Y: 0, Z: -9},
			Paddle2:   position{X: 0, Y: 0, Z: 9},
			Points:    points{Player1: 0, Player2: 0},
			KeyState:  make(map[string]bool),
			Direction: 1,
		},
		Clients: make(map[int]*websocket.Conn),
		mu:      sync.Mutex{},
	}
}

func Start(game *Game) {
	game.Started = true
	go func() {
		for range game.loopInterval.C {
			gameLoop()
		}
	}()
}
