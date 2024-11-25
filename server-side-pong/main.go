package main

import (
    "fmt"
    "math"
    "net/http"
    "sync"
    "time"
    "github.com/gorilla/websocket"
)

const (
    port           = ":4000"
    winningPoints  = 10
    initialBallSpeed float32 = 0.15
    maxAngleVariation = 25 * (math.Pi / 180) // 25 degrees in radians
)

var (
    gameStarted      = false
    gameLoopInterval *time.Ticker
    gameState        = GameState{
        Ball:      Position{X: 0, Y: 0, Z: 0},
        BallSpeed: Speed{X: initialBallSpeed, Z: initialBallSpeed},
        Paddle1:   Position{X: 0, Y: 0, Z: -9},
        Paddle2:   Position{X: 0, Y: 0, Z: 9},
        Points:    Points{Player1: 0, Player2: 0},
        KeyState:  make(map[string]bool),
        Direction: 1,
    }
    upgrader = websocket.Upgrader{
        CheckOrigin: func(r *http.Request) bool {
            return true
        },
    }
    clients = make(map[*websocket.Conn]*Client)
    mu      sync.Mutex
)

type Client struct {
    conn *websocket.Conn
    role string // "paddle1" or "paddle2"
}

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
    Ball      Position         `json:"ball"`
    BallSpeed Speed            `json:"ballSpeed"`
    Paddle1   Position         `json:"paddle1"`
    Paddle2   Position         `json:"paddle2"`
    Points    Points           `json:"points"`
    KeyState  map[string]bool  `json:"keyState"`
    Direction int              `json:"direction"`
}

func main() {
    http.HandleFunc("/", handleConnections)
    fmt.Println("WebSocket server is running on ws://localhost" + port)
    err := http.ListenAndServe(port, nil)
    if err != nil {
        fmt.Println("ListenAndServe: ", err)
    }
}
