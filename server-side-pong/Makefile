run:
	go run main.go

protoc:
	protoc --go_out=. \
		--go-grpc_out=. \
		grpc/protos/game.proto \
		grpc/protos/gameEvent.proto \
		grpc/protos/auth.proto