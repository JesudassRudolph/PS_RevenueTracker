document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginBtn = document.getElementById('loginBtn');
    const errorMessage = document.getElementById('errorMessage');
    const successMessage = document.getElementById('successMessage');
    const usernameInput = document.getElementById('username');
    const passwordInput = document.getElementById('password');

    // Form submission
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        await submitLogin();
    });

    // Clear error message on input
    usernameInput.addEventListener('input', function() {
        errorMessage.style.display = 'none';
    });
    passwordInput.addEventListener('input', function() {
        errorMessage.style.display = 'none';
    });

    async function submitLogin() {
        const username = usernameInput.value.trim();
        const password = passwordInput.value;
        const rememberMe = document.getElementById('rememberMe').checked;

        if (!username || !password) {
            showError('Please enter both username and password');
            return;
        }

        // Show loading state
        loginBtn.disabled = true;
        const btnText = loginBtn.querySelector('.btn-text');
        const spinner = loginBtn.querySelector('.spinner');
        btnText.textContent = 'Authenticating';
        spinner.style.display = 'inline-block';
        errorMessage.style.display = 'none';

        try {
            const response = await fetch('/api/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    remember_me: rememberMe
                })
            });

            const data = await response.json();

            if (response.ok) {
                showSuccess(data.message);
                setTimeout(() => {
                    window.location.href = data.redirect;
                }, 1000);
            } else {
                showError(data.message || 'Login failed');
            }
        } catch (error) {
            showError('An error occurred. Please try again.');
            console.error('Login error:', error);
        } finally {
            loginBtn.disabled = false;
            btnText.textContent = 'Login';
            spinner.style.display = 'none';
        }
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        successMessage.style.display = 'none';
    }

    function showSuccess(message) {
        successMessage.textContent = message;
        successMessage.style.display = 'block';
        errorMessage.style.display = 'none';
    }
});

async function checkHealth() {
    try {
        const response = await fetch('/health');
        const data = await response.json();
        
        if (response.ok && data.ldap_connected) {
            alert('✓ System Status: Healthy\n✓ LDAP Connection: Active');
        } else {
            alert('⚠ System Status: Check Connection\nLDAP: ' + (data.ldap_connected ? 'Connected' : 'Disconnected'));
        }
    } catch (error) {
        alert('✗ System Status: Unavailable\nPlease try again later.');
        console.error('Health check error:', error);
    }
}