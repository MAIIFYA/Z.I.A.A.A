// JavaScript for Sky Health Check Vote Page

document.addEventListener("DOMContentLoaded", function() {
    console.log("Vote page JS loaded.");

    // --- DOM Elements ---
    const voteForm = document.getElementById("vote-form");
    const voteMessage = document.getElementById("vote-message");
    const trendButtons = document.querySelectorAll("input[name=\"trend\"]");
    const voteValueInput = document.getElementById("vote_value");
    const trafficLightImage = document.getElementById("vote-traffic-light");
    const commentInput = document.getElementById("comment");
    const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

    // Card display elements
    const cardArea = document.getElementById("health-card-area");
    const cardTitle = document.getElementById("card-title");
    const cardDescription = document.getElementById("card-description");
    const cardCrappyExample = document.getElementById("card-crappy-example");
    const cardGoodExample = document.getElementById("card-good-example");
    const backButton = document.getElementById("back-button"); // Assuming a back button exists
    const voteSubmissionArea = document.getElementById("vote-submission-area");

    // Session/Card selection elements (Assuming these exist or will be added)
    const sessionSelect = document.getElementById("session-select"); // Needs to be added to HTML
    const cardSelect = document.getElementById("card-select"); // Needs to be added to HTML

    // --- State Variables ---
    let currentSessionId = null;
    let currentCardId = null;
    let currentCards = [];
    let currentCardIndex = -1;
    let currentVoteValue = ""; // Stores "red", "amber", "green"

    // --- Image Sources ---
    const neutralLightSrc = "/static/images/traffic_light_neutral.png"; // Adjust path if needed
    const redLightSrc = "/static/images/traffic_light_red.png";
    const amberLightSrc = "/static/images/traffic_light_amber.png"; // Add if exists
    const greenLightSrc = "/static/images/traffic_light_green.png";

    // --- API Endpoints ---
    const API_BASE = "/api/v1/";
    const SESSIONS_API = `${API_BASE}health-cards/api/sessions/`;
    const VOTES_API = `${API_BASE}votes/api/submit/`;
    const USER_VOTES_API = (sessionId, cardId) => `${API_BASE}votes/api/user/${sessionId}/?card_id=${cardId}`;

    // --- Helper Functions ---
    function showMessage(message, type = "info") {
        voteMessage.textContent = message;
        voteMessage.className = `alert alert-${type}`;
    }

    function clearMessage() {
        voteMessage.textContent = "";
        voteMessage.className = "";
    }

    async function fetchApi(url, options = {}) {
        const defaultOptions = {
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": csrfToken,
                "Accept": "application/json",
            },
        };
        const mergedOptions = { ...defaultOptions, ...options };
        mergedOptions.headers = { ...defaultOptions.headers, ...options.headers };

        try {
            const response = await fetch(url, mergedOptions);
            if (!response.ok) {
                let errorData;
                try {
                    errorData = await response.json();
                } catch (e) {
                    errorData = { detail: `HTTP error! Status: ${response.status}` };
                }
                throw new Error(errorData.detail || `HTTP error! Status: ${response.status}`);
            }
            // Handle cases where response might be empty (e.g., 204 No Content)
            if (response.status === 204) {
                return null; 
            }
            return await response.json();
        } catch (error) {
            console.error("API Fetch Error:", error);
            showMessage(`API Error: ${error.message}`, "danger");
            throw error; // Re-throw for calling function to handle
        }
    }

    // --- Voting Logic ---
    function setVoteValue(value) {
        currentVoteValue = value;
        voteValueInput.value = value;
        // Update traffic light image
        switch (value) {
            case "red":
                trafficLightImage.src = redLightSrc;
                break;
            case "amber":
                trafficLightImage.src = amberLightSrc;
                break;
            case "green":
                trafficLightImage.src = greenLightSrc;
                break;
            default:
                trafficLightImage.src = neutralLightSrc;
        }
        console.log("Vote value set to:", currentVoteValue);
        // Maybe add visual feedback (border, etc.) to the selected button
    }

    // TODO: Add clickable elements (buttons) for Red, Amber, Green
    // Example: Assuming buttons with data-vote="red", data-vote="amber", data-vote="green"
    document.querySelectorAll("[data-vote]").forEach(button => {
        button.addEventListener("click", () => {
            setVoteValue(button.dataset.vote);
            // Remove selected class from others, add to this one
            document.querySelectorAll("[data-vote]").forEach(btn => btn.classList.remove("selected"));
            button.classList.add("selected");
        });
    });

    // --- Card Loading and Display ---
    async function loadVoteForCard(sessionId, cardId) {
        try {
            const votes = await fetchApi(USER_VOTES_API(sessionId, cardId));
            // Assuming the API returns a list, and we care about the first/only vote for this user/card/session
            if (votes && votes.length > 0) {
                const vote = votes[0];
                setVoteValue(vote.vote_value);
                commentInput.value = vote.comment || "";
                // Select the correct trend radio button
                const trendRadioButton = document.querySelector(`input[name="trend"][value="${vote.trend}"]`);
                if (trendRadioButton) {
                    trendRadioButton.checked = true;
                }
                 // Mark the R/A/G button as selected
                 document.querySelectorAll("[data-vote]").forEach(btn => {
                     btn.classList.toggle("selected", btn.dataset.vote === vote.vote_value);
                 });
            } else {
                // Reset form if no previous vote
                resetVoteForm();
            }
        } catch (error) {
            console.error("Error loading previous vote:", error);
            // Don't show API error here, just proceed without pre-filling
            resetVoteForm();
        }
    }
    
    function resetVoteForm() {
        setVoteValue(""); // Reset to neutral
        commentInput.value = "";
        trendButtons.forEach(radio => radio.checked = false);
        document.querySelectorAll("[data-vote]").forEach(btn => btn.classList.remove("selected"));
        clearMessage();
    }

    function displayCard(card) {
        if (!card) {
            cardArea.style.display = "none";
            voteSubmissionArea.style.display = "none";
            return;
        }
        cardArea.style.display = "block";
        voteSubmissionArea.style.display = "block";
        currentCardId = card.id;

        cardTitle.textContent = card.title;
        cardDescription.textContent = card.description;
        cardCrappyExample.textContent = card.example_crappy;
        cardGoodExample.textContent = card.example_awesome;
        
        // Update hidden form field
        document.getElementById("card_id").value = card.id;

        // Load previous vote if exists
        loadVoteForCard(currentSessionId, currentCardId);
    }

    function navigateCards(direction) {
        if (currentCards.length === 0) return;
        
        const newIndex = currentCardIndex + direction;
        
        if (newIndex >= 0 && newIndex < currentCards.length) {
            currentCardIndex = newIndex;
            displayCard(currentCards[currentCardIndex]);
            // Update back/next button states if they exist
            backButton.style.display = (currentCardIndex > 0) ? "inline-block" : "none";
            // nextButton.style.display = (currentCardIndex < currentCards.length - 1) ? "inline-block" : "none";
        } else if (newIndex >= currentCards.length) {
            // Reached end - maybe show summary or thank you message
            showMessage("All cards voted! Thank you.", "success");
            cardArea.style.display = "none";
            voteSubmissionArea.style.display = "none";
        }
    }

    // --- Session Loading ---
    async function loadCardsForSession(sessionId) {
        currentSessionId = sessionId;
        document.getElementById("session_id").value = sessionId;
        try {
            // Fetch session details which should include the cards
            const sessionData = await fetchApi(`${SESSIONS_API}${sessionId}/`);
            currentCards = sessionData.cards || [];
            if (currentCards.length > 0) {
                currentCardIndex = 0;
                displayCard(currentCards[currentCardIndex]);
                backButton.style.display = "none"; // Hide back button on first card
            } else {
                showMessage("No health cards found for this session.", "warning");
                cardArea.style.display = "none";
                voteSubmissionArea.style.display = "none";
            }
        } catch (error) {
            showMessage("Error loading cards for the session.", "danger");
            cardArea.style.display = "none";
            voteSubmissionArea.style.display = "none";
        }
    }

    async function loadSessions() {
        if (!sessionSelect) return; // Don't run if select element doesn't exist
        try {
            const sessions = await fetchApi(SESSIONS_API);
            sessionSelect.innerHTML = ";<option value=\"\">-- Select a Session --</option>"; // Clear previous options
            sessions.forEach(session => {
                // Only show open sessions?
                if (session.status === "open") { 
                    const option = document.createElement("option");
                    option.value = session.id;
                    // Format display text (e.g., Team Name - QX YYYY)
                    option.textContent = `${session.team.name} - Q${session.quarter} ${session.year}`;
                    sessionSelect.appendChild(option);
                }
            });
            sessionSelect.disabled = false;
        } catch (error) {
            showMessage("Error loading sessions.", "danger");
            sessionSelect.disabled = true;
        }
    }

    // --- Event Listeners ---
    if (sessionSelect) {
        sessionSelect.addEventListener("change", (event) => {
            const selectedSessionId = event.target.value;
            if (selectedSessionId) {
                loadCardsForSession(selectedSessionId);
            } else {
                // Clear card area if no session selected
                currentSessionId = null;
                currentCards = [];
                currentCardIndex = -1;
                cardArea.style.display = "none";
                voteSubmissionArea.style.display = "none";
            }
        });
    }

    if (voteForm) {
        voteForm.addEventListener("submit", async function(event) {
            event.preventDefault();
            clearMessage();

            const voteValue = voteValueInput.value;
            const trend = document.querySelector("input[name=\"trend\"]:checked")?.value;
            const comment = commentInput.value;

            if (!currentSessionId || !currentCardId) {
                showMessage("Please select a session and card first.", "warning");
                return;
            }
            if (!voteValue) {
                showMessage("Please select a vote value (Red/Amber/Green).", "danger");
                return;
            }
            if (!trend) {
                showMessage("Please select a trend.", "danger");
                return;
            }

            showMessage("Submitting...", "info");

            try {
                const payload = {
                    session: currentSessionId,
                    card: currentCardId,
                    vote_value: voteValue,
                    trend: trend,
                    comment: comment
                };
                const data = await fetchApi(VOTES_API, {
                    method: "POST",
                    body: JSON.stringify(payload)
                });
                console.log("Vote submitted successfully:", data);
                showMessage("Vote saved successfully!", "success");
                // Move to the next card
                navigateCards(1);
            } catch (error) {
                // Error message already shown by fetchApi
                console.error("Error submitting vote:", error);
            }
        });
    }

    if (backButton) {
        backButton.addEventListener("click", () => {
            navigateCards(-1);
        });
    }

    // --- Initial Load ---
    loadSessions(); // Load sessions when the page loads
    // Initially hide card areas until session is selected
    cardArea.style.display = "none";
    voteSubmissionArea.style.display = "none";

});

