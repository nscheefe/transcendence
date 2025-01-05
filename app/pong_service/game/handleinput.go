package game

func handleInput(user_id int, game *Game, message map[string]interface{}) {
	game.Mu.Lock()
	defer game.Mu.Unlock()

	switch message["type"] {
	case "keyState":
		key := message["key"].(string)
		state := message["state"].(bool)
		if game.state.KeyState[user_id] == nil {
			game.state.KeyState[user_id] = make(map[string]bool)
		}
		game.state.KeyState[user_id][key] = state
	}
}
