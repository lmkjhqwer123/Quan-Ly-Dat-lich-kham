"""
Configuration Module
Đọc biến từ .env file
"""

import os
from dotenv import load_dotenv

# Load các biến từ .env file
load_dotenv()

# ============================================
# EMAIL CONFIG
# ============================================
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# ============================================
# DATABASE CONFIG
# ============================================
DATABASE_URL = os.getenv("DATABASE_URL")
MSSQL_SERVER = os.getenv("MSSQL_SERVER", "DESKTOP-V9NP2C3")
MSSQL_DATABASE = os.getenv("MSSQL_DATABASE", "QuanLyKhamBenhDB")
MSSQL_DRIVER = os.getenv("MSSQL_DRIVER", "ODBC Driver 17 for SQL Server")

# Database configuration dictionary for repository pattern
DB_CONFIG = {
    "server": MSSQL_SERVER,
    "database": MSSQL_DATABASE,
    "driver": MSSQL_DRIVER,
    "user": None,  # Using Windows Authentication (Trusted_Connection)
    "password": None
}

# ============================================
# SECURITY CONFIG
# ============================================
SECRET_KEY = os.getenv("SECRET_KEY")

# ============================================
# GEMINI API CONFIG
# ============================================
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Kiểm tra xem API Key có được set không
if not GEMINI_API_KEY:
    raise ValueError("ERROR: GEMINI_API_KEY is not set in .env file!")
