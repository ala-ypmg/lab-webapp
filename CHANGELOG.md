# Changelog

All notable changes to the YPMG Lab Workflow Webapp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- QC Logging page (between Workflow and Notes)
- QC Dashboard for admin view of quality issues
- Excel export with formatting
- PDF export for individual submissions
- Advanced chart visualizations
- Email notifications for submissions
- Full audit logging implementation
- User password reset functionality
- Bulk data import

---

## [1.5.1] - 2026-04-13

### Fixed
- Azure SQL 503 errors caused by firewall block (error 40615) — `utils/db_connection.py` now fails fast instead of hanging every request for 30s when the server IP is blocked
- Request pile-up during Azure SQL outages by caching connection health (30s failure TTL, 120s success TTL)
- Azure SQL Serverless auto-pause wake-ups (error 40613) now handled with a dedicated retry loop (up to 3 retries × 20s ≈ 60s total) so cold-start waits no longer surface as user-visible failures

### Changed
- Reduced Azure SQL `login_timeout` from 30s to 10s so blocked connections fail fast
- Added exponential-backoff retry logic (up to 2 retries) for transient Azure SQL errors; permanent errors — 40615 (firewall), 18456 (bad credentials), 40914 (tenant not found) — are never retried and log the exact Azure Portal path to fix
- Removed stale `.env` / `.env.example` references from README (secrets now managed outside the repo)

### Documentation
- README project structure updated to include `utils/db_connection.py`, `utils/case_number.py`, `routes/accessioning.py`, `models/case_prefix.py`, and new templates (`accessioning_workflow.html`, `coming_soon.html`)
- Added Azure SQL troubleshooting guidance covering errors 40615 and 40613

---

## [1.5.0] - 2026-04-11

### Changed
- Updated README.md with Azure SQL database configuration, connection details, and setup steps
- Fixed project structure documentation (replaced stale `documentations/` references with accurate `docs/` and `plans/` layout)
- Updated Technology Stack table to reflect Azure SQL via pymssql as production database
- Added QC Logging to Future Enhancements with link to implementation plan

### Removed
- `plans/azure_sql_migration_plan.md` — migration has been executed; operational reference consolidated into `docs/azure_sql_setup.md`

### Documentation
- Replaced boilerplate `frontend/ypb-daily-count/README.md` with YPB Daily Count-specific documentation
- Retained `docs/azure_sql_setup.md` as operational runbook
- Retained `plans/qc_logging_implementation_plan.md` as spec for upcoming QC Logging feature

---

## [1.4.0] - 2026-01-26

### Changed
- Consolidated all documentation into single comprehensive README
- Reorganized project documentation structure

### Removed
- `SECURITY_AUDIT.md` (merged into README)
- `REMOVE_ENV_FROM_HISTORY.md` (merged into README)
- `RESTRUCTURING_SUMMARY.md` (merged into README)
- `VERCEL_SETUP.md` (merged into README)
- `documentations/GETTING_STARTED.md` (merged into README)
- `documentations/DEPLOYMENT_GUIDE.md` (merged into README)
- `documentations/VERCEL_FIX_GUIDE.md` (merged into README)

---

## [1.3.0] - 2026-01-22

### Added
- YPB Daily Count workflow as page 2 for Checkout department
- YPB Daily Block Count Form React application (`frontend/ypb-daily-count/`)
- New route `routes/ypb_daily_count.py` for YPB workflow
- Template `templates/ypb_daily_count.html`
- Database migration `migrations/add_ypb_daily_count.py`

### Security
- Comprehensive security hardening and code restructuring
- Added `utils/config_validator.py` for configuration validation
- Added `utils/logging_config.py` for centralized logging
- Added `utils/security_middleware.py` for rate limiting and security headers
- Removed all debug `print()` statements from routes
- Fixed CSRF vulnerability in logout route (removed GET method)
- Fixed admin user creation bug (wrong function signature)
- Fixed email enumeration vulnerability with generic error messages
- Added Flask-Limiter for rate limiting
- Added Flask-Talisman for security headers

### Changed
- Logout endpoint now only accepts POST requests
- Registration error messages are now generic to prevent enumeration
- Improved logging throughout the application

