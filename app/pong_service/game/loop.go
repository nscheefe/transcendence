package game

import (
	"math"
	"math/rand/v2"
	"server-side-pong/grpc"
	"server-side-pong/websockets"
	"strconv"
)

func gameLoop(game *Game) {
	updateClients(game)

	if len(game.Clients) == 0 {
		stopGame(game)
		return
	}

	if game.State != GameStateInProgress {
		return
	}

	updatePaddlePositions(game)

	game.state.Ball.X += game.state.BallSpeed.X
	game.state.Ball.Z += game.state.BallSpeed.Z

	if game.state.Ball.X <= -4.5 || game.state.Ball.X >= 4.5 {
		game.state.BallSpeed.X = -game.state.BallSpeed.X
	}

	if game.state.Ball.Z <= -8.5 && game.state.Ball.Z >= -9 && game.state.Ball.X >= game.state.Paddle1.X-1 && game.state.Ball.X <= game.state.Paddle1.X+1 {
		game.state.BallSpeed.Z = -game.state.BallSpeed.Z
		impactPoint := game.state.Ball.X - game.state.Paddle1.X
		game.state.BallSpeed.X += impactPoint * 0.05
		game.state.Direction = 1
		if game.state.BallSpeed.Z < 0 {
			game.state.Direction = -1
		}
	}
	if game.state.Ball.Z >= 8.5 && game.state.Ball.Z <= 9 && game.state.Ball.X >= game.state.Paddle2.X-1 && game.state.Ball.X <= game.state.Paddle2.X+1 {
		game.state.BallSpeed.Z = -game.state.BallSpeed.Z
		impactPoint := game.state.Ball.X - game.state.Paddle2.X
		game.state.BallSpeed.X += impactPoint * 0.05
		game.state.Direction = 1
		if game.state.BallSpeed.Z < 0 {
			game.state.Direction = -1
		}
	}

	if game.state.Ball.Z <= -10 {
		game.state.Points.Player2++
		resetBall(game)
		checkWinner(game)
	} else if game.state.Ball.Z >= 10 {
		game.state.Points.Player1++
		resetBall(game)
		checkWinner(game)
	}

	broadcast(game, map[string]interface{}{
		"type":      "updateState",
		"ball":      game.state.Ball,
		"paddle1":   game.state.Paddle1,
		"paddle2":   game.state.Paddle2,
		"points":    game.state.Points,
		"direction": game.state.Direction,
	})
}

func updateClients(game *Game) {
	for _, client := range game.Clients {
		select {
		case msg := <-client.msgReceived:
			handleInput(msg.Id, game, msg.Msg)
		case id := <-client.connected:
			logGame(game, "client "+strconv.Itoa(id)+" connected")
			startGame(game)
		case id := <-client.disconnected:
			logGame(game, "client "+strconv.Itoa(id)+" disconnected")
			delete(game.Clients, id)
		default:
		}
	}
}

func startGame(game *Game) {
	if len(game.Clients) != 2 {
		logGame(game, "not enough clients to start game")
		return
	}
	game.State = GameStateInProgress

	sendIndividually(game, int(game.info.PlayerAId), map[string]interface{}{
		"type":   "gameStarted",
		"player": "player_a",
	})
	sendIndividually(game, int(game.info.PlayerBId), map[string]interface{}{
		"type":   "gameStarted",
		"player": "player_b",
	})

	_, err := grpc.GameCon.StartGame(int32(game.id))
	if err != nil {
		logGame(game, "GRPCerror starting game: "+err.Error())
	}

	logGame(game, "started")
}

func sendIndividually(game *Game, user_id int, msg map[string]interface{}) {
	select {
	case MsgToSend <- websockets.MsgToSend{
		Id:  user_id,
		Msg: msg,
	}:
	default:
		logGame(game, "error sending message to client ", user_id)
	}
}

func broadcast(game *Game, msg map[string]interface{}) {
	for user_id := range game.Clients {
		sendIndividually(game, user_id, msg)
	}
}

func updatePaddlePositions(game *Game) {
	for user_id, keyState := range game.state.KeyState {
		if user_id == int(game.info.PlayerAId) {
			if keyState["ArrowLeft"] && game.state.Paddle1.X < 4.5 {
				game.state.Paddle1.X += 0.1
			} else if keyState["a"] && game.state.Paddle1.X < 4.5 {
				game.state.Paddle1.X += 0.1
			}

			if keyState["ArrowRight"] && game.state.Paddle1.X > -4.5 {
				game.state.Paddle1.X -= 0.1
			} else if keyState["d"] && game.state.Paddle1.X > -4.5 {
				game.state.Paddle1.X -= 0.1
			}
		} else {
			if keyState["ArrowLeft"] && game.state.Paddle2.X > -4.5 {
				game.state.Paddle2.X -= 0.1
			} else if keyState["a"] && game.state.Paddle2.X > -4.5 {
				game.state.Paddle2.X -= 0.1
			}

			if keyState["ArrowRight"] && game.state.Paddle2.X < 4.5 {
				game.state.Paddle2.X += 0.1
			} else if keyState["d"] && game.state.Paddle2.X < 4.5 {
				game.state.Paddle2.X += 0.1
			}
		}
	}
}

func resetBall(game *Game) {
	randomX := (rand.Float32() - 0.5) * 9
	var randomZ float32 = 0.0

	game.state.Ball = position{X: randomX, Y: 0.5, Z: randomZ}

	baseAngle := math.Pi / 2
	if rand.Float64() < 0.5 {
		baseAngle = -math.Pi / 2
	}
	randomAngle := baseAngle + (rand.Float64()*2-1)*maxAngleVariation
	game.state.BallSpeed = speed{
		X: initialBallSpeed * float32(math.Cos(randomAngle)),
		Z: initialBallSpeed * float32(math.Sin(randomAngle)),
	}
	game.state.Direction = 1
	if game.state.BallSpeed.Z < 0 {
		game.state.Direction = -1
	}
	game.state.Paddle1.X = 0
	game.state.Paddle2.X = 0
}

func checkWinner(game *Game) {
	if game.state.Points.Player1 >= winningPoints || game.state.Points.Player2 >= winningPoints {
		game.State = GameStateFinished
		if game.state.Points.Player1 >= winningPoints {
			broadcast(game, map[string]interface{}{
				"type":   "gameOver",
				"winner": 1,
			})
		} else if game.state.Points.Player2 >= winningPoints {
			broadcast(game, map[string]interface{}{
				"type":   "gameOver",
				"winner": 2,
			})
		}
		err := grpc.GameCon.HandleGameFinished(int32(game.id), int32(game.state.Points.Player1), int32(game.state.Points.Player2), int32(game.state.Direction))
		if err != nil {
			logGame(game, "GRPC error handling game finished: "+err.Error())
		}
		stopGame(game)
	}
}

func stopGame(game *Game) {
	for _, client := range game.Clients {
		close(client.msgReceived)
		close(client.connected)
		close(client.disconnected)
	}
	game.loopInterval.Stop()
	delete(games, game.id)
	logGame(game, "stopped")
}
