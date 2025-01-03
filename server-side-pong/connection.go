package main

import (
	"fmt"
	"net/http"
    "github.com/gorilla/websocket"
)

func broadcast(message interface{}) {
    mu.Lock()
    defer mu.Unlock()
    for _, client := range clients {
        err := client.conn.WriteJSON(message)
        if err != nil {
            client.conn.Close()
            delete(clients, client.conn)
        }
    }
}

func handleConnections(w http.ResponseWriter, r *http.Request) {
    ws, err := upgrader.Upgrade(w, r, nil)
    if err != nil {
        fmt.Println("Failed to upgrade connection:", err)
        return
    }
    defer ws.Close()

    clientIP := r.RemoteAddr
    fmt.Printf("Client connected from %s\n", clientIP)

    // Read the initial handshake message
    var handshakeMessage map[string]interface{}
    if err := ws.ReadJSON(&handshakeMessage); err != nil {
        fmt.Println("Failed to read handshake message:", err)
        return
    }

    clientId, ok := handshakeMessage["clientId"].(string)
    if !ok {
        fmt.Println("Invalid handshake message: clientId missing or invalid")
        return
    }
	fmt.Println("Client ID:", clientId)

    mu.Lock()
    for _, client := range clients {
        if client.conn.RemoteAddr().String() == clientIP {
            ws.WriteMessage(websocket.TextMessage, []byte("Already connected"))
            mu.Unlock()
            return
        }
    }

    if len(clients) >= 2 {
        ws.WriteMessage(websocket.TextMessage, []byte("Game is full"))
        mu.Unlock()
        return
    }

    var role string
    if len(clients) == 0 {
        role = "paddle1"
    } else {
        role = "paddle2"
    }

    clients[ws] = &Client{conn: ws, role: role}
    mu.Unlock()

    fmt.Printf("Client connected as %s\n", role)

    // Send handshake response with the assigned role
    ws.WriteJSON(map[string]interface{}{
        "type": "handshakeResponse",
        "role": role,
    })

    if len(clients) == 2 && !gameStarted {
        startGame()
    }

    for {
        var msg map[string]interface{}
        err := ws.ReadJSON(&msg)
        if err != nil {
            fmt.Println("Client disconnected:", err)
            mu.Lock()
            delete(clients, ws)
            mu.Unlock()
            break
        }

        if msg["type"] == "keyState" {
            key := msg["key"].(string)
            state := msg["state"].(bool)
            mu.Lock()
            gameState.KeyState[key] = state
            mu.Unlock()
        }
    }
}

