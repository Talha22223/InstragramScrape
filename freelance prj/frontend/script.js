// API Base URL
const API_BASE_URL = 'http://localhost:5000/api';

// Global state
let analysisData = null;
let allComments = [];
let currentFilter = 'all';
let currentMode = 'single'; // 'single' or 'profile'
let currentPlatform = 'instagram'; // 'instagram' or 'facebook'

// DOM Elements
const urlForm = document.getElementById('urlForm');
const urlInput = document.getElementById('urlInput');
const profileUrlInput = document.getElementById('profileUrlInput');
const fromDateInput = document.getElementById('fromDateInput');
const maxPostsInput = document.getElementById('maxPostsInput');
const errorMessage = document.getElementById('errorMessage');
const inputSection = document.getElementById('inputSection');
const loadingSection = document.getElementById('loadingSection');
const dashboardSection = document.getElementById('dashboardSection');
const resetButton = document.getElementById('resetButton');
const commentTabs = document.getElementById('commentTabs');
const commentsList = document.getElementById('commentsList');
const singleMode = document.getElementById('singleMode');
const profileMode = document.getElementById('profileMode');
const analyzeButtonText = document.getElementById('analyzeButtonText');
const featureBulk = document.getElementById('featureBulk');
const singleIcon = document.getElementById('singleIcon');
const bulkIcon = document.getElementById('bulkIcon');

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    // Set max date to today
    const today = new Date().toISOString().split('T')[0];
    fromDateInput.max = today;
    
    urlForm.addEventListener('submit', handleAnalyze);
    resetButton.addEventListener('click', handleReset);
    
    // Platform buttons
    const platformButtons = document.querySelectorAll('.platform-btn');
    platformButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const platform = e.currentTarget.dataset.platform;
            switchPlatform(platform);
        });
    });
    
    // Mode buttons
    const modeButtons = document.querySelectorAll('.mode-btn');
    modeButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const mode = e.currentTarget.dataset.mode;
            switchMode(mode);
        });
    });
    
    // Tab buttons
    const tabButtons = commentTabs.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        button.addEventListener('click', (e) => {
            const filter = e.currentTarget.dataset.filter;
            setActiveTab(filter);
            filterComments(filter);
        });
    });
});

