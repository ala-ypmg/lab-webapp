# Azure SQL Database Setup Guide

This guide documents the setup and configuration for the YPMG Lab Webapp's Azure SQL databases.

---

## Table of Contents

1. [Connection Details](#connection-details)
2. [Network Access Configuration](#network-access-configuration-critical)
3. [SQL Authentication Setup](#sql-authentication-setup)
4. [Database Resume (Serverless)](#database-resume-serverless)
5. [Schema Migration](#schema-migration)
6. [Data Migration](#data-migration)
7. [Connection String Format](#connection-string-format)
8. [Security Best Practices](#security-best-practices)

---

## Connection Details

### Server Information

| Property | Value |
|----------|-------|
| **Server Name** | `ezeos.database.windows.net` |
| **Location** | West US 2 |
| **Server Admin** | `ala` |
| **Port** | 1433 (default) |

### Database Architecture

The application uses **two databases** for separation of concerns:

| Database | Purpose | Tier | Tables |
|----------|---------|------|--------|
| **`users`** | User authentication & admin data | Serverless GP_S_Gen5 | `users`, `admin_users` |
| **`ezeos`** | Form submissions & session data | Serverless GP_S_Gen5 (Free Limit) | `user_sessions`, `form_submissions`, `audit_log` |

> **Note**: Cross-database foreign key constraints are not supported in Azure SQL. Referential integrity between databases is enforced at the application level.

---

## Network Access Configuration (CRITICAL)

### ⚠️ Current Status: Public Network Access DISABLED

Before you can connect to the Azure SQL server, you **MUST** enable network access. The server is currently configured with public network access **disabled**.

### Step 1: Enable Public Network Access (Azure Portal)

1. **Navigate to Azure Portal**: https://portal.azure.com

2. **Go to your SQL Server**:
   - Search for "SQL servers" in the top search bar
   - Click on **`ezeos`** server

3. **Access Networking Settings**:
   - In the left sidebar, under **Security**, click **Networking**

4. **Enable Public Access**:
   - Under **Public network access**, select **"Selected networks"**
   - This allows you to whitelist specific IP addresses

5. **Save Changes**:
   - Click **Save** at the top of the page
   - Wait for the notification confirming the change

### Step 2: Add Firewall Rules

After enabling public access, you need to whitelist IP addresses:

#### Option A: Add Your Current IP (Quick Setup)

1. On the **Networking** page, look for **Firewall rules** section
2. Click **"+ Add your client IPv4 address (x.x.x.x)"**
3. Click **Save**

#### Option B: Add IP Range (For Organizations)

1. In the **Firewall rules** section, click **"+ Add a firewall rule"**
2. Enter:
   - **Rule name**: e.g., `Office-Network`
   - **Start IP**: Start of your IP range (e.g., `203.0.113.0`)
   - **End IP**: End of your IP range (e.g., `203.0.113.255`)
3. Click **OK**, then **Save**

#### Option C: Configure for GitHub Codespaces

GitHub Codespaces use dynamic IP addresses from Microsoft Azure data centers. To allow Codespaces connections:

**Option C.1: Allow Azure Services (Simplest)**

1. On the **Networking** page
2. Check the box: **"Allow Azure services and resources to access this server"**
3. Click **Save**

> ⚠️ **Security Note**: This allows any Azure service to attempt connections. Use only for development/testing.

**Option C.2: Use Codespace IP (More Secure but Manual)**

Each time you start a Codespace, find its IP:

```bash
# Run in Codespace terminal
curl -s ifconfig.me
```

Then add that IP to the firewall rules. Note: You'll need to update this when the Codespace restarts.

### Step 3: Verify Network Access

After configuring firewall rules, test connectivity:

```bash
# Using sqlcmd (if installed)
sqlcmd -S ezeos.database.windows.net -U ala -P 'YOUR_PASSWORD' -Q "SELECT 1"

# Or using Python
python -c "
import pyodbc
conn = pyodbc.connect(
    'DRIVER={ODBC Driver 17 for SQL Server};'
    'SERVER=ezeos.database.windows.net;'
    'DATABASE=users;'
    'UID=ala;'
    'PWD=YOUR_PASSWORD;'
    'Encrypt=yes;'
    'TrustServerCertificate=no;'
)
print('Connection successful!')
conn.close()
"
```

---

## SQL Authentication Setup

### Set Admin Password

If you haven't set a password for the admin user, or need to reset it:

1. **Navigate to Azure Portal**: https://portal.azure.com

2. **Go to your SQL Server**:
   - Search for "SQL servers"
   - Click on **`ezeos`**

3. **Reset Admin Password**:
   - In the left sidebar, under **Settings**, click **Properties**
   - Or go to **Overview** and click **Reset password**
   - Enter a new password meeting these requirements:
     - Minimum 8 characters
     - Contains uppercase, lowercase, numbers, and special characters
     - Does not contain the username

4. **Save the password securely** (e.g., in a password manager or Azure Key Vault)

### Create Application-Specific User (Recommended)

For production, create a dedicated database user instead of using the admin account:

```sql
-- Connect to "users" database
CREATE USER app_user WITH PASSWORD = 'SecureP@ssword123!';
ALTER ROLE db_datareader ADD MEMBER app_user;
ALTER ROLE db_datawriter ADD MEMBER app_user;

-- Connect to "ezeos" database
CREATE USER app_user WITH PASSWORD = 'SecureP@ssword123!';
ALTER ROLE db_datareader ADD MEMBER app_user;
ALTER ROLE db_datawriter ADD MEMBER app_user;
```

---

## Database Resume (Serverless)

Both databases use **serverless tier** with auto-pause enabled. When paused:
- No compute charges
- Database automatically resumes on first connection
- First connection may take **30-60 seconds** while resuming

### Check Database Status

**Via Azure Portal:**
1. Go to **SQL databases** in Azure Portal
2. Look at the **Status** column
3. Status will show: `Online`, `Paused`, or `Resuming`

**Via T-SQL:**
```sql
-- Must connect to master database
SELECT name, state_desc 
FROM sys.databases 
WHERE name IN ('users', 'ezeos');
```

### Manually Resume a Database

**Via Azure Portal:**
1. Navigate to the database (e.g., `ezeos` or `users`)
2. Click **Resume** button in the toolbar
3. Wait for status to change to `Online`

**Via REST API:**
```bash
# Using Azure CLI
az sql db update --resource-group ezeos --server ezeos \
    --name users --auto-pause-delay -1

# This disables auto-pause. To re-enable:
az sql db update --resource-group ezeos --server ezeos \
    --name users --auto-pause-delay 60
```

### Handle Resume in Application

The application should handle the initial connection delay gracefully:

```python
import pyodbc
import time

def connect_with_retry(connection_string, max_retries=3, delay=10):
    """Connect to Azure SQL with retry logic for serverless resume."""
    for attempt in range(max_retries):
        try:
            conn = pyodbc.connect(connection_string, timeout=60)
            return conn
        except pyodbc.Error as e:
            if attempt < max_retries - 1:
                print(f"Connection attempt {attempt + 1} failed, retrying in {delay}s...")
                time.sleep(delay)
            else:
                raise
```

---

## Schema Migration

### Prerequisites

1. ✅ Network access enabled (see [Network Access Configuration](#network-access-configuration-critical))
2. ✅ Admin password set (see [SQL Authentication Setup](#sql-authentication-setup))
3. ✅ Databases resumed (see [Database Resume](#database-resume-serverless))

### Migration Script Location

The schema migration script is located at:
```
migrations/azure_sql_schema.sql
```

### Execute Schema Migration

The script contains two sections that must be run against different databases:

#### Method 1: Using Azure Data Studio (Recommended)

1. **Download Azure Data Studio**: https://docs.microsoft.com/en-us/sql/azure-data-studio/download

2. **Connect to `users` database**:
   - Server: `ezeos.database.windows.net`
   - Database: `users`
   - Authentication: SQL Login
   - User name: `ala`
   - Password: Your admin password

3. **Run Section 1**:
   - Open `migrations/azure_sql_schema.sql`
   - Select SECTION 1 (from `-- SECTION 1: "users" DATABASE SCHEMA` to before SECTION 2)
   - Press F5 to execute

4. **Connect to `ezeos` database**:
   - Change connection to database: `ezeos`

5. **Run Section 2**:
   - Select SECTION 2 (from `-- SECTION 2: "ezeos" DATABASE SCHEMA` to end)
   - Press F5 to execute

#### Method 2: Using sqlcmd (Command Line)

```bash
# Navigate to project directory
cd /workspaces/lab-webapp

# Run Section 1 against "users" database
# (Extract Section 1 to a temp file first)
sqlcmd -S ezeos.database.windows.net \
       -d users \
       -U ala \
       -P 'YOUR_PASSWORD' \
       -i migrations/azure_sql_schema_users.sql

# Run Section 2 against "ezeos" database
sqlcmd -S ezeos.database.windows.net \
       -d ezeos \
       -U ala \
       -P 'YOUR_PASSWORD' \
       -i migrations/azure_sql_schema_ezeos.sql
```

#### Method 3: Using Python Script

```python
import pyodbc

def run_schema_migration(server, database, username, password, script_section):
    connection_string = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={server};"
        f"DATABASE={database};"
        f"UID={username};"
        f"PWD={password};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=60;"
    )
    
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()
    
    # Split script by GO statements and execute each batch
    batches = script_section.split('\nGO\n')
    for batch in batches:
        if batch.strip():
            cursor.execute(batch)
    
    conn.commit()
    conn.close()
    print(f"Schema migrated successfully to {database}")

# Usage:
# run_schema_migration('ezeos.database.windows.net', 'users', 'ala', 'password', section1_sql)
# run_schema_migration('ezeos.database.windows.net', 'ezeos', 'ala', 'password', section2_sql)
```

### Verify Migration

After running the migration, verify tables were created:

```sql
-- Run in each database
SELECT TABLE_NAME, TABLE_TYPE 
FROM INFORMATION_SCHEMA.TABLES 
WHERE TABLE_TYPE = 'BASE TABLE';

-- Expected results:
-- "users" database: users, admin_users
-- "ezeos" database: user_sessions, form_submissions, audit_log
```

---

## Data Migration

After the schema is created, migrate data from the SQLite database to Azure SQL.

### Prerequisites

1. ✅ Schema migration completed (tables exist in Azure SQL)
2. ✅ Network access enabled (your IP whitelisted)
3. ✅ Azure SQL credentials configured
4. ✅ ODBC Driver 17 for SQL Server installed
5. ✅ SQLite database available at `instance/lab_data.db`

### Migration Scripts

| Script | Purpose | Location |
|--------|---------|----------|
| **Data Migration** | Transfers data from SQLite to Azure SQL | `migrations/migrate_data_to_azure.py` |
| **Verification** | Validates migration integrity | `migrations/verify_migration.py` |

### Step 1: Set Environment Variables

Configure Azure SQL credentials before running the migration:

```bash
# Set Azure SQL credentials (Linux/macOS)
export AZURE_SQL_SERVER="ezeos.database.windows.net"
export AZURE_SQL_USERNAME="ala"
export AZURE_SQL_PASSWORD="your-password-here"

# Windows (cmd.exe)
set AZURE_SQL_SERVER=ezeos.database.windows.net
set AZURE_SQL_USERNAME=ala
set AZURE_SQL_PASSWORD=your-password-here

# Windows (PowerShell)
$env:AZURE_SQL_SERVER = "ezeos.database.windows.net"
$env:AZURE_SQL_USERNAME = "ala"
$env:AZURE_SQL_PASSWORD = "your-password-here"
```

### Step 2: Run Data Migration

Execute the migration script:

```bash
# Navigate to project directory
cd /workspaces/lab-webapp

# Run the migration
python migrations/migrate_data_to_azure.py
```

#### What the Migration Does

1. **Reads from SQLite**: `instance/lab_data.db`
2. **Writes to Azure SQL** in order:
   - `users` database: `users`, `admin_users`
   - `ezeos` database: `user_sessions`, `form_submissions`, `audit_log`
3. **Preserves IDs**: Uses `SET IDENTITY_INSERT ON/OFF`
4. **Converts types**: SQLite booleans → SQL Server BIT (0/1)
5. **Batch processing**: Inserts in batches of 100 for performance
6. **Skip duplicates**: Does not overwrite existing records

#### Expected Output

```
======================================================================
DATA MIGRATION: SQLite → Azure SQL
======================================================================

Source: instance/lab_data.db
Target Server: ezeos.database.windows.net
Target Databases: users, ezeos
Batch Size: 100

--------------------------------------------------
Step 1: Connect to source database (SQLite)
--------------------------------------------------
  ✓ Connected to SQLite: instance/lab_data.db

--------------------------------------------------
Step 2: Migrate to 'users' database
--------------------------------------------------
  Connecting to Azure SQL (users)... Connected.

==================================================
Migrating to 'users' database
==================================================

  Migrating table: users
    Reading from SQLite... 25 records found.
    Enabling IDENTITY_INSERT...
  [████████████████████████████████████████] 100.0% (25/25) users
    Successfully migrated 25 records.

  Migrating table: admin_users
    Reading from SQLite... 3 records found.
    Enabling IDENTITY_INSERT...
  [████████████████████████████████████████] 100.0% (3/3) admin_users
    Successfully migrated 3 records.

  ✓ Completed migration to 'users' database

...

======================================================================
MIGRATION SUMMARY REPORT
======================================================================

Table Name                 Source   Migrated    Skipped     Errors
----------------------------------------------------------------------
users                          25         25          0          0
admin_users                     3          3          0          0
user_sessions                  50         50          0          0
form_submissions               42         42          0          0
audit_log                     156        156          0          0
----------------------------------------------------------------------
TOTAL                         276        276          0          0

======================================================================
✅ MIGRATION COMPLETED SUCCESSFULLY
======================================================================
```

### Step 3: Verify Migration

After migration, verify data integrity:

```bash
python migrations/verify_migration.py
```

#### Verification Checks

1. **Record Count Comparison**: Ensures same number of records in SQLite and Azure SQL
2. **Sample Data Integrity**: Compares sample records field-by-field
3. **Type Conversion Validation**: Confirms boolean/BIT conversions are correct

#### Expected Verification Output

```
======================================================================
MIGRATION VERIFICATION: SQLite vs Azure SQL
======================================================================

Source: instance/lab_data.db
Target Server: ezeos.database.windows.net
Target Databases: users, ezeos
Sample Size: 5 records per table

--------------------------------------------------
Connecting to databases...
--------------------------------------------------
  ✓ Connected to SQLite: instance/lab_data.db

--------------------------------------------------
Verifying 'users' database...
--------------------------------------------------
  ✓ Connected to Azure SQL (users)

  Verifying 'users' database tables...
    Checking users... ✅
    Checking admin_users... ✅

--------------------------------------------------
Verifying 'ezeos' database...
--------------------------------------------------
  ✓ Connected to Azure SQL (ezeos)

  Verifying 'ezeos' database tables...
    Checking user_sessions... ✅
    Checking form_submissions... ✅
    Checking audit_log... ✅

================================================================================
MIGRATION VERIFICATION REPORT
================================================================================

--------------------------------------------------------------------------------
RECORD COUNT COMPARISON
--------------------------------------------------------------------------------

Table                       SQLite    Azure SQL      Match     Status
--------------------------------------------------------------------------------
users                           25          25        Yes     ✅ PASS
admin_users                      3           3        Yes     ✅ PASS
user_sessions                   50          50        Yes     ✅ PASS
form_submissions                42          42        Yes     ✅ PASS
audit_log                      156         156        Yes     ✅ PASS

--------------------------------------------------------------------------------
SAMPLE DATA INTEGRITY CHECKS
--------------------------------------------------------------------------------

  📋 users:
     ✅ Sample data integrity (5 records): 5/5 records match

  📋 admin_users:
     ✅ Sample data integrity (3 records): 3/3 records match

  📋 user_sessions:
     ✅ Sample data integrity (5 records): 5/5 records match

  📋 form_submissions:
     ✅ Sample data integrity (5 records): 5/5 records match

  📋 audit_log:
     ✅ Sample data integrity (5 records): 5/5 records match

================================================================================
VERIFICATION SUMMARY
================================================================================

  Total Tables Verified: 5
  Tables Passed: 5
  Tables Failed: 0

================================================================================
✅ VERIFICATION PASSED - Migration data is consistent
================================================================================
```

### Troubleshooting Data Migration

#### Error: "Table 'xxx' does not exist in Azure SQL"

**Cause**: Schema migration not completed.

**Solution**: Run the schema migration first (see [Schema Migration](#schema-migration))

#### Error: "IDENTITY_INSERT is already ON for table 'xxx'"

**Cause**: Previous migration failed mid-way.

**Solution**: Connect to Azure SQL and run:
```sql
SET IDENTITY_INSERT table_name OFF;
```

#### Error: "Violation of UNIQUE KEY constraint"

**Cause**: Data already exists in Azure SQL with the same ID.

**Solution**: The migration script automatically skips existing records. If you need to re-migrate:
```sql
-- WARNING: This deletes all data in the table
DELETE FROM table_name;
DBCC CHECKIDENT ('table_name', RESEED, 0);
```

#### Error: "String or binary data would be truncated"

**Cause**: Source data exceeds column size limits.

**Solution**: Check the data length and either:
1. Truncate the source data
2. Increase column size in Azure SQL schema

---

## Connection String Format

### Environment Variables

Set these environment variables in your `.env` file:

```env
# Azure SQL Database Configuration
AZURE_SQL_SERVER=ezeos.database.windows.net
AZURE_SQL_USERS_DATABASE=users
AZURE_SQL_EZEOS_DATABASE=ezeos
AZURE_SQL_USERNAME=ala
AZURE_SQL_PASSWORD=your-secure-password-here
AZURE_SQL_DRIVER={ODBC Driver 17 for SQL Server}
```

### Connection String Templates

#### For "users" Database (Authentication)
```
Driver={ODBC Driver 17 for SQL Server};
Server=ezeos.database.windows.net;
Database=users;
Uid=ala;
Pwd={your-password};
Encrypt=yes;
TrustServerCertificate=no;
Connection Timeout=30;
```

#### For "ezeos" Database (Sessions/Submissions)
```
Driver={ODBC Driver 17 for SQL Server};
Server=ezeos.database.windows.net;
Database=ezeos;
Uid=ala;
Pwd={your-password};
Encrypt=yes;
TrustServerCertificate=no;
Connection Timeout=30;
```

### Python Connection Example

```python
import os
import pyodbc

# Build connection strings from environment
def get_users_db_connection():
    return pyodbc.connect(
        f"DRIVER={os.environ.get('AZURE_SQL_DRIVER', '{ODBC Driver 17 for SQL Server}')};"
        f"SERVER={os.environ['AZURE_SQL_SERVER']};"
        f"DATABASE={os.environ.get('AZURE_SQL_USERS_DATABASE', 'users')};"
        f"UID={os.environ['AZURE_SQL_USERNAME']};"
        f"PWD={os.environ['AZURE_SQL_PASSWORD']};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )

def get_ezeos_db_connection():
    return pyodbc.connect(
        f"DRIVER={os.environ.get('AZURE_SQL_DRIVER', '{ODBC Driver 17 for SQL Server}')};"
        f"SERVER={os.environ['AZURE_SQL_SERVER']};"
        f"DATABASE={os.environ.get('AZURE_SQL_EZEOS_DATABASE', 'ezeos')};"
        f"UID={os.environ['AZURE_SQL_USERNAME']};"
        f"PWD={os.environ['AZURE_SQL_PASSWORD']};"
        f"Encrypt=yes;"
        f"TrustServerCertificate=no;"
        f"Connection Timeout=30;"
    )
```

---

## Security Best Practices

### During Migration (Temporary Settings)

- ✅ Enable public network access with specific IP rules
- ✅ Add only necessary IP addresses to firewall
- ✅ Use strong admin password
- ✅ Test in development before production

### After Migration (Production Hardening)

1. **Remove Development IPs**:
   - Go to Azure Portal → SQL Server → Networking
   - Remove any personal IP addresses used during development
   - Keep only production server IPs

2. **Disable "Allow Azure Services"** (if enabled for Codespaces):
   - Uncheck "Allow Azure services and resources to access this server"
   - Only enable specific IP ranges needed

3. **Consider Private Endpoint** (for Azure-hosted apps):
   - Provides private connectivity without public IP exposure
   - Azure Portal → SQL Server → Networking → Private endpoint connections

4. **Use Application-Specific User**:
   - Create a dedicated SQL user with minimal permissions
   - Don't use the admin account (`ala`) in production applications

5. **Enable Azure AD Authentication** (future enhancement):
   - More secure than SQL authentication
   - Supports Managed Identity for Azure-hosted apps

6. **Enable Advanced Threat Protection**:
   - Azure Portal → SQL Server → Microsoft Defender for Cloud
   - Detects anomalous activities and potential threats

7. **Review Audit Logs**:
   - Enable SQL Auditing: Azure Portal → SQL Server → Auditing
   - Store logs in Azure Storage for compliance

8. **Rotate Passwords Regularly**:
   - Schedule password rotation every 90 days
   - Use Azure Key Vault for secrets management

### Connection Security Checklist

- [ ] `Encrypt=yes` in connection string (required)
- [ ] `TrustServerCertificate=no` in connection string (validates server cert)
- [ ] Connection timeout set (prevents hanging connections)
- [ ] Credentials in environment variables (not in code)
- [ ] `.env` file in `.gitignore` (never commit secrets)
- [ ] Firewall rules restricted to necessary IPs only

---

## Troubleshooting

### Error: "Cannot open server 'ezeos' requested by the login"

**Cause**: Firewall blocking your IP address.

**Solution**: Add your IP to firewall rules (see [Network Access Configuration](#network-access-configuration-critical))

### Error: "Login failed for user 'ala'"

**Cause**: Wrong password or user doesn't exist.

**Solution**: Reset admin password in Azure Portal

### Error: "Database 'users' on server 'ezeos' is not currently available"

**Cause**: Database is paused (serverless auto-pause feature).

**Solution**: 
- Wait 30-60 seconds and retry (auto-resume)
- Or manually resume via Azure Portal

### Error: "ODBC Driver 17 for SQL Server not found"

**Cause**: ODBC driver not installed.

**Solution**: Install the driver:
```bash
# Linux (Ubuntu/Debian)
curl https://packages.microsoft.com/keys/microsoft.asc | apt-key add -
curl https://packages.microsoft.com/config/ubuntu/$(lsb_release -rs)/prod.list > /etc/apt/sources.list.d/mssql-release.list
apt-get update
ACCEPT_EULA=Y apt-get install -y msodbcsql17

# macOS
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_NO_ENV_FILTERING=1 ACCEPT_EULA=Y brew install msodbcsql17
```

### Error: "TCP Provider: A computer or network problem"

**Cause**: Network connectivity issue or wrong server name.

**Solution**:
- Verify server name is correct: `ezeos.database.windows.net`
- Check your internet connection
- Try pinging the server (though ICMP may be blocked)

---

## Quick Reference

| Task | Command/Location |
|------|------------------|
| Azure Portal | https://portal.azure.com |
| SQL Server Resource | SQL servers → ezeos |
| Networking Settings | SQL server → Security → Networking |
| Reset Password | SQL server → Overview → Reset password |
| Database Status | SQL databases → (database name) → Status |
| Schema Script | `migrations/azure_sql_schema.sql` |
| Data Migration Script | `migrations/migrate_data_to_azure.py` |
| Migration Verification | `migrations/verify_migration.py` |
| Connection Settings | `.env` file |

---

*Last Updated: 2026-04-11*
