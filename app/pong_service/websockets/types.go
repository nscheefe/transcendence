package websockets

type MsgReceived struct {
	Id  int
	Msg map[string]interface{}
}

type SentMsg struct {
	Id  int
	Msg map[string]interface{}
}