### Documentation
- Added comprehensive security audit report
- Added guide for removing .env from git history
- Added restructuring summary documentation

### Fixed
- Allow Vercel deployment with temporary SECRET_KEY validation bypass

---

## [1.2.0] - 2026-01-13

### Changed
- Restructured workflow form with subheadings and conditional logic
- Updated pathologist request fields in page2 route
- General code organization improvements

### Fixed
- AttributeError in page2 route by updating to new pathologist request fields

---

## [1.1.0] - 2026-01-12

### Added
- Services module (`services/`) for email and token functionality
  - `services/email.py` - Email sending with Flask-Mail
  - `services/tokens.py` - Token generation/validation for email confirmation
- User registration with email confirmation
- Domain-restricted registration (@ypmg.com only)
- Email confirmation flow with secure tokens
- Registration form (`forms/register_form.py`)
- Email templates (`templates/email/`)
- Resend confirmation functionality
- Migration script for email confirmation fields
- Vercel auto-initialization on cold start
- Coming Soon placeholder page

### Changed
- Updated department dropdown options
- Modified footer copyright information
- Converted final_block_time string to datetime.time for form pre-population
- Updated passcode field to password type
- Removed 4-digit passcode validation (now flexible)
- Updated email-validator from yanked version 2.1.0 to 2.2.0

### Fixed
- Seed user initialization issues
- Vercel deployment errors (multiple fixes)
- Session ID filter for FormSubmission queries
- Various Vercel build and runtime issues

### Removed
- `.github/workflows` directory
- Client-side passcode validation checks

---

## [1.0.0] - 2026-01-11

### Added
- Initial release of Lab Workflow Webapp
- 3-page sequential workflow (Login → Workflow → Notes → Confirmation)
- User authentication with Flask-Login
- Password hashing with bcrypt
- Server-side session management with Flask-Session
- Form validation with WTForms and CSRF protection
- Admin dashboard with role-based access (Levels 1-3)
- User management (create, activate/deactivate users)
- Data export to CSV format
- Reporting system (summary, department, trends)
- Submission browser with pagination
- SQLite database with proper schema
- Vercel deployment configuration
- PythonAnywhere deployment support

### Database Tables
- `users` - User authentication and profile
- `user_sessions` - Active workflow sessions
- `form_submissions` - Completed submissions
- `admin_users` - Admin privilege assignments
- `audit_log` - System audit trail (schema only)

### Security Features
- bcrypt password hashing with salt
- CSRF protection on all forms
- Server-side sessions (HTTPOnly cookies)
- Role-based access control
- Parameterized SQL queries (SQL injection prevention)
- XSS protection via Jinja2 auto-escaping

---

## Version History Summary

| Version | Date | Highlights |
|---------|------|------------|
| 1.5.1 | 2026-04-13 | Azure SQL resilience: firewall fast-fail, auto-pause handling |
| 1.5.0 | 2026-04-11 | Doc consolidation, Azure SQL in README, cleanup |
| 1.4.0 | 2026-01-26 | Documentation consolidation |
| 1.3.0 | 2026-01-22 | YPB Daily Count, Security hardening |
| 1.2.0 | 2026-01-13 | Workflow form restructuring |
| 1.1.0 | 2026-01-12 | Email confirmation, Vercel fixes |
| 1.0.0 | 2026-01-11 | Initial release |

---

## Migration Notes

### Upgrading to 1.3.0
- Run security middleware setup if not using Vercel
- Review and update SECRET_KEY if using default
- Logout forms must use POST method (update any custom logout links)

### Upgrading to 1.1.0
- Run `python migrate_add_email_confirmation.py` for existing databases
- Configure email settings in `.env` file
- Existing users are auto-confirmed with placeholder emails

### Fresh Installation
```bash
python init_db.py
python seed_users.py
```

---

## Contributors

- Gale La
- Claude Code (AI Assistant)

---

## Links

- **Repository**: [GitHub](https://github.com/coffinchaser/lab-webapp)
- **Issues**: [GitHub Issues](https://github.com/coffinchaser/lab-webapp/issues)
- **Documentation**: See README.md