// Switch between platforms
function switchPlatform(platform) {
    currentPlatform = platform;
    
    // Update button states
    const platformButtons = document.querySelectorAll('.platform-btn');
    platformButtons.forEach(btn => {
        if (btn.dataset.platform === platform) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Update the main logo icon
    const cardIcon = document.querySelector('.card-icon i');
    const cardIconContainer = document.querySelector('.card-icon');
    if (platform === 'instagram') {
        cardIcon.className = 'fab fa-instagram';
        cardIconContainer.classList.remove('fb-logo');
        cardIconContainer.classList.add('insta-logo');
    } else {
        cardIcon.className = 'fab fa-facebook';
        cardIconContainer.classList.remove('insta-logo');
        cardIconContainer.classList.add('fb-logo');
    }
    
    // Update placeholders and button text
    updatePlaceholders();
    hideError();
}

// Switch between single and profile mode
function switchMode(mode) {
    currentMode = mode;
    
    // Update button states
    const modeButtons = document.querySelectorAll('.mode-btn');
    modeButtons.forEach(btn => {
        if (btn.dataset.mode === mode) {
            btn.classList.add('active');
        } else {
            btn.classList.remove('active');
        }
    });
    
    // Show/hide appropriate inputs
    if (mode === 'single') {
        singleMode.style.display = 'block';
        profileMode.style.display = 'none';
    } else {
        singleMode.style.display = 'none';
        profileMode.style.display = 'block';
    }
    
    // Update placeholders and button text
    updatePlaceholders();
    hideError();
}

// Update placeholders and button text based on platform and mode
function updatePlaceholders() {
    if (currentPlatform === 'instagram') {
        if (currentMode === 'single') {
            urlInput.placeholder = 'https://www.instagram.com/p/ABC123...';
            analyzeButtonText.textContent = 'Analyze Post';
            featureBulk.textContent = '✓ Single post analysis';
        } else {
            profileUrlInput.placeholder = 'https://www.instagram.com/username/';
            analyzeButtonText.textContent = 'Analyze Profile';
            featureBulk.textContent = '✓ Bulk analysis of all posts from date';
        }
    } else {
        if (currentMode === 'single') {
            urlInput.placeholder = 'https://www.facebook.com/.../posts/... (Group, Page, or Profile post)';
            analyzeButtonText.textContent = 'Analyze Post';
            featureBulk.textContent = '✓ Single post analysis';
        } else {
            profileUrlInput.placeholder = 'https://www.facebook.com/... (Group, Page, or Profile URL)';
            analyzeButtonText.textContent = 'Analyze Facebook';
            featureBulk.textContent = '✓ Bulk analysis of all posts from date';
        }
    }
}

// Validate Instagram URL
function validateInstagramUrl(url) {
    const instagramRegex = /^https?:\/\/(www\.)?instagram\.com\/(p|reel)\/[\w-]+\/?/;
    return instagramRegex.test(url);
}

// Validate Instagram Profile URL
function validateInstagramProfileUrl(url) {
    const profileRegex = /^https?:\/\/(www\.)?instagram\.com\/[\w.]+\/?$/;
    return profileRegex.test(url);
}

// Validate Facebook URL (for bulk analysis - groups, pages, profiles)
function validateFacebookUrl(url) {
    // Accept groups, pages, profiles, or any facebook.com URL
    const facebookRegex = /^https?:\/\/(www\.)?facebook\.com\/(groups|pages|profile\.php|[\w.-]+)\/?.*$/;
    return facebookRegex.test(url);
}

// Validate Facebook Post URL (from any source: group, page, profile, public post)
function validateFacebookPostUrl(url) {
    // Accept any facebook.com URL that looks like a post
    // Be more permissive - just check it's a facebook URL with some content
    if (!url.includes('facebook.com')) return false;
    
    // Must have some kind of post indicator
    return url.includes('/posts/') || 
           url.includes('/permalink/') || 
           url.includes('/photo') || 
           url.includes('/video') || 
           url.includes('/story') ||
           url.includes('fbid=') ||
           url.match(/\/\d+\//); // Contains numeric ID
}

// Validate Facebook Group URL (for bulk analysis)
function validateFacebookGroupUrl(url) {
    const groupRegex = /^https?:\/\/(www\.)?facebook\.com\/groups\/[\w.-]+\/?(\?.*)?$/;
    return groupRegex.test(url);
}

// Show error
function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    if (currentMode === 'single') {
        urlInput.classList.add('input-error');
    } else {
        profileUrlInput.classList.add('input-error');
    }
}

// Hide error
function hideError() {
    errorMessage.style.display = 'none';
    urlInput.classList.remove('input-error');
    profileUrlInput.classList.remove('input-error');
    fromDateInput.classList.remove('input-error');
}

// Handle form submission
async function handleAnalyze(e) {
    e.preventDefault();
    hideError();
    
    let endpoint, body;
    
    if (currentMode === 'single') {
        // Single post analysis
        const url = urlInput.value.trim();
        
        if (!url) {
            showError(currentPlatform === 'instagram' ? 'Please enter an Instagram URL' : 'Please enter a Facebook post URL');
            return;
        }
        
        // Validate based on platform
        if (currentPlatform === 'instagram') {
            if (!validateInstagramUrl(url)) {
                showError('Please enter a valid Instagram post or reel URL');
                return;
            }
            endpoint = `${API_BASE_URL}/analyze`;
            body = { url, platform: 'instagram' };
        } else {
            if (!validateFacebookPostUrl(url)) {
                showError('Please enter a valid Facebook post URL. Copy the full URL from your browser.');
                return;
            }
            endpoint = `${API_BASE_URL}/analyze`;
            body = { url, platform: 'facebook' };
        }
        
    } else {
        // Bulk analysis (Profile or Group)
        const profileUrl = profileUrlInput.value.trim();
        const fromDate = fromDateInput.value;
        const maxPosts = parseInt(maxPostsInput.value) || 20;
        
        if (!profileUrl) {
            showError(currentPlatform === 'instagram' ? 'Please enter an Instagram profile URL' : 'Please enter a Facebook group URL');
            return;
        }
        
        // Validate based on platform
        if (currentPlatform === 'instagram') {
            if (!validateInstagramProfileUrl(profileUrl)) {
                showError('Please enter a valid Instagram profile URL (e.g., https://www.instagram.com/username/)');
                return;
            }
            endpoint = `${API_BASE_URL}/analyze-profile`;
            body = {
                profile_url: profileUrl,
                from_date: fromDate,
                max_posts: maxPosts
            };
        } else {
            // Clean the URL by removing query parameters for bulk analysis
            let cleanUrl = profileUrl.split('?')[0];
            if (!cleanUrl.endsWith('/')) {
                cleanUrl += '/';
            }
            
            if (!validateFacebookUrl(profileUrl)) {
                showError('Please enter a valid Facebook URL (group, page, or profile). Example: https://www.facebook.com/username/ or https://www.facebook.com/groups/123456/');
                return;
            }
            endpoint = `${API_BASE_URL}/analyze-facebook-group`;
            body = {
                group_url: cleanUrl,
                from_date: fromDate,
                max_posts: maxPosts
            };
        }
        
        if (!fromDate) {
            showError('Please select a start date');
            return;
        }
    }
    
    // Show loading with appropriate message
    inputSection.style.display = 'none';
    loadingSection.style.display = 'flex';
    
    // Update loading message based on platform and mode
    const loadingText = document.querySelector('.loading-text h2');
    if (currentPlatform === 'instagram') {
        loadingText.textContent = currentMode === 'single' ? 'Analyzing Instagram Post...' : 'Analyzing Instagram Profile...';
    } else {
        loadingText.textContent = currentMode === 'single' ? 'Analyzing Facebook Post...' : 'Analyzing Facebook Group...';
    }
    
    try {
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(body),
        });
        
        const result = await response.json();
        
        if (result.success) {
            // Add metadata to the data
            result.data.type = currentMode;
            result.data.platform = currentPlatform;
            
            analysisData = result.data;
            displayDashboard(result.data);
            
            if (currentMode === 'profile') {
                showNotification(`Analysis completed! Analyzed ${result.data.total_posts} posts with ${result.data.total_comments} comments.`, 'success');
            } else {
                showNotification('Analysis completed successfully!', 'success');
            }
        } else {
            // Handle error response with detailed information
            let errorMsg = result.error || 'Analysis failed';
            
            // Add solutions/suggestions if available
            if (result.details) {
                if (result.details.solutions) {
                    errorMsg += '\n\n' + result.details.solutions.join('\n');
                } else if (result.details.suggestions) {
                    errorMsg += '\n\n' + result.details.suggestions.join('\n');
                }
            }
            
            throw new Error(errorMsg);
        }
    } catch (error) {
        console.error('Error:', error);
        showNotification(error.message || 'Failed to analyze. Please try again.', 'error');
        handleReset();
    } finally {
        loadingSection.style.display = 'none';
    }
}

