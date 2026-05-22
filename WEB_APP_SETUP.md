# PS_RevenueTracker Web Application Setup Guide

## Overview

The PS_RevenueTracker web application is a Flask-based web application with LDAP authentication. It provides a modern, responsive web interface for user login and revenue tracking.

## Features

- ✅ Web-based login interface
- ✅ LDAP/Active Directory integration
- ✅ Session management
- ✅ Responsive design (works on desktop and mobile)
- ✅ Modern UI with gradient design
- ✅ Remember me functionality
- ✅ System health checks
- ✅ User dashboard

## Installation

### 1. Install Python Dependencies

```bash
cd web_app
pip install -r requirements.txt
```

### 2. System Requirements

#### Linux (Ubuntu/Debian)
```bash
sudo apt-get install python3-dev libldap2-dev libsasl2-dev libssl-dev
```

#### macOS
```bash
brew install openldap python3
```

#### Windows
Download pre-built wheels or use conda:
```bash
conda install -c conda-forge python-ldap
```

## Configuration

### Update LDAP Configuration

Edit `config/ldap_config.py`:

```python
LDAP_SERVER = 'your-ldap-server.com'  # or 'localhost'
LDAP_PORT = 389                        # 636 for LDAPS
USE_TLS = False                        # True for LDAPS
BASE_DN = 'dc=yourdomain,dc=com'      # Your directory base DN
```

### Flask Configuration

Edit `web_app/config.py` to customize Flask settings:

```python
SECRET_KEY = 'your-secret-key'  # Change in production!
DEBUG = False                    # Set to False in production
SESSION_COOKIE_SECURE = True     # Set to True with HTTPS
```

## Running the Application

### Development Mode

```bash
cd web_app
python app.py
```

Access the application at: **http://localhost:5000**

### Production Mode (using Gunicorn)

```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### Using Environment Variables

```bash
export FLASK_ENV=production
export SECRET_KEY='your-production-secret-key'
export LDAP_SERVER='your-ldap-server.com'
python app.py
```

## Application URLs

### Public Routes
- `GET /` - Redirects to login or dashboard
- `GET /login` - Login page
- `POST /api/login` - API endpoint for login
- `GET /health` - Health check endpoint

### Protected Routes (require login)
- `GET /dashboard` - Main dashboard
- `GET /api/user-info` - Get current user info
- `POST /logout` - Logout user

## API Endpoints

### POST /api/login
Authenticate user with LDAP

**Request:**
```json
{
  "username": "john.doe",
  "password": "password123",
  "remember_me": true
}
```

**Response (Success):**
```json
{
  "success": true,
  "message": "Welcome, john.doe!",
  "redirect": "/dashboard"
}
```

**Response (Error):**
```json
{
  "success": false,
  "message": "Invalid username or password"
}
```

### GET /health
Check application and LDAP health status

**Response:**
```json
{
  "status": "healthy",
  "ldap_connected": true
}
```

### POST /logout
Logout current user

**Response:**
```json
{
  "success": true,
  "message": "Logged out successfully",
  "redirect": "/login"
}
```

## Testing Locally

### 1. Start a Local LDAP Server (Docker)

```bash
docker run --rm -d \
  --name openldap \
  -p 389:389 \
  -p 636:636 \
  -e LDAP_ORGANISATION="Test Org" \
  -e LDAP_DOMAIN="example.com" \
  -e LDAP_ADMIN_PASSWORD="admin" \
  osixia/openldap:latest
```

### 2. Add Test Users

```bash
ldapadd -x -D "cn=admin,dc=example,dc=com" -w admin << EOF
dn: ou=users,dc=example,dc=com
objectClass: organizationalUnit
ou: users

dn: uid=testuser,ou=users,dc=example,dc=com
objectClass: inetOrgPerson
objectClass: organizationalPerson
objectClass: person
objectClass: top
uid: testuser
sn: User
cn: Test User
userPassword: testpassword
mail: testuser@example.com
EOF
```

### 3. Update LDAP Config

Edit `config/ldap_config.py`:
```python
LDAP_SERVER = 'localhost'
LDAP_PORT = 389
BASE_DN = 'dc=example,dc=com'
```

### 4. Run the Application

```bash
python web_app/app.py
```

### 5. Login

- Open browser: http://localhost:5000
- Username: `testuser`
- Password: `testpassword`
- Click Login

## Project Structure

```
web_app/
├── app.py                      # Flask application
├── config.py                   # Flask configuration
├── requirements.txt            # Python dependencies
├── templates/
│   ├── login.html             # Login page
│   └── dashboard.html         # Dashboard page
├── static/
│   ├── css/
│   │   ├── login.css          # Login styles
│   │   └── dashboard.css      # Dashboard styles
│   └── js/
│       ├── login.js           # Login functionality
│       └── dashboard.js       # Dashboard functionality
└── config/
    └── ldap_config.py         # LDAP configuration
```

## Troubleshooting

### Port 5000 Already in Use

```bash
# Run on different port
python -c "from app import app; app.run(port=8000)"
```

### LDAP Connection Issues

```bash
# Test LDAP connection
ldapsearch -x -H ldap://localhost:389 -b "dc=example,dc=com" "-dn"
```

### Session Not Working

```bash
# Clear session files
rm -rf flask_sessions/*
```

### Module Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt
```

## Security Recommendations

1. **Change Secret Key**: Set a strong SECRET_KEY in production
2. **Use HTTPS**: Set SESSION_COOKIE_SECURE = True with SSL certificate
3. **LDAPS**: Use LDAPS (port 636) for encrypted LDAP connections
4. **Environment Variables**: Use .env file for sensitive configuration
5. **Rate Limiting**: Implement rate limiting on login endpoint
6. **CORS**: Configure CORS if accessing from different domain
7. **Password Policy**: Enforce strong passwords in LDAP

## Deploying to Production

### Using Gunicorn + Nginx

**1. Install Gunicorn**
```bash
pip install gunicorn
```

**2. Create systemd service file** (`/etc/systemd/system/ps-revenue-tracker.service`):
```ini
[Unit]
Description=PS_RevenueTracker Web Application
After=network.target

[Service]
User=www-data
WorkingDirectory=/path/to/PS_RevenueTracker/web_app
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 127.0.0.1:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

**3. Start service**
```bash
sudo systemctl start ps-revenue-tracker
sudo systemctl enable ps-revenue-tracker
```

**4. Configure Nginx** (reverse proxy)
```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Support

For issues or questions:
1. Check the logs: `tail -f logs/web_app.log`
2. Test LDAP connection manually
3. Review Flask debug output
4. Check browser console for client-side errors
