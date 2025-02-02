
document.addEventListener('DOMContentLoaded', function () {
    let windowIsOpen = false;
    function openGenericTournamentWindow() {
        const dynamicWindows = document.querySelector('[data-dynamic-windows]');
        dynamicWindows.innerHTML = `
            <div id="pong-container">
                <button id="close-btn">Close</button>
                <div class="d-flex card bg-transparent text-light h-100 w-100" style="position: relative; z-index: 20;">
                    <div class="card-header">
                        <!-- Navigation Pills -->
                        <ul class="nav nav-tabs" id="tournamentTabs" role="tablist">
                            <li class="nav-item">
                                <button class="nav-link bg-transparent active" id="tournaments-tab" data-bs-toggle="tab" data-bs-target="#tournaments-tab-pane" type="button" role="tab" aria-controls="tournaments-tab-pane" aria-selected="true">
                                    Tournaments
                                </button>
                            </li>
                            <li class="nav-item">
                                <button class="nav-link bg-transparent" id="new-tournament-tab" data-bs-toggle="tab" data-bs-target="#new-tournament-tab-pane" type="button" role="tab" aria-controls="new-tournament-tab-pane" aria-selected="false">
                                    New Tournament
                                </button>
                            </li>
                        </ul>
                    </div>
                    <div class="tab-content card-body" id="tournamentTabContent">
                        <div class="tab-pane fade  show active" id="tournaments-tab-pane" role="tabpanel" aria-labelledby="tournaments-tab" tabindex="0">
                            <br>
                            <h1>Tournaments</h1>
                            <ul id="tournament" class="scrollable" style="width:100%; max-height:60vh">
                                <span>Loading Tournaments ....</span>
                            </ul>
                        </div>
                        <div class="tab-pane fade" id="new-tournament-tab-pane" role="tabpanel" aria-labelledby="new-tournament-tab" tabindex="0">
                            <div id="createTournamentContainer">
                                <h2>Create a New Tournament</h2>
                                <form id="createTournamentForm">
                                    <div>
                                        <label for="tournament-name">Tournament Name:</label>
                                        <input class="form-control bg-secondary text-light" id="tournament-name" type="text" maxlength="50"  placeholder="Enter tournament name" required />
                                    </div>
                                    <div>
                                        <label for="tournament-size">Tournament Size:</label>
                                        <select id="tournament-size" required class="form-control bg-secondary text-light">
                                            <option value="2">2</option>
                                            <option value="4">4</option>
                                            <option value="8">8</option>
                                            <option value="16">16</option>
                                        </select>
                                    </div>
                                    <button type="submit" class="btn btn-primary">Create Tournament</button>
                                </form>
                                <div id="tournamentMessage"></div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
        import('/static/js/tournament.js')
            .then((module) => {
                module.initTournamentsPage();
            })
            .catch((error) => {
                showToast('Error loading tournament module:', error);
            });
        windowIsOpen = true;
        const closeBtn = document.getElementById('close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                closeTournamentWindow();
                history.pushState(null, null, '#');
            });
        }
    }
    function closeTournamentWindow() {
        const dynamicWindows = document.querySelector('[data-dynamic-windows]');
        dynamicWindows.innerHTML = ''; // Clear the content
        windowIsOpen = false;
    }
    const tournamentBtn = document.getElementById('tournament-btn');
    tournamentBtn.addEventListener('click', (event) => {
        event.preventDefault();
        const targetHash = '#tournament';
        if (window.location.hash !== targetHash) {
            history.pushState(null, null, targetHash);
        }
        openGenericTournamentWindow();
    });
    window.addEventListener('popstate', () => {
        const targetHash = '#tournament';

        if (window.location.hash === targetHash) {
            if (!windowIsOpen) {
                openGenericTournamentWindow();
            }
        } else {
            if (windowIsOpen) {
                closeTournamentWindow();
            }
        }
    });
    if (window.location.hash === '#tournament') {
        openGenericTournamentWindow();
    }
    function openTournamentDetails(tournamentId) {
        const tournamentsTabPane = document.querySelector('[data-dynamic-windows]');
        tournamentsTabPane.innerHTML = `
        <div id="pong-container">
            <button id="close-btn">Close</button>
            <div class="d-flex card bg-transparent text-light h-100 w-100" style="position: relative; z-index: 20;">
                <section id="tournamentSection" class="tournamentSection">
                    <div class="text-light">
                        <div class="text-center py-4">
                            <h1 id="tournamentName">Tournament: ${tournamentId}</h1>
                        </div>
                        <div class="card bg-dark text-light mb-4 shadow">
                            <div class="card-body">
                                <div class="row">
                                    <div class="col-md-4 text-center">
                                        <h5>Start Date & Time</h5>
                                        <p id="tournamentDate">Start Date</p>
                                    </div>
                                    <div class="col-md-4 text-center">
                                        <h5>Players</h5>
                                        <p id="playerCount">Players Count</p>
                                    </div>
                                    <div class="col-md-4 text-center">
                                        <h5>Status</h5>
                                        <p id="tournamentStatus">Status</p>
                                    </div>
                                </div>
                            </div>
                        </div>
                        <div class="card bg-dark text-light mb-4 shadow scrollable" style="max-height: 50vh">
                            <div class="card-body">
                                <h4>Current Matches</h4>
                                <div id="currentMatches" class="list-group mt-3" style="flex-direction: column-reverse;"></div>
                                <div id="stateButtonContainer"></div>
                            </div>
                        </div>
                        <div class="card bg-dark text-light shadow scrollable" style="max-height: 20vh">
                            <div class="card-body">
                                <h4>Brackets</h4>
                                <div id="previousMatchesContainer"></div>
                            </div>
                        </div>
                    </div>
                </section>
            </div>
        </div>`;
        import('/static/js/tournamentDetails.js')
            .then((module) => {
                module.iniTournamenDetailPage();
            })
            .catch((error) => {
                showToast('Error loading tournament Details module:', error);
            });
    }
    function handleUrl() {
        const hash = window.location.hash.split('?')[0];
        const queryString = window.location.hash.includes('?')
            ? window.location.hash.split('?')[1]
            : '';
        if (hash === '#tournament') {
            if (queryString) {
                const urlParams = new URLSearchParams(queryString);
                tournamentId = parseInt(urlParams.get('tournament'));
                if (tournamentId) {
                    openTournamentDetails(tournamentId);
                } else {
                    openGenericTournamentWindow();
                }
            } else {
                openGenericTournamentWindow();
            }
        }
    }
    handleUrl();
    window.addEventListener('popstate', function () {
        handleUrl();
    });
    document.addEventListener('click', function (event) {
        if (event.target.id === 'close-btn') {
            const dynamicWindows = document.querySelector('[data-dynamic-windows]');
            dynamicWindows.innerHTML = '';
            history.pushState(null, null, '/home/');
        }
    });
});