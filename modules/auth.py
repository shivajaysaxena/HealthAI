import sqlite3
import hashlib
import os
from datetime import datetime

class AuthSystem:
    def __init__(self, db_path="users.db"):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize the user database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Medical history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS medical_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                transcript TEXT,
                translation TEXT,
                analysis TEXT,
                language_code TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def hash_password(self, password):
        """Hash password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def signup(self, username, email, password):
        """Register a new user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password_hash) VALUES (?, ?, ?)",
                (username, email, password_hash)
            )
            
            conn.commit()
            conn.close()
            return True, "Account created successfully!"
        except sqlite3.IntegrityError:
            return False, "Username or email already exists"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def login(self, username, password):
        """Authenticate user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            password_hash = self.hash_password(password)
            cursor.execute(
                "SELECT id, username, email FROM users WHERE username = ? AND password_hash = ?",
                (username, password_hash)
            )
            
            user = cursor.fetchone()
            conn.close()
            
            if user:
                return True, {
                    "id": user[0],
                    "username": user[1],
                    "email": user[2]
                }
            else:
                return False, "Invalid username or password"
        except Exception as e:
            return False, f"Error: {str(e)}"
    
    def save_medical_record(self, user_id, transcript, translation, analysis, language_code):
        """Save medical consultation to history"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """INSERT INTO medical_history 
                   (user_id, transcript, translation, analysis, language_code) 
                   VALUES (?, ?, ?, ?, ?)""",
                (user_id, transcript, translation, analysis, language_code)
            )
            
            conn.commit()
            conn.close()
            return True
        except Exception as e:
            print(f"Error saving record: {e}")
            return False
    
    def get_user_history(self, user_id):
        """Get medical history for a user"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute(
                """SELECT id, transcript, translation, analysis, language_code, created_at 
                   FROM medical_history 
                   WHERE user_id = ? 
                   ORDER BY created_at DESC""",
                (user_id,)
            )
            
            records = cursor.fetchall()
            conn.close()
            
            return records
        except Exception as e:
            print(f"Error fetching history: {e}")
            return []