// Display dashboard
function displayDashboard(data) {
    console.log('Displaying dashboard with data:', data); // Debug log
    
    // Handle both single post and profile analysis
    const comments = data.all_comments || data.comments || { positive: [], negative: [], neutral: [] };
    
    // Combine all comments
    allComments = [
        ...(comments.positive || []).map(c => ({ ...c, sentiment: 'positive' })),
        ...(comments.negative || []).map(c => ({ ...c, sentiment: 'negative' })),
        ...(comments.neutral || []).map(c => ({ ...c, sentiment: 'neutral' }))
    ].sort((a, b) => (b.likes || 0) - (a.likes || 0));
    
    console.log('Total comments loaded:', allComments.length); // Debug log
    
    // Update header based on analysis type
    const dashboardHeader = document.querySelector('.dashboard-header h2');
    if (data.type === 'profile' || data.total_posts) {
        const label = data.platform === 'instagram' ? 'Profile' : 'Group/Page';
        const urlLabel = data.platform === 'instagram' ? 'Profile' : 'URL';
        dashboardHeader.innerHTML = `
            Analysis Results - ${label}
            <div class="bulk-info">
                <div class="info-item"><strong>${urlLabel}:</strong> <span>${data.profile_url || data.url || data.group_url || 'N/A'}</span></div>
                <div class="info-item"><strong>From:</strong> <span>${data.from_date || 'N/A'}</span></div>
                <div class="info-item"><strong>Posts:</strong> <span>${data.total_posts || 0}</span></div>
            </div>
        `;
    } else {
        dashboardHeader.textContent = 'Analysis Results';
    }
    
    // Update stats
    displayStats(data);
    
    // Update charts
    displayCharts(data);
    
    // Display comments
    filterComments('all');
    
    // Update tab counts
    document.getElementById('allCount').textContent = data.total_comments;
    document.getElementById('positiveCount').textContent = data.sentiment_stats.positive;
    document.getElementById('negativeCount').textContent = data.sentiment_stats.negative;
    document.getElementById('neutralCount').textContent = data.sentiment_stats.neutral;
    
    // Show dashboard
    dashboardSection.style.display = 'block';
}

