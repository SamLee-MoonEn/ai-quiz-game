import pyrebase
import firebase_admin
from firebase_admin import credentials, firestore
import streamlit as st
from typing import Dict, List, Optional
from config import FIREBASE_CONFIG, FIREBASE_SERVICE_ACCOUNT_KEY
import json
import os

class FirebaseService:
    def __init__(self):
        self.firebase = None
        self.auth = None
        self.db = None
        self.realtime_db = None
        self.init_firebase()
    
    def init_firebase(self):
        """Firebase 초기화"""
        try:
            # Firebase 설정이 유효한지 확인
            if not FIREBASE_CONFIG.get("apiKey") or FIREBASE_CONFIG["apiKey"] == "your_firebase_api_key":
                st.warning("Firebase 설정이 필요합니다. setup_guide.md를 참고하여 설정해주세요.")
                return
            
            # Pyrebase 초기화 (인증 및 실시간 DB용)
            self.firebase = pyrebase.initialize_app(FIREBASE_CONFIG)
            self.auth = self.firebase.auth()
            self.realtime_db = self.firebase.database()
            
            # Firebase Admin 초기화 시도 (Firestore용) - 선택사항
            try:
                if not firebase_admin._apps:
                    if FIREBASE_SERVICE_ACCOUNT_KEY and os.path.exists(FIREBASE_SERVICE_ACCOUNT_KEY):
                        # 서비스 계정 키 파일이 있는 경우
                        cred = credentials.Certificate(FIREBASE_SERVICE_ACCOUNT_KEY)
                        firebase_admin.initialize_app(cred)
                        self.db = firestore.client()
                        st.success("Firestore 연결 성공! 고급 기능을 사용할 수 있습니다.")
                    else:
                        # 서비스 계정 키가 없는 경우 - 실시간 DB 사용
                        st.info("Firestore 대신 실시간 데이터베이스를 사용합니다.")
                        self.db = None
            except Exception as e:
                st.warning(f"Firestore 초기화 실패: {str(e)}. 실시간 데이터베이스를 사용합니다.")
                self.db = None
            
        except Exception as e:
            st.error(f"Firebase 초기화 실패: {str(e)}")
    
    def register_user(self, email: str, password: str, username: str) -> Optional[Dict]:
        """사용자 회원가입"""
        try:
            if not self.auth:
                st.error("Firebase 인증이 초기화되지 않았습니다.")
                return None
                
            user = self.auth.create_user_with_email_and_password(email, password)
            
            # 사용자 정보를 데이터베이스에 저장
            user_data = {
                "uid": user['localId'],
                "email": email,
                "username": username,
                "total_score": 0,
                "quiz_count": 0,
                "created_at": "2023-01-01"  # 실시간 DB에서는 서버 타임스탬프 사용 불가
            }
            
            # Firestore 또는 실시간 DB에 저장
            if self.db:
                # Firestore 사용
                self.db.collection('users').document(user['localId']).set(user_data)
            elif self.realtime_db:
                # 실시간 DB 사용
                self.realtime_db.child('users').child(user['localId']).set(user_data)
            
            return user
        except Exception as e:
            st.error(f"회원가입 실패: {str(e)}")
            return None
    
    def login_user(self, email: str, password: str) -> Optional[Dict]:
        """사용자 로그인"""
        try:
            if not self.auth:
                st.error("Firebase 인증이 초기화되지 않았습니다.")
                return None
                
            user = self.auth.sign_in_with_email_and_password(email, password)
            return user
        except Exception as e:
            st.error(f"로그인 실패: {str(e)}")
            return None
    
    def get_user_data(self, uid: str) -> Optional[Dict]:
        """사용자 데이터 조회"""
        try:
            if self.db:
                # Firestore 사용
                doc = self.db.collection('users').document(uid).get()
                if doc.exists:
                    return doc.to_dict()
            elif self.realtime_db:
                # 실시간 DB 사용
                user_data = self.realtime_db.child('users').child(uid).get()
                if user_data.val():
                    return user_data.val()
            return None
        except Exception as e:
            st.error(f"사용자 데이터 조회 실패: {str(e)}")
            return None
    
    def save_quiz_result(self, uid: str, score: int, total_questions: int, difficulty: str) -> bool:
        """퀴즈 결과 저장"""
        try:
            if not (self.db or self.realtime_db):
                st.warning("데이터베이스 연결이 없습니다.")
                return False
                
            # 퀴즈 결과 데이터
            quiz_result = {
                "uid": uid,
                "score": score,
                "total_questions": total_questions,
                "difficulty": difficulty,
                "timestamp": "2023-01-01"  # 실제로는 현재 시간을 사용
            }
            
            if self.db:
                # Firestore 사용
                quiz_result["timestamp"] = firestore.SERVER_TIMESTAMP
                self.db.collection('quiz_results').add(quiz_result)
                
                # 사용자 총점 업데이트
                user_ref = self.db.collection('users').document(uid)
                user_data = user_ref.get().to_dict()
                
                if user_data:
                    new_total_score = user_data.get('total_score', 0) + score
                    new_quiz_count = user_data.get('quiz_count', 0) + 1
                    
                    user_ref.update({
                        'total_score': new_total_score,
                        'quiz_count': new_quiz_count
                    })
            elif self.realtime_db:
                # 실시간 DB 사용
                import time
                quiz_result["timestamp"] = int(time.time())
                
                # 퀴즈 결과 저장
                self.realtime_db.child('quiz_results').push(quiz_result)
                
                # 사용자 총점 업데이트
                user_data = self.realtime_db.child('users').child(uid).get().val()
                if user_data:
                    new_total_score = user_data.get('total_score', 0) + score
                    new_quiz_count = user_data.get('quiz_count', 0) + 1
                    
                    self.realtime_db.child('users').child(uid).update({
                        'total_score': new_total_score,
                        'quiz_count': new_quiz_count
                    })
            
            return True
        except Exception as e:
            st.error(f"퀴즈 결과 저장 실패: {str(e)}")
            return False
    
    def get_leaderboard(self, limit: int = 10) -> List[Dict]:
        """리더보드 조회"""
        try:
            if self.db:
                # Firestore 사용
                users = self.db.collection('users')\
                              .order_by('total_score', direction=firestore.Query.DESCENDING)\
                              .limit(limit)\
                              .stream()
                
                leaderboard = []
                for user in users:
                    user_data = user.to_dict()
                    leaderboard.append({
                        'username': user_data.get('username', 'Unknown'),
                        'total_score': user_data.get('total_score', 0),
                        'quiz_count': user_data.get('quiz_count', 0)
                    })
                
                return leaderboard
            elif self.realtime_db:
                # 실시간 DB 사용
                users = self.realtime_db.child('users').get()
                if users.val():
                    user_list = []
                    for uid, user_data in users.val().items():
                        user_list.append({
                            'username': user_data.get('username', 'Unknown'),
                            'total_score': user_data.get('total_score', 0),
                            'quiz_count': user_data.get('quiz_count', 0)
                        })
                    
                    # 점수순으로 정렬
                    user_list.sort(key=lambda x: x['total_score'], reverse=True)
                    return user_list[:limit]
            
            return []
        except Exception as e:
            st.error(f"리더보드 조회 실패: {str(e)}")
            return []
    
    def get_user_quiz_history(self, uid: str, limit: int = 10) -> List[Dict]:
        """사용자 퀴즈 기록 조회"""
        try:
            if self.db:
                # Firestore 사용
                results = self.db.collection('quiz_results')\
                               .where('uid', '==', uid)\
                               .order_by('timestamp', direction=firestore.Query.DESCENDING)\
                               .limit(limit)\
                               .stream()
                
                history = []
                for result in results:
                    history.append(result.to_dict())
                
                return history
            elif self.realtime_db:
                # 실시간 DB 사용
                results = self.realtime_db.child('quiz_results').get()
                if results.val():
                    user_results = []
                    for key, result in results.val().items():
                        if result.get('uid') == uid:
                            user_results.append(result)
                    
                    # 타임스탬프순으로 정렬
                    user_results.sort(key=lambda x: x.get('timestamp', 0), reverse=True)
                    return user_results[:limit]
            
            return []
        except Exception as e:
            st.error(f"퀴즈 기록 조회 실패: {str(e)}")
            return [] 