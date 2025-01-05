package game

import (
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

type position struct {
	X float32 `json:"x"`
	Y float32 `json:"y"`
	Z float32 `json:"z"`
}

type speed struct {
	X float32 `json:"x"`
	Z float32 `json:"z"`
}

type points struct {
	Player1 int `json:"player1"`
	Player2 int `json:"player2"`
}

type GameState int

const (
	GameStatePending GameState = iota
	GameStateInProgress
	GameStateFinished
	GameStatePaused
)

type state struct {
	Ball      position                `json:"ball"`
	BallSpeed speed                   `json:"ballSpeed"`
	Paddle1   position                `json:"paddle1"`
	Paddle2   position                `json:"paddle2"`
	Points    points                  `json:"points"`
	KeyState  map[int]map[string]bool `json:"keyState"`
	Direction int                     `json:"direction"`
}

type Game struct {
	id           int
	Mu           sync.Mutex
	Clients      map[int]*websocket.Conn
	State        GameState
	loopInterval *time.Ticker
	state        state
}
