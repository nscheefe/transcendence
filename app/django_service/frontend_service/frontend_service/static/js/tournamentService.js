import { executeQuery, executeMutation,  } from './utils.js';

/**
 * Create a tournament room.
 * @param {string} name - The name of the tournament.
 * @returns {Promise<Object>} - The created tournament details.
 */
export const createTournament = async (name) => {
  const mutation = `
    mutation CreateTournament($name: String!) {
      create_tournament(name: $name) {
        id
        name
        created_at
        updated_at
      }
    }
  `;

  const variables = { name };

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
        users {
            id
play_order
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