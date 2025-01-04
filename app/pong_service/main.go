package main

import (
	"fmt"
	"math"
	"net/http"
	"sync"
	"time"

	"github.com/gorilla/websocket"
)

type Client struct {
	conn *websocket.Conn
	role string // "paddle1" or "paddle2"
}

func main() {
	http.HandleFunc("/", handleConnections)
	fmt.Println("WebSocket server is running on ws://localhost" + port)
	err := http.ListenAndServe(port, nil)
	if err != nil {
		fmt.Println("ListenAndServe: ", err)
	}
}
