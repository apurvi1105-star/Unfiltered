import os
from dotenv import load_dotenv
from groq import Groq
import mysql.connector
from fastapi import APIRouter

load_dotenv()
app = APIRouter()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY"))

def get_suggestion(emotion):
    prompt = """
    The user's current emotion is: {emotion}
    Give a brief, detailed practical and supportive suggestion
    that can help the user feel better.
    Keep the suggestion simple and friendly.
    Do not give medical diagnosis.
    """
    response = client.chat.completions.create(
        model="openai/gpt-oss-20b",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )
    return response.choices[0].message.content

def get_latest_emotion(username):
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="unfiltered")
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT e.emotion
    FROM emotions e
    JOIN diary_entry d
    ON e.diary_id = d.diary_id
    WHERE d.username = %s
    ORDER BY d.created_at DESC
    LIMIT 1
    """
    cursor.execute(query, (username,))
    data = cursor.fetchone()
    cursor.close()
    db.close()

    if data:
        return data["emotion"]

    return None

@app.get("/suggestion/{username}")
def suggestion(username: str):
    emotion = get_latest_emotion(username)

    if not emotion:
        return {
            "message": "No emotion found"}

    suggestion_text = get_suggestion(emotion)

    return {
        "emotion": emotion,
        "suggestion": suggestion_text}