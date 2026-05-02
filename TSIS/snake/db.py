
import psycopg2
import psycopg2.extras
from config import DB_DSN

#SQL schema 
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS players (
    id       SERIAL PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL
);

CREATE TABLE IF NOT EXISTS game_sessions (
    id            SERIAL PRIMARY KEY,
    player_id     INTEGER REFERENCES players(id),
    score         INTEGER   NOT NULL,
    level_reached INTEGER   NOT NULL,
    played_at     TIMESTAMP DEFAULT NOW()
);
"""


def get_connection():
    """Return a new psycopg2 connection. Raises on failure."""
    return psycopg2.connect(DB_DSN)


def init_db():
    """Create tables if they do not exist yet."""
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(SCHEMA_SQL)
        conn.close()
        return True
    except Exception as e:
        print(f"[DB] init_db error: {e}")
        return False


# Player helpers

def get_or_create_player(username: str) -> int | None:
    """Return player id, inserting a new row if the username is new."""
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO players (username) VALUES (%s) "
                    "ON CONFLICT (username) DO NOTHING",
                    (username,)
                )
                cur.execute(
                    "SELECT id FROM players WHERE username = %s",
                    (username,)
                )
                row = cur.fetchone()
        conn.close()
        return row[0] if row else None
    except Exception as e:
        print(f"[DB] get_or_create_player error: {e}")
        return None


def get_personal_best(username: str) -> int:
    """Return the highest score ever recorded for *username*, or 0."""
    try:
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute(
                """
                SELECT COALESCE(MAX(gs.score), 0)
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                WHERE p.username = %s
                """,
                (username,)
            )
            result = cur.fetchone()
        conn.close()
        return result[0] if result else 0
    except Exception as e:
        print(f"[DB] get_personal_best error: {e}")
        return 0


# Session helpers


def save_session(player_id: int, score: int, level_reached: int) -> bool:
    """Persist a completed game session. Returns True on success."""
    try:
        conn = get_connection()
        with conn:
            with conn.cursor() as cur:
                cur.execute(
                    "INSERT INTO game_sessions (player_id, score, level_reached) "
                    "VALUES (%s, %s, %s)",
                    (player_id, score, level_reached)
                )
        conn.close()
        return True
    except Exception as e:
        print(f"[DB] save_session error: {e}")
        return False


def get_leaderboard(limit: int = 10) -> list[dict]:
    """
    Return the top *limit* scores across all players.
    Each row: {rank, username, score, level_reached, played_at}
    """
    try:
        conn = get_connection()
        with conn.cursor(cursor_factory=psycopg2.extras.DictCursor) as cur:
            cur.execute(
                """
                SELECT
                    ROW_NUMBER() OVER (ORDER BY gs.score DESC) AS rank,
                    p.username,
                    gs.score,
                    gs.level_reached,
                    gs.played_at
                FROM game_sessions gs
                JOIN players p ON p.id = gs.player_id
                ORDER BY gs.score DESC
                LIMIT %s
                """,
                (limit,)
            )
            rows = [dict(r) for r in cur.fetchall()]
        conn.close()
        return rows
    except Exception as e:
        print(f"[DB] get_leaderboard error: {e}")
        return []