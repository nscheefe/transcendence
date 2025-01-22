import { fetchFriendships, fetchFriendsWithProfiles, addFriend } from './friendservice.js';
import { fetchUserProfileAndStats, fetchProfiles } from './profileservice.js';
import { showError, gql } from './utils.js';
import { createElement, DEFAULT_AVATAR, DEFAULT_USER_AVATAR, formatDate } from './domHelpers.js';

const NO_FRIENDS_HTML = '<p class="text-light">No friends available 😞.</p>';
const LOADING_FRIENDS_HTML = '<p class="text-light">Loading friends...</p>';
const NO_FRIENDS_WARNING = 'Sad ... you don\'t seem to have any friends 😞.';
let cachedFriendships = null; // Holds the friendships in memory
/**
 * Generates individual friend's HTML using the friendship and profile data.
 * @param {Object} friendship - Friendship object.
 * @param {Object} profile - Profile object for the friend.
 * @returns {HTMLElement} - Generated friend list item as DOM element.
 */
const generateFriendHTML = (friendship, profile) => {
    const avatarUrl = profile.avatarUrl || DEFAULT_AVATAR;
    const establishedDate = formatDate(friendship.establishedAt);

    return createElement(
        'li',
        `
        <div class="avatar me-3">
            <a href="/home/profile/${profile.userId}" class="text-decoration-none">
                <img src="${avatarUrl}"
                    alt="${profile.nickname || 'Friend Avatar'}"
                    class="rounded-circle"
                    style="width: 50px; height: 50px; object-fit: cover;" />
            </a>
        </div>
        <div>
            <a href="/home/profile/${profile.userId}" class="text-decoration-none">
                <h6>${profile.nickname || 'Unknown Friend'}</h6>
            </a>
            <p class="small mb-0" style="color:white">${profile.bio || 'No bio available.'}</p>
            <p class="small" style="color:white">Friends since: ${establishedDate}</p>
        </div>
        `,
        'list-group-item bg-dark text-light d-flex align-items-center p-3 rounded-3 mb-2'
    );
};

/**
 * Renders the list of friends with their profiles.
 * @param {Array} friendships - Array of friendship objects fetched from the API.
 * @param {Object} combinedData - Combined API data containing friendship details and profiles.
 * @param {HTMLElement} friendsContainer - The DOM container for the friends list.
 */
const renderFriendsList = (friendships, combinedData, friendsContainer) => {
    friendsContainer.innerHTML = '';
    let friendCount = 0;
    console.log("friends combined to render", friendships, combinedData)
    friendships.forEach((friendship, index) => {
        const profile = combinedData[`friend${index}`];
        if (friendship.accepted && profile) {
            const friendHtmlElement = generateFriendHTML(friendship, profile);
            friendsContainer.appendChild(friendHtmlElement);
            friendCount++;
        } else if (!profile) {
            console.warn(`No profile found for friend${index}.`);
        }
    });

    if (friendCount === 0) {
        friendsContainer.innerHTML = NO_FRIENDS_HTML;
    }
};

/**
 * Loads the friends list and their profiles.
 * @param {HTMLElement} friendsContainer - The DOM container for the friends list.
 */
const loadFriends = async (friendsContainer) => {
    friendsContainer.innerHTML = LOADING_FRIENDS_HTML;
    try {
        const data = await fetchFriendships(); // Fetch friendships data
        console.log("Received friendships data", data);

        // Ensure data is an array of objects
        const friendships = Array.isArray(data)
            ? data
            : Object.values(data); // If it's an object (with numeric keys), convert it to an array

        console.log("Is friendships an array?", Array.isArray(friendships)); // True if valid array

        // Check if friendships array is empty
        if (!friendships.length) {
            friendsContainer.innerHTML = `<p class="text-light">${NO_FRIENDS_WARNING}</p>`;
            return;
        }
                cachedFriendships = friendships; // Cache friendships here

        console.log("Received friendships data", friendships);

        // Fetch more data based on friendships
        const combinedData = await fetchFriendsWithProfiles(friendships);
        console.log("Received friendships cobined data", friendships);

        // Render the friends list
        renderFriendsList(combinedData.friendships, combinedData, friendsContainer);
    } catch (error) {
        console.error('Failed to load friends:', error);
        showError(friendsContainer, 'Failed to load friends. Try again later.');
    }
};

/**
 * Renders the profile and stats of the logged-in user.
 * @param {Object} user - User object returned from the API.
 * @param {Object} stats - User stats object returned from the API.
 * @param {HTMLElement} profileContainer - The DOM container for the user profile.
 */
