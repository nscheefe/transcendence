import { executeMutation,  } from './utils.js';

export async function createFriendGame(playerA, playerB) {
    const mutation = `
        mutation CreateFriendGame($playerA: Int!, $playerB: Int!) {
            create_friend_game(player_a: $playerA, player_b: $playerB) {
                id
                state
                points_player_a
                points_player_b
                player_a_id
                player_b_id
                finished
                created_at
                updated_at
            }
        }
    `;

    const variables = {
        playerA,
        playerB,
    };

    try {
        const response = await executeMutation(mutation, variables);
        return response.create_friend_game;
    } catch (error) {
        console.error('Error creating friend game:', error);
        throw error;
    }
}

export async function updateGameState(gameId, state) {
    const mutation = `
        mutation UpdateGameState($gameId: Int!, $state: String!) {
            update_game_state(game_id: $gameId, state: $state) {
                id
                state
                points_player_a
                points_player_b
                player_a_id
                player_b_id
                finished
                created_at
                updated_at
            }
        }
    `;

    const variables = {
        gameId,
        state,
    };

    try {
        const response = await executeMutation(mutation, variables);
        return response.update_game_state;
    } catch (error) {
        console.error('Error updating game state:', error);
        throw error;
    }
}