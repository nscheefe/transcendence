package websockets

import (
	"fmt"
	"net/http"
	"sync"

	"github.com/gorilla/websocket"
)

var (
	upgrader = websocket.Upgrader{
		CheckOrigin: func(r *http.Request) bool {
			return true
		},
	}

	clients = make(map[int]*websocket.Conn)
	mu      = sync.Mutex{}
)

type MsgToSend struct {
	Id  int
	Msg interface{}
}

func HandleConnection(w http.ResponseWriter, r *http.Request, id int, msgReceived chan<- MsgReceived, connected chan<- int, disconnected chan<- int) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		errorResponse(w, err.Error(), err, http.StatusInternalServerError)
		return
	}
	defer ws.Close()

	mu.Lock()
	clients[id] = ws
	mu.Unlock()
	connected <- id
	fmt.Println("Client connected: ", id)

	for {
		var msg map[string]interface{}
		err := ws.ReadJSON(&msg)
		if err != nil {
			fmt.Println("Error reading message from client", id, ":", err.Error())
			break
		}

		select {
		case msgReceived <- MsgReceived{Id: id, Msg: msg}:
		default:
			fmt.Println("Error sending message to recieved channel", id, ":", err.Error())
			return
		}
	}

	mu.Lock()
	delete(clients, id)
	mu.Unlock()
	disconnected <- id
	fmt.Println("Client disconnected: ", id)
}

func StartBroadcast(messages <-chan MsgToSend) {
	go HandleBroadcast(messages)
}

func HandleBroadcast(messages <-chan MsgToSend) {
	for msg := range messages {
		mu.Lock()
		if conn, exists := clients[msg.Id]; exists {
			err := conn.WriteJSON(msg.Msg)
			if err != nil {
				fmt.Println("Error sending message to client", msg.Id, ":", err.Error())
			}
		}
		mu.Unlock()
	}
}
