import mysql.connector
import json
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(BASE_DIR, "config.json")

def load_config():
    if not os.path.exists(config_path):
        print(f"Error: {config_path} not found. Please create it from the template.")
        return None
    with open(config_path, "r") as f:
        return json.load(f)

def initialize_database():
    config_data = load_config()
    if not config_data or "mysql" not in config_data:
        print("Invalid configuration data in config.json.")
        return

    db_config = config_data["mysql"]
    
    # Connection details
    host = db_config.get("host", "localhost")
    port = db_config.get("port", 3306)
    user = db_config.get("user", "root")
    password = db_config.get("password", "")
    db_name = db_config.get("database", "resume_gap_analyzer")

    print(f"Connecting to MySQL server at {host}:{port} as user '{user}'...")
    
    try:
        # Connect to server without database to create the database if missing
        conn = mysql.connector.connect(
            host=host,
            port=port,
            user=user,
            password=password
        )
        cursor = conn.cursor()
        
        # Create database
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
        print(f"Database '{db_name}' ensured.")
        
        # Switch to database
        cursor.execute(f"USE {db_name}")
        
        # Table 1: users
        print("Creating table 'users'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            ) ENGINE=InnoDB;
        """)

        # Table 2: user_resumes
        print("Creating table 'user_resumes'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_resumes (
                user_id INT PRIMARY KEY,
                name VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                location VARCHAR(100),
                linkedin VARCHAR(150),
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
            ) ENGINE=InnoDB;
        """)

        # Table 3: user_projects
        print("Creating table 'user_projects'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_projects (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                title VARCHAR(150) NOT NULL,
                description TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
        """)

        # Table 4: analyses
        print("Creating table 'analyses'...")
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS analyses (
                id INT AUTO_INCREMENT PRIMARY KEY,
                user_id INT NOT NULL,
                job_role VARCHAR(100) NOT NULL,
                match_score FLOAT NOT NULL,
                matched_skills TEXT NOT NULL,
                missing_skills TEXT NOT NULL,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
            ) ENGINE=InnoDB;
        """)
        
        conn.commit()
        print("Database schema initialized successfully!")
        
    except mysql.connector.Error as err:
        print(f"MySQL Database Error: {err}")
    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()

if __name__ == "__main__":
    initialize_database()
