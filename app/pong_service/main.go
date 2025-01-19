package main

import (
	"fmt"
	"net/http"
	"server-side-pong/game"
	"server-side-pong/grpc"
)

const (
	port = ":4000"
)

func main() {
	game.StartSender()
	grpc.InitClients()
	defer grpc.CloseClients()

	http.HandleFunc("/", game.HandleConnection)
	fmt.Println("WebSocket server is running on ws://localhost" + port)
	err := http.ListenAndServe(port, nil)
	if err != nil {
		panic(err)
	}
}
