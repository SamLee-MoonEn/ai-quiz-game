import firebase_admin
from firebase_admin import credentials, firestore, auth
import streamlit as st
import json
import os

class FirebaseService:
    def __init__(self):
        self.initialize_firebase()
        self.db = firestore.client()

    def initialize_firebase(self):
        if not firebase_admin._apps:
            if os.path.exists('firebase-credentials.json'):
                cred = credentials.Certificate('firebase-credentials.json')
            else:
                # For Streamlit Cloud deployment
                firebase_credentials = st.secrets.get("FIREBASE_CREDENTIALS", None)
                if firebase_credentials:
                    if isinstance(firebase_credentials, str):
                        cred_dict = json.loads(firebase_credentials)
                    else:
                        cred_dict = firebase_credentials
                    cred = credentials.Certificate(cred_dict)
                else:
                    raise Exception("Firebase credentials not found")
            
            firebase_admin.initialize_app(cred)

    def create_user(self, email, password):
        try:
            user = auth.create_user(email=email, password=password)
            return user.uid
        except Exception as e:
            st.error(f"Error creating user: {str(e)}")
            return None

    def get_user_by_email(self, email):
        try:
            user = auth.get_user_by_email(email)
            return user.uid
        except Exception:
            return None

    def verify_user(self, email, password):
        try:
            user_id = self.get_user_by_email(email)
            if user_id:
                return user_id
            return None
        except Exception as e:
            st.error(f"Error verifying user: {str(e)}")
            return None

    def save_score(self, user_id, score, difficulty):
        try:
            # Add score to user's history
            score_ref = self.db.collection('scores').document()
            score_ref.set({
                'user_id': user_id,
                'score': score,
                'difficulty': difficulty,
                'timestamp': firestore.SERVER_TIMESTAMP
            })
            return True
        except Exception as e:
            st.error(f"Error saving score: {str(e)}")
            return False

    def get_leaderboard(self):
        try:
            scores = self.db.collection('scores').order_by('score', direction=firestore.Query.DESCENDING).limit(10).stream()
            return [score.to_dict() for score in scores]
        except Exception as e:
            st.error(f"Error getting leaderboard: {str(e)}")
            return []

    def get_user_scores(self, user_id):
        try:
            scores = self.db.collection('scores').where('user_id', '==', user_id).order_by('timestamp', direction=firestore.Query.DESCENDING).stream()
            return [score.to_dict() for score in scores]
        except Exception as e:
            st.error(f"Error getting user scores: {str(e)}")
            return [] 