import { executeQuery, gql } from './utils.js';

/**
 * Fetches friendships for the logged-in user using plain string queries.
 * @returns {Promise<Array>} - Array of friendship objects.
 */
export const fetchFriendships = async () => {
    // Defining the GraphQL query as a plain string
    const GET_FRIENDSHIPS_QUERY = gql`
        query GetFriendships {
            user {
                friendships {
                    friendId
                    accepted
                    establishedAt
                    userId
                }
            }
        }
    `;

    try {
        const { user } = await executeQuery(GET_FRIENDSHIPS_QUERY);
        return user.friendships || [];
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
    return friendships
        .map(
            (friendship, index) => `
            friend${index}: profile(userId: ${friendship.friendId}) {
                additionalInfo
                avatarUrl
                nickname
                bio
                userId
            }
        `
        )
        .join('\n');
};

/**
 * Fetches friendships and associated profiles in one combined query using plain strings.
 * @param {Array} friendships - Array of friendship objects.
 * @returns {Promise<Object>} - Combined friendships and profiles data.
 */
export const fetchFriendsWithProfiles = async (friendships) => {
    // Build the dynamic profile query as a plain string
    const profileQueries = buildProfileQuery(friendships);

    const GET_FRIENDSHIPS_AND_PROFILES_QUERY = gql`
        query GetFriendshipsAndProfiles {
            friendships: user {
                friendships {
                    friendId
                    accepted
                    establishedAt
                    userId
                }
            }

            ${profileQueries}
        }
    `;

    try {
        return await executeQuery(GET_FRIENDSHIPS_AND_PROFILES_QUERY);
    } catch (error) {
        console.error('Failed to fetch friends and their profiles:', error);
        throw error;
    }
};