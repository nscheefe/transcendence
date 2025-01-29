import {
    createTournament,
    addUserToTournament,
    getTournaments,
} from './tournamentService.js';

// Fetch and render all tournaments with "Join" functionality
const loadTournaments = async () => {
    const tournamentListEl = document.getElementById('tournament'); // Tournament list container

    // Display the tournament list
    tournamentListEl.style.display = 'block';
    tournamentListEl.innerHTML = '<span>Loading Tournaments...</span>';  // Show loading message

    try {
        const response = await getTournaments();

        // Validate and parse the response
        const tournaments = response.tournaments || [];
        tournamentListEl.innerHTML = ''; // Clear loading message

        if (tournaments.length === 0) {
            tournamentListEl.innerHTML = '<span>No tournaments found.</span>';
        } else {
            tournaments.forEach((tournament) => {
                // Create a list item for each tournament
                const tournamentEl = document.createElement('li');
                tournamentEl.className = 'tournament-item';
                tournamentEl.style.listStyle = 'none';
                tournamentEl.style.padding = '10px';
                tournamentEl.style.borderBottom = '1px solid #444';

                // Tournament details with a Join button
                tournamentEl.innerHTML = `
                    <div>
                        <h2>${tournament.name}</h2>
                        <small>Created At: ${new Date(tournament.created_at).toLocaleString()}</small>
                        <br>
                        <button class="join-btn" data-id="${tournament.id}">Join Tournament</button>
                    </div>
                `;

                // Add an event listener to the Join button
                const joinButton = tournamentEl.querySelector('.join-btn');
                joinButton.addEventListener('click', async () => {
                    try {
                        const response = await addUserToTournament(tournament.id, userId); // Add your userId logic

                        // Handle errors from the API response
                        if (response.errors && response.errors.length > 0) {
                            const errorMessage = response.errors[0].message || 'Failed to join the tournament.';
                            alert(`Error: ${errorMessage}`);
                        } else {
                            alert(`Successfully joined the tournament: ${tournament.name}`);
                        }
                    } catch (error) {
                        console.error('Error joining tournament:', error);
                        alert('Failed to join the tournament. Please try again later.');
                    }
                });

                // Append the tournament element to the list
                tournamentListEl.appendChild(tournamentEl);
            });
        }
    } catch (error) {
        console.error('Error fetching tournaments:', error);
        tournamentListEl.innerHTML = '<span>Error loading tournaments. Please try again later.</span>';
    }
};

// Handle creating a new tournament
const handleCreateTournament = async () => {
    const tournamentName = prompt('Enter the name for the new tournament:');

    if (!tournamentName) {
        alert('Tournament name is required.');
        return;
    }

    try {
        const response = await createTournament({ name: tournamentName }); // Adjust based on your API
        if (response.errors && response.errors.length > 0) {
            alert(`Error creating tournament: ${response.errors[0].message}`);
        } else {
            alert('Tournament created successfully!');

            // Reload tournaments after creating a new one
            await loadTournaments();
        }
    } catch (error) {
        console.error('Error creating tournament:', error);
        alert('Failed to create a new tournament. Please try again later.');
    }
};

// Initialize the page
export const initTournamentsPage = async () => {
    await loadTournaments(); // Load the tournaments list

    // Add event listener for Create Tournament button
    const createButton = document.getElementById('create-tournament-btn'); // Assuming there's a button in your HTML
    if (createButton) {
        createButton.addEventListener('click', handleCreateTournament);
    }
};

// Start the process when the DOM is ready
document.addEventListener('DOMContentLoaded', initTournamentsPage);
