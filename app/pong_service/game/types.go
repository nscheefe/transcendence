package game

import (
	"time"

	"github.com/gorilla/websocket"
)

type Position struct {
	X float32 `json:"x"`
	Y float32 `json:"y"`
	Z float32 `json:"z"`
}

type Speed struct {
	X float32 `json:"x"`
	Z float32 `json:"z"`
}

type Points struct {
	Player1 int `json:"player1"`
	Player2 int `json:"player2"`
}

type GameState struct {
	Ball      Position        `json:"ball"`
	BallSpeed Speed           `json:"ballSpeed"`
	Paddle1   Position        `json:"paddle1"`
	Paddle2   Position        `json:"paddle2"`
	Points    Points          `json:"points"`
	KeyState  map[string]bool `json:"keyState"`
	Direction int             `json:"direction"`
}

type Game struct {
	Started          bool
	gameLoopInterval *time.Ticker
	gameState        GameState
	Clients          map[int]*websocket.Conn
}
