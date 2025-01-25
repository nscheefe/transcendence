import { getStatList } from "./statService.js"; // Import the StatList query function

/**
 * Renders the leaderboard UI with fetched StatList data.
 * @param {Array} statList - The list of profiles with their stats from the API.
 */
const renderLeaderboard = (statList) => {
  const leaderboard = document.getElementById("Leaderboard");
  leaderboard.innerHTML = ""; // Clear initial content

  if (!statList || statList.length === 0) {
    leaderboard.innerHTML = "<span>No data available for the leaderboard.</span>";
    return;
  }

  // Sort and render valid lists
  const sortedStatList = statList.sort((a, b) => b.stats.winRatio - a.stats.winRatio);
  sortedStatList.forEach((entry, index) => {
    const listItem = document.createElement("li");
    listItem.innerHTML = `
                    <a href="/home/profile/${entry.profile.userId}">

<div class="card bg-dark text-light shadow-sm rounded-3 p-3 leaderboard-entry">
    <div class="d-flex justify-content-between align-items-center">
        <!-- Index, Avatar, and Nickname Section -->

        <div class="d-flex align-items-center">
            <!-- Index Number -->
            <div class="index-number me-4">
                <h1 class="mb-0 text-light">${index + 1}</h1> <!-- Replace ${index} dynamically -->
            </div>
            <!-- Avatar -->
<div class="avatar me-3">
                <div class="avatar-container">
                    <img 
                        src="${entry.profile.avatarUrl || '/static/images/default-avatar.png'}" 
                        alt="User Avatar" 
                        class="rounded-circle"
                    />
                </div>
            </div>

            <!-- Nickname and Bio -->
            <div>
                <h4 class="mb-1">${entry.profile.nickname}</h4>
                <p class="small text-muted mb-0">${entry.profile.bio || 'No bio available.'}</p>
            </div>
        </div>
            

        <!-- Statistics Section -->
        <div class="text-center flex-grow-1 d-flex justify-content-evenly align-items-center">
            <!-- Total Games -->
            <div class="stat">
                <h6 class="fw-bold text-light">Total Games</h6>
                <span class="fs-5">${entry.stats.totalGames}</span>
            </div>
            <!-- Total Wins -->
            <div class="stat border-start border-secondary px-3">
                <h6 class="fw-bold text-primary">Total Wins</h6>
                <span class="fs-5 text-primary">${entry.stats.totalWins}</span>
            </div>
            <!-- Total Losses -->
            <div class="stat border-start border-secondary px-3">
                <h6 class="fw-bold text-danger">Total Losses</h6>
                <span class="fs-5 text-danger">${entry.stats.totalLosses}</span>
            </div>
        </div>
    </div>
</div>
</a>
    `;
    leaderboard.appendChild(listItem);
  });
};

/**
 * Fetches and displays the leaderboard.
 */
const fetchLeaderboard = async () => {
  try {
    const statList = await getStatList();
    console.log("Processed StatList:", statList); // Log the final stat list
    renderLeaderboard(statList);
  } catch (error) {
    console.error("Error fetching leaderboard data:", error.message);

    const leaderboard = document.getElementById("Leaderboard");
    leaderboard.innerHTML = "<span>Error loading leaderboard. Please try again later.</span>";
  }
};

// Automatically fetch and render the leaderboard when the page is ready
document.addEventListener("DOMContentLoaded", () => {
  fetchLeaderboard();
});