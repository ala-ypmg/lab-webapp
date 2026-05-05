# YPMG Lab Workflow Webapp

A Flask-based web application for capturing lab workflow data — multi-page sequential forms, session-based authentication, email confirmation, admin dashboard, and Azure App Service deployment.

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
- **Azure App Service Deployment**: Production hosting on Azure App Service with Azure SQL

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
| **Frontend SPAs** | React 18 + TypeScript + Vite (accessioning-workflow, ypb-daily-count) |
| **UI Components** | Material UI (MUI) v5 with unified navy/orange design system |
| **Typography** | Lato (Google Fonts CDN) for body/UI; Playfair Display (self-hosted variable font) for display headings |

---

## Project Structure

```
lab-webapp/
├── app.py                          # Main Flask application entry point
├── config.py                       # Configuration settings (dev/prod)
├── init_db.py                      # Database initialization script
├── seed_users.py                   # Create initial test users
├── requirements.txt                # Python dependencies
├── wsgi.py                         # WSGI entry point for production
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
│   ├── fonts/
│   │   ├── PlayfairDisplay-VariableFont_wght.ttf
│   │   └── PlayfairDisplay-Italic-VariableFont_wght.ttf
│   ├── js/
│   │   └── validation.js
│   └── assets/                     # Built frontend assets (committed after npm run build)
│
├── frontend/                       # React frontend applications
│   ├── accessioning-workflow/      # Accessioning Workflow React app
│   │   ├── src/
│   │   │   ├── components/
│   │   │   │   ├── AccessioningWorkflow.tsx  # Root component; owns state and submit logic
│   │   │   │   ├── CaseRowTable.tsx          # Generic dynamic-row table with per-row shake
│   │   │   │   ├── DownloadBackupDialog.tsx  # Offline backup (JSON/TXT) on DB errors
│   │   │   │   ├── Page1.tsx / Page2.tsx / Page3.tsx
│   │   │   │   ├── SuccessScreen.tsx
│   │   │   │   └── sections/               # Per-section table components
│   │   │   ├── contexts/
│   │   │   │   └── SubmitKeyContext.ts      # Submit-attempt counter context (for shake re-trigger)
│   │   │   ├── hooks/
│   │   │   │   └── useShake.ts             # Shake animation hook
│   │   │   ├── types/index.ts              # Shared TypeScript types
│   │   │   ├── constants/theme.ts          # Canonical MUI theme (navy/orange palette)
│   │   │   └── shake.css                   # @keyframes shake + .shake-error class
│   │   ├── package.json
│   │   └── vite.config.ts
│   └── ypb-daily-count/            # YPB Daily Count React app
│       ├── src/
│       │   └── constants/theme.ts  # MUI theme (mirrors accessioning palette)
│       ├── package.json
│       └── vite.config.ts
│
├── migrations/                     # Database migrations
│   ├── azure_sql_schema.sql        # Complete Azure SQL schema (users + main databases)
│   ├── add_ypb_daily_count.py
│   └── migrate_data_to_azure.py    # One-time SQLite → Azure SQL data migration
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

### Getting a Microsoft 365 App Password

1. Go to https://account.microsoft.com/security
2. Sign in with your Microsoft 365 account
3. Click **Advanced security options**
4. Under **Additional security**, click **Create a new app password**
5. Copy the generated password to `MAIL_PASSWORD`

### Configuration Files

| File | Purpose |
|------|---------|
| `config.py` | Flask configuration classes (Dev/Prod) |

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

### Workflow Steps

1. **Login** (Page 1) — Enter User ID, 4-digit passcode, and department. Check "Remember Me" if desired.
2. **Workflow Data** (Page 2) — Enter Final Block Time (optional), check applicable workflow items, and select task completion status.
3. **Additional Notes** (Page 3) — Enter any notes (up to 5000 characters).
4. **Confirmation** — Review the submission, then start a new entry or logout.

### New User Registration

1. Click **Register** on the login page
2. Enter User ID, a `@ypmg.com` email address, and a 4-digit passcode (entered twice to confirm)
3. Check your email for a confirmation link and click it to activate your account
4. Log in with your credentials

---

## Admin Guide

### Accessing the Admin Dashboard

Log in with admin credentials and navigate to `http://localhost:5000/admin`.

### Admin URLs

| Page | URL | Required Level |
|------|-----|----------------|
| Dashboard | `/admin` | 1+ |
| Submissions | `/admin/submissions` | 2+ |
| User Management | `/admin/users` | 3 |
| Reports | `/reports` | 1+ |
| Export CSV | `/export/csv` | 2+ |

### Admin Features

**Dashboard** — Overview of total submissions (today/week/month), active users, recent submissions, and quick links.

**User Management** (Level 3) — Create new users, activate/deactivate existing users, and view user details and activity.

**Export Data** — Export submissions to CSV, filtered by date range, department, or user.

**Reports** — Summary, department-wise breakdown, and time-based trends.

---

## Deployment

### Local Development

```bash
python app.py
```

