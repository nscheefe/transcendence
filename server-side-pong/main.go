package main

import (
    "fmt"
    "math"
    "math/rand"
    "net/http"
    "sync"
    "time"

    "github.com/gorilla/websocket"
)

const (
    port           = ":4000"
    winningPoints  = 10
    initialBallSpeed = 0.15
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
    clients = make(map[*websocket.Conn]bool)
    mu      sync.Mutex
)

type Position struct {
    X float64 `json:"x"`
    Y float64 `json:"y"`
    Z float64 `json:"z"`
}

type Speed struct {
    X float64 `json:"x"`
    Z float64 `json:"z"`
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

func resetBall() {
    randomX := (rand.Float64() - 0.5) * 9
    randomZ := 0.0

    gameState.Ball = Position{X: randomX, Y: 0.5, Z: randomZ}

    baseAngle := math.Pi / 2
    if rand.Float64() < 0.5 {
        baseAngle = -math.Pi / 2
    }
    randomAngle := baseAngle + (rand.Float64()*2-1)*maxAngleVariation
    gameState.BallSpeed = Speed{
        X: initialBallSpeed * math.Cos(randomAngle),
        Z: initialBallSpeed * math.Sin(randomAngle),
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
    if gameState.KeyState["ArrowLeft"] && gameState.Paddle1.X > -4.5 {
        gameState.Paddle1.X -= 0.1
    }
    if gameState.KeyState["ArrowRight"] && gameState.Paddle1.X < 4.5 {
        gameState.Paddle1.X += 0.1
    }
    if gameState.KeyState["a"] && gameState.Paddle2.X > -4.5 {
        gameState.Paddle2.X -= 0.1
    }
    if gameState.KeyState["d"] && gameState.Paddle2.X < 4.5 {
        gameState.Paddle2.X += 0.1
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
        "type":    "updateState",
        "ball":    gameState.Ball,
        "paddle1": gameState.Paddle1,
        "paddle2": gameState.Paddle2,
        "points":  gameState.Points,
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
}

func broadcast(message interface{}) {
    mu.Lock()
    defer mu.Unlock()
    for client := range clients {
        err := client.WriteJSON(message)
        if err != nil {
            client.Close()
            delete(clients, client)
        }
    }
}

func handleConnections(w http.ResponseWriter, r *http.Request) {
    ws, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        fmt.Println(err)
        return
    }
    defer ws.Close()

    mu.Lock()
    clients[ws] = true
    mu.Unlock()

    fmt.Println("Client connected")

    for {
        var msg map[string]interface{}
        err := ws.ReadJSON(&msg)
        if err != nil {
            fmt.Println("Client disconnected")
            mu.Lock()
            delete(clients, ws)
            mu.Unlock()
            break
        }

        if msg["type"] == "keyState" {
            key := msg["key"].(string)
            state := msg["state"].(bool)
            gameState.KeyState[key] = state
        }
    }

    if !gameStarted {
        startGame()
    }
}

func main() {
    http.HandleFunc("/", handleConnections)
    fmt.Println("WebSocket server is running on ws://localhost" + port)
    err := http.ListenAndServe(port, nil)
    if err != nil {
        fmt.Println("ListenAndServe: ", err)
    }
}
