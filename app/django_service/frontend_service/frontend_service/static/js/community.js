import {addFriend, blockUser, deleteFriendship, fetchFriendships, fetchFriendsWithProfiles} from './friendservice.js';
import {fetchProfileByUserId, fetchProfiles, fetchUserProfileAndStats} from './profileservice.js';
import {generateUserAvatarHTML, showError, userCache, initializeOnlineStatusSubscriptions} from './utils.js'; // Import the new function
import {createElement, DEFAULT_AVATAR, DEFAULT_USER_AVATAR, formatDate} from './domHelpers.js';
import {createFriendGame} from "./gameService.js"
import {startChatWithUser} from "./chatservice.js"
const friendsContainer = document.querySelector('#friends ul');
const profileContainer = document.getElementById('profile');
const profileLoading = document.getElementById('profile-loading');
const NO_FRIENDS_HTML = '<p class="text-light">No friends available 😞.</p>';
const LOADING_FRIENDS_HTML = '<p class="text-light">Loading friends...</p>';
const NO_FRIENDS_WARNING = 'Sad ... you don\'t seem to have any friends 😞.';
let cachedFriendships = null; // Holds the friendships in memory
const refetchFriends = async () => {
    const data = await fetchFriendships(); // Fetch friendships data

    // Ensure data is an array of objects
    const friendships = Array.isArray(data)
        ? data
        : Object.values(data); // If it's an object (with numeric keys), convert it to an array
    cachedFriendships = friendships;
};
const initializePageNavigation = () => {
    const tabs = document.querySelectorAll('#onpage-nav .nav-link');
    const tabContent = document.querySelectorAll('.tab-pane');

    // Handle tab click navigation
    tabs.forEach((tab) => {
        tab.addEventListener('click', async (event) => {
            event.preventDefault();

            // Deactivate all tabs
            tabs.forEach((otherTab) => {
                otherTab.classList.remove('active');
            });

            // Deactivate all tab content
            tabContent.forEach((content) => {
                content.classList.remove('show', 'active');
            });

            // Activate the clicked tab and its corresponding content
            tab.classList.add('active');
            const targetId = tab.getAttribute('href').substring(1); // Get the target tab content ID
            const targetContent = document.getElementById(targetId);
            if (targetContent) {
                targetContent.classList.add('show', 'active');

                // Update the URL hash to reflect the active tab
                window.history.pushState(null, '', `#${targetId}`);

                // Perform specific logic based on the active tab
                await handleTabSwitch(targetId);
            }
        });
    });
};
/**
 * Handles logic specific to each tab when it is activated.
 * @param {string} tabId - The ID of the activated tab content.
 */
const handleTabSwitch = async (tabId) => {
    // Define logic for each specific tab
    switch (tabId) {
        case 'profile':
            const profileContainer = document.getElementById('profile');
            const profileLoading = document.getElementById('profile-loading');
            await loadUserProfile(profileContainer, profileLoading); // Load the profile information
            break;

        case 'friends':
            const friendsContainer = document.querySelector('#friends ul');
            await loadFriends(friendsContainer); // Load the friends list
            break;

        case 'add-friend':
            const profilesContainer = document.getElementById('profilesContainer');
            const prevPageBtn = document.getElementById('prevPageBtn');
            const nextPageBtn = document.getElementById('nextPageBtn');
            const limit = 10; // Pagination limit
            let currentOffset = 0; // Initial offset

            // Fetch and render the initial set of profiles
            await fetchAndRenderProfiles(profilesContainer, prevPageBtn, nextPageBtn, limit, currentOffset);

            // Add listeners for pagination
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

            break;

        default:
            console.warn(`Unrecognized tab ID: ${tabId}`);
            break;
    }
};

// Initialize everything when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', async () => {
    const friendsContainer = document.querySelector('#friends ul');

    // Preload friends and initialize tab navigation
    await Promise.all([
        loadFriends(friendsContainer),
        initializePageNavigation()
    ]);

    // Check the initial URL hash and load the corresponding tab
    handleHashChange();

    // Listen to hash changes caused by back/forward buttons
    window.addEventListener('popstate', handleHashChange);
});

/**
 * Handles hash change and activates the appropriate tab and content.
 */