SQLite database is created in `instance/`. Hot reload is active.

### Azure App Service

The application runs on Azure App Service (Linux, Python 3.13) with gunicorn:

```
gunicorn --bind=0.0.0.0:8000 --workers=2 --timeout=120 app:app
```

**Required App Service environment variables:**

```bash
USE_AZURE_SQL=true
AZURE_SQL_SERVER=ezeos.database.windows.net
AZURE_SQL_DATABASE_USERS=users
AZURE_SQL_DATABASE_MAIN=main
AZURE_SQL_USERNAME=appuser
AZURE_SQL_PASSWORD=your-password
SECRET_KEY=your-secret-key
FLASK_ENV=production
```

Set via Azure CLI:
```bash
az webapp config appsettings set \
  --resource-group <rg> --name <app> \
  --settings USE_AZURE_SQL=true AZURE_SQL_USERNAME=appuser ...
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
| **PHI Protection** | Case number pattern detection blocks patient identifiers from Notes (client-side + server-side) |
| **Email Confirmation** | Secure token with 1-hour expiry |
| **Domain Restriction** | Only @ypmg.com emails can register |

### Security Best Practices

1. Generate a strong `SECRET_KEY`: `python -c "import secrets; print(secrets.token_urlsafe(32))"`
2. Never commit `.env` files — use `.env.example` as a template
3. HTTPS is enforced in production by Flask-Talisman
4. Rotate credentials if compromised
5. Rate limiting is enabled on authentication routes

The app validates security settings at startup — it checks that `SECRET_KEY` is not weak, validates cookie security settings, and warns about insecure configurations.

---

## Database

### Schema Overview

| Table | Database | Purpose |
|-------|----------|---------|
| `users` | `users` | User authentication and profile data |
| `admin_users` | `users` | Admin privilege assignments |
| `user_sessions` | `main` | Active workflow sessions |
| `form_submissions` | `main` | Completed form submissions |
| `audit_log` | `main` | System audit trail |
| `case_number_prefixes` | `main` | Valid case number prefixes and facilities |
| `accessioning_submissions` | `main` | Completed accessioning workflow payloads (JSON) |

### Database Commands

```bash
# Initialize database
python init_db.py

# Run migrations (if needed)
python migrate_add_email_confirmation.py
python migrations/add_ypb_daily_count.py

# Inspect the SQLite database
sqlite3 instance/lab_data.db
```

### Azure SQL (Production)

The application uses Azure SQL via `pymssql` with two databases for separation of concerns:

| Database | Purpose | Tables |
|----------|---------|--------|
| `users` | User authentication & admin data | `users`, `admin_users` |
| `main` | Sessions & submissions | `user_sessions`, `form_submissions`, `audit_log`, `accessioning_submissions`, `case_number_prefixes` |

**Environment Variables:**

```bash
USE_AZURE_SQL=true
AZURE_SQL_SERVER=ezeos.database.windows.net
AZURE_SQL_DATABASE_USERS=users
AZURE_SQL_DATABASE_MAIN=main
AZURE_SQL_USERNAME=appuser        # bare username; @shortservername is appended automatically
AZURE_SQL_PASSWORD=your-password
```

> **Note:** pymssql uses SQL Authentication only — Azure AD identities are not supported. Use a bare username (e.g., `appuser`); do not use a UPN like `user@tenant.onmicrosoft.com`.

Create a SQL contained database user in each database:

```sql
-- Run in both the users and main databases
CREATE USER appuser WITH PASSWORD = 'YourStrongPassword!';
ALTER ROLE db_datareader ADD MEMBER appuser;
ALTER ROLE db_datawriter ADD MEMBER appuser;
```

**Setup Steps:**
1. Enable public network access in Azure Portal and add firewall rules (or enable "Allow Azure services")
2. Run `migrations/azure_sql_schema.sql` — Section 1 against `users`, Section 2 against `main`
3. Create a SQL contained database user in both databases (see above)
4. Seed initial users via SQL (see [Troubleshooting → No Users in Azure SQL](#no-users-in-azure-sql))
5. (Optional) Migrate existing SQLite data: `python migrations/migrate_data_to_azure.py`

See [docs/azure_sql_setup.md](docs/azure_sql_setup.md) for the full setup and troubleshooting guide.

### Backup Strategy

For production: configure regular automated backups, store them off-site, and test restore procedures periodically.

---

## API Routes

### Authentication Routes

| Route | Method | Description |
|-------|--------|-------------|
| `/` | GET/POST | Login page |
| `/login` | GET/POST | Login page (alias) |
| `/logout` | POST | Logout (POST only — requires CSRF token) |
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
lsof -i :5000          # macOS/Linux
netstat -ano | findstr :5000  # Windows

python app.py --port 5001
```

#### Session Errors
```bash
rm -rf instance/flask_session/*
# Restart application
```

#### Email Not Sending
- Verify all `MAIL_*` environment variables are set
- Use an app-specific password, not your account password
- Confirm your organization allows SMTP access

#### No Users in Azure SQL

