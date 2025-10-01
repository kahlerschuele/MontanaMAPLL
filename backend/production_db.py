"""
Production Database Module
Handles SQLite database operations for well production data
"""

import sqlite3
from pathlib import Path
from typing import Optional, Dict, List
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "production.db"


def init_database():
    """Initialize the production database schema"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Wells table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS wells (
            api_number TEXT PRIMARY KEY,
            well_name TEXT,
            operator TEXT,
            status TEXT,
            field TEXT,
            county TEXT,
            first_production_date TEXT,
            last_production_date TEXT,
            total_oil_bbls REAL DEFAULT 0,
            total_gas_mcf REAL DEFAULT 0,
            total_water_bbls REAL DEFAULT 0,
            avg_daily_oil REAL DEFAULT 0,
            avg_daily_gas REAL DEFAULT 0,
            last_updated TEXT
        )
    """)

    # Monthly production table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS monthly_production (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            api_number TEXT NOT NULL,
            production_month TEXT NOT NULL,
            oil_bbls REAL DEFAULT 0,
            gas_mcf REAL DEFAULT 0,
            water_bbls REAL DEFAULT 0,
            days_produced INTEGER DEFAULT 0,
            FOREIGN KEY (api_number) REFERENCES wells(api_number),
            UNIQUE(api_number, production_month)
        )
    """)

    # Indexes for fast lookups
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_api ON monthly_production(api_number)")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_month ON monthly_production(production_month)")

    conn.commit()
    conn.close()
    logger.info(f"✓ Database initialized at {DB_PATH}")


def get_well_production(api_number: str) -> Optional[Dict]:
    """
    Get production data for a specific well by API number.

    Args:
        api_number: Well API number

    Returns:
        Dictionary with production data or None if not found
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    # Get well summary
    cursor.execute("""
        SELECT *
        FROM wells
        WHERE api_number = ?
    """, (str(api_number),))

    well = cursor.execute("SELECT * FROM wells WHERE api_number = ?", (str(api_number),)).fetchone()

    if not well:
        conn.close()
        return None

    # Get recent monthly production (last 12 months)
    cursor.execute("""
        SELECT production_month, oil_bbls, gas_mcf, water_bbls, days_produced
        FROM monthly_production
        WHERE api_number = ?
        ORDER BY production_month DESC
        LIMIT 12
    """, (str(api_number),))

    monthly_data = [dict(row) for row in cursor.fetchall()]

    conn.close()

    return {
        'api_number': well['api_number'],
        'well_name': well['well_name'],
        'operator': well['operator'],
        'status': well['status'],
        'field': well['field'],
        'county': well['county'],
        'total_oil_bbls': well['total_oil_bbls'],
        'total_gas_mcf': well['total_gas_mcf'],
        'total_water_bbls': well['total_water_bbls'],
        'barrels_per_day': well['avg_daily_oil'],
        'mcf_per_day': well['avg_daily_gas'],
        'first_production_date': well['first_production_date'],
        'latest_production_month': well['last_production_date'],
        'monthly_data': monthly_data,
        'last_updated': well['last_updated']
    }


def insert_production_data(well_data: Dict, monthly_data: List[Dict]):
    """
    Insert or update production data for a well.

    Args:
        well_data: Dictionary with well information
        monthly_data: List of monthly production records
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Insert or update well
    cursor.execute("""
        INSERT OR REPLACE INTO wells
        (api_number, well_name, operator, status, field, county,
         first_production_date, last_production_date,
         total_oil_bbls, total_gas_mcf, total_water_bbls,
         avg_daily_oil, avg_daily_gas, last_updated)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        well_data['api_number'],
        well_data.get('well_name'),
        well_data.get('operator'),
        well_data.get('status'),
        well_data.get('field'),
        well_data.get('county'),
        well_data.get('first_production_date'),
        well_data.get('last_production_date'),
        well_data.get('total_oil_bbls', 0),
        well_data.get('total_gas_mcf', 0),
        well_data.get('total_water_bbls', 0),
        well_data.get('avg_daily_oil', 0),
        well_data.get('avg_daily_gas', 0),
        datetime.now().isoformat()
    ))

    # Insert monthly data
    for month in monthly_data:
        cursor.execute("""
            INSERT OR REPLACE INTO monthly_production
            (api_number, production_month, oil_bbls, gas_mcf, water_bbls, days_produced)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (
            well_data['api_number'],
            month['production_month'],
            month.get('oil_bbls', 0),
            month.get('gas_mcf', 0),
            month.get('water_bbls', 0),
            month.get('days_produced', 0)
        ))

    conn.commit()
    conn.close()


def get_database_stats() -> Dict:
    """Get statistics about the production database"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    stats = {}

    # Count wells
    cursor.execute("SELECT COUNT(*) FROM wells")
    stats['total_wells'] = cursor.fetchone()[0]

    # Count production records
    cursor.execute("SELECT COUNT(*) FROM monthly_production")
    stats['total_monthly_records'] = cursor.fetchone()[0]

    # Date range
    cursor.execute("SELECT MIN(production_month), MAX(production_month) FROM monthly_production")
    date_range = cursor.fetchone()
    stats['earliest_month'] = date_range[0]
    stats['latest_month'] = date_range[1]

    conn.close()
    return stats


# Initialize database on import
if not DB_PATH.exists():
    init_database()