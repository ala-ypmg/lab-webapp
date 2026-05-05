# Changelog

All notable changes to the YPMG Lab Workflow Webapp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- `DownloadBackupDialog` component (`frontend/accessioning-workflow/src/components/DownloadBackupDialog.tsx`): when a submission fails due to a DB connection error (503) or a network failure, a dialog opens automatically offering two client-side backup downloads:
  - **JSON** — full structured payload (sans internal React IDs) plus a `meta` block with timestamp, user ID, and department; suitable for programmatic resubmission once the connection is restored
  - **Plain text** — human-readable report with section headings, per-field labels, notes, and the accessioning confirmation; suitable for printing or emailing
  - Files are named `accessioning_backup_<userId>_<timestamp>.(json|txt)` and generated entirely client-side — no round-trip needed
- `init_azure_sql_schema()` in `app.py`: idempotently creates all Azure SQL tables on every startup using `IF NOT EXISTS` guards; previously the Azure SQL startup block only verified the connection and never ran DDL, so tables introduced after the initial deployment (e.g. `accessioning_submissions`) were never created in the production database
- Unified design system across all frontend surfaces (Flask templates + both React SPAs)
  - Shared navy/orange color palette: primary `#17406a`, accent `#e8912c`, matching light/dark variants, text, border, and background tokens
  - **DM Sans** (Google Fonts CDN) replaces Roboto as the body/UI typeface across `templates/base.html`, both SPA `index.html` files, and both MUI `theme.ts` files
  - **Playfair Display** variable font (self-hosted in `static/fonts/`) applied to Flask app display and section headings (`.form-card h2`, `.form-section h3`, `.admin-container h2`)
  - Typography CSS custom properties added to `static/css/styles.css`: full type scale (`--text-xs` through `--text-2xl`), weight tokens, spacing, radius, and shadow tokens matching the design system spec
  - Button `font-weight` raised from 400 → 500 across all Flask-rendered pages

### Changed
- `accessioning_submit()` (`routes/accessioning.py`): DB connection failures now return **503** with `error_type: 'db_unavailable'` (triggers the backup download dialog); SQL execution failures continue to return 500 — the two error paths are now separate `try/except` blocks
- `accessioning_submit()`: raw exception strings are no longer forwarded to the client; the full error is logged server-side and a sanitized user-facing message is returned instead
- `init_azure_sql_schema()`: each DDL statement in both `users_ddl` and `main_ddl` is now committed individually; previously a single `conn.commit()` ran after all statements — a failure in any later statement (e.g. the `case_number_prefixes` seed INSERT) would cause pymssql to roll back all prior DDL on `conn.close()`, silently leaving new tables uncreated
- Submission error `Snackbar` now wraps an `Alert severity="error"` for a clearly styled red indicator and does not auto-dismiss — stays visible until the user explicitly closes it so errors are not missed
- `frontend/ypb-daily-count/src/constants/theme.ts`: aligned all color values, typography weights (h5/h6/subtitle1), font stack, and MUI palette secondary to match the accessioning-workflow theme; retained ypb-specific mobile component overrides (touch targets, rounded corners, iOS font-size)
- `static/css/styles.css`: updated all CSS custom properties to the accessioning palette; header background changed from dark grey (`#343a40`) to primary navy (`#17406a`); footer uses darker navy (`#102d4a`); button hover and table row-hover colors updated to match
- `frontend/ypb-daily-count/src/components/RunEntry.tsx`: replaced hardcoded hover color `#eef1f2` with `colors.border` from the theme

### Fixed
- `accessioning_submissions` table missing from the Azure SQL `main` database: the table existed in `init_db.py` (SQLite) but was never created via `init_azure_sql_schema()` because that function did not exist — submissions returned error 208 ("Invalid object name") on every attempt
- `TABLE_DATABASE_MAP` in `utils/db_connection.py` omitted `accessioning_submissions` and `case_number_prefixes`; `get_connection(for_table=...)` now routes them to the correct `main` database instead of silently falling through to the default

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

