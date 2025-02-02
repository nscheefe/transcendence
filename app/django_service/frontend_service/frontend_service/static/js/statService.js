import { executeQuery,  } from './utils.js';

// Define the GraphQL query using 
const GET_STATS_BY_USER_QUERY = `
  query StatsByUser($userId: Int!) {
  statsByUser(userId: $userId) {
                id
                userId
                stat {
                    winnerId
                    loserId
                    createdAt
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
    const response = await executeQuery(GET_STATS_BY_USER_QUERY, { userId });

    // Return the data from the response
    return response;
  } catch (error) {
    showToast('Error fetching stats by user:', error);
    throw error;
  }
};

const GET_STAT_LIST_QUERY = `
  query StatList {
    StatList {
      profile {
        id
        userId
        avatarUrl
        nickname
        bio
        additionalInfo
      }
      stats {
        totalGames
        totalWins
        totalLosses
        winRatio
      }
    }
  }
`;

/**
 * Fetch the list of profiles with their stats
 * @returns {Promise<Object>} - Returns a promise with the StatList data
 */
export const getStatList = async () => {
  try {
    // Log the raw response to see what is returned
    const response = await executeQuery(GET_STAT_LIST_QUERY);
    // Check if response and data exist, otherwise throw an error
    if (!response || !response.StatList) {
      throw new Error("Invalid response format: Missing data or StatList in response");
    }

    return response;
  } catch (error) {
    showToast("Error fetching StatList:", error);
    throw error;
  }
};
