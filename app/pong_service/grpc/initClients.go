package grpc

import "log"

var (
	AuthCon *AuthClient
	GameCon *GameClient
)

func InitClients() {
	var err error
	AuthCon, err = NewAuthClient("auth_service:50051")
	if err != nil {
		log.Println("Failed to create auth client: ", err)
	}

	GameCon, err = NewGameClient("game_service:50051")
	if err != nil {
		log.Println("Failed to create game client: ", err)
	}
}

func CloseClients() {
	AuthCon.Close()
	GameCon.Close()
}
