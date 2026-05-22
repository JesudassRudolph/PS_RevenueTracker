# PS_RevenueTracker - LDAP Login Setup Guide

This guide explains how to set up and configure the LDAP authentication system for PS_RevenueTracker.

## Overview

The application includes a PyQt5-based login screen with local LDAP directory integration. Users authenticate against an LDAP server (such as OpenLDAP, Active Directory, or other LDAP-compatible directories).

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Required packages:**
- `python-ldap`: LDAP protocol implementation
- `PyQt5`: GUI framework
- `PyQt5-sip`: PyQt5 support library

### 2. System Requirements (Linux/macOS)

#### For Linux:
```bash
# Ubuntu/Debian
sudo apt-get install python3-dev libldap2-dev libsasl2-dev libssl-dev

# CentOS/RHEL
sudo yum install python3-devel openldap-devel cyrus-sasl-devel openssl-devel
```

#### For macOS:
```bash
brew install openldap
brew install python3
pip install python-ldap
```

#### For Windows:
Download pre-built wheels from [Unofficial Python Wheel Repository](https://www.lfd.uci.edu/~gohlke/pythonlibs/#python-ldap) or use conda:
```bash
conda install -c conda-forge python-ldap pyqt5
```

## Configuration

### 1. Update LDAP Settings

Edit `config/ldap_config.py` with your LDAP server details:

```python
LDAP_SERVER = 'your-ldap-server.com'  # or 'localhost' for local LDAP
LDAP_PORT = 389                        # 636 for LDAPS
USE_TLS = False                        # True for LDAPS
BASE_DN = 'dc=yourdomain,dc=com'      # Your directory base DN
SEARCH_OU = 'ou=users'                # Where users are stored
```

### 2. Set Admin Credentials (Optional)

For user information lookups, set admin credentials:

```python
ADMIN_DN = 'cn=admin,dc=yourdomain,dc=com'
ADMIN_PASSWORD = 'your_admin_password'
```

## Running the Application

### Start the Application
```bash
python main.py
```

### Login Screen
The login screen will appear with:
- Username/Email input field
- Password input field
- "Remember me" option
- Login and Clear buttons

### User Authentication Flow
1. User enters username (or email)
2. Click "Login" button
3. Application searches LDAP directory for the user
4. If found, attempts to bind with provided password
5. On success, opens main dashboard
6. On failure, shows error message

## LDAP Directory Structure

The application expects an LDAP directory structure like:

```
dc=yourdomain,dc=com
├── ou=users
│   ├── uid=john.doe
│   │   ├── uid: john.doe
│   │   ├── mail: john.doe@example.com
│   │   ├── cn: John Doe
│   │   └── displayName: John Doe
│   └── uid=jane.smith
│       ├── uid: jane.smith
│       ├── mail: jane.smith@example.com
│       ├── cn: Jane Smith
│       └── displayName: Jane Smith
└── cn=admin
    └── userPassword: (hashed)
```

## Testing LDAP Connection

### Test with Python Script

```python
from auth.ldap_auth import LDAPAuthenticator

auth = LDAPAuthenticator(
    ldap_server='your-ldap-server.com',
    ldap_port=389,
    base_dn='dc=yourdomain,dc=com'
)

# Test connection
if auth.verify_connection():
    print("LDAP server is reachable!")
    
    # Test authentication
    success, user_dn = auth.authenticate_user('username', 'password')
    if success:
        print(f"Authentication successful! User DN: {user_dn}")
    else:
        print("Authentication failed!")
else:
    print("Cannot connect to LDAP server")
```

### Test with Command Line

```bash
# Using ldapsearch tool
ldapsearch -x -H ldap://localhost:389 -b "dc=example,dc=com" "(uid=testuser)"

# Test specific user authentication
ldapwhoami -x -H ldap://localhost:389 -D "uid=testuser,ou=users,dc=example,dc=com" -W
```

## Troubleshooting

### Connection Issues

**Error: "LDAP server is unavailable"**
- Check LDAP server is running: `ping your-ldap-server.com`
- Verify port is correct (389 for LDAP, 636 for LDAPS)
- Check firewall rules

**Error: "Connection timeout"**
- Increase timeout: Edit `ldap_auth.py` and modify `OPT_NETWORK_TIMEOUT`
- Check network connectivity
- Verify LDAP server performance

### Authentication Issues

**Error: "User not found in LDAP"**
- Verify base DN is correct: `BASE_DN = 'dc=yourdomain,dc=com'`
- Check user exists in directory
- Verify user search OU is correct

**Error: "Invalid credentials"**
- Verify password is correct
- Check user account is active (not disabled/expired)
- Verify user account in correct organizational unit

### Python Import Errors

**Error: "No module named 'ldap'"**
```bash
pip install --upgrade python-ldap
```

**Error: "No module named 'PyQt5'"**
```bash
pip install --upgrade PyQt5
```

## Setting Up Local LDAP (Development)

### Using OpenLDAP (Linux/macOS)

1. **Install OpenLDAP:**
   ```bash
   # Ubuntu/Debian
   sudo apt-get install slapd ldap-utils
   
   # macOS
   brew install openldap
   ```

2. **Start LDAP Server:**
   ```bash
   sudo slapd -f /etc/ldap/slapd.conf -u openldap
   ```

3. **Load LDAP Schema:**
   ```bash
   ldapadd -x -D "cn=admin,dc=example,dc=com" -W -f /path/to/schema.ldif
   ```

4. **Add Users:**
   ```bash
   ldapadd -x -D "cn=admin,dc=example,dc=com" -W << EOF
   dn: ou=users,dc=example,dc=com
   objectClass: organizationalUnit
   ou: users
   
   dn: uid=testuser,ou=users,dc=example,dc=com
   objectClass: inetOrgPerson
   uid: testuser
   sn: User
   cn: Test User
   userPassword: password123
   mail: testuser@example.com
   EOF
   ```

### Using Docker

```bash
docker run --rm -d \
  --name openldap \
  -p 389:389 \
  -p 636:636 \
  -e LDAP_ORGANISATION="My Organization" \
  -e LDAP_DOMAIN="example.com" \
  -e LDAP_ADMIN_PASSWORD="admin" \
  osixia/openldap:latest
```

## Security Best Practices

1. **Never hardcode passwords** - Use environment variables or secure config files
2. **Use LDAPS (TLS/SSL)** - Set `USE_TLS = True` and `LDAP_PORT = 636`
3. **Validate input** - Application already escapes filter characters
4. **Session timeout** - Set `SESSION_TIMEOUT` in config
5. **Failed login limits** - Monitor `MAX_LOGIN_ATTEMPTS` and `LOCKOUT_DURATION`
6. **Secure logs** - Restrict access to `logs/` directory
7. **Environment variables**:
   ```bash
   export LDAP_ADMIN_PASSWORD="secure_password"
   export LDAP_SERVER="production-ldap.example.com"
   ```

## File Structure

```
PS_RevenueTracker/
├── main.py                    # Application entry point
├── requirements.txt           # Python dependencies
├── config/
│   └── ldap_config.py        # LDAP configuration
├── auth/
│   ├── __init__.py
│   ├── ldap_auth.py          # LDAP authentication module
│   └── login_screen.py       # PyQt5 login UI
├── logs/                      # Application logs (auto-created)
└── README_LDAP_SETUP.md      # This file
```

## API Reference

### LDAPAuthenticator

```python
class LDAPAuthenticator:
    def __init__(ldap_server, ldap_port, base_dn, use_tls)
    def authenticate_user(username, password) -> Tuple[bool, str]
    def get_user_info(username, admin_dn, admin_password) -> Dict
    def verify_connection() -> bool
```

### LoginScreen

```python
class LoginScreen(QWidget):
    def __init__(ldap_config, on_login_success)
    def attempt_login()
    def clear_fields()
    login_successful = pyqtSignal(str)  # Emits on successful login
```

## Support

For issues or questions:
1. Check the Troubleshooting section
2. Review application logs in `logs/auth.log`
3. Test LDAP connection with command-line tools
4. Verify LDAP directory structure with `ldapsearch`

## References

- [python-ldap Documentation](https://www.python-ldap.org/)
- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [LDAP RFC 4511](https://tools.ietf.org/html/rfc4511)
- [OpenLDAP Documentation](https://www.openldap.org/doc/)