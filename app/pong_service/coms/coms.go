package coms

import (
	"fmt"
	"net/http"
	"server-side-pong/game"
	"sync"

	"github.com/gorilla/websocket"
)

var (
	mu sync.Mutex

	upgrader = websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true
		},
	}

	clients  = make(map[int]*websocket.Conn)
	gameList = make(map[int]*game.Game)
)

func HandleConnection(w http.ResponseWriter, r *http.Request) {
	cookie, _ := r.Cookie("jwt_token")

	user_id, err := handshake(cookie.Value)
	if err != nil {
		errorResponse(w, err.Error(), err, http.StatusUnauthorized)
		return
	}

	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		errorResponse(w, err.Error(), err, http.StatusInternalServerError)
		return
	}

	clients[user_id] = ws
	defer ws.Close()
	fmt.Println("Client connected:", user_id)
}

func disconnectClient(user_id int) {
	mu.Lock()
	for _, game := range gameList {
		if game.Clients[user_id] != nil {
			delete(game.Clients, user_id)
		}
	}
	delete(clients, user_id)
	mu.Unlock()
}
