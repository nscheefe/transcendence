package main

import (
	"fmt"
	"net/http"
)

const (
	port = ":4000"
)

func main() {
	http.HandleFunc("/", handleConnections)
	fmt.Println("WebSocket server is running on ws://localhost" + port)
	err := http.ListenAndServe(port, nil)
	if err != nil {
		panic(err)
	}
}
