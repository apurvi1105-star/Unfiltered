from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pwdlib import PasswordHash
import mysql.connector


app = APIRouter()

password_hash = PasswordHash.recommended()


class SignupData(BaseModel):
    full_name: str
    age: int
    gender: str
    email: str
    username: str
    password: str


def db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="unfiltered"
    )


@app.post("/signup")
def signup(data: SignupData):

    db = db_connection()
    cursor = db.cursor()

    try:

        hashed_password = password_hash.hash(data.password)

        query = """
        INSERT INTO users
        (username, full_name, age, gender, email, password)
        VALUES (%s, %s, %s, %s, %s, %s)
        """

        values = (
            data.username,
            data.full_name,
            data.age,
            data.gender,
            data.email,
            hashed_password
        )

        cursor.execute(query, values)
        db.commit()

        return {
            "success": True,
            "message": "Signup successful",
            "username": data.username
        }

    except mysql.connector.IntegrityError:

        db.rollback()

        raise HTTPException(
            status_code=400,
            detail="Username or email already exists"
        )

    finally:
        cursor.close()
        db.close()