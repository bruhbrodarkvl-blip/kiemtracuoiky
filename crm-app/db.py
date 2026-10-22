import os
import time
import psycopg2
from psycopg2 import pool
from contextlib import contextmanager

DB_HOST = os.getenv("DB_HOST", "crm-db")
DB_PORT = int(os.getenv("DB_PORT", "5432"))
DB_NAME = os.getenv("DB_NAME", "crm_db")
DB_USER = os.getenv("DB_USER", "crm_user")
DB_PASSWORD = os.getenv("DB_PASSWORD", "CrmSecurePass_2026!")

connection_pool = None

def get_pool():
    global connection_pool
    if connection_pool is None:
        retries = 10
        while retries > 0:
            try:
                connection_pool = pool.SimpleConnectionPool(
                    1, 20,
                    host=DB_HOST,
                    port=DB_PORT,
                    database=DB_NAME,
                    user=DB_USER,
                    password=DB_PASSWORD
                )
                print("Connected to PostgreSQL successfully!")
                break
            except Exception as e:
                retries -= 1
                print(f"Waiting for database... ({retries} left): {e}")
                time.sleep(3)
        if connection_pool is None:
            raise Exception("Cannot connect to PostgreSQL database!")
    return connection_pool

@contextmanager
def get_db_cursor(commit=False):
    p = get_pool()
    conn = p.getconn()
    try:
        with conn.cursor() as cur:
            yield cur
        if commit:
            conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        p.putconn(conn)

def check_db_health():
    try:
        with get_db_cursor() as cur:
            cur.execute("SELECT 1;")
            return True
    except Exception as e:
        print(f"DB Health check failed: {e}")
        return False
