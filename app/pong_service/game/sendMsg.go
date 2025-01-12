package game

import "server-side-pong/websockets"

var (
	MsgToSend = make(chan websockets.MsgToSend, 100)
)

func StartSender() {
	websockets.StartBroadcast(MsgToSend)
}