## [1.6.1] - 2026-04-27

### Fixed
- Logout returning 500 instead of completing: all logout forms (`base.html`, `confirmation.html`, `coming_soon.html`, `error.html`) were missing the `csrf_token` hidden input, causing flask-wtf to reject every POST with a 400 CSRFError
- `handle_database_error` (`app.py`) was catching all `Exception`s and re-raising them, which caused Flask to wrap HTTP errors (405 MethodNotAllowed, 400 CSRFError) as 500 Internal Server Error instead of their correct status codes; it now returns `HTTPException` instances directly

---

## [1.6.0] - 2026-04-27

### Added
- `accessioning_submissions` table (with indexes) added to `migrations/azure_sql_schema.sql` — was defined in `init_db.py` but missing from the Azure SQL migration script

### Fixed
- Azure SQL error 40532 ("Cannot open server requested by login"): `get_azure_connection_params` now always strips any existing `@domain` suffix from `AZURE_SQL_USERNAME` and re-appends the correct `@shortservername` — previously an email-format username (e.g. `ala@ypmg.com`) was passed through as-is and pymssql misread the domain part as the target server name
- `routes/accessioning.py` hardcoded SQLite-style `?` placeholders replaced with `{PH}` so the INSERT correctly uses `%s` under Azure SQL

### Changed
- Production database fully migrated from SQLite to Azure SQL; all tables created via `migrations/azure_sql_schema.sql`
- Authentication switched from Azure AD guest UPN to a SQL contained database user — pymssql supports SQL Authentication only, not Azure AD; `AZURE_SQL_USERNAME` should be a bare username (e.g. `appuser`) and the `@shortservername` suffix is now appended automatically
- Seed users must be inserted directly via SQL for Azure SQL deployments (`seed_users.py` is SQLite-only)

### Migration Notes
- Run `migrations/azure_sql_schema.sql` Section 1 against the `users` database and Section 2 against the `main` database
- Create a SQL contained database user in each database with `db_datareader` and `db_datawriter` roles; do not use Azure AD identities as pymssql requires SQL Authentication

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
| Unreleased | — | Design system: DM Sans + Playfair Display, retire Roboto; CSS token system |
| 1.6.1 | 2026-04-27 | Fix logout 500: missing CSRF tokens on logout forms; error handler HTTP passthrough |
| 1.6.0 | 2026-04-27 | Azure SQL production migration complete; error 40532 fix; accessioning schema |
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

- YPMG Lab Development Team
- Claude Code (AI Assistant)

---

## Links

