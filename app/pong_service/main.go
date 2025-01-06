package main

import (
	"fmt"
	"net/http"
	"server-side-pong/game"
)

const (
	port = ":4000"
)

func main() {
	http.HandleFunc("/", game.HandleConnection) // coms.go Handles all incoming WebSocket connections
	fmt.Println("WebSocket server is running on ws://localhost" + port)
	err := http.ListenAndServe(port, nil)
	if err != nil {
		panic(err)
	}
}
