from fastapi import APIRouter
import mysql.connector
import pandas as pd

app = APIRouter()

def db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="unfiltered"
    )
@app.get("/dashboard-data/{username}")
def get_dashboard_data(username: str):
    db = db_connection()
    cursor = db.cursor(dictionary=True)

    query = """
    SELECT
        e.diary_id,
        e.emotion,
        e.score
    FROM emotions e
    JOIN diary_entry d
    ON e.diary_id = d.diary_id
    WHERE d.username = %s
    ORDER BY d.created_at
    """

    cursor.execute(query, (username,))
    emotion_data = cursor.fetchall()

    cursor.close()
    db.close()

    if not emotion_data:
        return {"message": "No emotion data found"}

    df = pd.DataFrame(emotion_data)

    emotion_counts = df["emotion"].value_counts().to_dict()
    dominant_emotion = df["emotion"].mode()[0]
    total_entries = df["diary_id"].nunique()

    return {
        "username": username,
        "total_entries": total_entries,
        "dominant_emotion": dominant_emotion,
        "emotion_counts": emotion_counts
    }