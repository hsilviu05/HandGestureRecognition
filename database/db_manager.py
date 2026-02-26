import sqlite3
import hashlib
from contextlib import contextmanager

class DBManager:
    def __init__(self, database='users.db'):
        self.database = database
        self._initialize_db()
    
    def _initialize_db(self):
        """Create table if it doesn't exist"""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL,
                    best_score INTEGER DEFAULT 0
                )
            ''')
    
    @contextmanager
    def _get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.database)
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()
    
    def _hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username, password):
        try:
            with self._get_connection() as conn:
                conn.execute(
                    'INSERT INTO users (username, password_hash) VALUES (?, ?)',
                    (username, self._hash_password(password))
                )
            return True
        except sqlite3.IntegrityError:
            return False
    
    def authenticate_user(self, username, password):
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT password_hash FROM users WHERE username = ?',
                (username,)
            )
            row = cursor.fetchone()
        
        if row:
            return row[0] == self._hash_password(password)
        return False
    
    def update_score(self, username, score):
        with self._get_connection() as conn:
            conn.execute(
                'UPDATE users SET best_score = MAX(best_score, ?) WHERE username = ?',
                (score, username)
            )
    
    def get_leaderboard(self, limit=10):
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT username, best_score FROM users ORDER BY best_score DESC LIMIT ?',
                (limit,)
            )
            return cursor.fetchall()
    
    def get_user_info(self, username):
        with self._get_connection() as conn:
            cursor = conn.execute(
                'SELECT id, best_score FROM users WHERE username = ?',
                (username,)
            )
            return cursor.fetchone()