const renderUserProfile = (user, stats, statsByUser, profileContainer) => {
    const profile = user.profile;

    // Create the user profile section
    profileContainer.appendChild(
        createElement(
            'div',
            `
            <div class="d-flex align-items-center mb-3">
                <div class="avatar me-3">
                    <img src="${profile.avatarUrl || DEFAULT_USER_AVATAR}"
                        alt="User Avatar"
                        class="rounded-circle">
                </div>
                <div>
                    <h4>${profile.nickname} (${user.name})</h4>
                    <p>${profile.bio || 'No bio available.'}</p>
                    <p>Member since: ${formatDate(user.createdAt)}</p>
                </div>
            </div>
            <div>
                <h5>Contact Information</h5>
                <p>Email: ${user.mail || 'N/A'}</p>
                <h5>Additional Information</h5>
                <p>${profile.additionalInfo || 'No additional information available.'}</p>
                <h5>Stats:</h5>

                <!-- Stats Summary -->
                <div class="card bg-dark text-light shadow-sm rounded-3 p-3">
                    <div class="row text-center">
                        <div class="col">
                            <div class="p-2">
                                <h6 class="fw-bold text-light">Total Games</h6>
                                <span class="fs-5">${stats.totalGames}</span>
                            </div>
                        </div>
                        <div class="col border-start border-secondary">
                            <div class="p-2">
                                <h6 class="fw-bold text-win">Total Wins</h6>
                                <span class="fs-5 text-win">${stats.totalWins}</span>
                            </div>
                        </div>
                        <div class="col border-start border-secondary">
                            <div class="p-2">
                                <h6 class="fw-bold text-danger">Total Losses</h6>
                                <span class="fs-5 text-danger">${stats.totalLosses}</span>
                            </div>
                        </div>
                    </div>
                </div>

                <!-- Detailed User Stats -->
                <div class="stats-list mt-3">
                    ${statsByUser.map(stat => {
                        const date = stat.stat.createdAt; // Assume createdAt exists in stat.stat
                        const result = stat.didWin ? 'win' : 'loss';
                        const isWinner = stat.stat.winnerId === user.id;
                        const opponent = {
                            avatarUrl: stat.opponentAvatar || 'https://via.placeholder.com/50',
                            nickname: stat.opponentNickname || 'Unknown Player',
                        };

                        return `
                            <div class="game-stat bg-dark ${result === 'win' ? 'victory' : 'defeat'}">
                                <div class="d-flex justify-content-between mb-2">
                                    <span>${new Date(date).toLocaleDateString()}</span>
                                    <span class="badge ${result === 'win' ? 'bg-success' : 'bg-danger'}">
                                        ${result === 'win' ? 'Victory' : 'Defeat'}
                                    </span>
                                </div>
                                <div class="d-flex justify-content-around">
                                    <div class="player">
                                        <img src="${profile.avatarUrl || 'https://via.placeholder.com/50'}" alt="${profile.nickname}">
                                        <span>${isWinner ? 'You' : profile.nickname}</span>
                                    </div>
                                    <div class="vs text-bold">
                                        <span>VS</span>
                                    </div>
                                    <div class="opponent">
                                        <img src="${opponent.avatarUrl}" alt="${opponent.nickname}">
                                        <span>${opponent.nickname}</span>
                                    </div>
                                </div>
                            </div>
                        `;
                    }).join('')}
                </div>
            </div>
            `
        )
    );
};
/**
 * Loads the profile and stats of the logged-in user.
 * @param {HTMLElement} profileContainer - The DOM container for the user profile.
 * @param {HTMLElement} profileLoading - The loading container for the profile.
 */
const loadUserProfile = async (profileContainer, profileLoading) => {
    try {
        const data = await fetchUserProfileAndStats(userId);
        profileLoading.remove();

        if (data?.user) {
            renderUserProfile(data.user, data.calculateUserStats, data.statsByUser, profileContainer);
        } else {
            throw new Error('User data is missing.');
        }
    } catch (error) {
        console.error('Failed to load profile:', error);
        showError(profileLoading, 'Failed to load profile. Please try again later.');
    }
};

document.addEventListener('DOMContentLoaded', async () => {
    const friendsContainer = document.querySelector('#friends ul');
    const profileContainer = document.getElementById('profile');
    const profileLoading = document.getElementById('profile-loading');

    await Promise.all([loadFriends(friendsContainer), loadUserProfile(profileContainer, profileLoading)]);
});

const NO_PROFILES_HTML = '<p class="text-light">No profiles found.</p>';
const LOADING_PROFILES_HTML = '<p class="text-light">Loading profiles, please wait...</p>';

/**
 * Renders profiles into the DOM.
 * Disables the "Add Friend" button for profiles already in friendships.
 * @param {Array} profiles - The profiles to render.
 * @param {HTMLElement} profilesContainer - The container to render profiles in.
 */
