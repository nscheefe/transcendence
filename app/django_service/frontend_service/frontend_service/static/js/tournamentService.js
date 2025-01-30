import { executeQuery, executeMutation,  } from './utils.js';

/**
 * Create a tournament room.
 * @param {string} name - The name of the tournament.
 * @returns {Promise<Object>} - The created tournament details.
 */
export const createTournament = async (name, size) => {
  const mutation = `
    mutation CreateTournament($name: String!, $size: Int!) {
      create_tournament(name: $name, tournament_size: $size) {
        id
        name
        is_active
        started
        tournament_size
        start_time
        created_at
        updated_at
      }
    }
  `;

  const variables = { name, size };

  return executeMutation(mutation, variables);
};

/**
 * Add a user to a tournament.
 * @param {number} tournamentId - The ID of the tournament.
 * @param {number} userId - The ID of the user.
 * @returns {Promise<Object>} - Response indicating success and linked user details.
 */
export const addUserToTournament = async (tournamentId, userId) => {
  const mutation = `
    mutation AddUserToTournament($tournamentId: Int!, $userId: Int!) {
      create_tournament_user(tournament_id: $tournamentId, user_id: $userId) {
        success
        user {
          id
          name
          tournament_id
          created_at
          updated_at
        }
      }
    }
  `;

  const variables = { tournamentId, userId };

  return executeMutation(mutation, variables);
};

/**
 * Update a tournament user's details in a tournament.
 * @param {number} tournamentId - The ID of the tournament.
 * @param {number} userId - The ID of the user.
 * @param {Object} updates - The details to update for the user.
 * @param {string} [updates.state] - The user's state in the tournament.
 * @param {number} [updates.playOrder] - The user's play order in the tournament.
 * @param {number} [updates.gamesPlayed] - The number of games the user has played.
 * @returns {Promise<Object>} - Response indicating success and user details.
 */
export const updateTournamentUser = async (
  tournamentUserId,
  userId,
  { state, playOrder, gamesPlayed } = {}
) => {
  const mutation = `
    mutation UpdateTournamentUser(
      $tournamentUserId: Int!
      $state: String
      $playOrder: Int
      $gamesPlayed: Int
    ) {
      update_tournament_user(
        tournament_user_id: $tournamentUserId,
        state: $state,
        play_order: $playOrder,
        games_played: $gamesPlayed
      ) {
        success
        user {
          id
          name
          state
          play_order
          games_played
          tournament_id
          updated_at
        }
      }
    }
  `;

  const variables = { tournamentUserId, userId, state, playOrder, gamesPlayed };

  return executeMutation(mutation, variables);
};
/**
 * Retrieve the list of tournaments.
 * @returns {Promise<Array<Object>>} - A list of tournaments.
 */
export const getTournaments = async () => {
  const query = `
    query GetTournaments {
      tournaments {
        id
        name
        created_at
        updated_at
      }
    }
  `;
return executeQuery(query);
};

/**
 * Retrieve all users of a specific tournament.
 * @param {number} tournamentId - The ID of the tournament.
 * @returns {Promise<Array<Object>>} - A list of users in the tournament.
 */
export const getTournamentUsers = async (tournamentId) => {
  const query = `
    query GetTournamentUsers($tournamentId: Int!) {
      tournament_users(tournament_id: $tournamentId) {
        id
        user_id
        state
        play_order
        games_played
        created_at
        updated_at
      }
    }
  `;

  const variables = { tournamentId };

  return executeQuery(query, variables);
};



/**
 * Create a game for a tournament.
 * @param {number} gameId - The ID of the game.
 * @param {number} tournamentId - The ID of the tournament.
 * @param {number} userId - The ID of the user associated with the game.
 * @returns {Promise<Object>} - The created tournament game details.
 */
export const createTournamentGame = async (tournamentId, userId, opponentId) => {
  const mutation = `
    mutation CreateTournamentGame(
      $tournamentId: Int!
      $userId: Int!
      $opponentId: Int!
    ) {
      create_tournament_game(
        tournament_id: $tournamentId,
        user_id: $userId
        opponent_id: $opponentId
      ) {
        id
        game_id
        tournament_id
        user_id
        created_at
        updated_at
      }
    }
  `;

  const variables = { tournamentId, userId, opponentId };

  return executeMutation(mutation, variables);
};
/**
 * Fetch tournament details by ID.
 * @param {number} tournamentId - The ID of the tournament to query.
 * @returns {Promise<Object>} - The tournament details, including users.
 */
export const getTournamentById = async (tournamentId) => {
  const query = `
    query GetTournament($tournamentId: Int!) {
      tournament(tournament_id: $tournamentId) {
          id
        name
        created_at
        updated_at
        started
        start_time
        tournament_size
        users {
            id
          play_order
          state
          user_id
          games_played
          created_at
            updated_at
        }
      }
    }
  `;
  const variables = { tournamentId };

return executeQuery(query, variables);
};

/**
 * Retrieve all games of a specific tournament.
 * @param {number} tournamentId - The ID of the tournament.
 * @returns {Promise<Array<Object>>} - A list of games in the tournament.
 */
export const getTournamentGames = async (tournamentId) => {
  const query = `
    query GetTournamentGames($tournamentId: Int!) {
      tournament_games(tournament_id: $tournamentId) {
        id
        game_id
        tournament_id
        created_at
        updated_at
      }
    }
  `;

  const variables = { tournamentId };

  return executeQuery(query, variables);
};
