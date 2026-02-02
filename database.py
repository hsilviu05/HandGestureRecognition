import sqlite3
import hashlib

class Database:
    def __init__(self, db_name="signlearn.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password_hash TEXT,
                best_score INTEGER DEFAULT 0
            )
        ''')
        self.conn.commit()

    def _hash_password(self, password):
        """Transformă parola în hash SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username, password):
        try:
            hashed = self._hash_password(password)
            self.cursor.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", 
                                (username, hashed))
            self.conn.commit()
            return True
        except sqlite3.IntegrityError:
            return False

    def login_user(self, username, password):
        hashed = self._hash_password(password)
        self.cursor.execute("SELECT * FROM users WHERE username = ? AND password_hash = ?", 
                            (username, hashed))
        return self.cursor.fetchone()

    def update_best_score(self, username, score):
        self.cursor.execute("UPDATE users SET best_score = ? WHERE username = ? AND best_score < ?", 
                            (score, username, score))
        self.conn.commit()