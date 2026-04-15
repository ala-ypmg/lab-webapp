import os

# Database type detection
USE_AZURE_SQL = os.environ.get('USE_AZURE_SQL', 'false').lower() == 'true'
PH = '%s' if USE_AZURE_SQL else '?'

if USE_AZURE_SQL:
    import pymssql
else:
    import sqlite3


def get_connection(db_path):
    """
    Get database connection based on configuration.
    Prefixes are stored in the ezeos database.
    """
    if USE_AZURE_SQL:
        from utils.db_connection import get_ezeos_connection
        return get_ezeos_connection()
    else:
        return sqlite3.connect(db_path)


class CaseNumberPrefix:
    """Model for case number prefixes and their associated facilities"""

    def __init__(self, id=None, prefix=None, facility=None, is_active=True, created_at=None):
        self.id = id
        self.prefix = prefix
        self.facility = facility
        self.is_active = bool(is_active) if is_active is not None else True
        self.created_at = created_at

    def to_dict(self):
        return {
            'id': self.id,
            'prefix': self.prefix,
            'facility': self.facility,
            'is_active': self.is_active,
            'created_at': self.created_at,
        }

    # -------------------------------------------------------------------------
    # Table initialization (SQLite only; Azure SQL uses the migration script)
    # -------------------------------------------------------------------------

    @staticmethod
    def create_table(db_path):
        """Create table and seed data for SQLite environments"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS case_number_prefixes (
                    id        INTEGER PRIMARY KEY AUTOINCREMENT,
                    prefix    TEXT    NOT NULL UNIQUE,
                    facility  TEXT    NOT NULL,
                    is_active INTEGER DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            # Seed if empty
            cursor.execute('SELECT COUNT(*) FROM case_number_prefixes')
            if cursor.fetchone()[0] == 0:
                seed_data = [
                    ('KAS', 'AH Bakersfield'),
                    ('KAB', 'AH Bakersfield'),
                    ('KAN', 'AH Bakersfield'),
                    ('KAF', 'AH Bakersfield'),
                    ('KDS', 'AH Delano'),
                    ('KDB', 'AH Delano'),
                    ('KDN', 'AH Delano'),
                    ('KDF', 'AH Delano'),
                    ('KHS', 'AH Specialty Bakersfield'),
                    ('KHB', 'AH Specialty Bakersfield'),
                    ('KHN', 'AH Specialty Bakersfield'),
                    ('KHF', 'AH Specialty Bakersfield'),
                    ('KTS', 'AH Tehachapi'),
                    ('KTB', 'AH Tehachapi'),
                    ('KTN', 'AH Tehachapi'),
                    ('KTF', 'AH Tehachapi'),
                    ('KS',  'Bakersfield OP'),
                    ('KB',  'Bakersfield OP'),
                    ('KN',  'Bakersfield OP'),
                    ('KF',  'Bakersfield OP'),
                    ('TC-KPO', 'Bakersfield TC'),
                    ('VKS', 'Kaweah Health Medical Center'),
                    ('VKB', 'Kaweah Health Medical Center'),
                    ('VKN', 'Kaweah Health Medical Center'),
                    ('VKF', 'Kaweah Health Medical Center'),
                    ('VVS', 'Visalia'),
                    ('VVB', 'Visalia'),
                    ('VVN', 'Visalia'),
                    ('VVF', 'Visalia'),
                    ('SVS', 'Visalia'),
                ]
                cursor.executemany(
                    'INSERT INTO case_number_prefixes (prefix, facility) VALUES (?, ?)',
                    seed_data
                )

            conn.commit()
        finally:
            conn.close()

    # -------------------------------------------------------------------------
    # Queries
    # -------------------------------------------------------------------------

    @staticmethod
    def get_all(db_path, active_only=True):
        """Return all prefixes, optionally filtered to active ones"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            if active_only:
                cursor.execute(
                    'SELECT id, prefix, facility, is_active, created_at '
                    'FROM case_number_prefixes WHERE is_active = 1 ORDER BY facility, prefix'
                )
            else:
                cursor.execute(
                    'SELECT id, prefix, facility, is_active, created_at '
                    'FROM case_number_prefixes ORDER BY facility, prefix'
                )
            return [CaseNumberPrefix(*row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_by_prefix(db_path, prefix):
        """Look up a single prefix record"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            cursor.execute(
                f'SELECT id, prefix, facility, is_active, created_at '
                f'FROM case_number_prefixes WHERE prefix = {PH}',
                (prefix,)
            )
            row = cursor.fetchone()
            return CaseNumberPrefix(*row) if row else None
        finally:
            conn.close()

    @staticmethod
    def get_by_facility(db_path, facility, active_only=True):
        """Return all prefixes for a given facility"""
        conn = get_connection(db_path)
        cursor = conn.cursor()
        try:
            if active_only:
                cursor.execute(
                    f'SELECT id, prefix, facility, is_active, created_at '
                    f'FROM case_number_prefixes WHERE facility = {PH} AND is_active = 1 ORDER BY prefix',
                    (facility,)
                )
            else:
                cursor.execute(
                    f'SELECT id, prefix, facility, is_active, created_at '
                    f'FROM case_number_prefixes WHERE facility = {PH} ORDER BY prefix',
                    (facility,)
                )
            return [CaseNumberPrefix(*row) for row in cursor.fetchall()]
        finally:
            conn.close()

    @staticmethod
    def get_grouped_by_facility(db_path, active_only=True):
        """
        Return prefixes grouped by facility.

        Returns a list of dicts: [{'facility': str, 'prefixes': [str, ...]}, ...]
        """
        rows = CaseNumberPrefix.get_all(db_path, active_only=active_only)
        groups = {}
        for row in rows:
            groups.setdefault(row.facility, []).append(row.prefix)
        return [{'facility': facility, 'prefixes': prefixes}
                for facility, prefixes in groups.items()]
