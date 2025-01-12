package game

import (
	"fmt"
	"net/http"
)

func errorResponse(w http.ResponseWriter, message string, err error, statusCode int) {
	fmt.Println(err)
	w.WriteHeader(statusCode)
	w.Write([]byte(message))
}

func logGame(game *Game, message ...any) {
	fmt.Println("Game ", game.id, ": ", fmt.Sprint(message...))
}
