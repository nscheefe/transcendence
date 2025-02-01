package websockets

import (
	"net/http"
	"sync"

	"server-side-pong/grpc"
	"github.com/gorilla/websocket"
)

const DisconnectedState string = "DISCONNECTED"

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

func HandleConnection(w http.ResponseWriter, r *http.Request, id int, msgReceived chan<- MsgReceived, connected chan<- int, disconnected chan<- int, gameID int) {
	ws, err := upgrader.Upgrade(w, r, nil)
	if err != nil {
		errorResponse(w, err.Error(), err, http.StatusInternalServerError)
		return
	}
	defer ws.Close()

	logWebsocket("Client connected: ", id)

	mu.Lock()
	clients[id] = ws
	mu.Unlock()
	select {
	case connected <- id:
	default:
		logWebsocket("Error sending message to connected channel ", id)
	}

	for {
		var msg map[string]interface{}
		err := ws.ReadJSON(&msg)
		if err != nil {
			logWebsocket("Error reading message from client ", id, ": ", err.Error())
			break
		}

		if !sendMessageSafely(msgReceived, MsgReceived{Id: id, Msg: msg}) {
			logWebsocket("Error sending message to recieved channel ", id)
			break
		}
	}

	logWebsocket("Client disconnected: ", id)

	mu.Lock()
	delete(clients, id)
	mu.Unlock()

	if !sendMessageSafelyInt(disconnected, id) {
		logWebsocket("Error sending message to disconnected channel ", id)
	}

	_, err = grpc.GameCon.UpdateGameState(int32(gameID), DisconnectedState)
	if err != nil {
		logWebsocket("GRPCerror updating game state: ", err.Error())
	}
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
				logWebsocket("Error sending message to client ", msg.Id, ": ", err.Error())
			}
		}
		mu.Unlock()
	}
}

func sendMessageSafely(ch chan<- MsgReceived, msg MsgReceived) bool {
	defer func() {
		if r := recover(); r != nil {
			// Channel was closed
			return
		}
	}()

	select {
	case ch <- msg:
		return true
	default:
		return false
	}
}

func sendMessageSafelyInt(ch chan<- int, msg int) bool {
	defer func() {
		if r := recover(); r != nil {
			// Channel was closed
			return
		}
	}()

	select {
	case ch <- msg:
		return true
	default:
		return false
	}
}
