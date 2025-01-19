package game

import (
	"errors"
	"net/http"
	"server-side-pong/grpc"
	"server-side-pong/websockets"
	"strconv"
)

func HandleConnection(w http.ResponseWriter, r *http.Request) {
	user_id, game, err := handshake(r)
	if err != nil {
		errorResponse(w, err.Error(), err, http.StatusUnauthorized)
		return
	}

	game.Clients[user_id] = Clients{
		msgReceived:  make(chan websockets.MsgReceived, 100),
		connected:    make(chan int, 1),
		disconnected: make(chan int, 1),
	}

	websockets.HandleConnection(w, r, user_id, game.Clients[user_id].msgReceived, game.Clients[user_id].connected, game.Clients[user_id].disconnected)
}

var games = make(map[int]*Game)

// var user_id_int int = 0

func handshake(r *http.Request) (int, *Game, error) {
	// user_id_int++
	// if games[1] == nil {
	// 	games[1] = initGame(1)
	// }
	// return user_id_int, games[1], nil
	token, err_token := r.Cookie("jwt_token")
	// _, err_game_id := r.Cookie("game_id")

	if err_token != nil {
		// if err_user_id == nil && err_game_id == nil {
		// 	user_id, _ := strconv.Atoi(user_id.Value)
		// 	// Ensure game is initialized
		// 	if game == nil {
		// 		game = initGame(1) // or appropriate initialization
		// 		if game == nil {
		// 			return 0, nil, errors.New("failed to initialize game")
		// 		}
		// 	}
		// 	return user_id, game, nil
		// }
		return 0, nil, errors.New("jwt_token is required")
	}

	userID, err := grpc.AuthCon.GetUserIDFromJwtToken(token.Value)
	if err != nil {
		return 0, nil, errors.New("invalid jwt token")
	}

	game, err := grpc.GameCon.GetOnGoingGameByUser(int32(userID))
	if err != nil {
		return 0, nil, errors.New("no ongoing game found for user " + strconv.Itoa(int(userID)) + ": " + err.Error())
	}

	gameID := int(game.Id)
	if games[gameID] == nil {
		games[gameID] = initGame(gameID, game)
	}

	return int(userID), games[gameID], nil
}
