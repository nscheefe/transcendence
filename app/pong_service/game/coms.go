package game

import (
	"fmt"
	"net/http"

	"github.com/gorilla/websocket"
)

var (
	upgrader = websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true
		},
	}

	gameList = make(map[int]*Game)
)

func HandleConnection(w http.ResponseWriter, r *http.Request) {
	user_id, game, err := handshake(r)
	if err != nil {
		errorResponse(w, err.Error(), err, http.StatusUnauthorized)
		return
	}

	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		errorResponse(w, err.Error(), err, http.StatusInternalServerError)
		return
	}
	defer ws.Close()

	game.Mu.Lock()
	game.Clients[user_id] = ws

	fmt.Println("Client connected:", user_id)

	if game.State == GameStatePending && len(game.Clients) == 2 {
		game.Mu.Unlock()
		start(game)
	} else {
		game.Mu.Unlock()
	}

	for {
		var msg map[string]interface{}
		err := ws.ReadJSON(&msg)
		game.Mu.Lock()
		if game.State != GameStateInProgress {
			game.Mu.Unlock()
			break
		}
		game.Mu.Unlock()
		if err != nil {
			disconnectClient(user_id, game)
			break
		}

		handleInput(user_id, game, msg)
	}
}

func disconnectClient(user_id int, game *Game) {
	game.Mu.Lock()
	if game.Clients[user_id] != nil {
		delete(game.Clients, user_id)
	}
	if len(game.Clients) < 2 {
		game.State = GameStateFinished
		gameList[game.id] = nil
	}
	game.Mu.Unlock()
	fmt.Println("Client disconnected:", user_id)
}

func broadcast(game *Game, message map[string]interface{}) {
	game.Mu.Lock()

	for user_id, client := range game.Clients {
		err := client.WriteJSON(message)
		if err != nil {
			fmt.Println("Error broadcasting message:", err)
			game.Mu.Unlock()
			disconnectClient(user_id, game)
			game.Mu.Lock()
		}
	}

	game.Mu.Unlock()
}
