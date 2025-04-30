// Sky Health Check Main JavaScript

// Wait for the DOM to be fully loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize tooltips
    initTooltips();
    
    // Initialize staggered animations
    initStaggeredAnimations();
    
    // Initialize traffic light voting system
    initTrafficLightVoting();
    
    // Initialize charts if Chart.js is available
    if (typeof Chart !== 'undefined') {
        initCharts();
    }
    
    // Initialize notifications
    initNotifications();
    
    // Add page transition effect
    addPageTransitionEffect();
    
    // Initialize sidebar toggle
    initSidebarToggle();
});

// Initialize Bootstrap tooltips
function initTooltips() {
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
}

// Initialize staggered animations for lists
function initStaggeredAnimations() {
    const staggeredItems = document.querySelectorAll('.staggered-item');
    
    if (staggeredItems.length > 0) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach((entry, index) => {
                if (entry.isIntersecting) {
                    setTimeout(() => {
                        entry.target.classList.add('show');
                    }, index * 100); // Stagger by 100ms
                    observer.unobserve(entry.target);
                }
            });
        }, { threshold: 0.1 });
        
        staggeredItems.forEach(item => {
            observer.observe(item);
        });
    }
}

// Initialize traffic light voting system
function initTrafficLightVoting() {
    const trafficLightOptions = document.querySelectorAll('.traffic-light-option');
    
    trafficLightOptions.forEach(option => {
        option.addEventListener('click', function() {
            // Get the parent traffic light container
            const trafficLight = this.closest('.traffic-light');
            
            // Remove selected class from all options in this traffic light
            trafficLight.querySelectorAll('.traffic-light-option').forEach(opt => {
                opt.classList.remove('selected');
            });
            
            // Add selected class to the clicked option
            this.classList.add('selected');
            
            // Add bounce animation
            this.classList.add('vote-animation');
            this.classList.add('selected');
            
            // Get the vote value (red, amber, green)
            const voteValue = this.getAttribute('data-value');
            
            // Get the card ID and session ID
            const cardId = trafficLight.getAttribute('data-card-id');
            const sessionId = trafficLight.getAttribute('data-session-id');
            
            // Get the comment
            const commentElement = trafficLight.nextElementSibling.querySelector('textarea');
            const comment = commentElement ? commentElement.value : '';
            
            // Submit the vote via AJAX
            submitVote(sessionId, cardId, voteValue, comment);
        });
    });
}

// Submit vote via AJAX
function submitVote(sessionId, cardId, voteValue, comment) {
    // Create the request data
    const data = {
        session_id: sessionId,
        card_id: cardId,
        vote_value: voteValue,
        comment: comment
    };
    
    // Send the AJAX request
    fetch('/votes/api/vote/submit/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCookie('csrftoken')
        },
        body: JSON.stringify(data)
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showNotification('Vote submitted successfully!', 'success');
        } else {
            showNotification('Error: ' + data.error, 'error');
        }
    })
    .catch(error => {
        showNotification('Error submitting vote: ' + error, 'error');
    });
}

