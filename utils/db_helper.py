import os
import json
import sqlite3
import bcrypt
import random
import tempfile
from urllib.parse import urlparse, unquote

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Dynamic database driver imports
try:
    import psycopg2
    from psycopg2.extras import RealDictCursor
except ImportError:
    psycopg2 = None

try:
    import pymysql
    import pymysql.cursors
except ImportError:
    pymysql = None

try:
    import mysql.connector
except ImportError:
    mysql = None

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
config_path = os.path.join(BASE_DIR, "config.json")

_active_db_type = None  # 'postgres', 'mysql', 'sqlite'


def get_sqlite_db_path():
    """Returns a writable path for SQLite database, supporting Vercel, Docker, and Serverless environments."""
    if os.environ.get("VERCEL") or os.environ.get("AWS_LAMBDA_FUNCTION_NAME"):
        return os.path.join(tempfile.gettempdir(), "resume_analyzer.db")
    return os.path.join(BASE_DIR, "resume_analyzer.db")


def load_config():
    """Loads database config from config.json if available."""
    if not os.path.exists(config_path):
        return {}
    try:
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def get_db_type(conn):
    """Detects database engine type from a connection object."""
    if hasattr(conn, 'row_factory'):
        return 'sqlite'
    if psycopg2 and isinstance(conn, psycopg2.extensions.connection):
        return 'postgres'
    if 'psycopg' in str(type(conn)).lower():
        return 'postgres'
    return 'mysql'


def init_sqlite_db():
    """Initializes the SQLite schema."""
    db_path = get_sqlite_db_path()
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            is_verified INTEGER DEFAULT 1,
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


