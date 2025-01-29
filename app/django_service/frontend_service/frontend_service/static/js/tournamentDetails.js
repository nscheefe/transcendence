import { getTournamentById } from "./tournamentService.js";
import { fetchProfileByUserId } from "./profileservice.js";

document.addEventListener("DOMContentLoaded", async () => {
    const treeContainer = document.querySelector("#tournamentPlayer");
    const startTimeElement = document.getElementById("startTime");
    const tournamentNameElement = document.querySelector("#tournamentName");
    const tournamentInfoElement = document.querySelector("#tournamentInfo");
    const startDateElement = document.querySelector("#startDate");
    const playerCountElement = document.querySelector("#playerCount");

    const startTime = "10/14/2023, 4:30 PM"; // Example start time, dynamically fetched below

    // Dynamically set the start time
    if (startTimeElement) {
        startTimeElement.textContent = `Start Time: ${startTime}`;
    }

    try {
        // Fetch the tournament data
        const tournamentData = await getTournamentById(tournamentId);
        console.log("Fetched tournament data:", tournamentData);

        // Extract important tournament details
        const tournament = tournamentData?.tournament;
        const players = tournament?.users;

        // Check for valid data
        if (!players || !Array.isArray(players)) {
            throw new Error("Tournament data is missing or invalid: 'users' array not found.");
        }

        // Dynamically set tournament name and other details
        if (tournamentNameElement) {
            tournamentNameElement.textContent = tournament?.name || "Tournament Name Unavailable";
        }
        if (tournamentInfoElement) {
            tournamentInfoElement.textContent = tournament?.info || "No additional information about this tournament.";
        }
        if (startDateElement) {
            startDateElement.textContent = `Start Date: ${tournament?.start_date || "Unknown"}`;
        }
        if (playerCountElement) {
            playerCountElement.textContent = `Number of Players: ${players.length}`;
        }

        // Sort players by play_order to determine matchups
        const sortedPlayers = [...players].sort((a, b) => a.play_order - b.play_order);

        // Generate the tournament tree and display it
        const treeHtml = await generateTournamentTree(sortedPlayers);
        treeContainer.innerHTML = treeHtml;
    } catch (error) {
        console.error("Error fetching tournament details:", error);
        treeContainer.innerHTML = `<p class="error">Failed to load tournament data</p>`;
    }
});

/**
 * Function to generate a nested tournament tree from sorted player data.
 * @param {Array} players - Array of player objects sorted by `play_order`.
 * @returns {Promise<string>} - HTML string for the tournament tree.
 */
async function generateTournamentTree(players) {
    // Recursive async function to build the tree
    async function buildTree(currentPlayers) {
        if (currentPlayers.length === 1) {
            // Fetch profile data for the single player
            const profile = await fetchProfileByUserId(currentPlayers[0].user_id);
            const playerHtml = await getPlayerHtml(profile, currentPlayers[0].games_played);
            return `
                <li>
                    ${playerHtml}
                </li>
            `;
        }

        let nextRoundPlayers = [];
        let treeHtml = "<ul>\n";

        // Pair players and build subtrees for matches
        for (let i = 0; i < currentPlayers.length; i += 2) {
            if (i + 1 < currentPlayers.length) {
                // Fetch profiles for both players and render the match
                const profile1 = await fetchProfileByUserId(currentPlayers[i].user_id);
                const profile2 = await fetchProfileByUserId(currentPlayers[i + 1].user_id);
                console.log("profile1", profile1);
                console.log("profile2", profile2);
                const playerHtml1 = await getPlayerHtml(profile1, currentPlayers[i].games_played);
                const playerHtml2 = await getPlayerHtml(profile2, currentPlayers[i + 1].games_played);

                treeHtml += `
                    <li>
                        <a href="#">Match ${Math.floor(i / 2) + 1}</a>
                        <ul>
                            ${await buildTree([currentPlayers[i]])}
                            ${await buildTree([currentPlayers[i + 1]])}
                        </ul>
                    </li>
                `;
                nextRoundPlayers.push({ play_order: `Winner of Match ${Math.floor(i / 2) + 1}`, games_played: currentPlayers[i].games_played + 1 });
            } else {
                // Single player advances automatically if odd number
                const profile = await fetchProfileByUserId(currentPlayers[i].user_id);
                const playerHtml = await getPlayerHtml(profile, currentPlayers[i].games_played);

                treeHtml += `
                    <li>
                        ${playerHtml}
                    </li>
                `;
                nextRoundPlayers.push(currentPlayers[i]);
            }
        }

        treeHtml += "</ul>";
        return treeHtml;
    }

    // Start building tree from the full list of players
    const nestedTree = await buildTree(players);

    // Wrap the entire tree with a root-level container
    return `
        <div class="tree">
            <ul>
                <li>
                    <a href="#">Tournament Winner</a>
                    ${nestedTree}
                </li>
            </ul>
        </div>
    `;
}

/**
 * Helper function to generate HTML for a player using their profile and current games_played.
 * @param {Object} profile - Player profile object containing avatar and username.
 * @param {number} games_played - Number of rounds the player has participated in.
 * @returns {string} - HTML snippet for the player.
 */
async function getPlayerHtml(playerData, games_played) {
    console.log("Debug: Entering getPlayerHtml");
    console.log("Debug: Profile data received:", playerData);
    console.log("Debug: Games played value received:", games_played);

    // Extract the nested profile object
    const profile = playerData.profile || {}; // Safely access the nested profile object

    // Extract avatarUrl, nickname, and other values from the nested profile
    const avatar = profile.avatarUrl || "/images/default_avatar.png"; // Fallback for missing avatar
    const nickname = profile.nickname || "Unknown Player";           // Fallback for nickname
    const rounds = games_played ?? "N/A";                            // Fallback for games played

    console.log(`Debug: Processed values - Avatar: ${avatar}, Nickname: ${nickname}, Rounds: ${rounds}`);

    // Generate HTML output
    const html = `
        <a href="/home/profile/${profile.id || '#'}" class="player">
<img 
    src="${avatar}" 
    alt="${nickname}" 
    class="avatar"
    height="60" 
    width="60" 
    style="border-radius: 50%; max-width: 210px; max-height: 210px; object-fit: cover;"
/><br>
            <span class="username">${nickname}</span><br>
            <span class="round-info">Round: ${rounds}</span>
        </a>
    `;

    console.log("Debug: Generated HTML:", html);
    return html;
}