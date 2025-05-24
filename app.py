import streamlit as st
import pandas as pd
import plotly.express as px
from firebase_service import FirebaseService
from quiz_service import QuizService
from config import QUIZ_DIFFICULTY_LEVELS, QUESTIONS_PER_QUIZ, FIREBASE_CONFIG
import time

# 페이지 설정
st.set_page_config(
    page_title="AI 퀴즈 게임",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS 스타일링
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #FF6B6B;
        text-align: center;
        margin-bottom: 2rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .score-container {
        background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
        padding: 1rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin: 1rem 0;
    }
    .question-container {
        background: #f8f9fa;
        padding: 2rem;
        border-radius: 15px;
        border: 1px solid #dee2e6;
        margin: 1rem 0;
    }
    .option-button {
        width: 100%;
        padding: 0.5rem;
        margin: 0.25rem 0;
        border: none;
        border-radius: 5px;
        background: #e9ecef;
        color: #495057;
        cursor: pointer;
        transition: all 0.3s;
    }
    .option-button:hover {
        background: #4ECDC4;
        color: white;
    }
    .correct-answer {
        background: #28a745 !important;
        color: white !important;
    }
    .wrong-answer {
        background: #dc3545 !important;
        color: white !important;
    }
    .leaderboard-container {
        background: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    .demo-banner {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        text-align: center;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# 세션 상태 초기화
def init_session_state():
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'quiz_started' not in st.session_state:
        st.session_state.quiz_started = False
    if 'questions' not in st.session_state:
        st.session_state.questions = []
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'score' not in st.session_state:
        st.session_state.score = 0
    if 'quiz_finished' not in st.session_state:
        st.session_state.quiz_finished = False
    if 'user_answers' not in st.session_state:
        st.session_state.user_answers = []
    if 'show_result' not in st.session_state:
        st.session_state.show_result = False
    if 'demo_mode' not in st.session_state:
        st.session_state.demo_mode = False
    if 'demo_username' not in st.session_state:
        st.session_state.demo_username = ""

# Firebase 및 Quiz 서비스 초기화
@st.cache_resource
def get_services():
    firebase_service = FirebaseService()
    quiz_service = QuizService()
    return firebase_service, quiz_service

def check_firebase_config():
    """Firebase 설정 확인"""
    return (FIREBASE_CONFIG.get("apiKey") and 
            FIREBASE_CONFIG["apiKey"] != "your_firebase_api_key" and
            FIREBASE_CONFIG["apiKey"] != "")

def main():
    init_session_state()
    firebase_service, quiz_service = get_services()
    
    # Firebase 설정 확인
    firebase_available = check_firebase_config()
    
    # 헤더
    st.markdown('<h1 class="main-header">🧠 AI 퀴즈 게임</h1>', unsafe_allow_html=True)
    
    # Firebase 미설정 시 데모 모드 안내
    if not firebase_available:
        st.markdown('''
        <div class="demo-banner">
            <h3>🎯 데모 모드로 즐기기</h3>
            <p>Firebase 설정 없이도 퀴즈를 즐길 수 있습니다!<br>
            로그인 기능을 원하시면 setup_guide.md를 참고하여 Firebase를 설정해주세요.</p>
        </div>
        ''', unsafe_allow_html=True)
    
    # 사이드바
    with st.sidebar:
        st.title("🎯 게임 메뉴")
        
        if firebase_available and st.session_state.user:
            user_data = firebase_service.get_user_data(st.session_state.user['localId'])
            if user_data:
                st.success(f"안녕하세요, {user_data.get('username', 'User')}님!")
                st.info(f"총점: {user_data.get('total_score', 0)}점")
                st.info(f"퀴즈 횟수: {user_data.get('quiz_count', 0)}회")
            
            if st.button("로그아웃", type="secondary"):
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        elif st.session_state.demo_mode:
            st.success(f"안녕하세요, {st.session_state.demo_username}님!")
            st.info("🎯 데모 모드")
            
            if st.button("데모 종료", type="secondary"):
                st.session_state.demo_mode = False
                st.session_state.demo_username = ""
                for key in ['quiz_started', 'questions', 'current_question', 'score', 'quiz_finished', 'user_answers', 'show_result']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()
        
        # 페이지 선택
        if (firebase_available and st.session_state.user) or st.session_state.demo_mode:
            if firebase_available and st.session_state.user:
                page = st.selectbox(
                    "페이지 선택",
                    ["🎮 퀴즈 게임", "🏆 리더보드", "📊 내 기록"]
                )
            else:
                page = st.selectbox(
                    "페이지 선택",
                    ["🎮 퀴즈 게임", "📊 내 기록 (데모)"]
                )
        else:
            page = "🔐 로그인"
    
    # 메인 컨텐츠
    if not st.session_state.demo_mode and (not firebase_available or not st.session_state.user):
        show_auth_page(firebase_service, firebase_available)
    elif page == "🎮 퀴즈 게임":
        show_quiz_page(firebase_service, quiz_service)
    elif page == "🏆 리더보드":
        show_leaderboard_page(firebase_service)
    elif page == "📊 내 기록":
        show_user_history_page(firebase_service)
    elif page == "📊 내 기록 (데모)":
        show_demo_history_page()

def show_auth_page(firebase_service, firebase_available):
    st.title("🔐 로그인 / 회원가입")
    
    # 데모 모드 옵션
    st.markdown("---")
    st.subheader("🎯 즉시 시작하기")
    
    col1, col2 = st.columns(2)
    
    with col1:
        demo_username = st.text_input("사용자명 (데모용)", placeholder="닉네임을 입력하세요")
    
    with col2:
        if st.button("데모 모드로 시작", type="primary", use_container_width=True):
            if demo_username.strip():
                st.session_state.demo_mode = True
                st.session_state.demo_username = demo_username.strip()
                st.success("데모 모드로 시작합니다! 🎮")
                time.sleep(1)
                st.rerun()
            else:
                st.error("사용자명을 입력해주세요.")
    
    st.info("💡 데모 모드에서는 점수가 저장되지 않지만 모든 퀴즈 기능을 사용할 수 있습니다.")
    
    if firebase_available:
        st.markdown("---")
        
        tab1, tab2 = st.tabs(["로그인", "회원가입"])
        
        with tab1:
            st.subheader("로그인")
            email = st.text_input("이메일", key="login_email")
            password = st.text_input("비밀번호", type="password", key="login_password")
            
            if st.button("로그인", type="primary"):
                if email and password:
                    user = firebase_service.login_user(email, password)
                    if user:
                        st.session_state.user = user
                        st.success("로그인 성공!")
                        time.sleep(1)
                        st.rerun()
                else:
                    st.error("이메일과 비밀번호를 입력해주세요.")
        
        with tab2:
            st.subheader("회원가입")
            username = st.text_input("사용자명", key="register_username")
            email = st.text_input("이메일", key="register_email")
            password = st.text_input("비밀번호", type="password", key="register_password")
            password_confirm = st.text_input("비밀번호 확인", type="password", key="register_password_confirm")
            
            if st.button("회원가입", type="primary"):
                if not all([username, email, password, password_confirm]):
                    st.error("모든 필드를 입력해주세요.")
                elif password != password_confirm:
                    st.error("비밀번호가 일치하지 않습니다.")
                elif len(password) < 6:
                    st.error("비밀번호는 6자 이상이어야 합니다.")
                else:
                    user = firebase_service.register_user(email, password, username)
                    if user:
                        st.success("회원가입 성공! 로그인 탭에서 로그인해주세요.")
    else:
        st.markdown("---")
        st.info("🔧 Firebase를 설정하면 계정 생성 및 점수 저장 기능을 사용할 수 있습니다.")
        st.info("📖 setup_guide.md 파일을 참고하여 Firebase를 설정해보세요.")

def show_demo_history_page():
    st.title("📊 데모 모드 기록")
    
    # 세션에 저장된 데모 기록 표시
    if 'demo_history' not in st.session_state:
        st.session_state.demo_history = []
    
    if st.session_state.demo_history:
        st.subheader("📈 이번 세션 기록")
        
        total_quizzes = len(st.session_state.demo_history)
        total_score = sum(record['score'] for record in st.session_state.demo_history)
        avg_score = total_score / total_quizzes if total_quizzes > 0 else 0
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 퀴즈 수", total_quizzes)
        
        with col2:
            st.metric("총점", total_score)
        
        with col3:
            st.metric("평균 점수", f"{avg_score:.1f}")
        
        # 최근 기록
        st.subheader("최근 퀴즈 기록")
        for i, record in enumerate(reversed(st.session_state.demo_history)):
            score = record['score']
            total_questions = record['total_questions']
            difficulty = record['difficulty']
            accuracy = (score / (total_questions * 10)) * 100
            
            st.write(f"**{i+1}회차** - 점수: {score}점 | 정답률: {accuracy:.1f}% | 난이도: {difficulty}")
        
        if st.button("기록 초기화"):
            st.session_state.demo_history = []
            st.rerun()
            
    else:
        st.info("아직 퀴즈 기록이 없습니다. 첫 번째 퀴즈를 시작해보세요!")

def show_quiz_page(firebase_service, quiz_service):
    if not st.session_state.quiz_started:
        st.title("🎮 퀴즈 게임 시작")
        
        col1, col2 = st.columns(2)
        
        with col1:
            difficulty = st.selectbox("난이도 선택", QUIZ_DIFFICULTY_LEVELS)
        
        with col2:
            st.info(f"문제 수: {QUESTIONS_PER_QUIZ}문항\n점수: 문제당 10점")
        
        if st.button("퀴즈 시작!", type="primary", use_container_width=True):
            with st.spinner("AI가 문제를 생성중입니다..."):
                questions = quiz_service.generate_quiz_questions(difficulty)
                if questions:
                    st.session_state.questions = questions
                    st.session_state.quiz_started = True
                    st.session_state.current_question = 0
                    st.session_state.score = 0
                    st.session_state.quiz_finished = False
                    st.session_state.user_answers = []
                    st.session_state.difficulty = difficulty
                    st.session_state.show_result = False
                    st.rerun()
                else:
                    st.error("💥 문제 생성에 실패했습니다!")
                    st.warning("📋 다음 사항을 확인해주세요:")
                    st.write("• OpenAI API 키가 올바르게 설정되었는지 확인")
                    st.write("• 인터넷 연결 상태 확인")
                    st.write("• API 사용량 한도 확인")
                    st.info("🔄 위 사항을 확인한 후 '퀴즈 시작!' 버튼을 다시 눌러주세요.")
        
        # API 설정 안내
        if not quiz_service.api_available:
            st.markdown("---")
            st.subheader("🔑 OpenAI API 설정이 필요합니다")
            st.warning("현재 OpenAI API가 설정되지 않아 퀴즈를 플레이할 수 없습니다.")
            
            with st.expander("📖 API 키 설정 방법"):
                st.write("**1단계:** [OpenAI 플랫폼](https://platform.openai.com/)에 가입")
                st.write("**2단계:** API 키 생성")
                st.write("**3단계:** 프로젝트 루트에 `.env` 파일 생성")
                st.code("OPENAI_API_KEY=your_api_key_here")
                st.write("**4단계:** 앱 재시작")
                st.info("💡 자세한 설정 방법은 `setup_guide.md` 파일을 참고하세요.")
    
    elif st.session_state.quiz_started and not st.session_state.quiz_finished:
        show_quiz_question(firebase_service, quiz_service)
    
    elif st.session_state.quiz_finished:
        show_quiz_result(firebase_service, quiz_service)

def show_quiz_question(firebase_service, quiz_service):
    current_q = st.session_state.current_question
    question = st.session_state.questions[current_q]
    
    # 진행률 표시
    progress = (current_q + 1) / len(st.session_state.questions)
    st.progress(progress)
    st.write(f"문제 {current_q + 1} / {len(st.session_state.questions)}")
    
    # 현재 점수 표시
    st.markdown(f'''
    <div class="score-container">
        <h3>현재 점수: {st.session_state.score}점</h3>
    </div>
    ''', unsafe_allow_html=True)
    
    # 문제 표시
    st.markdown(f'''
    <div class="question-container">
        <h2>{question["question"]}</h2>
    </div>
    ''', unsafe_allow_html=True)
    
    # 답안 선택
    user_answer = st.radio(
        "답을 선택하세요:",
        range(len(question["options"])),
        format_func=lambda x: f"{chr(65+x)}. {question['options'][x]}",
        key=f"question_{current_q}"
    )
    
    if st.button("답안 제출", type="primary"):
        # 답안 기록
        is_correct = quiz_service.check_answer(user_answer, question["correct_answer"])
        st.session_state.user_answers.append({
            "question": question["question"],
            "user_answer": user_answer,
            "correct_answer": question["correct_answer"],
            "is_correct": is_correct,
            "explanation": question["explanation"]
        })
        
        # 점수 업데이트
        if is_correct:
            st.session_state.score += 10
        
        # 다음 문제로 이동 또는 퀴즈 종료
        if current_q + 1 < len(st.session_state.questions):
            st.session_state.current_question += 1
            st.session_state.show_result = True
        else:
            st.session_state.quiz_finished = True
            
            # 결과 저장
            if st.session_state.demo_mode:
                # 데모 모드: 세션에 저장
                if 'demo_history' not in st.session_state:
                    st.session_state.demo_history = []
                st.session_state.demo_history.append({
                    'score': st.session_state.score,
                    'total_questions': len(st.session_state.questions),
                    'difficulty': st.session_state.difficulty
                })
            elif st.session_state.user:
                # Firebase 사용자: 데이터베이스에 저장
                firebase_service.save_quiz_result(
                    st.session_state.user['localId'],
                    st.session_state.score,
                    len(st.session_state.questions),
                    st.session_state.difficulty
                )
        
        st.rerun()
    
    # 이전 문제 결과 표시
    if st.session_state.show_result and st.session_state.user_answers:
        last_answer = st.session_state.user_answers[-1]
        if last_answer["is_correct"]:
            st.success(f"정답입니다! 🎉")
        else:
            st.error(f"틀렸습니다. 😢")
            correct_option = chr(65 + last_answer["correct_answer"])
            st.info(f"정답: {correct_option}. {st.session_state.questions[current_q-1]['options'][last_answer['correct_answer']]}")
        
        st.info(f"설명: {last_answer['explanation']}")
        st.session_state.show_result = False

def show_quiz_result(firebase_service, quiz_service):
    st.title("🎉 퀴즈 완료!")
    
    total_questions = len(st.session_state.questions)
    correct_answers = sum(1 for answer in st.session_state.user_answers if answer["is_correct"])
    accuracy = (correct_answers / total_questions) * 100
    
    # 결과 요약
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("총점", f"{st.session_state.score}점")
    
    with col2:
        st.metric("정답률", f"{accuracy:.1f}%")
    
    with col3:
        st.metric("정답/총문제", f"{correct_answers}/{total_questions}")
    
    # 성과에 따른 메시지
    if accuracy >= 80:
        st.success("🌟 훌륭합니다! 상식 박사네요!")
    elif accuracy >= 60:
        st.info("👍 좋은 결과입니다!")
    else:
        st.warning("💪 더 공부해서 다시 도전해보세요!")
    
    # 상세 결과
    st.subheader("📋 상세 결과")
    
    for i, (question, answer) in enumerate(zip(st.session_state.questions, st.session_state.user_answers)):
        with st.expander(f"문제 {i+1}: {question['question'][:30]}..."):
            st.write(f"**문제:** {question['question']}")
            
            options_text = ""
            for j, option in enumerate(question['options']):
                if j == answer['correct_answer']:
                    options_text += f"**{chr(65+j)}. {option}** ✅\n"
                elif j == answer['user_answer']:
                    if answer['is_correct']:
                        options_text += f"**{chr(65+j)}. {option}** ✅\n"
                    else:
                        options_text += f"**{chr(65+j)}. {option}** ❌\n"
                else:
                    options_text += f"{chr(65+j)}. {option}\n"
            
            st.markdown(options_text)
            st.write(f"**설명:** {answer['explanation']}")
    
    # 새 퀴즈 시작
    if st.button("새 퀴즈 시작", type="primary"):
        st.session_state.quiz_started = False
        st.session_state.quiz_finished = False
        st.session_state.questions = []
        st.session_state.current_question = 0
        st.session_state.score = 0
        st.session_state.user_answers = []
        st.session_state.show_result = False
        st.rerun()

def show_leaderboard_page(firebase_service):
    st.title("🏆 리더보드")
    
    leaderboard = firebase_service.get_leaderboard(20)
    
    if leaderboard:
        # 차트 생성
        df = pd.DataFrame(leaderboard)
        
        # 상위 10명 바 차트
        top_10 = df.head(10)
        fig = px.bar(
            top_10, 
            x='username', 
            y='total_score',
            title="상위 10명 점수",
            labels={'username': '사용자명', 'total_score': '총점'},
            color='total_score',
            color_continuous_scale='viridis'
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
        
        # 리더보드 테이블
        st.subheader("📊 전체 순위")
        
        for i, user in enumerate(leaderboard):
            rank = i + 1
            
            if rank == 1:
                emoji = "🥇"
            elif rank == 2:
                emoji = "🥈"
            elif rank == 3:
                emoji = "🥉"
            else:
                emoji = f"{rank}위"
            
            col1, col2, col3, col4 = st.columns([1, 3, 2, 2])
            
            with col1:
                st.markdown(f"**{emoji}**")
            
            with col2:
                st.write(user['username'])
            
            with col3:
                st.write(f"{user['total_score']}점")
            
            with col4:
                st.write(f"{user['quiz_count']}회")
        
    else:
        st.info("아직 리더보드에 데이터가 없습니다. 첫 번째 퀴즈를 도전해보세요!")

def show_user_history_page(firebase_service):
    st.title("📊 내 퀴즈 기록")
    
    user_history = firebase_service.get_user_quiz_history(st.session_state.user['localId'], 20)
    
    if user_history:
        # 통계 요약
        df = pd.DataFrame(user_history)
        
        total_quizzes = len(df)
        total_score = df['score'].sum()
        avg_score = df['score'].mean()
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("총 퀴즈 수", total_quizzes)
        
        with col2:
            st.metric("총점", total_score)
        
        with col3:
            st.metric("평균 점수", f"{avg_score:.1f}")
        
        # 점수 변화 그래프
        fig = px.line(
            df.reset_index(), 
            x='index', 
            y='score',
            title="퀴즈별 점수 변화",
            labels={'index': '퀴즈 번호', 'score': '점수'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # 난이도별 통계
        if 'difficulty' in df.columns:
            difficulty_stats = df.groupby('difficulty')['score'].agg(['count', 'mean']).round(1)
            st.subheader("난이도별 통계")
            st.dataframe(difficulty_stats, use_container_width=True)
        
        # 최근 기록
        st.subheader("최근 퀴즈 기록")
        for record in user_history[:10]:
            score = record.get('score', 0)
            total_questions = record.get('total_questions', 5)
            difficulty = record.get('difficulty', '보통')
            
            accuracy = (score / (total_questions * 10)) * 100
            
            st.write(f"**점수:** {score}점 | **정답률:** {accuracy:.1f}% | **난이도:** {difficulty}")
    
    else:
        st.info("아직 퀴즈 기록이 없습니다. 첫 번째 퀴즈를 시작해보세요!")

if __name__ == "__main__":
    main() 