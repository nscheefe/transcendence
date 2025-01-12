package game

import "server-side-pong/websockets"

var (
	MsgToSend    = make(chan websockets.MsgToSend, 100)
	MsgReceived  = make(chan websockets.MsgReceived, 100)
	Connected    = make(chan int, 100)
	Disconnected = make(chan int, 100)
)

func StartGameManager() {
	go websockets.StartBroadcast(MsgToSend)
}
