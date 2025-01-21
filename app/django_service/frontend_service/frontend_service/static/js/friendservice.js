import { executeQuery, executeMutation, gql } from './utils.js';

/**
 * Fetches friendships for the logged-in user using plain string queries.
 * @returns {Promise<Array>} - Array of friendship objects.
 */
export const fetchFriendships = async () => {
    // Defining the GraphQL query as a plain string
    const GET_FRIENDSHIPS_QUERY = gql`
        query GetFriendships {
                friendships {
                    friendId
                    accepted
                    establishedAt
                    userId
                }
        }
    `;

    try {
        const friendships = await executeQuery(GET_FRIENDSHIPS_QUERY);
        console.log("friendships", friendships);
        return friendships || [];
    } catch (error) {
        console.error('Failed to fetch friendships:', error);
        throw error;
    }
};

/**
 * Dynamically generates a GraphQL query to fetch profiles for each friend ID.
 * @param {Array} friendships - Array of friendship objects.
 * @returns {String} - The combined GraphQL query for fetching profiles.
 */
const buildProfileQuery = (friendships) => {
    // Debug: Log the original nested friendships array
    console.log("Input friendships (nested):", friendships);

    // Step 1: Flatten the friendships array
    const flattenedFriendships = friendships.flat();

    // Debug: Log the flattened friendships array
    console.log("Flattened friendships array:", flattenedFriendships);

    const query = flattenedFriendships
        .map((friendship, index) => {
            // Ensure friendId is properly cast as a number
            const friendId = Number(friendship.friendId);

            // Validate friendId to avoid NaN in the query
            if (isNaN(friendId)) {
                console.warn(`Invalid "friendId" detected for friend${index}:`, friendship.friendId);
                return ""; // Skip invalid entries
            }

            // Build the query segment for each friend
            const querySegment = `
            friend${index}: profile(userId: ${friendId}) {
                additionalInfo
                avatarUrl
                nickname
                bio
                userId
            }
        `;

            // Debug: Log the generated query segment
            console.log(`Generated query segment for friend${index}:\n`, querySegment);

            return querySegment;
        })
        .filter((segment) => segment) // Remove any empty segments
        .join("\n");

    // Debug: Log the final generated query
    console.log("Generated profile query:\n", query);

    return query;
};

/**
 * Fetches friendships and associated profiles in one combined query using plain strings.
 * @param {Array} friendships - Array of friendship objects.
 * @returns {Promise<Object>} - Combined friendships and profiles data.
 */
export const fetchFriendsWithProfiles = async (friendships) => {
    // Debug: Log the input friendships before processing
    console.log("Fetching profiles with friendships data:", friendships);

    // Handle edge cases with a warning
    if (!friendships || friendships.length === 0) {
        console.warn("No friendships data provided. Returning empty result.");
        return { friendships: [], profiles: [] };
    }

    const profileQueries = buildProfileQuery(friendships);

    // Debug: Log the dynamic GraphQL query to be sent
    console.log("Final GraphQL query for fetching friendships and profiles:\n", profileQueries);

    const GET_FRIENDSHIPS_AND_PROFILES_QUERY = gql`
        query GetFriendshipsAndProfiles {
   friendships {
                    friendId
                    accepted
                    establishedAt
                    userId
                }

            ${profileQueries}
        }
    `;

    try {
        // Debug: Indicate that the query execution is starting
        console.log("Executing GraphQL query for friendships and profiles...");

        const result = await executeQuery(GET_FRIENDSHIPS_AND_PROFILES_QUERY);

        // Debug: Log the result of the GraphQL query
        console.log("GraphQL query result:", result);

        return result;
    } catch (error) {
        // Debug: Log detailed error information
        console.error("Failed to fetch friends and their profiles:", error);
        console.error("Query that caused the error:\n", GET_FRIENDSHIPS_AND_PROFILES_QUERY);

        throw error;
    }
};


/**
 * Sends a request to add a friend by their user ID.
 * @param {Number} friendId - The ID of the friend to add.
 * @returns {Promise<Object>} - Response object with success status and message.
 */
export const addFriend = async (friendId) => {
    // Define the Add Friend mutation
const ADD_FRIEND_MUTATION = gql`
  mutation AddFriend($friendId: Int!) {
      manageFriendship(
          friendshipData: {
              create:{
                  friendId: $friendId,
              }
          }
      ) {
          success
          message
      }
  }
`;

// Example variables
const variables = {
    friendId, // Pass friendId dynamically
};

    try {
        // Execute the mutation using the utility function
        const { manageFriendship } = await executeMutation(ADD_FRIEND_MUTATION, variables);
        return manageFriendship; // Return the success status and message
    } catch (error) {
        console.error('Error adding friend:', error);
        throw error; // Re-throw the error for the caller to handle
    }
};