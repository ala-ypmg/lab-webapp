-- ==============================================================================
-- Azure SQL Schema Migration Script for YPMG Lab Webapp
-- ==============================================================================
-- 
-- Server: ezeos.database.windows.net
-- Location: westus2
-- 
-- This script creates the complete database schema for the YPMG Lab Webapp
-- migration from SQLite to Azure SQL Database.
--
-- DATABASE ARCHITECTURE:
--   - Database: "users"  → User authentication and admin tables
--   - Database: "main"   → Sessions, form submissions, and audit logs
--
-- IMPORTANT: Foreign key references between databases are NOT supported in 
-- Azure SQL. Cross-database referential integrity is enforced at the 
-- application level.
--
-- EXECUTION ORDER:
--   1. Connect to "users" database and run Section 1
--   2. Connect to "main" database and run Section 2
--
-- Generated: 2026-01-27
-- ==============================================================================


-- ==============================================================================
-- SECTION 1: "users" DATABASE SCHEMA
-- ==============================================================================
-- Connect to: ezeos.database.windows.net / users
-- Run this section while connected to the "users" database
-- ==============================================================================

-- -----------------------------------------------------------------------------
-- Table: users
-- Purpose: Stores user authentication and profile information
-- SQLite Migration: INTEGER PRIMARY KEY AUTOINCREMENT → INT IDENTITY(1,1)
--                   BOOLEAN → BIT
--                   TIMESTAMP → DATETIME2
--                   TEXT → NVARCHAR(MAX)
-- -----------------------------------------------------------------------------

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'users')
BEGIN
    CREATE TABLE users (
        -- Primary key with auto-increment
        id INT PRIMARY KEY IDENTITY(1,1),
        
        -- User identifier (e.g., employee ID or username)
        user_id NVARCHAR(50) NOT NULL,
        
        -- Email address (lowercase, used for login)
        email NVARCHAR(255) NOT NULL,
        
        -- Bcrypt hashed password/passcode
        passcode_hash NVARCHAR(255) NOT NULL,
        
        -- Account creation timestamp
        created_at DATETIME2 DEFAULT GETDATE(),
        
        -- Last successful login timestamp
        last_login DATETIME2 NULL,
        
        -- Account status (1=active, 0=disabled)
        is_active BIT DEFAULT 1,
        
        -- Email confirmation status (1=confirmed, 0=pending)
        is_confirmed BIT DEFAULT 0,
        
        -- Email confirmation timestamp
        confirmed_at DATETIME2 NULL,
        
        -- Unique constraints
        CONSTRAINT UQ_users_user_id UNIQUE (user_id),
        CONSTRAINT UQ_users_email UNIQUE (email)
    );
    
    PRINT 'Table [users] created successfully.';
END
ELSE
BEGIN
    PRINT 'Table [users] already exists. Skipping creation.';
END
GO

-- Indexes for users table
-- idx_users_user_id: Fast lookup by user_id (login flow)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_users_user_id' AND object_id = OBJECT_ID('users'))
BEGIN
    CREATE INDEX idx_users_user_id ON users(user_id);
    PRINT 'Index [idx_users_user_id] created.';
END
GO

-- idx_users_email: Fast lookup by email (login flow, registration check)
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_users_email' AND object_id = OBJECT_ID('users'))
BEGIN
    CREATE INDEX idx_users_email ON users(email);
    PRINT 'Index [idx_users_email] created.';
END
GO

-- -----------------------------------------------------------------------------
-- Table: admin_users
-- Purpose: Stores administrator privileges for users
-- Note: References users.id in the same database
-- -----------------------------------------------------------------------------

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'admin_users')
BEGIN
    CREATE TABLE admin_users (
        -- Primary key with auto-increment
        id INT PRIMARY KEY IDENTITY(1,1),
        
        -- Reference to users.id (same database, FK supported)
        user_id INT NOT NULL,
        
        -- Admin privilege level (1=basic admin, 2=super admin, etc.)
        admin_level INT DEFAULT 1,
        
        -- When admin access was granted
        created_at DATETIME2 DEFAULT GETDATE(),
        
        -- Foreign key constraint (within same database)
        CONSTRAINT FK_admin_users_user FOREIGN KEY (user_id) 
            REFERENCES users(id) ON DELETE CASCADE
    );
    
    PRINT 'Table [admin_users] created successfully.';
