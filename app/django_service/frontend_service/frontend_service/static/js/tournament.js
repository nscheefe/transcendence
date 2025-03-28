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
        const response = await getTournaments() || [];

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
                    <div class="d-flex justify-content-between align-items-center p-3 border-bottom">
                        <div>
                            <a href="#tournament?tournament=${tournament.id}" class="text-decoration-none">
                                <h5 class="mb-0">${tournament.name}</h5>
                                <small class=" d-block">
                                    Created At: ${new Date(tournament.created_at).toLocaleString()}
                                </small>
                                <small class=" d-block">
                                    Tournament Size: ${tournament.tournament_size}
                                </small>
                                <small class=" d-block">
                                    Start Time: ${new Date(tournament.start_time).toLocaleString()}
                                </small>
                            </a>
                        </div>
                        <button class="btn btn-primary join-btn" data-id="${tournament.id}">Join Tournament</button>
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
                            showToast(`Error: ${errorMessage}`);
                        }else {
                            history.pushState(null, '', `?tournament=${tournament.id}`);
                        }
                    } catch (error) {
                        showToast('Error joining tournament:', error);
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


const createTournamentForm = document.getElementById('createTournamentForm');
const tournamentMessage = document.getElementById('tournamentMessage');

const handleCreateTournament = async (event) => {
    event.preventDefault();

    // Retrieve form input values
    const tournamentName = document.getElementById('tournament-name').value.trim();
    const tournamentSize = parseInt(document.getElementById('tournament-size').value.trim(), 10);
    const tournamentStartAt = new Date();

    // Validate inputs
    if (!tournamentName) {
        showToast('Tournament name is required.');
        return;
    }
    if (!tournamentSize || isNaN(tournamentSize) || [2, 4, 8, 16].indexOf(tournamentSize) === -1) {
        showToast('A valid tournament size is required.');
        return;
    }
    if (!tournamentStartAt) {
        showToast('A valid start time is required.');
        return;
    }

    try {
        // Convert the start time to a format compatible with backend expectations (remove 'Z')
        const rawDate = new Date(tournamentStartAt); // Parse input as Date object
        const formattedDate = rawDate.toISOString().split('Z')[0]; // Remove 'Z' suffix

        // Call `createTournament` function with the input values
        const response = await createTournament(tournamentName, tournamentSize);

        // Handle response
        if (response.errors && response.errors.length > 0) {
            tournamentMessage.textContent = `Error creating tournament: ${response.errors[0].message}`;
            tournamentMessage.style.color = 'red';
        } else {
            tournamentMessage.textContent = 'Tournament created successfully!';
            tournamentMessage.style.color = 'green';

            // Reload tournaments or perform any required actions
            await loadTournaments();

            // Reset the form
            createTournamentForm.reset();
        }
    } catch (error) {
        console.error('Error creating tournament:', error);
        tournamentMessage.textContent = 'Failed to create a new tournament. Please try again later.';
        tournamentMessage.style.color = 'red';
    }
};

// Add event listener for form submission
createTournamentForm.addEventListener('submit', handleCreateTournament);


export const initTournamentsPage = async () => {
    await loadTournaments(); // Load the tournaments list

    // Add event listener for Create Tournament button
    const createButton = document.getElementById('create-tournament-btn'); // Assuming there's a button in your HTML
    if (createButton) {
        createButton.addEventListener('click', handleCreateTournament);
    }
};


// Start the process when the DOM is ready