- **Repository**: [GitHub](https://github.com/coffinchaser/lab-webapp)
- **Issues**: [GitHub Issues](https://github.com/coffinchaser/lab-webapp/issues)
- **Documentation**: See README.md
# Changelog

All notable changes to the YPMG Lab Workflow Webapp will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Added
- PHI guard on the Notes field — both submission paths now reject notes containing a case number pattern (`YY[PREFIX]-NNNNN`, e.g. `25RR-15616`):
  - `utils/case_number.py`: new `contains_case_number(text)` function using an unanchored, case-insensitive `_SCAN` regex
  - `frontend/src/utils/caseNumber.ts`: matching `containsCaseNumber(text)` function
  - `AccessioningWorkflow.tsx`: notes validated in `handleSubmit` before the fetch; error message displayed inline under the textarea and cleared on edit
  - `routes/accessioning.py`: server-side guard returns 400 with a user-facing error if notes contain a case number — cannot be bypassed by disabling JS
  - `forms/notes_form.py`: `no_case_numbers` WTForms validator added to `NotesForm.notes` so the traditional multi-page workflow is also covered
  - `tests/test_case_number.py`: 8 new tests for `contains_case_number` (embedded match, case-insensitive, standalone, plain prose, empty string, non-string, partial year, short suffix)
- Dismissable info alert above the Notes textarea: *"Do not include case numbers and other PHI in your notes!"*; state is local to the component and survives neither page navigation nor session reset
- Shake animation (`shake.css`, `hooks/useShake.ts`) on all validation error elements — fires on first trigger and re-fires on repeated submit attempts even when the same error persists:
  - `@keyframes shake` with `cubic-bezier(0.36, 0.07, 0.19, 0.97)` lateral translate; `prefers-reduced-motion` fallback removes animation and applies a `#fff3f3` background tint
  - `useShake(active, version)` hook: removes `.shake-error` after 400ms so it replays cleanly; re-triggers whenever `version` increments independently of `active`
  - `SubmitKeyContext` provides the submit counter via React context, avoiding prop-drilling through section components
  - `AccessioningWorkflow.tsx`: `submitKey` state increments on every validation failure (both `handleNavigate` page-1 guard and `handleSubmit` error block)
  - Page 1: error text shakes; Page 2: page-level `Alert` shakes; Page 3: notes `TextField` and accessioned `FormHelperText` shake independently; `CaseRowTable`: entire row `Paper` card shakes when any field in the row has an error (extracted `RowCard` component since hooks cannot be called inside `.map`)
- `DownloadBackupDialog` component (`frontend/accessioning-workflow/src/components/DownloadBackupDialog.tsx`): when a submission fails due to a DB connection error (503) or a network failure, a dialog opens automatically offering two client-side backup downloads:
  - **JSON** — full structured payload (sans internal React IDs) plus a `meta` block with timestamp, user ID, and department; suitable for programmatic resubmission once the connection is restored
  - **Plain text** — human-readable report with section headings, per-field labels, notes, and the accessioning confirmation; suitable for printing or emailing
  - Files are named `accessioning_backup_<userId>_<timestamp>.(json|txt)` and generated entirely client-side — no round-trip needed
- `init_azure_sql_schema()` in `app.py`: idempotently creates all Azure SQL tables on every startup using `IF NOT EXISTS` guards; previously the Azure SQL startup block only verified the connection and never ran DDL, so tables introduced after the initial deployment (e.g. `accessioning_submissions`) were never created in the production database
- Unified design system across all frontend surfaces (Flask templates + both React SPAs)
  - Shared navy/orange color palette: primary `#17406a`, accent `#e8912c`, matching light/dark variants, text, border, and background tokens
  - **DM Sans** (Google Fonts CDN) replaces Roboto as the body/UI typeface across `templates/base.html`, both SPA `index.html` files, and both MUI `theme.ts` files
  - **Playfair Display** variable font (self-hosted in `static/fonts/`) applied to Flask app display and section headings (`.form-card h2`, `.form-section h3`, `.admin-container h2`)
  - Typography CSS custom properties added to `static/css/styles.css`: full type scale (`--text-xs` through `--text-2xl`), weight tokens, spacing, radius, and shadow tokens matching the design system spec
  - Button `font-weight` raised from 400 → 500 across all Flask-rendered pages

### Changed
- "No" accessioning warning on Page 3 updated from *"Incomplete accessioning noted. Document outstanding cases in the session notes above before submitting."* to *"Please indicate how many specimens are not yet accessioned. Do not include case numbers and other PHI."*
- `accessioning_submit()` (`routes/accessioning.py`): DB connection failures now return **503** with `error_type: 'db_unavailable'` (triggers the backup download dialog); SQL execution failures continue to return 500 — the two error paths are now separate `try/except` blocks
- `accessioning_submit()`: raw exception strings are no longer forwarded to the client; the full error is logged server-side and a sanitized user-facing message is returned instead
- `init_azure_sql_schema()`: each DDL statement in both `users_ddl` and `ezeos_ddl` is now committed individually; previously a single `conn.commit()` ran after all statements — a failure in any later statement (e.g. the `case_number_prefixes` seed INSERT) would cause pymssql to roll back all prior DDL on `conn.close()`, silently leaving new tables uncreated
- Submission error `Snackbar` now wraps an `Alert severity="error"` for a clearly styled red indicator and does not auto-dismiss — stays visible until the user explicitly closes it so errors are not missed
- `frontend/ypb-daily-count/src/constants/theme.ts`: aligned all color values, typography weights (h5/h6/subtitle1), font stack, and MUI palette secondary to match the accessioning-workflow theme; retained ypb-specific mobile component overrides (touch targets, rounded corners, iOS font-size)
- `static/css/styles.css`: updated all CSS custom properties to the accessioning palette; header background changed from dark grey (`#343a40`) to primary navy (`#17406a`); footer uses darker navy (`#102d4a`); button hover and table row-hover colors updated to match
- `frontend/ypb-daily-count/src/components/RunEntry.tsx`: replaced hardcoded hover color `#eef1f2` with `colors.border` from the theme

### Fixed
- `accessioning_submissions` table missing from the Azure SQL `ezeos` database: the table existed in `init_db.py` (SQLite) but was never created via `init_azure_sql_schema()` because that function did not exist — submissions returned error 208 ("Invalid object name") on every attempt
- `TABLE_DATABASE_MAP` in `utils/db_connection.py` omitted `accessioning_submissions` and `case_number_prefixes`; `get_connection(for_table=...)` now routes them to the correct `ezeos` database instead of silently falling through to the default

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

## [1.6.1] - 2026-04-27

### Fixed
- Logout returning 500 instead of completing: all logout forms (`base.html`, `confirmation.html`, `coming_soon.html`, `error.html`) were missing the `csrf_token` hidden input, causing flask-wtf to reject every POST with a 400 CSRFError
- `handle_database_error` (`app.py`) was catching all `Exception`s and re-raising them, which caused Flask to wrap HTTP errors (405 MethodNotAllowed, 400 CSRFError) as 500 Internal Server Error instead of their correct status codes; it now returns `HTTPException` instances directly

---

## [1.6.0] - 2026-04-27

### Added
- `accessioning_submissions` table (with indexes) added to `migrations/azure_sql_schema.sql` — was defined in `init_db.py` but missing from the Azure SQL migration script

### Fixed
- Azure SQL error 40532 ("Cannot open server requested by login"): `get_azure_connection_params` now always strips any existing `@domain` suffix from `AZURE_SQL_USERNAME` and re-appends the correct `@shortservername` — previously an email-format username (e.g. `ala@ypmg.com`) was passed through as-is and pymssql misread the domain part as the target server name
- `routes/accessioning.py` hardcoded SQLite-style `?` placeholders replaced with `{PH}` so the INSERT correctly uses `%s` under Azure SQL

### Changed
- Production database fully migrated from SQLite to Azure SQL; all tables created via `migrations/azure_sql_schema.sql`
- Authentication switched from Azure AD guest UPN to a SQL contained database user — pymssql supports SQL Authentication only, not Azure AD; `AZURE_SQL_USERNAME` should be a bare username (e.g. `appuser`) and the `@shortservername` suffix is now appended automatically
- Seed users must be inserted directly via SQL for Azure SQL deployments (`seed_users.py` is SQLite-only)

### Migration Notes
- Run `migrations/azure_sql_schema.sql` Section 1 against the `users` database and Section 2 against the `ezeos` database
- Create a SQL contained database user in each database with `db_datareader` and `db_datawriter` roles; do not use Azure AD identities as pymssql requires SQL Authentication

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
| Unreleased | — | PHI guard on Notes (case number detection, frontend + backend); shake animation on errors; design system: DM Sans + Playfair Display |
| 1.6.1 | 2026-04-27 | Fix logout 500: missing CSRF tokens on logout forms; error handler HTTP passthrough |
| 1.6.0 | 2026-04-27 | Azure SQL production migration complete; error 40532 fix; accessioning schema |
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

- YPMG Lab Development Team
- Claude Code (AI Assistant)

---

## Links

- **Repository**: [GitHub](https://github.com/coffinchaser/lab-webapp)
- **Issues**: [GitHub Issues](https://github.com/coffinchaser/lab-webapp/issues)
- **Documentation**: See README.md