END
ELSE
BEGIN
    PRINT 'Table [admin_users] already exists. Skipping creation.';
END
GO

-- Index for admin_users table
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_admin_users_user_id' AND object_id = OBJECT_ID('admin_users'))
BEGIN
    CREATE INDEX idx_admin_users_user_id ON admin_users(user_id);
    PRINT 'Index [idx_admin_users_user_id] created.';
END
GO


-- ==============================================================================
-- SECTION 2: "main" DATABASE SCHEMA
-- ==============================================================================
-- Connect to: ezeos.database.windows.net / main
-- Run this section while connected to the "main" database
-- ==============================================================================

-- -----------------------------------------------------------------------------
-- Table: user_sessions
-- Purpose: Stores active workflow sessions with form state
-- Note: user_id references users.id in the "users" database
--       (Cross-database FK not supported - enforced at application level)
-- -----------------------------------------------------------------------------

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'user_sessions')
BEGIN
    CREATE TABLE user_sessions (
        -- Primary key with auto-increment
        id INT PRIMARY KEY IDENTITY(1,1),
        
        -- Unique session identifier (UUID or similar)
        session_id NVARCHAR(255) NOT NULL,
        
        -- Reference to users.id (in "users" database - no FK constraint)
        -- Application enforces referential integrity
        user_id INT NOT NULL,
        
        -- Workflow navigation state
        current_page INT DEFAULT 1,
        max_page_reached INT DEFAULT 1,
        
        -- Session timestamps
        started_at DATETIME2 DEFAULT GETDATE(),
        completed BIT DEFAULT 0,
        login_timestamp DATETIME2 NULL,
        
        -- Department selection
        department NVARCHAR(50) NULL,
        
        -- Remember me preference
        remember_me BIT DEFAULT 0,
        
        -- YPB Daily Count form data (JSON stored as text)
        ypb_daily_count_data NVARCHAR(MAX) NULL,
        
        -- Page 2 fields: Final Block Time
        final_block_time TIME NULL,
        
        -- Page 2 fields: IHC status (done/pending/na)
        baked_ihcs_pt_link NVARCHAR(10) NULL,
        ihcs_in_pt_link NVARCHAR(10) NULL,
        non_baked_ihc NVARCHAR(10) NULL,
        ihcs_in_buffer_wash NVARCHAR(10) NULL,

        -- Page 3 fields: Pathologist requests
        pathologist_requests_status NVARCHAR(20) NULL,
        request_source_email BIT NULL,
        request_source_orchard BIT NULL,
        request_source_send_out BIT NULL,
        in_progress_her2 NVARCHAR(10) NULL,
        
        -- Page 3 fields: Other settings
        upfront_special_stains NVARCHAR(20) NULL,
        peloris_maintenance NVARCHAR(20) NULL,
        notes NVARCHAR(MAX) NULL,
        
        -- Unique constraint on session_id
        CONSTRAINT UQ_user_sessions_session_id UNIQUE (session_id)
    );
    
    PRINT 'Table [user_sessions] created successfully.';
END
ELSE
BEGIN
    PRINT 'Table [user_sessions] already exists. Skipping creation.';
END
GO

-- Indexes for user_sessions table
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_sessions_user_id' AND object_id = OBJECT_ID('user_sessions'))
BEGIN
    CREATE INDEX idx_sessions_user_id ON user_sessions(user_id);
    PRINT 'Index [idx_sessions_user_id] created.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_sessions_session_id' AND object_id = OBJECT_ID('user_sessions'))
