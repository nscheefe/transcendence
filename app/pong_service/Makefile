run:
	go run main.go

protoc:
	protoc --go_out=. --go_opt=paths=source_relative \
		--go-grpc_out=. --go-grpc_opt=paths=source_relative \
		grpc/protos/game.proto \
		grpc/protos/gameEvent.proto \
		grpc/protos/auth.proto

