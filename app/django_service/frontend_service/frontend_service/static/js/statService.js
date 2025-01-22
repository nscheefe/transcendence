import { executeQuery, gql } from './utils.js';

// Define the GraphQL query using gql
const GET_STATS_BY_USER_QUERY = gql`
  query StatsByUser($userId: Int!) {
    statsByUser(userId: $userId) {
      id
      userId
      stat {
        winnerId
        loserId
      }
      didWin
    }
  }
`;

/**
 * Fetch stats for a specific user by ID
 * @param {number} userId - The ID of the user to fetch stats for
 * @returns {Promise<Object>} - Returns a promise with the stats data
 */
export const getStatsByUser = async (userId) => {
  try {
    // Execute the query, passing the userId as a variable
    const response = await executeQuery(GET_STATS_BY_USER_QUERY, { userId });

    // Return the data from the response
    return response.data.statsByUser;
  } catch (error) {
    console.error('Error fetching stats by user:', error);
    throw error;
  }
};