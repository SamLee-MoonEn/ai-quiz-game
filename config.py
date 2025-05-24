import os
import json
from dotenv import load_dotenv
import streamlit as st

# Load environment variables
load_dotenv()

# OpenAI API Key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY") or st.secrets.get("OPENAI_API_KEY")

# Firebase Credentials
FIREBASE_CREDENTIALS = None
if os.getenv("FIREBASE_CREDENTIALS"):
    FIREBASE_CREDENTIALS = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
elif st.secrets.get("FIREBASE_CREDENTIALS"):
    FIREBASE_CREDENTIALS = json.loads(st.secrets.get("FIREBASE_CREDENTIALS"))

# Quiz Configuration
QUESTIONS_PER_QUIZ = 5
POINTS_PER_CORRECT_ANSWER = 10
QUIZ_DIFFICULTY_LEVELS = ["쉬움", "보통", "어려움"]

# Default backup questions in case API fails
BACKUP_QUESTIONS = [
    {
        "question": "대한민국의 수도는?",
        "options": ["서울", "부산", "인천", "대구"],
        "correct_answer": "서울",
        "difficulty": "쉬움"
    },
    {
        "question": "1 + 1 = ?",
        "options": ["1", "2", "3", "4"],
        "correct_answer": "2",
        "difficulty": "쉬움"
    }
]

# Firebase Configuration
FIREBASE_CONFIG = {
    "apiKey": os.getenv("FIREBASE_API_KEY") or st.secrets.get("FIREBASE_API_KEY"),
    "authDomain": os.getenv("FIREBASE_AUTH_DOMAIN") or st.secrets.get("FIREBASE_AUTH_DOMAIN"),
    "projectId": os.getenv("FIREBASE_PROJECT_ID") or st.secrets.get("FIREBASE_PROJECT_ID"),
    "storageBucket": os.getenv("FIREBASE_STORAGE_BUCKET") or st.secrets.get("FIREBASE_STORAGE_BUCKET"),
    "messagingSenderId": os.getenv("FIREBASE_MESSAGING_SENDER_ID") or st.secrets.get("FIREBASE_MESSAGING_SENDER_ID"),
    "appId": os.getenv("FIREBASE_APP_ID") or st.secrets.get("FIREBASE_APP_ID"),
    "databaseURL": os.getenv("FIREBASE_DATABASE_URL") or st.secrets.get("FIREBASE_DATABASE_URL")
}

# Firebase Service Account Key Path (for admin operations)
FIREBASE_SERVICE_ACCOUNT_KEY = os.getenv("FIREBASE_SERVICE_ACCOUNT_KEY", "") 