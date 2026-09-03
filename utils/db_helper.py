import mysql.connector
import sqlite3
import bcrypt
import json
import os
import random

import tempfile

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(BASE_DIR, "config.json")

_use_sqlite = False

def get_sqlite_db_path():
    """Returns a writable path for SQLite database, supporting Vercel and Serverless environments."""
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return os.path.join(tempfile.gettempdir(), "resume_analyzer.db")
    return os.path.join(BASE_DIR, "resume_analyzer.db")

def load_config():
    if not os.path.exists(config_path):
        return {
            "mysql": {
                "host": "localhost",
                "port": 3306,
                "user": "root",
                "password": "",
                "database": "resume_gap_analyzer"
            }
        }
    try:
        with open(config_path, "r") as f:
            return json.load(f)
    except Exception:
        return {"mysql": {}}

def init_sqlite_db():
    db_path = get_sqlite_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_verified INTEGER DEFAULT 0,
            verification_code TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_resumes (
            user_id INTEGER PRIMARY KEY,
            name TEXT,
            phone TEXT,
            email TEXT,
            location TEXT,
            linkedin TEXT,
            objective TEXT,
            education TEXT,
            languages TEXT,
            tools TEXT,
            concepts TEXT,
            achievements TEXT,
            activities TEXT,
            `database` TEXT,
            extra_curricular TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_projects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            title TEXT NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            job_role TEXT NOT NULL,
            match_score REAL NOT NULL,
            matched_skills TEXT NOT NULL,
            missing_skills TEXT NOT NULL,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    conn.close()
    print("SQLite database initialized successfully at", db_path)

def get_connection():
    global _use_sqlite
    
    # In Vercel or cloud serverless environments, automatically use SQLite in writable /tmp
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        _use_sqlite = True
        db_path = get_sqlite_db_path()
        if not os.path.exists(db_path):
            init_sqlite_db()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

    if _use_sqlite:
        db_path = get_sqlite_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn
    
    try:
        config = load_config().get("mysql", {})
        if not config.get("host") or config.get("host") == "localhost":
            # If no remote MySQL configured, fallback immediately
            raise Exception("No active remote MySQL configured")
            
        conn = mysql.connector.connect(
            host=config.get("host", "localhost"),
            port=config.get("port", 3306),
            user=config.get("user", "root"),
            password=config.get("password", ""),
            database=config.get("database", "resume_gap_analyzer")
        )
        return conn
    except Exception as e:
        _use_sqlite = True
        init_sqlite_db()
        db_path = get_sqlite_db_path()
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row
        return conn

def is_sqlite_conn(conn):
    return hasattr(conn, 'row_factory')

def execute_query(conn, cursor, query, params=()):
    if is_sqlite_conn(conn):
        # Translate MySQL parameter %s to SQLite ?
        query = query.replace("%s", "?")
    cursor.execute(query, params)

def fetch_one(cursor, is_sqlite):
    row = cursor.fetchone()
    if row is None:
        return None
    return dict(row) if is_sqlite else row

def fetch_all(cursor, is_sqlite):
    rows = cursor.fetchall()
    return [dict(row) for row in rows] if is_sqlite else rows

def hash_password(password):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(password, hashed):
    try:
        return bcrypt.checkpw(password.encode('utf-8'), hashed.encode('utf-8'))
    except Exception:
        return False

def generate_otp():
    return "".join(random.choices("0123456789", k=6))

def register_user(username, email, password):
    conn = get_connection()
    is_sqlite = is_sqlite_conn(conn)
    cursor = conn.cursor()
    try:
        hashed = hash_password(password)
        query = "INSERT INTO users (username, email, password_hash, is_verified, verification_code) VALUES (%s, %s, %s, 1, NULL)"
        execute_query(conn, cursor, query, (username.strip(), email.strip().lower(), hashed))
        conn.commit()
        user_id = cursor.lastrowid
        print(f"\n[SIGNUP] User '{username}' registered and activated successfully.\n")
        return {"user_id": user_id, "username": username, "email": email}
    except Exception as e:
        err_msg = str(e)
        if "UNIQUE" in err_msg or "Duplicate entry" in err_msg or (hasattr(e, 'errno') and e.errno == 1062):
            raise Exception("Username or Email already registered.")
        else:
            raise e
    finally:
        cursor.close()
        conn.close()

def verify_user_otp(username_or_email, otp):
    conn = get_connection()
    is_sqlite = is_sqlite_conn(conn)
    cursor = conn.cursor(dictionary=not is_sqlite)
    try:
        query = "SELECT id, username, verification_code, is_verified FROM users WHERE username = %s OR email = %s"
        execute_query(conn, cursor, query, (username_or_email.strip(), username_or_email.strip().lower()))
        user = fetch_one(cursor, is_sqlite)
        if not user:
            return {"success": False, "message": "User not found."}
        if user["is_verified"]:
            return {"success": True, "message": "Account already verified."}
        if user["verification_code"] == otp.strip():
            # Update user status to verified
            update_query = "UPDATE users SET is_verified = 1, verification_code = NULL WHERE id = %s"
            update_cursor = conn.cursor()
            execute_query(conn, update_cursor, update_query, (user["id"],))
            conn.commit()
            update_cursor.close()
            return {"success": True, "message": "Account verified successfully!"}
        return {"success": False, "message": "Invalid verification code."}
    finally:
        cursor.close()
        conn.close()

def generate_and_update_otp(username_or_email):
    conn = get_connection()
    is_sqlite = is_sqlite_conn(conn)
    cursor = conn.cursor(dictionary=not is_sqlite)
    try:
        query = "SELECT id, username, email, is_verified FROM users WHERE username = %s OR email = %s"
        execute_query(conn, cursor, query, (username_or_email.strip(), username_or_email.strip().lower()))
        user = fetch_one(cursor, is_sqlite)
        if not user:
            return {"success": False, "message": "User not found."}
        if user["is_verified"]:
            return {"success": True, "message": "Account already verified."}
        
        otp = generate_otp()
        update_query = "UPDATE users SET verification_code = %s WHERE id = %s"
        update_cursor = conn.cursor()
        execute_query(conn, update_cursor, update_query, (otp, user["id"]))
        conn.commit()
        update_cursor.close()
        return {
            "success": True, 
            "user_id": user["id"], 
            "username": user["username"], 
            "email": user["email"], 
            "otp": otp
        }
    finally:
        cursor.close()
        conn.close()

def authenticate_user(username, password):
    conn = get_connection()
    is_sqlite = is_sqlite_conn(conn)
    cursor = conn.cursor(dictionary=not is_sqlite)
    try:
        query = "SELECT id, username, email, password_hash, is_verified FROM users WHERE username = %s OR email = %s"
        execute_query(conn, cursor, query, (username.strip(), username.strip().lower()))
        user = fetch_one(cursor, is_sqlite)
        if user and verify_password(password, user["password_hash"]):
            if not user["is_verified"]:
                raise Exception("Account is not verified yet. Please verify your account.")
            return {
                "id": user["id"],
                "username": user["username"],
                "email": user["email"]
            }
        return None
    finally:
        cursor.close()
        conn.close()

def run_migrations():
    conn = get_connection()
    if is_sqlite_conn(conn):
        conn.close()
        return
        
    cursor = conn.cursor()
    try:
        # Check if column `is_verified` exists in `users`
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'users' 
              AND COLUMN_NAME = 'is_verified'
        """)
        if not cursor.fetchone():
            print("Migration: Adding `is_verified` column to `users`...")
            cursor.execute("ALTER TABLE users ADD COLUMN `is_verified` TINYINT DEFAULT 0;")
            
        # Check if column `verification_code` exists in `users`
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'users' 
              AND COLUMN_NAME = 'verification_code'
        """)
        if not cursor.fetchone():
            print("Migration: Adding `verification_code` column to `users`...")
            cursor.execute("ALTER TABLE users ADD COLUMN `verification_code` VARCHAR(6) NULL;")

        # Check if column `database` exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'user_resumes' 
              AND COLUMN_NAME = 'database'
        """)
        if not cursor.fetchone():
            print("Migration: Adding `database` column to `user_resumes`...")
            cursor.execute("ALTER TABLE user_resumes ADD COLUMN `database` TEXT;")
            
        # Check if column `extra_curricular` exists
        cursor.execute("""
            SELECT COLUMN_NAME 
            FROM INFORMATION_SCHEMA.COLUMNS 
            WHERE TABLE_SCHEMA = DATABASE() 
              AND TABLE_NAME = 'user_resumes' 
              AND COLUMN_NAME = 'extra_curricular'
        """)
        if not cursor.fetchone():
            print("Migration: Adding `extra_curricular` column to `user_resumes`...")
            cursor.execute("ALTER TABLE user_resumes ADD COLUMN `extra_curricular` TEXT;")
        
        conn.commit()
        print("Migration: Check complete. Schema up to date.")
    except Exception as e:
        print(f"Migration: Error while running migrations: {e}")
    finally:
        cursor.close()
        conn.close()

def save_resume(user_id, name, phone, email, location, linkedin, objective, education, languages, tools, concepts, achievements, activities, database, extra_curricular):
    conn = get_connection()
    is_sqlite = is_sqlite_conn(conn)
    cursor = conn.cursor(dictionary=not is_sqlite)
    try:
        # Check if exists
        check_query = "SELECT 1 FROM user_resumes WHERE user_id = %s"
        execute_query(conn, cursor, check_query, (user_id,))
        exists = fetch_one(cursor, is_sqlite)
        
        if exists:
            query = """
                UPDATE user_resumes SET
                    name = %s, phone = %s, email = %s, location = %s, linkedin = %s,
                    objective = %s, education = %s, languages = %s, tools = %s, concepts = %s,
                    achievements = %s, activities = %s, `database` = %s, extra_curricular = %s
                WHERE user_id = %s
            """
            params = (name, phone, email, location, linkedin, objective, education, languages, tools, concepts, achievements, activities, database, extra_curricular, user_id)
        else:
            query = """
                INSERT INTO user_resumes (
                    user_id, name, phone, email, location, linkedin, objective, education, languages, tools, concepts, achievements, activities, `database`, extra_curricular
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """
            params = (user_id, name, phone, email, location, linkedin, objective, education, languages, tools, concepts, achievements, activities, database, extra_curricular)
        
        write_cursor = conn.cursor()
        execute_query(conn, write_cursor, query, params)
        conn.commit()
        write_cursor.close()
    finally:
        cursor.close()
        conn.close()

def load_resume(user_id):
    conn = get_connection()
    is_sqlite = is_sqlite_conn(conn)
    cursor = conn.cursor(dictionary=not is_sqlite)
    try:
        query = "SELECT * FROM user_resumes WHERE user_id = %s"
        execute_query(conn, cursor, query, (user_id,))
        return fetch_one(cursor, is_sqlite)
    finally:
        cursor.close()
        conn.close()

def save_projects(user_id, projects):
    conn = get_connection()
    is_sqlite = is_sqlite_conn(conn)
    cursor = conn.cursor()
    try:
        delete_query = "DELETE FROM user_projects WHERE user_id = %s"
        execute_query(conn, cursor, delete_query, (user_id,))
        for proj in projects:
            title = proj.get("title", "").strip()
            desc = proj.get("desc", "").strip()
            if title or desc:
                insert_query = "INSERT INTO user_projects (user_id, title, description) VALUES (%s, %s, %s)"
                execute_query(conn, cursor, insert_query, (user_id, title, desc))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def load_projects(user_id):
    conn = get_connection()
    is_sqlite = is_sqlite_conn(conn)
    cursor = conn.cursor(dictionary=not is_sqlite)
    try:
        query = "SELECT title, description FROM user_projects WHERE user_id = %s ORDER BY id ASC"
        execute_query(conn, cursor, query, (user_id,))
        rows = fetch_all(cursor, is_sqlite)
        return [{"title": row["title"], "desc": row["description"]} for row in rows]
    finally:
        cursor.close()
        conn.close()

def log_analysis(user_id, job_role, match_score, matched_skills, missing_skills):
    conn = get_connection()
    is_sqlite = is_sqlite_conn(conn)
    cursor = conn.cursor()
    try:
        query = "INSERT INTO analyses (user_id, job_role, match_score, matched_skills, missing_skills) VALUES (%s, %s, %s, %s, %s)"
        execute_query(conn, cursor, query, (user_id, job_role, match_score, ", ".join(matched_skills), ", ".join(missing_skills)))
        conn.commit()
    finally:
        cursor.close()
        conn.close()

def load_analysis_history(user_id):
    conn = get_connection()
    is_sqlite = is_sqlite_conn(conn)
    cursor = conn.cursor(dictionary=not is_sqlite)
    try:
        query = "SELECT job_role, match_score, matched_skills, missing_skills, analyzed_at FROM analyses WHERE user_id = %s ORDER BY analyzed_at DESC"
        execute_query(conn, cursor, query, (user_id,))
        return fetch_all(cursor, is_sqlite)
    finally:
        cursor.close()
        conn.close()
