from fastapi import APIRouter
from pydantic import BaseModel
from pwdlib import PasswordHash
import mysql.connector
import hmac

app = APIRouter()
password_hash = PasswordHash.recommended()

class LoginData(BaseModel):
    username: str
    password: str

def db_connection():
    return mysql.connector.connect(
        host="localhost",
        user="root",
        password="root",
        database="unfiltered"
    )

@app.post("/login")
def login(data: LoginData):

    db = db_connection()
    cursor = db.cursor()

    try:

        query = """
        SELECT password
        FROM users
        WHERE username = %s
        """

        cursor.execute(query, (data.username,))
        user = cursor.fetchone()

        if not user:
            return {
                "success": False,
                "message": "Invalid username or password"
            }

        stored_password = user[0]
        password_correct = False

        if stored_password.startswith("$argon2"):

            try:
                password_correct = password_hash.verify(
                    data.password,
                    stored_password
                )

            except Exception:
                password_correct = False

        else:

            password_correct = hmac.compare_digest(
                data.password,
                stored_password
            )

            if password_correct:

                new_hash = password_hash.hash(data.password)

                update_query = """
                UPDATE users
                SET password = %s
                WHERE username = %s
                """

                cursor.execute(
                    update_query,
                    (new_hash, data.username)
                )

                db.commit()

        if password_correct:

            return {
                "success": True,
                "message": "Login successful",
                "username": data.username
            }

        return {
            "success": False,
            "message": "Invalid username or password"
        }

    finally:
        cursor.close()
        db.close()