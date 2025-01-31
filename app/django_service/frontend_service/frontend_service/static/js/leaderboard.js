import { getStatList } from "./statService.js"; // Import the StatList query function
import { generateUserAvatarHTML, fillUserCache, userCache, initializeOnlineStatusSubscriptions} from "./utils.js";

/**
 * Renders the leaderboard UI with fetched StatList data.
 * @param {Array} statList - The list of profiles with their stats from the API.
 */
const renderLeaderboard = (statList) => {
  const leaderboard = document.getElementById("Leaderboard");
  if (!leaderboard) return; // Ensure the element exists
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
                <h1 class="mb-0 text-light">${index + 1}</h1>
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
 * Renders the top 3 leaderboard UI with fetched StatList data.
 * @param {Array} statList - The list of profiles with their stats from the API.
 */
const renderTop3Leaderboard = (statList) => {
  const leaderboardTop3 = document.getElementById("leaderboard-top-3");
  if (!leaderboardTop3) return; // Ensure the element exists
  leaderboardTop3.innerHTML = ""; // Clear initial content

  if (!statList || statList.length === 0) {
    leaderboardTop3.innerHTML = "<span>No data available for the leaderboard.</span>";
    return;
  }

  // Sort and render the top 3 entries
  const sortedStatList = statList.sort((a, b) => b.stats.winRatio - a.stats.winRatio);
  sortedStatList.slice(0, 3).forEach((entry, index) => {
    userCache[entry.profile.userId] = entry; // Add the user to the cache
    const listItem = document.createElement("li");
    const avatarHTML = generateUserAvatarHTML(entry.profile.userId, 50);
    listItem.classList.add("leaderboard-item");
    listItem.innerHTML = `
      <a href="/home/profile/${entry.profile.userId}" class="bg-transparent text-decoration-none">
        <div class="card bg-transparent text-light shadow-sm rounded-1 p-3 leaderboard-entry blur-background border-dark" style="--bs-border-opacity: .5;">
          <div class="d-flex justify-content-between align-items-center">
            <!-- Index, Avatar, and Nickname Section -->
            <div class="d-flex align-items-center">
              <!-- Index Number -->
              <!-- Avatar -->
              <div class="avatar me-3">
              <div class="text-center d-flex flex-row align-items-center justify-content-evenly mb-2">
                <div class="index-number me-1">
                  <h2 class="mb-0">${index + 1}</h1>
                </div>
                <div class="avatar-container">
                ${avatarHTML}
                </div>
              </div>
                <h4 class="mb-1">${entry.profile.nickname}</h4>
              </div>
              <!-- Nickname and Bio -->
              <div class="d-flex flex-column">
                <div class="text-center flex-grow-1 d-flex justify-content-evenly align-items-center">
                  <!-- Total Games -->
                  <div class="stat px-3">
                    <h6 class="fw-bold">Games</h6>
                    <span class="fs-5">${entry.stats.totalGames}</span>
                  </div>
                  <!-- Total Wins -->
                  <div class="stat text-success border-start border-secondary px-3">
                    <h6 class="fw-bold">Wins</h6>
                    <span class="fs-5 ">${entry.stats.totalWins}</span>
                  </div>
                  <!-- Total Losses -->
                  <div class="stat border-start border-secondary px-3">
                    <h6 class="fw-bold text-danger">Losses</h6>
                    <span class="fs-5 text-danger">${entry.stats.totalLosses}</span>
                  </div>
              </div>
            </div>
            <!-- Statistics Section -->
            </div>
          </div>
        </div>
      </a>
    `;
    leaderboardTop3.appendChild(listItem);
  });
};

/**
 * Fetches and displays the leaderboard.
 */
const fetchLeaderboard = async () => {
  try {
    const response = await getStatList();
    const statList = response.StatList;
    if (!Array.isArray(statList)) {
      throw new Error("StatList is not an array");
    }
    console.log("Processed StatList:", statList); // Log the final stat list
    renderLeaderboard(statList);
  } catch (error) {
    console.error("Error fetching leaderboard data:", error.message);

    const leaderboard = document.getElementById("Leaderboard");
    if (leaderboard) {
      leaderboard.innerHTML = "<span>Error loading leaderboard. Please try again later.</span>";
    }
  }
};

/**
 * Fetches and displays the top 3 leaderboard.
 */
const fetchTop3Leaderboard = async () => {
  try {
    const response = await getStatList();
    const statList = response.StatList;
    if (!Array.isArray(statList)) {
      throw new Error("StatList is not an array");
    }
    console.log("Processed StatList:", statList); // Log the final stat list
    renderTop3Leaderboard(statList);
    initializeOnlineStatusSubscriptions();
  } catch (error) {
    console.error("Error fetching leaderboard data:", error.message);

    const leaderboardTop3 = document.getElementById("leaderboard-top-3");
    if (leaderboardTop3) {
      leaderboardTop3.innerHTML = "<span>Error loading leaderboard. Please try again later.</span>";
    }
  }
};

// Automatically fetch and render the top 3 leaderboard when the page is ready
document.addEventListener("DOMContentLoaded", () => {
  if (document.getElementById("leaderboard-top-3")) {
    fetchTop3Leaderboard();
  }
  if (document.getElementById("Leaderboard")) {
    fetchLeaderboard();
  }
});
