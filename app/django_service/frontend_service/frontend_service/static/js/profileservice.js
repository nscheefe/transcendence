import { executeQuery, gql } from './utils.js';

/**
 * Fetches the user's profile and stats.
 * @param {number} userId - The user's ID.
 * @returns {Promise<object>} The user's profile and stats.
 */
   export const fetchUserProfileAndStats = async (userId) => {
       const GET_USER_PROFILE_AND_STATS_QUERY = gql`
        query GetUserProfileAndStats($userId: Int!) {
            user {
                id
                name
                mail
                blocked
                createdAt
                updatedAt
                roleId
                lastLogin
                lastLoginIp
                profile {
                    avatarUrl
                    additionalInfo
                    bio
                    nickname
                }
            }
            calculateUserStats(userId: $userId) {
                totalGames
                totalWins
                totalLosses
            }
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

       try {
           const result = await executeQuery(GET_USER_PROFILE_AND_STATS_QUERY, { userId });
           return result;
       } catch (error) {
           console.error('Error fetching user profile and stats:', error);
           throw error;
       }
   };

/**
 * Fetches all profiles with pagination support.
 * @param {number} limit - The maximum number of profiles to fetch.
 * @param {number} offset - The offset for pagination.
 * @returns {Promise<object>} The paginated list of profiles.
 */
export const fetchProfiles = async (limit, offset) => {


    const GET_ALL_PROFILES_QUERY = gql`
        query GetAllProfiles($limit: Int!, $offset: Int!) {
            getAllProfiles(limit: $limit, offset: $offset) {
                profiles {
                    additionalInfo
                    avatarUrl
                    bio
                    nickname
                    userId
                }
            }
        }
    `;

    try {
        const result = await executeQuery(GET_ALL_PROFILES_QUERY, { limit, offset });
        return result;
    } catch (error) {
        console.error('Error fetching profiles with pagination:', error);
        throw error;
    }
};

/**
 * Fetches a user's profile by the provided user ID.
 * @param {number} userId - The user's ID.
 * @returns {Promise<object>} The user's profile.
 */
export const fetchProfileByUserId = async (userId) => {

    const GET_PROFILE_BY_USER_ID_QUERY = gql`
        query GetProfile($userId: Int!) {
            profile(userId: $userId) {
                id
                userId
                avatarUrl
                nickname
                bio
                additionalInfo
            }
        }
    `;

    try {
        const result = await executeQuery(GET_PROFILE_BY_USER_ID_QUERY, { userId });
        return result;
    } catch (error) {
        console.error('Error fetching profile by user ID:', error);
        throw error;
    }
};