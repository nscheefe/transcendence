import {fetchFriendships, fetchFriendsWithProfiles} from './friendservice.js';
import {fetchUserProfileAndStats, fetchProfiles} from './profileservice.js';
import {showError} from './utils.js';
import {createElement, DEFAULT_AVATAR, DEFAULT_USER_AVATAR, formatDate} from './domHelpers.js';

const NO_FRIENDS_HTML = '<p class="text-light">No friends available 😞.</p>';
const LOADING_FRIENDS_HTML = '<p class="text-light">Loading friends...</p>';
const NO_FRIENDS_WARNING = 'Sad ... you don\'t seem to have any friends 😞.';

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
        const friendships = await fetchFriendships();

        if (!friendships.length) {
            friendsContainer.innerHTML = `<p class="text-light">${NO_FRIENDS_WARNING}</p>`;
            return;
        }

        const combinedData = await fetchFriendsWithProfiles(friendships);
        renderFriendsList(friendships, combinedData, friendsContainer);
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
const renderUserProfile = (user, stats, profileContainer) => {
    const profile = user.profile;

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
                                <h6 class="fw-bold text-primary">Total Wins</h6>
                                <span class="fs-5 text-primary">${stats.totalWins}</span>
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
            </div>
            `,
            'user-profile'
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
        const data = await fetchUserProfileAndStats(userId); // Replace 'userId' appropriately
        profileLoading.remove();

        if (data?.user) {
            renderUserProfile(data.user, data.calculateUserStats, profileContainer);
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
 * @param {Array} profiles - The profiles to render.
 * @param {HTMLElement} profilesContainer - The container to render profiles in.
 */
const renderProfiles = (profiles, profilesContainer) => {
    profilesContainer.innerHTML = '';

    if (profiles.length === 0) {
        profilesContainer.innerHTML = NO_PROFILES_HTML;
        return;
    }
    profiles.forEach((profile) => {
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
                <button class="btn btn-success btn-sm">Add Friend</button>
            </li>
        `;
        profilesContainer.innerHTML += profileHTML;
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

