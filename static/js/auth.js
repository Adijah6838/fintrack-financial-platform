// Utility function for Bootstrap alerts
function showAlert(message, type = 'danger') {
    const alertBox = document.getElementById('alertBox');
    if (!alertBox) return;
    alertBox.innerHTML = `
        <div class="alert alert-${type} alert-dismissible fade show" role="alert">
            ${message}
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
        </div>
    `;
}

// Authentication State Management
const token = localStorage.getItem('token');
const userRole = localStorage.getItem('userRole');
const navLinks = document.getElementById('navLinks');

if (token) {
    // User is logged in
    if (navLinks) {
        navLinks.innerHTML = `
            <li class="nav-item"><a class="nav-link" href="/dashboard">Dashboard</a></li>
            ${userRole === 'ADMIN' ? '<li class="nav-item"><a class="nav-link" href="/admin">Admin</a></li>' : ''}
            <li class="nav-item"><a class="nav-link text-danger" href="#" onclick="logout()">Logout</a></li>
        `;
    }
} else {
    // User is logged out
    if (navLinks) {
        navLinks.innerHTML = `
            <li class="nav-item"><a class="nav-link" href="/">Login</a></li>
            <li class="nav-item"><a class="nav-link" href="/register">Register</a></li>
        `;
    }
    // Protect pages
    const path = window.location.pathname;
    if (path === '/dashboard' || path === '/admin') {
        window.location.href = '/';
    }
}

function logout() {
    localStorage.removeItem('token');
    localStorage.removeItem('userRole');
    window.location.href = '/';
}

// Global API Fetch Wrapper (Adds Authorization Header)
async function apiFetch(url, options = {}) {
    const token = localStorage.getItem('token');
    const headers = {
        'Content-Type': 'application/json',
        ...(token ? { 'Authorization': `Bearer ${token}` } : {}),
        ...options.headers
    };
    
    const response = await fetch(url, { ...options, headers });
    const data = await response.json();
    
    if (response.status === 401) {
        logout(); // Token expired
        throw new Error('Unauthorized');
    }
    
    return { response, data };
}