from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import mysql.connector
from datetime import date
from emo_model import analyze_emotions

app = APIRouter()

class Diary(BaseModel):
    username: str
    diary_entry: str

class DiaryUpdate(BaseModel):
    diary_entry: str

def db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="unfiltered"
    )

@app.post("/diary")
def save_diary(data: Diary):

    detected_emotions = analyze_emotions(data.diary_entry)
    db = db_connection()
    cursor = db.cursor()

    diary_query = """
    INSERT INTO diary_entry (username, diary_entry)
    VALUES (%s, %s)
    """

    cursor.execute(
        diary_query,
        (data.username, data.diary_entry)
    )
    diary_id = cursor.lastrowid

    emotion_query = """
    INSERT INTO emotions (diary_id, emotion, score)
    VALUES (%s, %s, %s)
    """

    for result in detected_emotions:
        cursor.execute(
            emotion_query,
            (
                diary_id,
                result["emotion"],
                result["score"]
            )
        )

    db.commit()
    cursor.close()
    db.close()

    return {
        "message": "Diary entry saved and analysed successfully",
        "diary_id": diary_id,
        "username": data.username,
        "emotions": detected_emotions
    }

@app.get("/diary/{username}")
def get_diary(username: str):

    db = db_connection()
    cursor = db.cursor(dictionary=True)

    diary_query = """
    SELECT * FROM diary_entry
    WHERE username = %s
    ORDER BY created_at DESC
    """
    cursor.execute(diary_query, (username,))
    entries = cursor.fetchall()

    emotion_query = """
    SELECT emotion, score
    FROM emotions
    WHERE diary_id = %s
    ORDER BY score DESC
    """

    for entry in entries:
        cursor.execute(
            emotion_query,
            (entry["diary_id"],)
        )
        entry["emotions"] = cursor.fetchall()
    cursor.close()
    db.close()
    return entries

@app.put("/diary/{diary_id}")
def update_diary(diary_id: int, data: DiaryUpdate):

    detected_emotions = analyze_emotions(data.diary_entry)
    db = db_connection()
    cursor = db.cursor()

    diary_query = """
    UPDATE diary_entry
    SET diary_entry = %s
    WHERE diary_id = %s
    """

    cursor.execute(
        diary_query,
        (data.diary_entry, diary_id)
    )

    delete_emotions_query = """
    DELETE FROM emotions
    WHERE diary_id = %s
    """

    cursor.execute(
        delete_emotions_query,
        (diary_id,)
    )

    emotion_query = """
    INSERT INTO emotions (diary_id, emotion, score)
    VALUES (%s, %s, %s)
    """

    for result in detected_emotions:
        cursor.execute(
            emotion_query,
            (
                diary_id,
                result["emotion"],
                result["score"]
            )
        )
    db.commit()
    cursor.close()
    db.close()

    return {
        "message": "Diary entry updated and analysed successfully",
        "emotions": detected_emotions
    }

@app.delete("/diary/{diary_id}")
def delete_diary(diary_id: int):

    db = db_connection()
    cursor = db.cursor()

    query = """
    DELETE FROM diary_entry
    WHERE diary_id = %s
    """

    cursor.execute(query, (diary_id,))
    db.commit()
    cursor.close()
    db.close()

    return {
        "message": "Diary entry and its emotions deleted successfully"}


@app.get("/dashboard/{username}")
def create_dashboard(
    username: str,
    start_date: date,
    end_date: date
):

    if start_date > end_date:
        raise HTTPException(
            status_code=400,
            detail="Start date cannot be after end date")
    db = db_connection()
    cursor = db.cursor(dictionary=True)

    total_query = """
    SELECT COUNT(*) AS total_entries
    FROM diary_entry
    WHERE username = %s
    AND DATE(created_at) BETWEEN %s AND %s
    """
    cursor.execute(
        total_query,
        (username, start_date, end_date)
    )
    total_entries = cursor.fetchone()["total_entries"]

    emotion_query = """
    SELECT
        e.emotion,
        COUNT(*) AS occurrence_count,
        ROUND(AVG(e.score), 4) AS average_score
    FROM emotions e
    JOIN diary_entry d
    ON e.diary_id = d.diary_id
    WHERE d.username = %s
    AND DATE(d.created_at) BETWEEN %s AND %s
    GROUP BY e.emotion
    ORDER BY occurrence_count DESC, average_score DESC
    """

    cursor.execute(
        emotion_query,
        (username, start_date, end_date)
    )

    emotion_summary = cursor.fetchall()

    for emotion in emotion_summary:
        emotion["average_score"] = float(
            emotion["average_score"]
        )

    dominant_emotion = None

    if emotion_summary:
        dominant_emotion = emotion_summary[0]["emotion"]

    cursor.close()
    db.close()

    return {
        "username": username,
        "start_date": start_date,
        "end_date": end_date,
        "total_entries": total_entries,
        "dominant_emotion": dominant_emotion,
        "emotion_summary": emotion_summary}