const renderProfiles = (profiles, profilesContainer) => {
    profilesContainer.innerHTML = '';

    if (profiles.length === 0) {
        profilesContainer.innerHTML = NO_PROFILES_HTML;
        return;
    }
    console.log("cached",cachedFriendships);
    const flattenedFriendships = cachedFriendships?.flat() || [];

    profiles.forEach((profile) => {
        // Check if the profile userId exists in cachedFriendships
  const isFriendAlready = flattenedFriendships.some(
            (friendship) => friendship.friendId == profile.userId
        );

        console.log("isalread friend:", isFriendAlready);
        const profileHTML = `
            <li class="list-group-item bg-dark text-light d-flex justify-content-between align-items-center p-3 rounded-3 mb-2">
                <div class="d-flex align-items-center">
                    <div class="avatar me-3">
                        <a href="/home/profile/${profile.userId}" class="text-decoration-none">
                            <img src="${profile.avatarUrl || 'https://via.placeholder.com/50'}"
                                 alt="Profile Avatar"
                                 class="rounded-circle"
                                 style="width: 50px; height: 50px; object-fit: cover;">
                        </a>
                    </div>
                    <div>
                        <a href="/home/profile/${profile.userId}" class="text-decoration-none">
                            <h6>${profile.nickname || 'Unknown User'}</h6>
                        </a>
                        <p class="small mb-0" style="color:white;">${profile.bio || 'No bio available.'}</p>
                    </div>
                </div>
                <button
                    class="btn ${isFriendAlready ? 'btn-secondary' : 'btn-success'} btn-sm"
                    data-friend-id="${profile.userId}"
                    ${isFriendAlready ? 'disabled' : ''}>
                    ${isFriendAlready ? 'Friend Added' : 'Add Friend'}
                </button>
            </li>
        `;
        profilesContainer.innerHTML += profileHTML;
    });

    // Attach event listeners to "Add Friend" buttons
    const buttons = profilesContainer.querySelectorAll('.btn-success');
    buttons.forEach((button) => {
        button.addEventListener('click', async (event) => {
            event.preventDefault();

            const friendId = parseInt(button.getAttribute('data-friend-id'), 10);
            if (isNaN(friendId)) {
                console.error("Invalid friend ID.");
                return;
            }

            try {
                // Call the addFriend service function
                const response = await addFriend(friendId);

                if (response && response.success) {
                    console.log(`Friend added successfully: ${response.message}`);
                    button.textContent = "Friend Added!";
                    button.classList.remove("btn-success");
                    button.classList.add("btn-secondary");
                    button.disabled = true; // Disable the button after a successful add
                    // Optionally update cachedFriendships
                    cachedFriendships.push({ friendId }); // Add the new friend to the cache
                } else {
                    console.error(`Failed to add friend: ${response.message}`);
                    alert(`Error: ${response.message}`);
                }
            } catch (error) {
                console.error("An unexpected error occurred:", error);
                alert("An unexpected error occurred. Please try again later.");
            }
        });
    });
};

/**
 * Fetches profiles using pagination and renders them to the DOM.
 * @param {HTMLElement} profilesContainer - The container to display profiles.
 * @param {HTMLElement} prevPageBtn - The "Previous" page button.
 * @param {HTMLElement} nextPageBtn - The "Next" page button.
 * @param {number} limit - Number of profiles per page.
 * @param {number} offset - The offset for pagination.
 */
const fetchAndRenderProfiles = async (
    profilesContainer,
    prevPageBtn,
    nextPageBtn,
    limit,
    offset
) => {
    profilesContainer.innerHTML = LOADING_PROFILES_HTML;

    try {
        const data = await fetchProfiles(limit, offset);
        if (data && data.getAllProfiles) {
            const profiles = data.getAllProfiles.profiles;

            renderProfiles(profiles, profilesContainer);
            prevPageBtn.disabled = offset === 0;
            nextPageBtn.disabled = profiles.length < limit;
        } else {
            throw new Error('Unable to fetch profiles.');
        }
    } catch (error) {
        console.error('Failed to fetch profiles:', error);
        profilesContainer.innerHTML = `<p class="text-danger">Failed to load profiles. Please try again later.</p>`;
    }
};

document.addEventListener('DOMContentLoaded', async () => {
    const profilesContainer = document.querySelector('#profilesContainer');
    const prevPageBtn = document.getElementById('prevPageBtn');
    const nextPageBtn = document.getElementById('nextPageBtn');
    const limit = 10;
    let currentOffset = 0;
    await fetchAndRenderProfiles(profilesContainer, prevPageBtn, nextPageBtn, limit, currentOffset);
    prevPageBtn.addEventListener('click', async () => {
        if (currentOffset > 0) {
            currentOffset -= limit;
            await fetchAndRenderProfiles(profilesContainer, prevPageBtn, nextPageBtn, limit, currentOffset);
        }
    });
    nextPageBtn.addEventListener('click', async () => {
        currentOffset += limit;
        await fetchAndRenderProfiles(profilesContainer, prevPageBtn, nextPageBtn, limit, currentOffset);
    });
});
