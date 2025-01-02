package grpc

import (
	"context"
	"fmt"
	pb "server-side-pong/grpc/protos"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"
	"google.golang.org/protobuf/types/known/timestamppb"
)

type GameClient struct {
	client pb.GameServiceClient
	conn   *grpc.ClientConn
}

func NewGameClient(address string) (*GameClient, error) {
	conn, err := grpc.Dial(address, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, fmt.Errorf("failed to connect: %v", err)
	}

	client := pb.NewGameServiceClient(conn)
	return &GameClient{
		client: client,
		conn:   conn,
	}, nil
}

func (c *GameClient) Close() error {
	return c.conn.Close()
}

func (c *GameClient) CreateGame(playerAID, playerBID int32) (*pb.Game, error) {
	req := &pb.CreateGameRequest{
		State:         "initial",
		PointsPlayerA: 0,
		PointsPlayerB: 0,
		PlayerAId:     playerAID,
		PlayerBId:     playerBID,
	}

	return c.client.CreateGame(context.Background(), req)
}

func (c *GameClient) StartGame(gameID int32) (*pb.StartGameResponse, error) {
	req := &pb.StartGameRequest{
		GameId: gameID,
	}

	return c.client.StartGame(context.Background(), req)
}

func (c *GameClient) GetGame(gameID int32) (*pb.Game, error) {
	req := &pb.GetGameRequest{
		GameId: gameID,
	}

	return c.client.GetGame(context.Background(), req)
}

func (c *GameClient) GetOngoingGames() ([]*pb.Game, error) {
	req := &pb.GetOngoingGamesRequest{}

	resp, err := c.client.GetOngoingGames(context.Background(), req)
	if err != nil {
		return nil, err
	}

	return resp.Games, nil
}

func (c *GameClient) HandleGameFinished(gameID int32, pointsA, pointsB, winnerID int32) error {
	req := &pb.GameFinishedRequest{
		GameId:         gameID,
		PointsPlayerA:  pointsA,
		PointsPlayerB:  pointsB,
		WinnerPlayerId: winnerID,
	}

	_, err := c.client.HandleGameFinished(context.Background(), req)
	return err
}

func (c *GameClient) GetGameEvent(eventID int32) (*pb.GameEvent, error) {
	req := &pb.GetGameEventRequest{
		GameEventId: eventID,
	}

	return c.client.GetGameEvent(context.Background(), req)
}

func (c *GameClient) CreateGameEvent(gameID int32, eventType string, eventData string, timestamp *timestamppb.Timestamp) (*pb.GameEvent, error) {
	req := &pb.CreateGameEventRequest{
		GameId:    gameID,
		EventType: eventType,
		EventData: eventData,
		Timestamp: timestamp,
	}

	return c.client.CreateGameEvent(context.Background(), req)
}
