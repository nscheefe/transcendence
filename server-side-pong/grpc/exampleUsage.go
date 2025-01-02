func exampleUsage() {
	// Create a new client
	client, err := grpcClient.NewGameClient("localhost:50051")
	if err != nil {
		fmt.Printf("Failed to create client: %v\n", err)
		return
	}
	defer client.Close()

	// Create a new game
	game, err := client.CreateGame(1, 2) // playerA ID = 1, playerB ID = 2
	if err != nil {
		fmt.Printf("Failed to create game: %v\n", err)
		return
	}

	// Start the game
	startResp, err := client.StartGame(game.Id)
	if err != nil {
		fmt.Printf("Failed to start game: %v\n", err)
		return
	}

	fmt.Printf("Game started! Connect to WebSocket at: %s\n", startResp.WebsocketUrl)

	// Get ongoing games
	games, err := client.GetOngoingGames()
	if err != nil {
		fmt.Printf("Failed to get ongoing games: %v\n", err)
		return
	}

	fmt.Printf("Found %d ongoing games\n", len(games))

	// When game is finished
	err = client.HandleGameFinished(game.Id, 10, 8, 1) // Player A won 10-8
	if err != nil {
		fmt.Printf("Failed to handle game finished: %v\n", err)
		return
	}
}