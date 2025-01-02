run:
	go run main.go

protoc:
	protoc --go_out=. \
		--go-grpc_out=. \
		grpc/game.proto \
		grpc/gameEvent.proto