const handleHashChange = () => {
    const currentHash = window.location.hash.substring(1); // Get the hash without the "#" symbol
    if (!currentHash) {
        return; // No hash, just return
    }

    // Find the navigation link corresponding to the hash
    const activeTab = document.querySelector(`#onpage-nav .nav-link[href="#${currentHash}"]`);

    if (activeTab) {
        activeTab.click(); // Trigger a click event to update the UI
    } else {
        console.warn(`No matching tab found for hash: #${currentHash}`);
    }
};
/**
 * Generates individual friend's HTML using the friendship and profile data.
 * @param {Object} friendship - Friendship object.
 * @param {Object} profile - Profile object for the friend.
 * @returns {HTMLElement} - Generated friend list item as DOM element.
 */
const generateFriendHTML = (friendship, profile) => {
    const establishedDate = formatDate(friendship.establishedAt);
    const avatarUrl = profile.avatarUrl || DEFAULT_AVATAR;

    if (!userCache[profile.userId]) {
        userCache[profile.userId] = {profile};
    }

    return createElement(
        'li', // tagName
        `
        <div class="avatar me-3">
            <a href="/home/profile/${profile.userId}" class="text-decoration-none">
                ${generateUserAvatarHTML(profile.userId, 50)}
            </a>
        </div>
        <div>
            <a href="/home/profile/${profile.userId}" class="text-decoration-none">
                <h6>${profile.nickname || 'Unknown Friend'}</h6>
            </a>
            <p class="small mb-0" style="color:white">${profile.bio || 'No bio avaixlable.'}</p>
            <p class="small" style="color:white">Friends since: ${establishedDate}</p>
        </div>
        <div class="ms-auto d-flex gap-2">

            <button class="btn btn-primary btn-sm start-chat-room" data-friendship-id="${friendship.id}" data-user-id="${profile.userId}">
                Start Chat
            </button>
            <button class="btn btn-success btn-sm start-game" data-friendship-id="${profile.userId}">
                Play a Game
            </button>
            <button class="btn btn-danger btn-sm delete-friend" data-friendship-id="${friendship.id}">
                Delete
            </button>
        </div>
        `,
        'list-group-item bg-dark text-light d-flex align-items-center p-3 rounded-3 mb-2', // className
        {},
        {id: `friendship-${friendship.id}`}
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
        const data = await fetchFriendships(); // Fetch friendships data

        // Ensure data is an array of objects
        const friendships = Array.isArray(data)
            ? data
            : Object.values(data); // If it's an object (with numeric keys), convert it to an array


        // Check if friendships array is empty
        if (!friendships.length) {
            friendsContainer.innerHTML = `<p class="text-light">${NO_FRIENDS_WARNING}</p>`;
            return;
        }
        cachedFriendships = friendships; // Cache friendships here


        // Fetch more data based on friendships
        const combinedData = await fetchFriendsWithProfiles(friendships);

        // Render the friends list
        renderFriendsList(combinedData.friendships, combinedData, friendsContainer);
    } catch (error) {
        console.error('Failed to load friends:', error);
        showError(friendsContainer, 'Failed to load friends. Try again later.');
    }
};


/*************************************************************************************************************/
async function loadOpponentProfile(opponentId) {
    try {
        const opponent = await fetchProfileByUserId(opponentId);

        return opponent; // Use the resolved value if needed later
    } catch (error) {
        console.error('Failed to fetch opponent profile:', error);
    }
}

/**
 * Renders the profile and stats of the logged-in user.
 * @param {Object} user - User object returned from the API.
 * @param {Object} stats - User stats object returned from the API.
 * @param {HTMLElement} profileContainer - The DOM container for the user profile.
 */
