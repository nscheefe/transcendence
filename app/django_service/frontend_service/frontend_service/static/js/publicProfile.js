import { fetchProfileByUserId } from './profileservice.js';
import {getStatsByUser} from "./statService.js";


const renderDetailedUserStats = async (statsByUser, userProfile, userId) => {
    const opponents = await Promise.all(
        statsByUser.map(async (stat) => {
            const isWinner = stat.stat.winnerId === userId;
            const opponentId = isWinner ? stat.stat.loserId : stat.stat.winnerId;
            return { opponentId, opponent: await fetchProfileByUserId(opponentId) };
        })
    );
    return `
        <div class="stats-list mt-3 scrollable" style="max-height: 50vh">
            ${statsByUser.map((stat) => {
                const date = stat.stat.createdAt;
                const result = stat.didWin ? 'win' : 'loss';
                const opponentData = opponents.find(o => o.opponentId === (stat.stat.winnerId === userId ? stat.stat.loserId : stat.stat.winnerId));
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
                                <img src="${userProfile.profile.avatarUrl || 'https://via.placeholder.com/50'}" alt="${userProfile.profile.nickname}">
                                <span>${userProfile.profile.nickname}</span>
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
    `;
};
const updateUserGameStats = async (userId, userProfile) => {
    try {
        const response = await getStatsByUser(userId);

        const statsByUser = response.statsByUser;
        if (!Array.isArray(statsByUser)) {
            throw new Error('Invalid statsByUser: not an array');
        }
        const statsContainer = document.getElementById('user-games-stats');
        if (!statsContainer) {
            showToast("Container with id 'user-games-stats' not found!");
            return;
        }
        const statsHtml = await renderDetailedUserStats(statsByUser, userProfile, userId);
        statsContainer.innerHTML = statsHtml;
    } catch (error) {
        showToast('Error in updateUserGameStats:', error);
        const statsContainer = document.getElementById('user-games-stats');
        if (statsContainer) {
            statsContainer.innerHTML = `
                <div class="alert alert-danger mt-3" role="alert">
                    Unable to load user game stats. Please try again later.
                </div>
            `;
        }
    }
};
document.addEventListener('DOMContentLoaded', async () => {
    const profile = await fetchProfileByUserId(profileUserId);
    await updateUserGameStats(profileUserId, profile);
});