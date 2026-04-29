import os
from dotenv import load_dotenv
import pyodbc
import time

load_dotenv()

# MSSQL Config
DRIVER = os.getenv("SQL_DRIVER")
SERVER = os.getenv("SQL_SERVER")
DATABASE = os.getenv("SQL_DATABASE")
USERNAME = os.getenv("SQL_USERNAME")
PASSWORD = os.getenv("SQL_PASSWORD")

def get_db_connection(retries=3, delay=3):

    conn_str = (
        f"DRIVER={{ODBC Driver 17 for SQL Server}};"
        f"SERVER={os.getenv('SQL_SERVER')};"
        f"DATABASE={os.getenv('SQL_DATABASE')};"
        f"UID={os.getenv('SQL_USERNAME')};"
        f"PWD={os.getenv('SQL_PASSWORD')};"
        "TrustServerCertificate=yes;"
    )

    for i in range(retries):
        try:
            return pyodbc.connect(conn_str, timeout=30)
        except Exception as e:
            print(f" DB connect retry {i+1}: {e}")
            time.sleep(delay)

    return None
