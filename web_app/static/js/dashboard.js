document.addEventListener('DOMContentLoaded', function() {
    // Set user name
    const userNameElement = document.getElementById('userName');
    userNameElement.textContent = document.getElementById('sessionUser').textContent;

    // Format login time
    const loginTimeStr = document.getElementById('sessionLoginTime').textContent;
    if (loginTimeStr) {
        const loginTime = new Date(loginTimeStr);
        const formattedTime = loginTime.toLocaleString();
        document.getElementById('loginTime').textContent = `Logged in at: ${formattedTime}`;
    }

    // Logout functionality
    const logoutBtn = document.getElementById('logoutBtn');
    logoutBtn.addEventListener('click', async function() {
        if (confirm('Are you sure you want to logout?')) {
            try {
                const response = await fetch('/logout', {
                    method: 'POST'
                });
                const data = await response.json();
                if (response.ok) {
                    window.location.href = data.redirect;
                }
            } catch (error) {
                console.error('Logout error:', error);
                alert('Logout failed. Please try again.');
            }
        }
    });
});