`seed_users.py` targets SQLite only. For Azure SQL, insert seed users directly via the Azure Portal Query Editor against the `users` database — generate bcrypt hashes and insert rows with `is_confirmed=1`. See `seed_users.py` for the user list.

#### Azure SQL: "Cannot open server requested by login" (error 40532)

`AZURE_SQL_USERNAME` contains an `@domain` suffix that pymssql misreads as the target server name. Use a bare username (e.g., `appuser`) — `utils/db_connection.py` appends the correct `@shortservername` automatically.

#### Azure SQL: 503 errors / "Cannot open server" (error 40615)

The client IP is blocked by the Azure SQL firewall. Add a firewall rule:

- Azure Portal → SQL servers → `ezeos` → Security → Networking
- Add the server's outbound IP (or enable "Allow Azure services")

`utils/db_connection.py` fast-fails with a 10s login timeout and caches the failure for 30s to prevent request pile-up, but the underlying fix is the firewall rule.

#### Logout Returns 500 / "CSRF token is missing"

Logout requires a POST with a CSRF token. Use a form, not a plain link:

```html
<form action="{{ url_for('auth.logout') }}" method="post">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
    <button type="submit">Logout</button>
</form>
```

A plain `<a href="/logout">` sends a GET request, which the route rejects with 405.

#### Accessioning submission fails with error 208 ("Invalid object name 'accessioning_submissions'")

The `accessioning_submissions` table does not exist in the `main` database. Restart the app service — `init_azure_sql_schema()` runs on every startup and creates missing tables via `IF NOT EXISTS` guards.

If the problem persists, create the table manually in the Azure Portal Query Editor against the `main` database:

```sql
IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'accessioning_submissions')
CREATE TABLE accessioning_submissions (
    id              INT PRIMARY KEY IDENTITY(1,1),
    user_id         INT           NOT NULL,
    submitted_at    DATETIME2     DEFAULT GETDATE(),
    submission_data NVARCHAR(MAX) NOT NULL
);
CREATE INDEX idx_accessioning_user_id      ON accessioning_submissions(user_id);
CREATE INDEX idx_accessioning_submitted_at ON accessioning_submissions(submitted_at);
```

#### Accessioning submission shows "Database Unavailable" dialog

The database was unreachable at submission time. Use the **Download JSON** or **Download plain text** buttons to save your session data locally, then resubmit once the connection is restored (or forward the backup to your administrator).

#### Azure SQL: Intermittent timeouts on first request (error 40613)

Azure SQL Serverless auto-pauses idle databases; cold starts take 30–60s. The connection handler retries up to 3× with a 20s delay. To disable auto-pause:

- Azure Portal → SQL databases → Compute + storage → Auto-pause delay → **No pause**

### Reset Everything

```bash
rm instance/lab_data.db
rm -rf instance/flask_session/
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
python -m pytest
python test_email_confirmation.py
```

### Adding New Features

1. Create route in `routes/`
2. Create form in `forms/` (if needed)
3. Create template in `templates/`
4. Register blueprint in `app.py`
5. Add migration in `migrations/` (if database schema changes)

### Frontend Development

Both React apps share the same navy/orange color palette and typography defined in each app's `src/constants/theme.ts`. When updating colors or fonts, update both files to keep them in sync.

**Typography:**
- **Lato** — body/UI font, loaded from Google Fonts CDN in each SPA's `index.html` and in `templates/base.html`
- **Playfair Display** — self-hosted variable font (`static/fonts/`), used for display and section headings in Flask templates via `@font-face` in `static/css/styles.css`

**Shared utilities (accessioning-workflow):**

| File | Purpose |
|------|---------|
| `src/hooks/useShake.ts` | `useShake(active, version)` — returns `'shake-error'` or `''`; animation replays whenever `version` increments, even if `active` is already true |
| `src/contexts/SubmitKeyContext.ts` | Provides the current submit-attempt counter to any component in the tree without prop-drilling |
| `src/shake.css` | `@keyframes shake` and `.shake-error`; `prefers-reduced-motion` disables animation and applies a `#fff3f3` tint instead |

**Accessioning Workflow**
```bash
cd frontend/accessioning-workflow
npm install
npm run dev     # Development server at http://localhost:5173
npm run build   # Production build → static/assets/
```

**YPB Daily Count**
```bash
cd frontend/ypb-daily-count
npm install
npm run dev     # Development server at http://localhost:5174
npm run build   # Production build → static/assets/
```

After building, commit the updated files in `static/assets/` so the Flask server serves the latest bundle.

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

This project is for internal YPMG lab use. See `LICENSE` for details.

---

## Support

For issues or questions:
1. Check this README and the Troubleshooting section
2. Review application logs
3. Yell at Gale in Vietnamese. Southern dialect is preferable.

---

## References

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-Mail](https://pythonhosted.org/Flask-Mail/)
- [Flask-Limiter](https://flask-limiter.readthedocs.io/)
- [Flask-Talisman](https://github.com/GoogleCloudPlatform/flask-talisman)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
