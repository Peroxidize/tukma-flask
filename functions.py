from flask import jsonify
from datetime import datetime
import sqlite3

DATABASE = "messages.db"

# Function to initialize the database
def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content TEXT NOT NULL,
                date_created TIMESTAMP NOT NULL,
                role TEXT NOT NULL,
                access_key TEXT NOT NULL
                name TEXT NOT NULL
                email TEXT NOT NULL
            )
        """
        )
        conn.commit()


def insert_msg(content, access_key, role, name, email):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO messages (content, date_created, role, access_key, name, email)
            VALUES (?, ?, ?, ?)
        """,
            (content, datetime.now(), role, access_key, name, email),
        )
        conn.commit()

        
def check_record(access_key, name, email):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        cursor.execute("""
            SELECT id FROM interview_status 
            WHERE access_key = ? AND email = ? AND name = ?
        """, (access_key, email, name))
        existing_record = cursor.fetchone()

        if existing_record:
            return jsonify({"message": "access key already exists"}), 400
        return False


def get_messages(access_key, name, email):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()

        # Verify the access key exists
        cursor.execute("""
            SELECT id FROM interview_status 
            WHERE access_key = ? AND email = ? AND name = ?
        """, (access_key, email, name))
        message_count = cursor.fetchone()[0]

        if message_count == 0:
            return (
                jsonify(
                    {
                        "status": "error",
                        "message": "No messages found for this access key",
                    }
                ),
                404,
            )

        # Retrieve all messages
        cursor.execute(
            """
            SELECT id, content, date_created, role 
            FROM messages 
            WHERE access_key = ? AND email = ? AND name = ? 
            ORDER BY date_created ASC
            """,
            (access_key, email, name),
        )

        # Format the response
        messages = [
            {
                "id": row[0],
                "content": row[1],
                "timestamp": row[2],
                "role": row[3],  # 'user' or 'assistant' typically
            }
            for row in cursor.fetchall()
        ]

        return jsonify(
            {
                "status": "success",
                "access_key": access_key,
                "message_count": message_count,
                "messages": messages,
            }, 200
        )

        
def get_history(access_key, name, email):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT role, content
            FROM messages 
            WHERE access_key = ? AND email = ? AND name = ? 
            ORDER BY date_created ASC
            """,
            (access_key, email, name),
        )

    messages = cursor.fetchall()

    return messages

    
def get_applicants(access_key):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(
            """
            SELECT DISTINCT name, email
            FROM messages 
            WHERE access_key = ? 
            ORDER BY date_created ASC
            """,
            (access_key,),
        )

    applicants = cursor.fetchall()

    return jsonify({"status:": "success", "applicants": applicants}, 200)