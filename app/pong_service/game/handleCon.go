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

	websockets.HandleConnection(w, r, user_id, game.Clients[user_id].msgReceived, game.Clients[user_id].connected, game.Clients[user_id].disconnected, game.info.Id)
}

var games = make(map[int]*Game)

func handshake(r *http.Request) (int, *Game, error) {
	token, err_token := r.Cookie("jwt_token")
	if err_token != nil {
		return 0, nil, errors.New("jwt_token is required: " + err_token.Error())
	}

	userID, err := grpc.AuthCon.GetUserIDFromJwtToken(token.Value)
	if err != nil {
		return 0, nil, errors.New("invalid jwt token")
	}

	gameIDStr := r.URL.Query().Get("gameId")
	var gameID int
	if gameIDStr != "" {
		gameID, err = strconv.Atoi(gameIDStr)
		if err != nil {
			return 0, nil, errors.New("invalid game ID")
		}
	} else {
		game, err := grpc.GameCon.GetOnGoingGameByUser(int32(userID))
		if err != nil {
			return 0, nil, errors.New("no ongoing game found for user " + strconv.Itoa(int(userID)) + ": " + err.Error())
		}
		gameID = int(game.Id)
		if games[gameID] == nil {
			games[gameID] = initGame(gameID, game)
		}
	}

	if games[gameID] == nil {
		game, err := grpc.GameCon.GetGameByID(int32(gameID))
		if err != nil {
			return 0, nil, errors.New("game not found: " + err.Error())
		}
		if game.Finished {
			return 0, nil, errors.New("game is finished")
		}
		games[gameID] = initGame(gameID, game)
	}

	return int(userID), games[gameID], nil
}
