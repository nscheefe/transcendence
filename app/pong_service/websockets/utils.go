package websockets

import (
	"fmt"
	"net/http"
)

func errorResponse(w http.ResponseWriter, message string, err error, statusCode int) {
	fmt.Println(err)
	w.WriteHeader(statusCode)
	w.Write([]byte(message))
}

func logWebsocket(message ...any) {
	fmt.Println("Websocket: " + fmt.Sprint(message...))
}
