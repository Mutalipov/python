# connect.py — returns a psycopg2 connection using config.py
import psycopg2
from config import DB_CONFIG


def get_connection():
    """Return a new psycopg2 connection."""
    return psycopg2.connect(**DB_CONFIG)


def get_cursor(conn):
    """Return a dict-style cursor."""
    return conn.cursor()