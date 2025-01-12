package game

import (
	"errors"
	"net/http"
	"strconv"
)

func HandleConnection(w http.ResponseWriter, r *http.Request) {
	user_id, game, err := handshake(r)
	if err != nil {
		errorResponse(w, err.Error(), err, http.StatusUnauthorized)
		return
	}
}

func handshake(r *http.Request) (int, *Game, error) {
	_, err_token := r.Cookie("jwt_token")
	user_id, err_user_id := r.Cookie("user_id")
	game_id, err_game_id := r.Cookie("game_id")

	if err_token != nil {
		if err_user_id == nil && err_game_id == nil {
			user_id, _ := strconv.Atoi(user_id.Value)
			game_id, _ := strconv.Atoi(game_id.Value)
			return user_id, genTestGame(game_id), nil
		}
		return 0, nil, errors.New("jwt_token is required")
	}

	return 0, nil, nil
}

func genTestGame(game_id int) *Game {
	if gameList[game_id] != nil {
		return gameList[game_id]
	}

	gameList[game_id] = initGame(game_id)
	return gameList[game_id]
}
