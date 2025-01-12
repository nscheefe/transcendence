        const graphqlEndpoint = "/graphql/"; // Replace with your actual GraphQL endpoint
//@ToDo: needs to be gernalist and refactored
        const fetchGraphQL = async (query) => {
            try {
                const response = await fetch(graphqlEndpoint, {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query}),
                    credentials: 'include'
                });

                if (response.ok) {
                    const result = await response.json();
                    if (result.errors) throw new Error('GraphQL Errors');
                    return result.data;
                } else {
                    throw new Error(`Network error: ${response.statusText}`);
                }
            } catch (error) {
                console.error('GraphQL request failed:', error);
                throw error;
            }
        };
        document.addEventListener("DOMContentLoaded", async () => {
            const friendsContainer = document.querySelector("#friends ul");
            friendsContainer.innerHTML = `<p class="text-light">Loading friends...</p>`;

            // Helper function to send GraphQL requests
            const fetchGraphQL = async (query) => {
                try {
                    const response = await fetch("/graphql/", {
                        method: "POST",
                        headers: {"Content-Type": "application/json"},
                        body: JSON.stringify({query}),
                        credentials: "include",
                    });

                    const {data, errors} = await response.json();
                    if (errors) throw new Error(errors[0].message);
                    return data;
                } catch (error) {
                    console.error("GraphQL error:", error);
                    throw error;
                }
            };

            // Step 1: Fetch friendships
            const friendshipsQuery = `
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
                const {user} = await fetchGraphQL(friendshipsQuery);
                const friendships = user.friendships;

                if (!friendships || friendships.length === 0) {
                    friendsContainer.innerHTML = `<p class="text-light">Sad ... you don't seem to have any friends 😞.</p>`;
                    return;
                }

                // Step 2: Dynamically build combined query for all friend profiles based on friend IDs
                const profileQueries = friendships
                    .map((friendship, index) => `
              friend${index}: profile(userId: ${friendship.friendId}) {
                additionalInfo
                avatarUrl
                nickname
                bio
                userId
        }
            `)
                    .join("\n");

                const combinedQuery = `
            query GetFriendshipsAndProfiles {
                friendships: user {
                    friendships {
                        friendId
                        accepted
                        establishedAt
                        userId
                    }
                }

                ${profileQueries}  # Dynamically-added profile queries
            }
        `;

                // Step 3: Fetch combined data (both friendships and profiles in one request)
                const data = await fetchGraphQL(combinedQuery);
                console.log("Fetched Data:", data);
                // Step 4: Render friends list dynamically
                friendsContainer.innerHTML = ""; // Clear the initial loading message

                friendships.forEach((friendship, index) => {
                    // Skip unaccepted friendships if needed
                    if (!friendship.accepted) return;

                    const profile = data[`friend${index}`]; // Access each friend's profile dynamically

                    // Handle potential missing profile data gracefully
                    if (!profile) {
                        console.error(`Profile for friend${index} not found.`);
                        return;
                    }

                    // Add friend item to the container
                    const friendHTML = `
                <li class="list-group-item bg-dark text-light d-flex align-items-center p-3 rounded-3 mb-2">
                    <div class="avatar me-3">
<a href="/home/profile/${profile.userId}" class="text-decoration-none">

                        <img src="${profile.avatarUrl || 'https://via.placeholder.com/50'}"
                             alt="${profile.nickname || 'Friend Avatar'}"
                             class="rounded-circle"
                             style="width: 50px; height: 50px; object-fit: cover;" />
</a>
                    </div>
                    <div>
<a href="/home/profile/${profile.userId}" class="text-decoration-none">

                        <h6>${profile.nickname || "Unknown Friend"}</h6>
</a>
                        <p class="small mb-0" style="color:white">${profile.bio || "No bio available."}</p>
                        <p class="small" style="color:white">Friends since: ${new Date(friendship.establishedAt).toLocaleDateString()}</p>
                    </div>
                </li>
            `;
                    friendsContainer.innerHTML += friendHTML;
                });
            } catch (error) {
                console.error("Failed to fetch data:", error);
                friendsContainer.innerHTML = `<p class="text-danger">Failed to load friends. Try again later.</p>`;
            }
        });
        document.addEventListener("DOMContentLoaded", async () => {
            const profileContainer = document.getElementById("profile");
            const profileLoading = document.getElementById("profile-loading");
            const query = `
            query MyQuery {
                user {
                    profile {
                        avatarUrl
                        additionalInfo
                        bio
                        nickname
                        userId
                    }
                    createdAt
                    name
                    mail
                }
                 calculateUserStats(userId: ${userId}) {
            totalGames
            totalWins
            totalLosses
        }
            }
        `;

            try {
                const data = await fetchGraphQL(query);
                if (data && data.user) {
                    const user = data.user;
                    const profile = user.profile;
                    const stats = data.calculateUserStats;

                    // Remove loading message
                    profileLoading.remove();

                    // Add content dynamically
                    profileContainer.innerHTML += `
                    <div class="d-flex align-items-center mb-3">
                        <div class="avatar me-3">
                            <img src="${profile.avatarUrl || 'https://via.placeholder.com/100'}"
                                 alt="User Avatar"
                                 class="rounded-circle">
                        </div>
                        <div>
                            <h4>${profile.nickname} (${user.name})</h4>
                            <p>${profile.bio || "No bio available"}</p>
                            <p>Member since: ${new Date(user.createdAt).toLocaleDateString()}</p>
                        </div>
                    </div>
                    <div>
                        <h5>Contact Information</h5>
                        <p>Email: ${user.mail || "N/A"}</p>
                        <h5>Additional Information</h5>
                        <p>${profile.additionalInfo || "No additional information available"}</p>
                        <h5> Stats:</h5>
 <div class="card bg-dark text-light shadow-sm rounded-3 p-3">
        <div class="row text-center">
            <!-- Total Games -->
            <div class="col">
                <div class="p-2">
                    <h6 class="fw-bold text-light">Total Games</h6>
                                    <span class="fs-5">${stats.totalGames}</span>
                </div>
            </div>

            <!-- Total Wins -->
            <div class="col border-start border-secondary">
                <div class="p-2">
                    <h6 class="fw-bold text-primary">Total Wins</h6>
                                    <span class="fs-5 text-primary">${stats.totalWins}</span>
                </div>
            </div>

            <!-- Total Losses -->
            <div class="col border-start border-secondary">
                <div class="p-2">
                    <h6 class="fw-bold text-danger">Total Losses</h6>
                                    <span class="fs-5 text-danger">${stats.totalLosses}</span>
                </div>
            </div>
        </div>
    </div>
                         <ul class="list-group">
        <!-- Example 1: Win (Logged-in user wins) -->
        <li class="list-group-item bg-dark text-light d-flex align-items-center justify-content-between p-3 rounded-3 mb-2 border border-secondary">
            <!-- User's side -->
            <div class="d-flex align-items-center">
                <img src="https://via.placeholder.com/50" alt="user-avatar"
                     class="rounded-circle me-2 border border-primary"
                     style="width: 50px; height: 50px; object-fit: cover;">
                <h6 class="mb-0 text-primary">You</h6>
            </div>

            <!-- VS in the middle -->
            <div>
                <h6 class="text-secondary fw-bold">VS</h6>
            </div>

            <!-- Opponent's side -->
            <div class="d-flex align-items-center">
                <h6 class="mb-0 text-danger me-2">Opponent</h6>
                <img src="https://via.placeholder.com/50" alt="opponent-avatar"
                     class="rounded-circle border border-danger"
                     style="width: 50px; height: 50px; object-fit: cover;">
            </div>
        </li>

        <!-- Example 2: Lose (Logged-in user loses) -->
        <li class="list-group-item bg-dark text-light d-flex align-items-center justify-content-between p-3 rounded-3 mb-2 border border-secondary">
            <!-- User's side -->
            <div class="d-flex align-items-center">
                <img src="https://via.placeholder.com/50" alt="user-avatar"
                     class="rounded-circle me-2 border border-danger"
                     style="width: 50px; height: 50px; object-fit: cover;">
                <h6 class="mb-0 text-danger">You</h6>
            </div>

            <!-- VS in the middle -->
            <div>
                <h6 class="text-secondary fw-bold">VS</h6>
            </div>

            <!-- Opponent's side -->
            <div class="d-flex align-items-center">
                <h6 class="mb-0 text-primary me-2">Opponent</h6>
                <img src="https://via.placeholder.com/50" alt="opponent-avatar"
                     class="rounded-circle border border-primary"
                     style="width: 50px; height: 50px; object-fit: cover;">
            </div>
        </li>
    </ul>
                    </div>
                `;
                } else {
                    throw new Error("User data is missing");
                }
            } catch (error) {
                profileLoading.innerHTML = `
                <p class="text-danger">Failed to load profile. Please try again later.</p>
            `;
            }
        });
        document.addEventListener("DOMContentLoaded", async () => {
            const profilesContainer = document.getElementById("profilesContainer");
            const loadingProfiles = document.getElementById("loadingProfiles");
            const prevPageBtn = document.getElementById("prevPageBtn");
            const nextPageBtn = document.getElementById("nextPageBtn");

            // Pagination state
            let currentOffset = 0;
            const limit = 10;

            const fetchProfilesQuery = (limit, offset) => `
        query GetAllProfiles {
            getAllProfiles(limit: ${limit}, offset: ${offset}) {
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

            const renderProfiles = (profiles) => {
                profilesContainer.innerHTML = ""; // Clear current profiles

                if (profiles.length === 0) {
                    profilesContainer.innerHTML = `<p class="text-light">No profiles found.</p>`;
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

                            <h6>${profile.nickname || "Unknown User"}</h6>
</a>
                            <p class="small mb-0" style="color:white;">${profile.bio || "No bio available."}</p>
                        </div>
                    </div>
                    <button class="btn btn-success btn-sm">Add Friend</button>
                </li>
            `;
                    profilesContainer.innerHTML += profileHTML;
                });
            };

            const fetchProfiles = async (offset) => {
                const query = fetchProfilesQuery(limit, offset);

                try {
                    const data = await fetchGraphQL(query);

                    if (data && data.getAllProfiles) {
                        const profiles = data.getAllProfiles.profiles;

                        // Render profiles
                        renderProfiles(profiles);

                        // Update pagination controls
                        prevPageBtn.disabled = currentOffset === 0; // Disable "Previous" on the first page
                        nextPageBtn.disabled = profiles.length < limit; // Disable "Next" if fewer profiles than the limit are returned
                    } else {
                        throw new Error("Unable to fetch profiles");
                    }
                } catch (error) {
                    console.error("Failed to fetch profiles:", error);
                    profilesContainer.innerHTML = `<p class="text-danger">Failed to load profiles.</p>`;
                }
            };

            // Event listeners for pagination
            prevPageBtn.addEventListener("click", () => {
                if (currentOffset > 0) {
                    currentOffset -= limit;
                    fetchProfiles(currentOffset);
                }
            });

            nextPageBtn.addEventListener("click", () => {
                currentOffset += limit;
                fetchProfiles(currentOffset);
            });

            // Initial fetch
            await fetchProfiles(currentOffset);
        });