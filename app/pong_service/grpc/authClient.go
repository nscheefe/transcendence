package grpc

import (
	"context"
	"fmt"

	"google.golang.org/grpc"
	"google.golang.org/grpc/credentials/insecure"

	pb "server-side-pong/grpc/protos"
)

type AuthClient struct {
	client pb.AuthServiceClient
	conn   *grpc.ClientConn
}

func NewAuthClient(address string) (*AuthClient, error) {
	conn, err := grpc.NewClient(address, grpc.WithTransportCredentials(insecure.NewCredentials()))
	if err != nil {
		return nil, fmt.Errorf("failed to connect: %v", err)
	}

	client := pb.NewAuthServiceClient(conn)
	return &AuthClient{
		client: client,
		conn:   conn,
	}, nil
}

func (c *AuthClient) Close() error {
	return c.conn.Close()
}

func (c *AuthClient) GetUserIDFromJwtToken(jwtToken string) (int32, error) {
	req := &pb.GetUserIDFromJwtTokenRequest{
		JwtToken: jwtToken,
	}

	resp, err := c.client.GetUserIDFromJwtToken(context.Background(), req)
	if err != nil {
		return 0, err
	}

	return resp.UserId, nil
}
