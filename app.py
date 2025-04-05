from flask import Flask, request, jsonify, render_template
from flask_socketio import SocketIO, emit, join_room, leave_room
from datetime import datetime
from openai import OpenAI
from pathlib import Path
from io import BytesIO
from dotenv import load_dotenv
import sqlite3, os, io, json
from functions import check_record, init_db, insert_msg, get_messages, get_history, get_applicants

load_dotenv()

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)


@app.route("/start_interview", methods=["POST"])
def start_interview():
    data = request.get_json()

    access_key = data.get("accessKey")
    name = data.get("name")
    email = data.get("email")
    prompt = data.get("prompt")

    variables = [access_key, name, email, prompt]

    for var in variables:
        if not var:
            return jsonify({"error": "incomplete params"}), 400

    result = check_record(access_key, name, email)
    if result != False:
        return result
    
    insert_msg(prompt, access_key, "system", name, email)

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "system", "content": prompt}],
    )

    msg = response.choices[0].message.content

    insert_msg(msg, access_key, "system", name, email)

    response_data = {
        "status": "Interview has started",
    }

    return jsonify(response_data), 200


@app.route("/get_messages/<access_key>/<name>/<email>", methods=["GET"])
def messages(access_key, name, email):
    return get_messages(access_key, name, email)


@app.route("/get_applicants/<access_key>", methods=["GET"])
def applicants(access_key):
    return get_applicants(access_key)


@app.route("/reply", methods=["POST"])
def get_messages():
    data = request.get_json()

    access_key = data.get("accessKey")
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    insert_msg(message, access_key, "user", name, email)

    messages = get_history(access_key, name, email)
    response = client.chat.completions.create(model="gpt-4o-mini", messages=messages)

    insert_msg(response, access_key, "system", name, email)

    return jsonify({"system": response}), 200

    

if __name__ == "__main__":
    # Initialize the database when the app starts
    init_db()
    socketio.run(app, debug=True)