BEGIN
    CREATE INDEX idx_sessions_session_id ON user_sessions(session_id);
    PRINT 'Index [idx_sessions_session_id] created.';
END
GO

-- -----------------------------------------------------------------------------
-- Table: form_submissions
-- Purpose: Stores completed form submissions (immutable records)
-- Note: user_id references users.id in the "users" database
--       session_id references user_sessions.id in this database
-- -----------------------------------------------------------------------------

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'form_submissions')
BEGIN
    CREATE TABLE form_submissions (
        -- Primary key with auto-increment
        id INT PRIMARY KEY IDENTITY(1,1),
        
        -- Reference to user_sessions.id (same database - FK supported)
        session_id INT NOT NULL,
        
        -- Reference to users.id (in "users" database - no FK constraint)
        -- Application enforces referential integrity
        user_id INT NOT NULL,
        
        -- Original login timestamp from session
        login_timestamp DATETIME2 NOT NULL,
        
        -- Department for this submission
        department NVARCHAR(50) NOT NULL,
        
        -- Session settings
        remember_me BIT DEFAULT 0,
        
        -- YPB Daily Count form data (JSON)
        ypb_daily_count_data NVARCHAR(MAX) NULL,
        
        -- Page 2 data
        final_block_time TIME NULL,
        baked_ihcs_pt_link NVARCHAR(10) NULL,
        ihcs_in_pt_link NVARCHAR(10) NULL,
        non_baked_ihc NVARCHAR(10) NULL,
        ihcs_in_buffer_wash NVARCHAR(10) NULL,

        -- Page 3 data
        pathologist_requests_status NVARCHAR(20) NULL,
        request_source_email BIT NULL,
        request_source_orchard BIT NULL,
        request_source_send_out BIT NULL,
        in_progress_her2 NVARCHAR(10) NULL,
        upfront_special_stains NVARCHAR(20) NULL,
        peloris_maintenance NVARCHAR(20) NULL,
        notes NVARCHAR(MAX) NULL,
        
        -- Submission timestamp
        submitted_at DATETIME2 DEFAULT GETDATE(),
        
        -- Foreign key to user_sessions (same database)
        CONSTRAINT FK_form_submissions_session FOREIGN KEY (session_id) 
            REFERENCES user_sessions(id) ON DELETE CASCADE
    );
    
    PRINT 'Table [form_submissions] created successfully.';
END
ELSE
BEGIN
    PRINT 'Table [form_submissions] already exists. Skipping creation.';
END
GO

-- Indexes for form_submissions table
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_submissions_user_id' AND object_id = OBJECT_ID('form_submissions'))
BEGIN
    CREATE INDEX idx_submissions_user_id ON form_submissions(user_id);
    PRINT 'Index [idx_submissions_user_id] created.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_submissions_department' AND object_id = OBJECT_ID('form_submissions'))
BEGIN
    CREATE INDEX idx_submissions_department ON form_submissions(department);
    PRINT 'Index [idx_submissions_department] created.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_submissions_timestamp' AND object_id = OBJECT_ID('form_submissions'))
BEGIN
    CREATE INDEX idx_submissions_timestamp ON form_submissions(submitted_at);
    PRINT 'Index [idx_submissions_timestamp] created.';
END
GO

-- -----------------------------------------------------------------------------
-- Table: audit_log
-- Purpose: Stores audit trail of user actions for compliance and debugging
-- Note: user_id references users.id in the "users" database
--       (Cross-database FK not supported - enforced at application level)
-- -----------------------------------------------------------------------------

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'audit_log')
BEGIN
    CREATE TABLE audit_log (
        -- Primary key with auto-increment
        id INT PRIMARY KEY IDENTITY(1,1),
        
        -- Reference to users.id (in "users" database - no FK constraint)
        -- Application enforces referential integrity
        user_id INT NOT NULL,
        
        -- Action performed (e.g., 'LOGIN', 'SUBMIT_FORM', 'UPDATE_PROFILE')
        action NVARCHAR(100) NOT NULL,
        
        -- Table affected by the action (if applicable)
        table_name NVARCHAR(50) NULL,
        
        -- Record ID affected (if applicable)
        record_id INT NULL,
        
        -- When the action occurred
        timestamp DATETIME2 DEFAULT GETDATE(),
        
        -- Client IP address (IPv4 or IPv6)
        ip_address NVARCHAR(45) NULL,
        
        -- Additional details (JSON or text description)
        details NVARCHAR(MAX) NULL
    );
    
    PRINT 'Table [audit_log] created successfully.';
