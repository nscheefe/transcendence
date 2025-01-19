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
		log.Println("GRPC: Failed to create auth client: ", err)
	}
	log.Println("GRPC: Auth client created")

	GameCon, err = NewGameClient("game_service:50051")
	if err != nil {
		log.Println("GRPC: Failed to create game client: ", err)
	}
	log.Println("GRPC: Game client created")
}

func CloseClients() {
	AuthCon.Close()
	GameCon.Close()
}