// Initialize charts
function initCharts() {
    // Team summary chart
    const teamSummaryChartElement = document.getElementById('teamSummaryChart');
    if (teamSummaryChartElement) {
        const ctx = teamSummaryChartElement.getContext('2d');
        
        // Get the data from the data attributes
        const redVotes = parseInt(teamSummaryChartElement.getAttribute('data-red') || 0);
        const amberVotes = parseInt(teamSummaryChartElement.getAttribute('data-amber') || 0);
        const greenVotes = parseInt(teamSummaryChartElement.getAttribute('data-green') || 0);
        
        new Chart(ctx, {
            type: 'doughnut',
            data: {
                labels: ['Red', 'Amber', 'Green'],
                datasets: [{
                    data: [redVotes, amberVotes, greenVotes],
                    backgroundColor: ['#ff3333', '#ffbf00', '#00cc66'],
                    borderWidth: 0
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    animateScale: true,
                    animateRotate: true,
                    duration: 2000,
                    easing: 'easeOutBounce'
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Department summary chart
    const departmentSummaryChartElement = document.getElementById('departmentSummaryChart');
    if (departmentSummaryChartElement) {
        const ctx = departmentSummaryChartElement.getContext('2d');
        
        // Get the data from the data attributes
        const teams = JSON.parse(departmentSummaryChartElement.getAttribute('data-teams') || '[]');
        const redData = JSON.parse(departmentSummaryChartElement.getAttribute('data-red') || '[]');
        const amberData = JSON.parse(departmentSummaryChartElement.getAttribute('data-amber') || '[]');
        const greenData = JSON.parse(departmentSummaryChartElement.getAttribute('data-green') || '[]');
        
        new Chart(ctx, {
            type: 'bar',
            data: {
                labels: teams,
                datasets: [
                    {
                        label: 'Red',
                        data: redData,
                        backgroundColor: '#ff3333',
                        borderWidth: 0
                    },
                    {
                        label: 'Amber',
                        data: amberData,
                        backgroundColor: '#ffbf00',
                        borderWidth: 0
                    },
                    {
                        label: 'Green',
                        data: greenData,
                        backgroundColor: '#00cc66',
                        borderWidth: 0
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                },
                scales: {
                    x: {
                        stacked: true
                    },
                    y: {
                        stacked: true,
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
    
    // Trend chart
    const trendChartElement = document.getElementById('trendChart');
    if (trendChartElement) {
        const ctx = trendChartElement.getContext('2d');
        
        // Get the data from the data attributes
        const labels = JSON.parse(trendChartElement.getAttribute('data-labels') || '[]');
        const redData = JSON.parse(trendChartElement.getAttribute('data-red') || '[]');
        const amberData = JSON.parse(trendChartElement.getAttribute('data-amber') || '[]');
        const greenData = JSON.parse(trendChartElement.getAttribute('data-green') || '[]');
        
        new Chart(ctx, {
            type: 'line',
            data: {
                labels: labels,
                datasets: [
                    {
                        label: 'Red',
                        data: redData,
                        borderColor: '#ff3333',
                        backgroundColor: 'rgba(255, 51, 51, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Amber',
                        data: amberData,
                        borderColor: '#ffbf00',
                        backgroundColor: 'rgba(255, 191, 0, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    },
                    {
                        label: 'Green',
                        data: greenData,
                        borderColor: '#00cc66',
                        backgroundColor: 'rgba(0, 204, 102, 0.1)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.4
                    }
                ]
            },
            options: {
                responsive: true,
                maintainAspectRatio: false,
                animation: {
                    duration: 2000,
                    easing: 'easeOutQuart'
                },
                scales: {
                    y: {
                        beginAtZero: true,
                        max: 100
                    }
                },
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                }
            }
        });
    }
}

// Initialize notifications
function initNotifications() {
    // Create notification container if it doesn't exist
    if (!document.querySelector('.notification-container')) {
        const container = document.createElement('div');
        container.className = 'notification-container';
        document.body.appendChild(container);
    }
}

// Show notification
function showNotification(message, type = 'info', duration = 3000) {
    const container = document.querySelector('.notification-container');
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.innerHTML = `
        <div class="notification-content">
            <div class="notification-message">${message}</div>
        </div>
    `;
    
    // Add to container
    container.appendChild(notification);
    
    // Show notification with animation
    setTimeout(() => {
        notification.classList.add('show');
    }, 10);
    
    // Hide and remove after duration
    setTimeout(() => {
        notification.classList.remove('show');
        
        // Remove from DOM after animation completes
        setTimeout(() => {
            notification.remove();
        }, 300);
    }, duration);
}

// Add page transition effect
function addPageTransitionEffect() {
    // Add transition class to main content
    const mainContent = document.querySelector('.main-content');
    if (mainContent) {
        mainContent.classList.add('page-transition');
    }
    
    // Add transition to all links that lead to internal pages
    document.querySelectorAll('a').forEach(link => {
        // Only add for internal links
        if (link.hostname === window.location.hostname && !link.hasAttribute('data-no-transition')) {
            link.addEventListener('click', function(e) {
                // Don't add transition for links with specific targets or download attributes
                if (this.getAttribute('target') === '_blank' || this.hasAttribute('download')) {
                    return;
                }
                
                e.preventDefault();
                
                // Fade out
                document.body.classList.add('page-transitioning-out');
                
                // Navigate after animation
                setTimeout(() => {
                    window.location.href = this.href;
                }, 300);
            });
        }
    });
    
    // Add class to body when page loads
    window.addEventListener('load', function() {
        document.body.classList.add('page-loaded');
    });
}

// Initialize sidebar toggle
function initSidebarToggle() {
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar = document.querySelector('.sidebar');
    const mainContent = document.querySelector('.main-content');
    
    if (sidebarToggle && sidebar && mainContent) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.toggle('sidebar-collapsed');
            mainContent.classList.toggle('main-content-expanded');
        });
    }
}

// Helper function to get CSRF token from cookies
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

// Traffic Light Animation
class TrafficLightAnimation {
    constructor(element) {
        this.element = element;
        this.lights = element.querySelectorAll('.traffic-light-option');
        this.init();
    }
    
    init() {
        // Add initial animation
        this.lights.forEach((light, index) => {
            setTimeout(() => {
                light.classList.add('animate__animated', 'animate__bounceIn');
            }, index * 200);
        });
        
        // Add click animation
        this.lights.forEach(light => {
            light.addEventListener('click', () => {
                // Remove previous animations
                light.classList.remove('animate__bounceIn', 'animate__rubberBand');
                
                // Force reflow
                void light.offsetWidth;
                
                // Add new animation
                light.classList.add('animate__animated', 'animate__rubberBand');
            });
        });
    }
}

// Initialize traffic light animations
function initTrafficLightAnimations() {
    const trafficLights = document.querySelectorAll('.traffic-light');
    trafficLights.forEach(light => {
        new TrafficLightAnimation(light);
    });
}

// Comment summarization
function summarizeComments(sessionId, cardId) {
    // Show loading spinner
    const summaryElement = document.getElementById(`summary-${sessionId}-${cardId}`);
    if (summaryElement) {
        summaryElement.innerHTML = '<div class="spinner-container"><div class="spinner"></div></div>';
    }
    
    // Fetch summary from API
    fetch(`/votes/api/vote/summarize/${sessionId}/${cardId}/`)
        .then(response => response.json())
        .then(data => {
            if (summaryElement) {
                if (data.summary) {
                    summaryElement.innerHTML = `<div class="summary-content">${data.summary}</div>`;
                    
                    // Add fade-in animation
                    const summaryContent = summaryElement.querySelector('.summary-content');
                    if (summaryContent) {
                        summaryContent.classList.add('fade-in');
                    }
                } else if (data.error) {
                    summaryElement.innerHTML = `<div class="text-danger">${data.error}</div>`;
                }
            }
        })
        .catch(error => {
            if (summaryElement) {
                summaryElement.innerHTML = `<div class="text-danger">Error: ${error}</div>`;
            }
        });
}

// Load team summary data
function loadTeamSummary(teamId, sessionId = null) {
    const summaryContainer = document.getElementById('teamSummaryContainer');
    if (!summaryContainer) return;
    
    // Show loading spinner
    summaryContainer.innerHTML = '<div class="spinner-container"><div class="spinner"></div></div>';
    
    // Build URL
    let url = `/summaries/api/team-summary/${teamId}/`;
    if (sessionId) {
        url += `${sessionId}/`;
    }
    
    // Fetch summary data
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Create summary content
            let html = `
                <div class="card shadow-sm mb-4 fade-in">
                    <div class="card-header bg-white">
                        <h5 class="mb-0">Team Summary: ${data.team.name}</h5>
                        <div class="text-muted small">Q${data.session.quarter} ${data.session.year}</div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="chart-container">
                                    <canvas id="teamVoteDistributionChart" 
                                        data-red="${data.vote_distribution.red}" 
                                        data-amber="${data.vote_distribution.amber}" 
                                        data-green="${data.vote_distribution.green}"></canvas>
                                </div>
                            </div>
                            <div class="col-md-8">
                                <div class="stats-container">
                                    <div class="row">
                                        <div class="col-md-4">
                                            <div class="stat-card text-center p-3 mb-3 bg-light rounded">
                                                <div class="stat-title">Participation</div>
                                                <div class="stat-value">${data.participation_rate.toFixed(1)}%</div>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="stat-card text-center p-3 mb-3 bg-light rounded">
                                                <div class="stat-title">Team Members</div>
                                                <div class="stat-value">${data.team.members_count}</div>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="stat-card text-center p-3 mb-3 bg-light rounded">
                                                <div class="stat-title">Trend</div>
                                                <div class="stat-value">
                                                    ${data.trend.improving > 0 ? '<i class="fas fa-arrow-up text-success"></i>' : 
                                                      data.trend.declining > 0 ? '<i class="fas fa-arrow-down text-danger"></i>' : 
                                                      '<i class="fas fa-arrows-alt-h text-warning"></i>'}
                                                </div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="trend-chart-container mt-4">
                                    <h6>Historical Trend</h6>
                                    <canvas id="teamTrendChart" 
                                        data-labels='${JSON.stringify(data.historical_data.map(d => d.label))}' 
                                        data-red='${JSON.stringify(data.historical_data.map(d => d.red))}' 
                                        data-amber='${JSON.stringify(data.historical_data.map(d => d.amber))}' 
                                        data-green='${JSON.stringify(data.historical_data.map(d => d.green))}'></canvas>
                                </div>
                            </div>
                        </div>
                        
                        <div class="card-votes mt-4">
                            <h6>Vote Distribution by Card</h6>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Card</th>
                                            <th>Red</th>
                                            <th>Amber</th>
                                            <th>Green</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
            `;
            
            // Add rows for each card
            Object.keys(data.card_votes).forEach(cardId => {
                const card = data.card_votes[cardId];
                html += `
                    <tr class="staggered-item">
                        <td>${card.title}</td>
                        <td>${card.red}</td>
                        <td>${card.amber}</td>
                        <td>${card.green}</td>
                        <td>
                            <button class="btn btn-sm btn-outline-primary" 
                                onclick="summarizeComments(${data.session.id}, ${cardId})">
                                View Comments
                            </button>
                        </td>
                    </tr>
                `;
            });
            
            html += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Update container
            summaryContainer.innerHTML = html;
            
            // Initialize charts
            initCharts();
            
            // Initialize staggered animations
            initStaggeredAnimations();
        })
        .catch(error => {
            summaryContainer.innerHTML = `
                <div class="alert alert-danger">
                    Error loading team summary: ${error}
                </div>
            `;
        });
}

// Load department summary data
function loadDepartmentSummary(departmentId, quarter = null, year = null) {
    const summaryContainer = document.getElementById('departmentSummaryContainer');
    if (!summaryContainer) return;
    
    // Show loading spinner
    summaryContainer.innerHTML = '<div class="spinner-container"><div class="spinner"></div></div>';
    
    // Build URL
    let url = `/summaries/api/department-summary/${departmentId}/`;
    if (quarter && year) {
        url += `${quarter}/${year}/`;
    }
    
    // Fetch summary data
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Create summary content
            let html = `
                <div class="card shadow-sm mb-4 fade-in">
                    <div class="card-header bg-white">
                        <h5 class="mb-0">Department Summary: ${data.department.name}</h5>
                        <div class="text-muted small">Q${data.period.quarter} ${data.period.year}</div>
                    </div>
                    <div class="card-body">
                        <div class="row">
                            <div class="col-md-4">
                                <div class="chart-container">
                                    <canvas id="departmentVoteDistributionChart" 
                                        data-red="${data.vote_distribution.red}" 
                                        data-amber="${data.vote_distribution.amber}" 
                                        data-green="${data.vote_distribution.green}"></canvas>
                                </div>
                            </div>
                            <div class="col-md-8">
                                <div class="stats-container">
                                    <div class="row">
                                        <div class="col-md-4">
                                            <div class="stat-card text-center p-3 mb-3 bg-light rounded">
                                                <div class="stat-title">Teams</div>
                                                <div class="stat-value">${data.statistics.total_teams}</div>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="stat-card text-center p-3 mb-3 bg-light rounded">
                                                <div class="stat-title">Engineers</div>
                                                <div class="stat-value">${data.statistics.total_engineers}</div>
                                            </div>
                                        </div>
                                        <div class="col-md-4">
                                            <div class="stat-card text-center p-3 mb-3 bg-light rounded">
                                                <div class="stat-title">Participation</div>
                                                <div class="stat-value">${data.statistics.participation_rate.toFixed(1)}%</div>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                                
                                <div class="trend-chart-container mt-4">
                                    <h6>Historical Trend</h6>
                                    <canvas id="departmentTrendChart" 
                                        data-labels='${JSON.stringify(data.historical_data.map(d => d.label))}' 
                                        data-red='${JSON.stringify(data.historical_data.map(d => d.red))}' 
                                        data-amber='${JSON.stringify(data.historical_data.map(d => d.amber))}' 
                                        data-green='${JSON.stringify(data.historical_data.map(d => d.green))}'></canvas>
                                </div>
                            </div>
                        </div>
                        
                        <div class="team-votes mt-4">
                            <h6>Vote Distribution by Team</h6>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Team</th>
                                            <th>Red</th>
                                            <th>Amber</th>
                                            <th>Green</th>
                                            <th>Trend</th>
                                        </tr>
                                    </thead>
                                    <tbody>
            `;
            
            // Add rows for each team
            Object.keys(data.team_votes).forEach(teamId => {
                const team = data.team_votes[teamId];
                html += `
                    <tr class="staggered-item">
                        <td>${team.name}</td>
                        <td>${team.red_percent.toFixed(1)}%</td>
                        <td>${team.amber_percent.toFixed(1)}%</td>
                        <td>${team.green_percent.toFixed(1)}%</td>
                        <td>
                            ${team.trend === 'improving' ? '<i class="fas fa-arrow-up text-success"></i>' : 
                              team.trend === 'declining' ? '<i class="fas fa-arrow-down text-danger"></i>' : 
                              '<i class="fas fa-arrows-alt-h text-warning"></i>'}
                        </td>
                    </tr>
                `;
            });
            
            html += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        
                        <div class="card-votes mt-4">
                            <h6>Vote Distribution by Card</h6>
                            <div class="table-responsive">
                                <table class="table table-hover">
                                    <thead>
                                        <tr>
                                            <th>Card</th>
                                            <th>Red</th>
                                            <th>Amber</th>
                                            <th>Green</th>
                                        </tr>
                                    </thead>
                                    <tbody>
            `;
            
            // Add rows for each card
            Object.keys(data.card_votes).forEach(cardId => {
                const card = data.card_votes[cardId];
                html += `
                    <tr class="staggered-item">
                        <td>${card.title}</td>
                        <td>${card.red_percent.toFixed(1)}%</td>
                        <td>${card.amber_percent.toFixed(1)}%</td>
                        <td>${card.green_percent.toFixed(1)}%</td>
                    </tr>
                `;
            });
            
            html += `
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            
            // Update container
            summaryContainer.innerHTML = html;
            
            // Initialize charts
            initCharts();
            
            // Initialize staggered animations
            initStaggeredAnimations();
        })
        .catch(error => {
            summaryContainer.innerHTML = `
                <div class="alert alert-danger">
                    Error loading department summary: ${error}
                </div>
            `;
        });
}