END
ELSE
BEGIN
    PRINT 'Table [audit_log] already exists. Skipping creation.';
END
GO

-- Indexes for audit_log table
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_audit_user_id' AND object_id = OBJECT_ID('audit_log'))
BEGIN
    CREATE INDEX idx_audit_user_id ON audit_log(user_id);
    PRINT 'Index [idx_audit_user_id] created.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_audit_timestamp' AND object_id = OBJECT_ID('audit_log'))
BEGIN
    CREATE INDEX idx_audit_timestamp ON audit_log(timestamp);
    PRINT 'Index [idx_audit_timestamp] created.';
END
GO


-- -----------------------------------------------------------------------------
-- Table: accessioning_submissions
-- Purpose: Stores completed accessioning workflow submissions (JSON payload)
-- Note: user_id references users.id in the "users" database
--       (Cross-database FK not supported - enforced at application level)
-- -----------------------------------------------------------------------------

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'accessioning_submissions')
BEGIN
    CREATE TABLE accessioning_submissions (
        id INT PRIMARY KEY IDENTITY(1,1),
        user_id INT NOT NULL,
        submitted_at DATETIME2 DEFAULT GETDATE(),
        submission_data NVARCHAR(MAX) NOT NULL
    );
    PRINT 'Table [accessioning_submissions] created successfully.';
END
ELSE
BEGIN
    PRINT 'Table [accessioning_submissions] already exists. Skipping creation.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_accessioning_user_id' AND object_id = OBJECT_ID('accessioning_submissions'))
BEGIN
    CREATE INDEX idx_accessioning_user_id ON accessioning_submissions(user_id);
    PRINT 'Index [idx_accessioning_user_id] created.';
END
GO

IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_accessioning_submitted_at' AND object_id = OBJECT_ID('accessioning_submissions'))
BEGIN
    CREATE INDEX idx_accessioning_submitted_at ON accessioning_submissions(submitted_at);
    PRINT 'Index [idx_accessioning_submitted_at] created.';
END
GO


-- -----------------------------------------------------------------------------
-- Table: case_number_prefixes
-- Purpose: Stores all valid case number prefixes and their associated facilities
-- Used by: YPB Daily Count form for prefix selection and facility auto-population
-- -----------------------------------------------------------------------------

IF NOT EXISTS (SELECT * FROM sys.tables WHERE name = 'case_number_prefixes')
BEGIN
    CREATE TABLE case_number_prefixes (
        -- Primary key with auto-increment
        id INT PRIMARY KEY IDENTITY(1,1),

        -- The case number prefix (e.g., 'KAS', 'TC-KPO')
        prefix NVARCHAR(20) NOT NULL,

        -- The facility this prefix belongs to
        facility NVARCHAR(100) NOT NULL,

        -- Whether this prefix is currently active/selectable
        is_active BIT DEFAULT 1,

        -- When this record was created
        created_at DATETIME2 DEFAULT GETDATE(),

        -- Unique constraint on prefix
        CONSTRAINT UQ_case_number_prefixes_prefix UNIQUE (prefix)
    );

    PRINT 'Table [case_number_prefixes] created successfully.';
END
ELSE
BEGIN
    PRINT 'Table [case_number_prefixes] already exists. Skipping creation.';
END
GO