def init_postgres_db(conn):
    """Initializes PostgreSQL schema."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_verified INT DEFAULT 1,
            verification_code VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_resumes (
            user_id INT PRIMARY KEY,
            name VARCHAR(255),
            phone VARCHAR(50),
            email VARCHAR(255),
            location VARCHAR(255),
            linkedin VARCHAR(255),
            objective TEXT,
            education TEXT,
            languages TEXT,
            tools TEXT,
            concepts TEXT,
            achievements TEXT,
            activities TEXT,
            "database" TEXT,
            extra_curricular TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_projects (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id SERIAL PRIMARY KEY,
            user_id INT NOT NULL,
            job_role VARCHAR(255) NOT NULL,
            match_score DOUBLE PRECISION NOT NULL,
            matched_skills TEXT NOT NULL,
            missing_skills TEXT NOT NULL,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    cursor.close()


def init_mysql_db(conn):
    """Initializes MySQL schema."""
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(100) UNIQUE NOT NULL,
            email VARCHAR(255) UNIQUE NOT NULL,
            password_hash VARCHAR(255) NOT NULL,
            is_verified INT DEFAULT 1,
            verification_code VARCHAR(20),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_resumes (
            user_id INT PRIMARY KEY,
            name VARCHAR(255),
            phone VARCHAR(50),
            email VARCHAR(255),
            location VARCHAR(255),
            linkedin VARCHAR(255),
            objective TEXT,
            education TEXT,
            languages TEXT,
            tools TEXT,
            concepts TEXT,
            achievements TEXT,
            activities TEXT,
            `database` TEXT,
            extra_curricular TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_projects (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            title VARCHAR(255) NOT NULL,
            description TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS analyses (
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT NOT NULL,
            job_role VARCHAR(255) NOT NULL,
            match_score DOUBLE NOT NULL,
            matched_skills TEXT NOT NULL,
            missing_skills TEXT NOT NULL,
            analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    conn.commit()
    cursor.close()


def get_connection():
    """
    Universal database connection factory.
    Auto-detects and connects to PostgreSQL, MySQL, or SQLite based on:
    1. DATABASE_URL / POSTGRES_URL / MYSQL_URL environment variables
    2. DB_HOST, DB_USER, DB_PASSWORD, DB_NAME environment variables
    3. config.json
    4. SQLite fallback (in persistent path or /tmp on serverless)
    """
    global _active_db_type

    # 1. Check for Cloud Database Connection Strings (Render, Supabase, Neon, Railway, Heroku)
    db_url = os.environ.get("DATABASE_URL") or os.environ.get("POSTGRES_URL") or os.environ.get("POSTGRESQL_URL") or os.environ.get("MYSQL_URL")
    
    if db_url and db_url.strip():
        db_url_clean = db_url.strip()
        # Normalize postgres:// to postgresql://
        if db_url_clean.startswith("postgres://"):
            db_url_clean = "postgresql://" + db_url_clean[len("postgres://"):]
        
        parsed = urlparse(db_url_clean)
        scheme = parsed.scheme.lower()

        # Connect to PostgreSQL (Neon, Supabase, Render Postgres, etc.)
        if "postgres" in scheme:
            if psycopg2:
                try:
                    conn = psycopg2.connect(db_url_clean, cursor_factory=RealDictCursor)
                    conn.autocommit = False
                    _active_db_type = 'postgres'
                    return conn
                except Exception as e:
                    print(f"Warning: PostgreSQL connection failed ({e}). Checking alternatives...")

        # Connect to MySQL (TiDB, PlanetScale, Railway MySQL, etc.)
        elif "mysql" in scheme:
            host = parsed.hostname
            port = parsed.port or 3306
            user = parsed.username
            password = unquote(parsed.password or "")
            dbname = parsed.path.lstrip("/")
            
            if pymysql:
                try:
                    conn = pymysql.connect(
                        host=host, port=port, user=user, password=password, database=dbname,
                        cursorclass=pymysql.cursors.DictCursor, autocommit=False
                    )
                    _active_db_type = 'mysql'
                    return conn
                except Exception as e:
                    print(f"Warning: PyMySQL connection failed ({e}). Checking alternatives...")
            elif mysql and hasattr(mysql, 'connector'):
                try:
                    conn = mysql.connector.connect(
                        host=host, port=port, user=user, password=password, database=dbname
                    )
                    _active_db_type = 'mysql'
                    return conn
                except Exception as e:
                    print(f"Warning: MySQL.connector failed ({e}). Checking alternatives...")

    # 2. Check Individual Environment Variables (DB_HOST, DB_USER, etc.)
    db_host = os.environ.get("DB_HOST")
    if db_host and db_host != "localhost":
        db_user = os.environ.get("DB_USER", "root")
        db_password = os.environ.get("DB_PASSWORD", "")
        db_name = os.environ.get("DB_NAME", "resume_gap_analyzer")
        db_port = int(os.environ.get("DB_PORT", 5432 if os.environ.get("DB_TYPE") == "postgres" else 3306))
        db_type = os.environ.get("DB_TYPE", "postgres" if db_port == 5432 else "mysql").lower()

        if db_type == "postgres" and psycopg2:
            try:
                conn = psycopg2.connect(
                    host=db_host, port=db_port, user=db_user, password=db_password, dbname=db_name,
                    cursor_factory=RealDictCursor
                )
                _active_db_type = 'postgres'
                return conn
            except Exception as e:
                print(f"Warning: Postgres connection from env failed ({e}).")
        elif db_type == "mysql":
            if pymysql:
                try:
                    conn = pymysql.connect(
                        host=db_host, port=db_port, user=db_user, password=db_password, database=db_name,
                        cursorclass=pymysql.cursors.DictCursor
                    )
                    _active_db_type = 'mysql'
                    return conn
                except Exception as e:
                    print(f"Warning: PyMySQL connection from env failed ({e}).")
            elif mysql and hasattr(mysql, 'connector'):
                try:
                    conn = mysql.connector.connect(
                        host=db_host, port=db_port, user=db_user, password=db_password, database=db_name
                    )
                    _active_db_type = 'mysql'
                    return conn
                except Exception as e:
                    print(f"Warning: MySQL connection from env failed ({e}).")

    # 3. Check config.json (Local MySQL if configured)
    cfg = load_config().get("mysql", {})
    if cfg.get("host") and cfg.get("user"):
        if mysql and hasattr(mysql, 'connector'):
            try:
                conn = mysql.connector.connect(
                    host=cfg.get("host", "localhost"),
                    port=int(cfg.get("port", 3306)),
                    user=cfg.get("user", "root"),
                    password=cfg.get("password", ""),
                    database=cfg.get("database", "resume_gap_analyzer")
                )
                _active_db_type = 'mysql'
                return conn
            except Exception as e:
                print(f"Local MySQL connection notice: {e}")
        elif pymysql:
            try:
                conn = pymysql.connect(
                    host=cfg.get("host", "localhost"),
                    port=int(cfg.get("port", 3306)),
                    user=cfg.get("user", "root"),
                    password=cfg.get("password", ""),
                    database=cfg.get("database", "resume_gap_analyzer"),
                    cursorclass=pymysql.cursors.DictCursor
                )
                _active_db_type = 'mysql'
                return conn
            except Exception as e:
                print(f"Local PyMySQL connection notice: {e}")

    # 4. Universal Fallback to SQLite (Zero configuration needed)
    _active_db_type = 'sqlite'
    db_path = get_sqlite_db_path()
    if not os.path.exists(db_path):
        init_sqlite_db()
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def is_sqlite_conn(conn):
    return get_db_type(conn) == 'sqlite'


def execute_query(conn, cursor, query, params=()):
    """Executes a parameterized SQL query with automatic syntax adaptation for SQLite, MySQL, and PostgreSQL."""
    db_type = get_db_type(conn)
    if db_type == 'sqlite':
        query = query.replace("%s", "?")
    elif db_type == 'postgres':
        query = query.replace("`database`", '"database"').replace("`extra_curricular`", '"extra_curricular"')
    elif db_type == 'mysql':
        query = query.replace('"database"', "`database`").replace('"extra_curricular"', "`extra_curricular`")
    
    cursor.execute(query, params)


def fetch_one(cursor, is_sqlite=None):
    """Fetches a single row as a standardized dictionary."""
    row = cursor.fetchone()
    if row is None:
        return None
    if isinstance(row, dict):
        return row
    if hasattr(row, 'keys'):
        return dict(row)
    if cursor.description:
        col_names = [col[0] for col in cursor.description]
        return dict(zip(col_names, row))
    return row


def fetch_all(cursor, is_sqlite=None):
    """Fetches all rows as a standardized list of dictionaries."""
    rows = cursor.fetchall()
    if not rows:
        return []
    result = []
    for r in rows:
        if isinstance(r, dict):
            result.append(r)
        elif hasattr(r, 'keys'):
            result.append(dict(r))
        elif cursor.description:
            col_names = [col[0] for col in cursor.description]
            result.append(dict(zip(col_names, r)))
        else:
            result.append(r)
    return result


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
    db_type = get_db_type(conn)
    cursor = conn.cursor()
    try:
        hashed = hash_password(password)
        if db_type == 'postgres':
            query = "INSERT INTO users (username, email, password_hash, is_verified, verification_code) VALUES (%s, %s, %s, 1, NULL) RETURNING id"
            execute_query(conn, cursor, query, (username.strip(), email.strip().lower(), hashed))
            row = cursor.fetchone()
            user_id = row['id'] if isinstance(row, dict) else (row[0] if row else None)
        else:
            query = "INSERT INTO users (username, email, password_hash, is_verified, verification_code) VALUES (%s, %s, %s, 1, NULL)"
            execute_query(conn, cursor, query, (username.strip(), email.strip().lower(), hashed))
            user_id = cursor.lastrowid
        
        conn.commit()

        if not user_id:
            check_cursor = conn.cursor()
            execute_query(conn, check_cursor, "SELECT id FROM users WHERE username = %s", (username.strip(),))
            res_user = fetch_one(check_cursor)
            if res_user:
                user_id = res_user["id"]
            check_cursor.close()

        print(f"\n[SIGNUP] User '{username}' registered and activated successfully.\n")
        return {"user_id": user_id, "username": username, "email": email}
    except Exception as e:
        err_msg = str(e)
        if "UNIQUE" in err_msg or "Duplicate entry" in err_msg or "duplicate key" in err_msg or (hasattr(e, 'errno') and e.errno == 1062):
            raise Exception("Username or Email already registered.")
        else:
            raise e
    finally:
        cursor.close()
        conn.close()


def verify_user_otp(username_or_email, otp):
    conn = get_connection()
    is_sqlite = is_sqlite_conn(conn)
    cursor = conn.cursor()
    try:
        query = "SELECT id, username, verification_code, is_verified FROM users WHERE username = %s OR email = %s"
        execute_query(conn, cursor, query, (username_or_email.strip(), username_or_email.strip().lower()))
        user = fetch_one(cursor, is_sqlite)
        if not user:
            return {"success": False, "message": "User not found."}
        if user["is_verified"]:
            return {"success": True, "message": "Account already verified."}
        if user["verification_code"] == otp.strip():
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
    cursor = conn.cursor()
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
    cursor = conn.cursor()
    try:
        query = "SELECT id, username, email, password_hash, is_verified FROM users WHERE username = %s OR email = %s"
        execute_query(conn, cursor, query, (username.strip(), username.strip().lower()))
        user = fetch_one(cursor, is_sqlite)
        if user and verify_password(password, user["password_hash"]):
            if not user.get("is_verified", 1):
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
    """Initializes schema and runs necessary column migrations on startup."""
    conn = get_connection()
    db_type = get_db_type(conn)
    
    if db_type == 'sqlite':
        init_sqlite_db()
        conn.close()
        return
    elif db_type == 'postgres':
        init_postgres_db(conn)
        conn.close()
        print("PostgreSQL database initialized and schema up to date.")
        return
        
    cursor = conn.cursor()
    try:
        init_mysql_db(conn)
        conn.commit()
        print("MySQL database initialized and schema up to date.")
    except Exception as e:
        print(f"Migration check warning: {e}")
    finally:
        cursor.close()
        conn.close()


def save_resume(user_id, name, phone, email, location, linkedin, objective, education, languages, tools, concepts, achievements, activities, database, extra_curricular):
    conn = get_connection()
    is_sqlite = is_sqlite_conn(conn)
    cursor = conn.cursor()
    try:
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
    cursor = conn.cursor()
    try:
        query = "SELECT * FROM user_resumes WHERE user_id = %s"
        execute_query(conn, cursor, query, (user_id,))
        return fetch_one(cursor, is_sqlite)
    finally:
        cursor.close()
        conn.close()


def save_projects(user_id, projects):
    conn = get_connection()
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
    cursor = conn.cursor()
    try:
        query = "SELECT title, description FROM user_projects WHERE user_id = %s ORDER BY id ASC"
        execute_query(conn, cursor, query, (user_id,))
        rows = fetch_all(cursor, is_sqlite)
        return [{"title": row.get("title", ""), "desc": row.get("description", "")} for row in rows]
    finally:
        cursor.close()
        conn.close()


def log_analysis(user_id, job_role, match_score, matched_skills, missing_skills):
    conn = get_connection()
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
    cursor = conn.cursor()
    try:
        query = "SELECT job_role, match_score, matched_skills, missing_skills, analyzed_at FROM analyses WHERE user_id = %s ORDER BY analyzed_at DESC"
        execute_query(conn, cursor, query, (user_id,))
        return fetch_all(cursor, is_sqlite)
    finally:
        cursor.close()
        conn.close()