// Display stats cards
function displayStats(data) {
    console.log('Display stats called with:', data); // Debug
    
    const { sentiment_stats, total_comments } = data;
    const statsGrid = document.getElementById('statsGrid');
    
    if (!sentiment_stats) {
        console.error('No sentiment_stats in data:', data);
        return;
    }
    
    const stats = [
        {
            icon: 'fas fa-comments',
            title: 'Total Comments',
            value: total_comments || 0,
            color: '#667eea'
        },
        {
            icon: 'fas fa-smile',
            title: 'Positive',
            value: `${sentiment_stats.positive_percentage || 0}%`,
            subtitle: `${sentiment_stats.positive || 0} comments`,
            color: '#27ae60'
        },
        {
            icon: 'fas fa-frown',
            title: 'Negative',
            value: `${sentiment_stats.negative_percentage || 0}%`,
            subtitle: `${sentiment_stats.negative || 0} comments`,
            color: '#e74c3c'
        },
        {
            icon: 'fas fa-meh',
            title: 'Neutral',
            value: `${sentiment_stats.neutral_percentage || 0}%`,
            subtitle: `${sentiment_stats.neutral || 0} comments`,
            color: '#95a5a6'
        }
    ];
    
    statsGrid.innerHTML = stats.map(stat => `
        <div class="stat-card">
            <div class="stat-icon" style="color: ${stat.color}">
                <i class="${stat.icon}"></i>
            </div>
            <div class="stat-content">
                <h4>${stat.title}</h4>
                <p class="stat-value" style="color: ${stat.color}">${stat.value}</p>
                ${stat.subtitle ? `<span class="stat-subtitle">${stat.subtitle}</span>` : ''}
            </div>
        </div>
    `).join('');
}