-- Index for fast facility lookups
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_prefixes_facility' AND object_id = OBJECT_ID('case_number_prefixes'))
BEGIN
    CREATE INDEX idx_prefixes_facility ON case_number_prefixes(facility);
    PRINT 'Index [idx_prefixes_facility] created.';
END
GO

-- Index for active prefix filtering
IF NOT EXISTS (SELECT * FROM sys.indexes WHERE name = 'idx_prefixes_is_active' AND object_id = OBJECT_ID('case_number_prefixes'))
BEGIN
    CREATE INDEX idx_prefixes_is_active ON case_number_prefixes(is_active);
    PRINT 'Index [idx_prefixes_is_active] created.';
END
GO

-- Seed data: insert all known prefixes if the table is empty
IF NOT EXISTS (SELECT 1 FROM case_number_prefixes)
BEGIN
    INSERT INTO case_number_prefixes (prefix, facility) VALUES
        -- AH Bakersfield
        ('KAS', 'AH Bakersfield'),
        ('KAB', 'AH Bakersfield'),
        ('KAN', 'AH Bakersfield'),
        ('KAF', 'AH Bakersfield'),
        -- AH Delano
        ('KDS', 'AH Delano'),
        ('KDB', 'AH Delano'),
        ('KDN', 'AH Delano'),
        ('KDF', 'AH Delano'),
        -- AH Specialty Bakersfield
        ('KHS', 'AH Specialty Bakersfield'),
        ('KHB', 'AH Specialty Bakersfield'),
        ('KHN', 'AH Specialty Bakersfield'),
        ('KHF', 'AH Specialty Bakersfield'),
        -- AH Tehachapi
        ('KTS', 'AH Tehachapi'),
        ('KTB', 'AH Tehachapi'),
        ('KTN', 'AH Tehachapi'),
        ('KTF', 'AH Tehachapi'),
        -- Bakersfield OP
        ('KS',  'Bakersfield OP'),
        ('KB',  'Bakersfield OP'),
        ('KN',  'Bakersfield OP'),
        ('KF',  'Bakersfield OP'),
        -- Bakersfield TC
        ('TC-KPO', 'Bakersfield TC'),
        -- Kaweah Health Medical Center
        ('VKS', 'Kaweah Health Medical Center'),
        ('VKB', 'Kaweah Health Medical Center'),
        ('VKN', 'Kaweah Health Medical Center'),
        ('VKF', 'Kaweah Health Medical Center'),
        -- Visalia
        ('VVS', 'Visalia'),
        ('VVB', 'Visalia'),
        ('VVN', 'Visalia'),
        ('VVF', 'Visalia'),
        ('SVS', 'Visalia');

    PRINT 'Seed data inserted into [case_number_prefixes] (30 rows).';
END
ELSE
BEGIN
    PRINT 'Table [case_number_prefixes] already has data. Skipping seed.';
END
GO


-- ==============================================================================
-- VERIFICATION QUERIES
-- ==============================================================================
-- Run these after migration to verify schema was created correctly
-- ==============================================================================

-- Verify tables in "users" database:
-- SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';

-- Verify tables in "main" database:
-- SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';

-- Check foreign keys:
-- SELECT 
--     fk.name AS ForeignKey,
--     OBJECT_NAME(fk.parent_object_id) AS ParentTable,
--     COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS ParentColumn,
--     OBJECT_NAME(fk.referenced_object_id) AS ReferencedTable,
--     COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS ReferencedColumn
-- FROM sys.foreign_keys fk
-- INNER JOIN sys.foreign_key_columns fkc ON fk.object_id = fkc.constraint_object_id;

-- Check indexes:
-- SELECT 
--     t.name AS TableName,
--     i.name AS IndexName,
--     i.type_desc AS IndexType
-- FROM sys.indexes i
-- INNER JOIN sys.tables t ON i.object_id = t.object_id
-- WHERE i.name IS NOT NULL AND i.name LIKE 'idx_%';


-- ==============================================================================
-- END OF MIGRATION SCRIPT
-- ==============================================================================
