# YPMG Lab Workflow Webapp

A comprehensive Flask-based web application for capturing lab workflow data with multi-page sequential forms, session-based authentication, email confirmation, admin dashboard, and Vercel serverless deployment support.

---

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Technology Stack](#technology-stack)
- [Project Structure](#project-structure)
- [Quick Start](#quick-start)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [User Guide](#user-guide)
- [Admin Guide](#admin-guide)
- [Deployment](#deployment)
  - [Local Development](#local-development)
  - [PythonAnywhere](#pythonanywhere-deployment)
  - [Vercel Deployment](#vercel-deployment)
- [Security](#security)
- [Database](#database)
- [API Routes](#api-routes)
- [Troubleshooting](#troubleshooting)
- [Development](#development)
- [License](#license)

---

## Overview

The YPMG Lab Workflow Webapp is a sequential multi-page application designed for lab technicians to log workflow data efficiently. It includes:

- **3-Page Sequential Workflow**: Login → Workflow Data → Notes → Confirmation
- **Email Confirmation System**: Domain-restricted registration with email verification
- **Admin Dashboard**: User management, data export, and reporting
- **Multi-Platform Deployment**: Supports local, PythonAnywhere, and Vercel

---

## Features

### User Features

| Feature | Description |
|---------|-------------|
| **Sequential Workflow** | 3-page data entry with flexible back-navigation |
| **User Registration** | Domain-restricted (@ypmg.com) with email confirmation |
| **Session Management** | Resume incomplete sessions, remember-me functionality |
| **Department Selection** | Pre-configured department options |
| **Form Validation** | Client and server-side validation |

### Admin Features

| Feature | Access Level | Description |
|---------|--------------|-------------|
| **Dashboard** | Level 1+ | Overview statistics, recent submissions |
| **Reports** | Level 1+ | Summary, department, and trend reports |
| **Data Export** | Level 2+ | Export submissions to CSV format |
| **Submission Browser** | Level 2+ | View and search all submissions |
| **User Management** | Level 3 | Create, activate/deactivate users |

### Admin Access Levels

- **Level 1**: View dashboard and reports
- **Level 2**: Level 1 + Export data and browse submissions
- **Level 3**: Level 2 + User management (create/deactivate users)

---

## Technology Stack

| Component | Technology |
|-----------|------------|
| **Backend** | Flask 3.x, Python 3.8+ |
| **Database** | SQLite 3 (dev/local), Azure SQL via pymssql (production) |
| **Authentication** | Flask-Login, bcrypt password hashing |
| **Sessions** | Flask-Session (server-side) |
| **Forms** | WTForms with CSRF protection |
| **Email** | Flask-Mail (Microsoft 365 SMTP) |
| **Security** | Flask-Talisman, Flask-Limiter |
| **Frontend** | HTML5, CSS3, Vanilla JavaScript |
| **Frontend (YPB)** | React + TypeScript + Vite |

---

## Project Structure

```
lab-webapp/
├── app.py                          # Main Flask application entry point
├── config.py                       # Configuration settings (dev/prod/vercel)
├── init_db.py                      # Database initialization script
├── seed_users.py                   # Create initial test users
├── requirements.txt                # Python dependencies
├── vercel.json                     # Vercel deployment configuration
├── wsgi.py                         # WSGI entry point for production
│
├── api/                            # Vercel serverless functions
│   └── index.py                    # Vercel entry point
│
├── models/                         # Database models
│   ├── __init__.py
│   ├── user.py                     # User model with email confirmation
│   ├── session.py                  # Workflow session model
│   ├── submission.py               # Form submission model
│   └── case_prefix.py              # Case number prefix model (accessioning)
│
├── routes/                         # Application routes (blueprints)
│   ├── __init__.py
│   ├── auth.py                     # Authentication (login/register/confirm)
│   ├── page1.py                    # Page 1 - Login flow
│   ├── page2.py                    # Page 2 - Workflow data entry
│   ├── page3.py                    # Page 3 - Notes entry
│   ├── admin.py                    # Admin dashboard and user management
│   ├── export.py                   # Data export functionality
│   ├── reports.py                  # Reporting system
│   ├── ypb_daily_count.py          # YPB Daily Count workflow
│   └── accessioning.py             # Accessioning workflow (Checkout dept)
│
├── forms/                          # WTForms form definitions
│   ├── __init__.py
│   ├── login_form.py               # Login form
│   ├── register_form.py            # Registration form with email
│   ├── workflow_form.py            # Workflow data form
│   └── notes_form.py               # Notes entry form
│
├── services/                       # Business logic services
│   ├── __init__.py
│   ├── email.py                    # Email sending (Flask-Mail)
│   └── tokens.py                   # Token generation/validation
│
├── utils/                          # Utility modules
│   ├── __init__.py
│   ├── audit.py                    # Audit logging
│   ├── case_number.py              # Case number generation (accessioning)
│   ├── config_validator.py         # Configuration validation
│   ├── db_connection.py            # Azure SQL / SQLite connection handling
│   ├── logging_config.py           # Logging setup
│   └── security_middleware.py      # Rate limiting, security headers
│
├── templates/                      # Jinja2 HTML templates
│   ├── base.html                   # Base template
│   ├── login.html                  # Login page
│   ├── register.html               # Registration page
│   ├── resend_confirmation.html    # Resend confirmation page
│   ├── workflow.html               # Page 2 - Workflow
│   ├── notes.html                  # Page 3 - Notes
│   ├── confirmation.html           # Submission confirmation
│   ├── ypb_daily_count.html        # YPB Daily Count page
│   ├── accessioning_workflow.html  # Accessioning workflow page
│   ├── coming_soon.html            # Placeholder page
│   ├── error.html                  # Error page
│   ├── admin/                      # Admin templates
│   │   ├── dashboard.html
│   │   ├── users.html
│   │   ├── submissions.html
│   │   ├── submission_detail.html
│   │   └── reports.html
│   └── email/                      # Email templates
│       ├── confirm.html
│       ├── confirm.txt
│       ├── welcome.html
│       └── welcome.txt
│
├── static/                         # Static assets
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   └── validation.js
│   └── assets/                     # Built frontend assets
│
├── frontend/                       # React frontend applications
│   └── ypb-daily-count/            # YPB Daily Count React app
│       ├── src/
│       ├── package.json
│       └── vite.config.ts
│
├── migrations/                     # Database migrations
│   └── add_ypb_daily_count.py
│
├── instance/                       # Instance-specific files (auto-created)
│   ├── lab_data.db                 # SQLite database
│   └── flask_session/              # Server-side sessions
│
├── docs/                           # Documentation
│   └── azure_sql_setup.md          # Azure SQL setup and migration guide
│
├── plans/                          # Implementation plans
│   └── qc_logging_implementation_plan.md  # QC Logging feature spec
│
├── favicon.svg                     # App favicon (adaptive color)
├── .gitignore                      # Git ignore patterns
└── LICENSE                         # License file
```

---

## Quick Start

### 5-Minute Setup

```bash
# 1. Clone and navigate to project
cd lab-webapp

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Initialize database
python init_db.py

# 5. Seed test users
python seed_users.py

# 6. Run the application
python app.py

# 7. Open browser: http://localhost:5000
```

### Test Credentials

| Type | User ID | Passcode | Access |
|------|---------|----------|--------|
| Regular User | `user1` | `1111` | Workflow only |
| Regular User | `user2` | `2222` | Workflow only |
| Histology Tech | `histology_tech` | `3333` | Workflow only |
| Cyto Tech | `cytotech` | `4444` | Workflow only |
| Lab Manager | `labmanager` | `5555` | Admin Level 2 |
| Admin | `admin` | `1234` | Admin Level 3 (Full) |

---

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package installer)
- Git (optional, for cloning)

### Step-by-Step Installation

1. **Clone or download the project**
   ```bash
   git clone <repository-url>
   cd lab-webapp
   ```

2. **Create virtual environment** (recommended)
   ```bash
   python -m venv venv

   # Activate on Windows:
   venv\Scripts\activate

   # Activate on macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```

5. **Initialize the database**
   ```bash
   python init_db.py
   ```

6. **Seed initial users** (optional but recommended)
   ```bash
   python seed_users.py
   ```

---

## Configuration

### Environment Variables

Create a `.env` file based on `.env.example`:

```bash
# Application
SECRET_KEY=your-secret-key-here  # Generate: python -c "import secrets; print(secrets.token_urlsafe(32))"
FLASK_APP=app.py
FLASK_ENV=development  # or 'production'

# Email (Microsoft 365)
MAIL_SERVER=smtp.office365.com
MAIL_PORT=587
MAIL_USE_TLS=True
MAIL_USERNAME=your-email@ypmg.com
MAIL_PASSWORD=your-app-password  # Use app-specific password
MAIL_DEFAULT_SENDER=your-email@ypmg.com

# Registration
ALLOWED_EMAIL_DOMAIN=ypmg.com
ADMIN_EMAIL=admin@ypmg.com
CONFIRMATION_TOKEN_EXPIRY=3600  # 1 hour in seconds
```

### Getting Microsoft 365 App Password

1. Go to https://account.microsoft.com/security
2. Sign in with your Microsoft 365 account
3. Click **Advanced security options**
4. Under **Additional security**, click **Create a new app password**
5. Copy the generated password to `MAIL_PASSWORD`

### Configuration Files

| File | Purpose |
|------|---------|
| `config.py` | Flask configuration classes (Dev/Prod/Vercel) |
| `vercel.json` | Vercel deployment settings |

---

## Running the Application

### Development Mode

```bash
python app.py
```

Access at: `http://localhost:5000`

### Production Mode (Gunicorn)

```bash
gunicorn -w 4 -b 0.0.0.0:5000 wsgi:app
```

### With Custom Port

```bash
python app.py --port 8080
```

---

## User Guide

### User Workflow

1. **Login** (Page 1)
   - Navigate to `http://localhost:5000`
   - Enter User ID and 4-digit passcode
   - Select department
   - Optionally check "Remember Me"
   - Click "Login & Continue"

2. **Workflow Data** (Page 2)
   - Enter optional Final Block Time
   - Check applicable workflow items
   - Select task completion status
   - Click "Continue to Notes" (or go back to Page 1)

3. **Additional Notes** (Page 3)
   - Enter any additional notes (up to 5000 characters)
   - Click "Submit" (or go back to Page 2)

4. **Confirmation**
   - View submission confirmation with details
   - Click "Start New Entry" or "Logout"

### New User Registration

1. Click "Register" on login page
2. Enter:
   - User ID (display name)
   - Email (@ypmg.com only)
   - 4-digit passcode (twice to confirm)
3. Submit registration
4. Check email for confirmation link
5. Click link to confirm account
6. Login with credentials

---

## Admin Guide

### Accessing Admin Dashboard

1. Login with admin credentials (e.g., `admin`/`1234`)
2. Navigate to: `http://localhost:5000/admin`

### Admin URLs

| Page | URL | Required Level |
|------|-----|----------------|
| Dashboard | `/admin` | 1+ |
| Submissions | `/admin/submissions` | 2+ |
| User Management | `/admin/users` | 3 |
| Reports | `/reports` | 1+ |
| Export CSV | `/export/csv` | 2+ |

### Admin Features

**Dashboard** - Overview of:
- Total submissions (today/week/month)
- Active users count
- Recent submissions list
- Quick links to other features

**User Management** (Level 3):
- Create new users with User ID, Email, and Passcode
- Activate/deactivate users
- View user details and activity

**Export Data**:
- Export submissions to CSV
- Filter by date range, department, user
- Download for external analysis

**Reports**:
- **Summary Report**: Overall statistics
- **Department Report**: Department-wise breakdown
- **Trends Analysis**: Time-based trends and patterns

---

## Deployment

### Local Development

```bash
# Development server with debug mode
python app.py
```

- Debug mode enabled
- SQLite database in `instance/`
- Hot reload on code changes

### PythonAnywhere Deployment

1. **Upload files** to PythonAnywhere

2. **Update `wsgi.py`** with your username:
   ```python
   project_home = '/home/YOUR_USERNAME/lab-webapp'
   ```

3. **Create virtual environment**:
   ```bash
   mkvirtualenv --python=/usr/bin/python3.10 labenv
   pip install -r requirements.txt
   ```

4. **Set environment variables** in Web tab or upload `.env`

5. **Configure WSGI** in PythonAnywhere Web tab

6. **Reload** web app

### Vercel Deployment

#### Quick Setup

1. **Generate secure SECRET_KEY**:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. **Add Environment Variables in Vercel Dashboard**:
   - Go to: Vercel Dashboard → Project → Settings → Environment Variables
   - Add required variables (see Configuration section)

3. **Deploy**:
   ```bash
   vercel --prod
   ```

#### Vercel-Specific Notes

**Database Persistence Warning**: Vercel uses ephemeral `/tmp` storage for SQLite.
- Database resets on cold starts
- Use persistent database for production (Vercel Postgres, PlanetScale, Supabase)

**Environment Detection**: App automatically detects Vercel and uses:
- In-memory sessions (cookies)
- Database at `/tmp/lab_data.db`
- HTTPS enforcement
- Security headers enabled

#### Vercel Commands

```bash
# Deploy to production
vercel --prod

# View logs
vercel logs --follow

# List environment variables
vercel env ls

# Add environment variable
vercel env add SECRET_KEY production
```

---

## Security

### Security Features

| Feature | Implementation |
|---------|----------------|
| **Password Hashing** | bcrypt with salt |
| **CSRF Protection** | WTForms CSRF tokens |
| **Session Security** | Server-side sessions, HTTPOnly cookies |
| **Rate Limiting** | Flask-Limiter (configurable) |
| **Security Headers** | Flask-Talisman (CSP, HSTS, X-Frame-Options) |
| **Input Validation** | WTForms validators, parameterized SQL |
| **Email Confirmation** | Secure token with 1-hour expiry |
| **Domain Restriction** | Only @ypmg.com emails can register |

### Security Best Practices

1. **Generate Strong SECRET_KEY**:
   ```python
   import secrets
   print(secrets.token_urlsafe(32))
   ```

2. **Never commit `.env` files** - Use `.env.example` as template

3. **Use HTTPS in production** - Enforced by Flask-Talisman

4. **Rotate credentials** if compromised

5. **Enable rate limiting** for authentication routes

### Security Configuration Validation

The app validates security settings at startup:
- Checks SECRET_KEY is not default/weak
- Validates cookie security settings
- Warns about insecure configurations

---

## Database

### Schema Overview

| Table | Purpose |
|-------|---------|
| `users` | User authentication and profile data |
| `user_sessions` | Active workflow sessions |
| `form_submissions` | Completed form submissions |
| `admin_users` | Admin privilege assignments |
| `audit_log` | System audit trail |

### Database Commands

```bash
# Initialize database
python init_db.py

# Run migrations (if needed)
python migrate_add_email_confirmation.py
python migrations/add_ypb_daily_count.py

# View database (using SQLite browser)
sqlite3 instance/lab_data.db
```

### Azure SQL (Production)

The application supports Azure SQL as a production database backend via `pymssql`. The server uses two databases for separation of concerns:

| Database | Purpose | Tables |
|----------|---------|--------|
| `users` | User authentication & admin data | `users`, `admin_users` |
| `ezeos` | Sessions & submissions | `user_sessions`, `form_submissions`, `audit_log` |

**Environment Variables:**
```bash
AZURE_SQL_SERVER=ezeos.database.windows.net
AZURE_SQL_USERS_DATABASE=users
AZURE_SQL_EZEOS_DATABASE=ezeos
AZURE_SQL_USERNAME=your-username
AZURE_SQL_PASSWORD=your-password
```

**Setup Steps:**
1. Enable public network access in Azure Portal and add firewall rules
2. Run schema migration: `migrations/azure_sql_schema.sql`
3. (Optional) Migrate existing SQLite data: `python migrations/migrate_data_to_azure.py`

See [docs/azure_sql_setup.md](docs/azure_sql_setup.md) for the full setup and troubleshooting guide.

### Backup Strategy

For production:
- Regular automated backups
- Off-site backup storage
- Test restore procedures

---

## API Routes

### Authentication Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET/POST | Login page |
| `/login` | GET/POST | Login page (alias) |
| `/logout` | POST | Logout (POST only for CSRF) |
| `/register` | GET/POST | User registration |
| `/confirm/<token>` | GET | Email confirmation |
| `/resend-confirmation` | GET/POST | Resend confirmation email |

### Workflow Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/page2` | GET/POST | Workflow data entry |
| `/page3` | GET/POST | Notes entry |
| `/confirmation` | GET | Submission confirmation |

### Admin Routes

| Route | Method | Description | Level |
|-------|--------|-------------|-------|
| `/admin` | GET | Dashboard | 1+ |
| `/admin/submissions` | GET | Browse submissions | 2+ |
| `/admin/users` | GET/POST | User management | 3 |
| `/reports` | GET | Reports page | 1+ |
| `/export/csv` | GET | Export to CSV | 2+ |

---

## Troubleshooting

### Common Issues

#### Database Not Found
```bash
python init_db.py
```

#### No Users Available
```bash
python seed_users.py
```

#### Module Not Found Error
```bash
pip install -r requirements.txt
```

#### Port Already in Use
```bash
# Find process using port 5000
netstat -ano | findstr :5000  # Windows
lsof -i :5000                 # macOS/Linux

# Use different port
python app.py --port 5001
```

#### Session Errors
```bash
rm -rf instance/flask_session/*
# Restart application
```

#### Invalid User ID or Passcode
- Ensure `seed_users.py` was run
- Check database exists at `instance/lab_data.db`

#### Email Not Sending
- Verify MAIL_* environment variables are set
- Use app-specific password (not account password)
- Check if organization allows SMTP access

#### FUNCTION_INVOCATION_FAILED (Vercel)
- Usually means import error or missing module
- Check Vercel function logs for Python traceback
- Verify all files are committed to git
- Test imports locally: `python -c "from app import app"`

#### Azure SQL: 503 errors / "Cannot open server" (error 40615)
The client IP is blocked by the Azure SQL firewall. `utils/db_connection.py` fast-fails (10s login timeout) and caches the failure for 30s to prevent request pile-up, but the underlying fix is to add the firewall rule:
- Azure Portal → SQL servers → `ezeos` → Security → Networking
- Add the server's outbound IP (or enable "Allow Azure services")

#### Azure SQL: Intermittent timeouts on first request (error 40613)
Azure SQL Serverless auto-pauses idle databases and cold-starts take 30–60s. The connection handler retries up to 3× with a 20s delay (~60s total). If cold starts are consistently user-facing, disable auto-pause:
- Azure Portal → SQL databases → Compute + storage → Auto-pause delay → **No pause**

### Reset Everything

```bash
# Delete database
rm instance/lab_data.db

# Delete sessions
rm -rf instance/flask_session/

# Reinitialize
python init_db.py
python seed_users.py
```

---

## Development

### Code Style

- Follow PEP 8 guidelines
- Use type hints where possible
- Document functions with docstrings

### Testing

```bash
# Run tests
python -m pytest

# Test email confirmation
python test_email_confirmation.py

# Test Vercel initialization
python test_vercel_init.py
```

### Adding New Features

1. Create route in `routes/`
2. Create form in `forms/` (if needed)
3. Create template in `templates/`
4. Register blueprint in `app.py`
5. Add migrations in `migrations/` (if database changes)

### Frontend Development (YPB Daily Count)

```bash
cd frontend/ypb-daily-count
npm install
npm run dev     # Development server
npm run build   # Production build
```

---

## Future Enhancements

- [ ] QC Logging page between Workflow and Notes (see [plans/qc_logging_implementation_plan.md](plans/qc_logging_implementation_plan.md))
- [ ] QC Dashboard: admin view of quality issues by category and time
- [ ] Excel export with formatting
- [ ] PDF export for individual submissions
- [ ] Advanced chart visualizations
- [ ] Email notifications for submissions
- [ ] Full audit logging implementation
- [ ] User password reset functionality
- [ ] Bulk data import
- [ ] Advanced filtering and search
- [ ] Comprehensive test suite

---

## License

This project is for internal YPMG lab use. See `LICENSE` file for details.

---

## Support

For issues or questions:
1. Check this README and troubleshooting section
2. Review application logs
3. Yell at Gale in Vietnamese. Southern dialect is most effective

---

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-Mail](https://pythonhosted.org/Flask-Mail/)
- [Flask-Limiter](https://flask-limiter.readthedocs.io/)
- [Flask-Talisman](https://github.com/GoogleCloudPlatform/flask-talisman)
- [Vercel Python Runtime](https://vercel.com/docs/functions/serverless-functions/runtimes/python)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
