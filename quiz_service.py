import openai
import json
import random
from typing import Dict, List
import streamlit as st
from config import OPENAI_API_KEY, QUESTIONS_PER_QUIZ

class QuizService:
    def __init__(self):
        self.client = None
        self.api_available = False
        
        if OPENAI_API_KEY and OPENAI_API_KEY.strip() and OPENAI_API_KEY != "your_openai_api_key_here":
            try:
                self.client = openai.OpenAI(api_key=OPENAI_API_KEY)
                self.api_available = True
                st.success("🤖 OpenAI API 연결 성공! AI가 맞춤형 문제를 생성합니다.")
            except Exception as e:
                st.error(f"❌ OpenAI API 연결 실패: {str(e)}")
                st.warning("⚠️ API 키를 확인해주세요. API 키가 없으면 퀴즈를 플레이할 수 없습니다.")
                self.client = None
                self.api_available = False
        else:
            st.error("💡 OpenAI API 키가 필요합니다!")
            st.info("🔑 API 키를 설정하지 않으면 퀴즈를 플레이할 수 없습니다.")
            st.info("📖 setup_guide.md 파일을 참고하여 OpenAI API 키를 설정해주세요.")
            self.api_available = False
    
    def generate_quiz_questions(self, difficulty: str = "보통", num_questions: int = QUESTIONS_PER_QUIZ) -> List[Dict]:
        """
        OpenAI를 사용하여 퀴즈 문제 생성 (백업 문제 없음)
        """
        if not self.client or not self.api_available:
            st.error("❌ OpenAI API가 설정되지 않았습니다.")
            st.info("🔑 API 키를 설정해주세요. 백업 문제는 제공하지 않습니다.")
            return []
        
        # API 호출 전 사용자에게 알림
        with st.spinner("🤖 AI가 새로운 문제를 생성 중입니다..."):
            try:
                difficulty_prompts = {
                    "쉬움": "초등학생도 알 수 있는 매우 기본적인",
                    "보통": "중고등학생 수준의 일반적인",
                    "어려움": "대학생이나 성인이 알만한 고급"
                }
                
                difficulty_description = difficulty_prompts.get(difficulty, "일반적인")
                
                prompt = f"""
                {difficulty_description} 상식 문제 {num_questions}개를 생성해주세요.
                각 문제는 4지선다 형식이어야 하며, 다음 JSON 형식으로 반환해주세요:

                {{
                    "questions": [
                        {{
                            "question": "문제 내용",
                            "options": ["선택지1", "선택지2", "선택지3", "선택지4"],
                            "correct_answer": 0,
                            "explanation": "정답 설명"
                        }}
                    ]
                }}

                조건:
                - 한국어로 작성
                - correct_answer는 정답의 인덱스 (0-3)
                - 다양한 분야의 상식 문제 (역사, 과학, 지리, 문화, 스포츠 등)
                - 명확하고 정확한 정답이 있는 문제
                - 설명은 간단명료하게 작성
                - 정확히 {num_questions}개의 문제를 생성해주세요
                """
                
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "당신은 교육 전문가이며, 양질의 퀴즈 문제를 생성하는 전문가입니다. 요청된 개수만큼 정확히 문제를 생성해주세요."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.7,
                    max_tokens=2500
                )
                
                content = response.choices[0].message.content
                
                # JSON 파싱
                try:
                    quiz_data = json.loads(content)
                    questions = quiz_data.get("questions", [])
                    if questions and len(questions) >= num_questions:
                        st.success("✨ AI가 새로운 문제를 성공적으로 생성했습니다!")
                        return questions[:num_questions]
                    else:
                        st.error(f"❌ AI가 충분한 문제를 생성하지 못했습니다. (요청: {num_questions}개, 생성: {len(questions)}개)")
                        st.warning("⚠️ 다시 시도해주세요.")
                        return []
                except json.JSONDecodeError as e:
                    st.error(f"❌ AI 응답 해석 실패: {str(e)}")
                    st.warning("⚠️ AI 응답을 이해할 수 없습니다. 다시 시도해주세요.")
                    return []
                    
            except openai.AuthenticationError:
                st.error("❌ OpenAI API 인증 실패!")
                st.warning("🔑 API 키가 유효하지 않습니다. 설정을 확인해주세요.")
                self.api_available = False
                return []
            
            except openai.RateLimitError:
                st.error("❌ API 사용량 한도 초과!")
                st.warning("⏰ 잠시 후 다시 시도해주세요.")
                return []
            
            except openai.APIConnectionError:
                st.error("❌ OpenAI 서버 연결 실패!")
                st.warning("🌐 인터넷 연결을 확인하고 다시 시도해주세요.")
                return []
            
            except openai.APIError as e:
                st.error(f"❌ OpenAI API 오류: {str(e)}")
                st.warning("⚠️ API 서비스에 문제가 있습니다. 잠시 후 다시 시도해주세요.")
                return []
            
            except Exception as e:
                st.error(f"❌ 예상치 못한 오류 발생: {str(e)}")
                st.warning("⚠️ 시스템 오류가 발생했습니다. 다시 시도해주세요.")
                return []
    
    def check_answer(self, user_answer: int, correct_answer: int) -> bool:
        """
        답안 체크
        """
        return user_answer == correct_answer
    
    def calculate_score(self, correct_answers: int, total_questions: int) -> int:
        """
        점수 계산
        """
        from config import POINTS_PER_CORRECT_ANSWER
        return correct_answers * POINTS_PER_CORRECT_ANSWER 