// Display charts
function displayCharts(data) {
    console.log('Display charts called with:', data); // Debug
    
    const { sentiment_stats, topic_stats } = data;
    
    if (!sentiment_stats) {
        console.error('No sentiment_stats in data:', data);
        return;
    }
    
    // Sentiment Chart
    const sentimentCtx = document.getElementById('sentimentChart').getContext('2d');
    new Chart(sentimentCtx, {
        type: 'pie',
        data: {
            labels: ['Positive', 'Negative', 'Neutral'],
            datasets: [{
                data: [
                    sentiment_stats.positive,
                    sentiment_stats.negative,
                    sentiment_stats.neutral
                ],
                backgroundColor: ['#27ae60', '#e74c3c', '#95a5a6']
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
    
    // Topic Chart (if negative comments exist)
    if (Object.keys(topic_stats).length > 0) {
        document.getElementById('topicChartContainer').style.display = 'block';
        
        const topicCtx = document.getElementById('topicChart').getContext('2d');
        const topicLabels = Object.keys(topic_stats);
        const topicData = Object.values(topic_stats);
        
        new Chart(topicCtx, {
            type: 'bar',
            data: {
                labels: topicLabels,
                datasets: [{
                    label: 'Number of Comments',
                    data: topicData,
                    backgroundColor: [
                        '#e74c3c', '#c0392b', '#e67e22', '#d35400',
                        '#f39c12', '#f1c40f', '#16a085', '#27ae60'
                    ]
                }]
            },
            options: {
                responsive: true,
                maintainAspectRatio: true,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Filter comments
function filterComments(filter) {
    currentFilter = filter;
    let filteredComments = allComments;
    
    if (filter !== 'all') {
        filteredComments = allComments.filter(c => c.sentiment === filter);
    }
    
    displayComments(filteredComments);
}

// Display comments
function displayComments(comments) {
    if (comments.length === 0) {
        commentsList.innerHTML = '<div class="no-comments"><p>No comments to display</p></div>';
        return;
    }
    
    commentsList.innerHTML = comments.map(comment => {
        const sentimentColor = getSentimentColor(comment.sentiment);
        const sentimentEmoji = getSentimentEmoji(comment.sentiment);
        
        return `
            <div class="comment-card">
                <div class="comment-header">
                    <div class="comment-user">
                        <i class="fas fa-user user-icon"></i>
                        <span class="username">@${comment.username || 'unknown'}</span>
                    </div>
                    ${comment.likes > 0 ? `
                        <div class="likes">
                            <i class="fas fa-heart"></i> ${comment.likes}
                        </div>
                    ` : ''}
                </div>
                
                <div class="comment-text">${escapeHtml(comment.text)}</div>
                
                <div class="comment-footer">
                    <div class="sentiment-badge" style="background: ${sentimentColor}20; color: ${sentimentColor}">
                        <span>${sentimentEmoji}</span>
                        <span>${comment.sentiment}</span>
                        ${comment.confidence ? `<span>(${Math.round(comment.confidence * 100)}%)</span>` : ''}
                    </div>
                    
                    ${comment.topic && comment.sentiment === 'negative' ? `
                        <div class="topic-badge">
                            <i class="fas fa-tag"></i>
                            <span>${comment.topic}</span>
                        </div>
                    ` : ''}
                </div>
            </div>
        `;
    }).join('');
}

// Helper functions
function getSentimentColor(sentiment) {
    switch (sentiment) {
        case 'positive': return '#27ae60';
        case 'negative': return '#e74c3c';
        default: return '#95a5a6';
    }
}

function getSentimentEmoji(sentiment) {
    switch (sentiment) {
        case 'positive': return '😊';
        case 'negative': return '😞';
        default: return '😐';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function setActiveTab(filter) {
    const tabButtons = commentTabs.querySelectorAll('.tab-button');
    tabButtons.forEach(button => {
        if (button.dataset.filter === filter) {
            button.classList.add('active');
        } else {
            button.classList.remove('active');
        }
    });
}

// Show notification
function showNotification(message, type) {
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 1rem 1.5rem;
        background: ${type === 'success' ? '#27ae60' : '#e74c3c'};
        color: white;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        z-index: 1000;
        animation: slideIn 0.3s ease;
    `;
    
    document.body.appendChild(notification);
    
    setTimeout(() => {
        notification.remove();
    }, 3000);
}

// Handle reset
function handleReset() {
    analysisData = null;
    allComments = [];
    currentFilter = 'all';
    urlInput.value = '';
    hideError();
    
    dashboardSection.style.display = 'none';
    loadingSection.style.display = 'none';
    inputSection.style.display = 'flex';
}

// Add slide-in animation
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }
`;
document.head.appendChild(style);