const renderUserProfile = async (user, stats, statsByUser, profileContainer) => {
    const profile = user.profile;

    // Preload opponent profiles in parallel
    const opponents = await Promise.all(
        statsByUser.map(async (stat) => {
            const isWinner = stat.stat.winnerId === user.id;
            const opponentId = isWinner ? stat.stat.loserId : stat.stat.winnerId;
            return {opponentId, opponent: await fetchProfileByUserId(opponentId)};
        })
    );

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
                <style>
                  .pie-chart {
                    position: relative;
                    width: 100px;
                    height: 100px;
                    border-radius: 50%;
                     background: conic-gradient(
        #0d6efd 0% calc(var(--wins) * 1%),  
        #dc3545 calc(var(--wins) * 1%) 100%
         );
                    margin: auto;
                  }

                  .pie-chart .center-text {
                    position: absolute;
                    top: 50%;
                    left: 50%;
                    transform: translate(-50%, -50%);
                    text-align: center;
                  }

                  .pie-chart .center-text h6 {
                    margin: 0;
                    font-size: 1rem;
                    color: white;
                  }

                  .pie-chart .center-text span {
                    font-size: 0.9rem;
                    color: lightgray;
                  }
                </style>
                <div class="d-flex justify-content-between mb-4">

                <!-- Stats Summary -->
                <div class="card bg-dark text-light shadow-sm rounded-3 p-3" style="width:66%">
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
                 <div class="card bg-dark text-light shadow-sm rounded-3 p-3 " style="width:33%">
                    <div class="pie-chart" style="--wins: ${(stats.totalGames > 0 ? (stats.totalWins / stats.totalGames) * 100 : 0)};">
                      <div class="center-text">
                            <h6>${stats.totalGames}</h6>
                            <span>Total Games</span>
                      </div>
                    </div>

                 </div>
                </div>
                <!-- Detailed User Stats -->
                <div class="stats-list mt-3 scrollable">
                    ${statsByUser.map((stat, index) => {
                const date = stat.stat.createdAt;
                const result = stat.didWin ? 'win' : 'loss';
                const opponentData = opponents.find(o => o.opponentId === (stat.stat.winnerId === user.id ? stat.stat.loserId : stat.stat.winnerId));
                const opponent = opponentData?.opponent?.profile || {};
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
                                        <span>You</span>
                                    </div>
                                    <div class="vs text-bold">
                                        <span>VS</span>
                                    </div>
                                    <div class="opponent">
                                    <a href="/home/profile/${opponent.userId}">
                                        <img src="${opponent.avatarUrl || 'https://via.placeholder.com/50'}" alt="${opponent.nickname || 'Opponent'}">
                                        <span>${opponent.nickname || 'Opponent'}</span>
                                    </a>
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
        profileContainer.innerHTML = '';

        const data = await fetchUserProfileAndStats(userId);
        if (profileLoading) {
            profileLoading.remove();
        }
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



const NO_PROFILES_HTML = '<p class="text-light">No profiles found.</p>';
const LOADING_PROFILES_HTML = '<p class="text-light">Loading profiles, please wait...</p>';

const updateFlattendFriendships = async (flattenedFriendships) => {
    await refetchFriends();
    flattenedFriendships = Array.isArray(cachedFriendships) ? cachedFriendships.flat() : [];
    return flattenedFriendships;
};

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

    let flattenedFriendships = Array.isArray(cachedFriendships) ? cachedFriendships.flat() : [];

    profiles.forEach((profile) => {
        userCache[profile.userId] = {profile}; // Cache the profile for later use
        // Check if the profile userId exists in cachedFriendships
        const isFriendAlready = flattenedFriendships.some(
            (friendship) => friendship.friendId == profile.userId && friendship.accepted
        );

        const isBlocked = flattenedFriendships.some(
            (friendship) => friendship.friendId == profile.userId && friendship.blocked
        );

        const friendship = flattenedFriendships.find(
            (friendship) => friendship.friendId == profile.userId
        );

        const friendshipId = friendship ? friendship.id : 0;
        const avatarHtml = generateUserAvatarHTML(profile.userId, 50);

        const profileHTML = `
        <li class="list-group-item bg-dark text-light d-flex justify-content-between align-items-center p-3 rounded-3 mb-2">
            <div class="d-flex align-items-center">
                <div class="avatar me-3">
                    ${avatarHtml}
                    </a>
                </div>
                <div>
                    <a href="/home/profile/${profile.userId}" class="text-decoration-none">
                        <h6>${profile.nickname || 'Unknown User'}</h6>
                    </a>
                    <p class="small mb-0" style="color:white;">${profile.bio || 'No bio available.'}</p>
                </div>
            </div>
            <div>
                <button
                    class="btn ${isFriendAlready ? 'btn-secondary' : 'btn-success'} btn-sm"
                    data-friend-id="${profile.userId}"
                    ${isFriendAlready ? 'disabled' : ''}>
                    ${isFriendAlready ? 'Friend Added' : 'Add Friend'}
                </button>
                <button id="block-user"
                    class="btn ${isBlocked ? 'btn-outline-danger' : 'btn-danger'} btn-sm"
                    data-user-id="${profile.userId}"
                    data-blocked="${isBlocked}"
                    data-friendship-id="${friendshipId}">
                        ${isBlocked ? 'Unblock' : 'Block'}
                </button>
            </div>
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
                    refetchFriends(); // Refresh the cached friendships
                    button.textContent = "Friend Added!";
                    button.classList.remove("btn-success");
                    button.classList.add("btn-secondary");
                    button.disabled = true; // Disable the button after a successful add
                    // Optionally update cachedFriendships
                    cachedFriendships.push({friendId}); // Add the new friend to the cache
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

    // Attach event listeners to "Block/Unblock" buttons
    const blockButtons = profilesContainer.querySelectorAll('#block-user');
    blockButtons.forEach((button) => {
        button.addEventListener('click', async (event) => {
            event.preventDefault();

            const block = button.getAttribute('data-blocked') === 'false';
            const id = parseInt(button.getAttribute('data-friendship-id'), 10);
            const userId = parseInt(button.getAttribute('data-user-id'), 10);
            if (isNaN(userId)) {
                console.error("Invalid user ID.");
                return;
            }

            try {
                const response = await blockUser(id, block, userId);

                if (response && response.success) {
                    flattenedFriendships = await updateFlattendFriendships(flattenedFriendships); // Refresh the cached friendships
                    const updatedFriendship = flattenedFriendships.find((friendship) => friendship.friendId == userId);
                    if (block) {
                        button.textContent = "Unblock";
                        button.setAttribute('data-blocked', 'true');
                        button.classList.remove("btn-danger");
                        button.classList.add("btn-outline-danger");
                        if (updatedFriendship) {
                            button.setAttribute('data-friendship-id', updatedFriendship.id);
                        }
                    } else {
                        button.textContent = "Block";
                        button.setAttribute('data-blocked', 'false');
                        button.classList.remove("btn-outline-danger");
                        button.classList.add("btn-danger");
                    }
                } else {
                    console.error(`Failed to update block status: ${response.message}`);
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
            initializeOnlineStatusSubscriptions(); // Initialize online status subscriptions
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


async function initProfileList(){
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
}
async function initProfile(){

    await Promise.all([loadFriends(friendsContainer), loadUserProfile(profileContainer, profileLoading)]);

}

initProfileList();
initProfile()
loadFriends(friendsContainer);


document.addEventListener('DOMContentLoaded', async () => {
    const friendsContainer = document.querySelector('#friends ul');



    friendsContainer.addEventListener('click', async (event) => {
        // Handle "Delete Friend" button click
        if (event.target.classList.contains('delete-friend')) {
            const friendshipId = parseInt(event.target.getAttribute('data-friendship-id'), 10);

            if (!isNaN(friendshipId)) {
                try {

                    const response = await deleteFriendship(friendshipId);

                    if (response && response.success) {

                        const elementToRemove = document.getElementById(`friendship-${friendshipId}`);
                        if (elementToRemove) {
                            elementToRemove.remove(); // Remove from the DOM
                        } else {
                            console.error(`Element with id "friendship-${friendshipId}" not found.`);
                        }
                    } else {
                        console.error(`Failed to delete friendship: ${response ? response.message : 'Unknown error'}`);
                        alert(`Error: ${response.message || 'Failed to delete friendship.'}`);
                    }
                } catch (error) {
                    console.error("An unexpected error occurred while deleting friendship:", error);
                    alert("An error occurred while deleting the friendship. Please try again later.");
                }
            }
        } else if (event.target.classList.contains('start-game')) {
            // Handle "Play a Game" button click
            const friendUserId = parseInt(event.target.getAttribute('data-friendship-id'), 10);

            if (!isNaN(friendUserId)) {
                try {
                    // Call the createFriendGame GraphQL mutation
                    const game = await createFriendGame(userId, friendUserId);
                    //alert(`Game created successfully! Game ID: ${game.id}`);
                    showToast(`Game created successfully! Check Chat To Play Game!`);
                } catch (error) {
                    console.error("Error creating the game:", error);
                    alert("Failed to create the game. Please try again later.");
                }
            } else {
                console.error("Invalid friendUserId in the data-friendship-id attribute.");
            }
        } else if (event.target.classList.contains('start-chat-room')) {
            // Handle "Start Chat" button click
            const friendshipId = parseInt(event.target.getAttribute('data-friendship-id'), 10);
            const friendUserId = parseInt(event.target.getAttribute('data-user-id'), 10);

            if (!isNaN(friendUserId)) {
                try {
                    // Call the startChatWithUser function
                    const chatRoom = await startChatWithUser(friendUserId);
                    showToast(`Chat room created successfully! Chat Room ID: ${chatRoom.id}`);
                } catch (error) {
                    console.error("Error starting the chat:", error);
                    showToast("Failed to start the chat. Please try again later.");
                }
            } else {
                console.error("Invalid friendUserId in the data-friendship-id attribute.");
            }
        }
    });
});