# 🧠 AI 퀴즈 게임

OpenAI API와 Firebase를 활용한 실시간 상식 퀴즈 게임입니다. AI가 자동으로 생성하는 다양한 난이도의 문제를 풀고, 다른 사용자들과 점수를 경쟁해보세요!

## ✨ 주요 기능

- 🤖 **AI 문제 생성**: OpenAI GPT를 활용한 실시간 상식 문제 생성
- 👤 **사용자 인증**: Firebase Authentication을 통한 안전한 로그인/회원가입
- 📊 **점수 시스템**: 퀴즈 결과를 자동으로 계산하고 저장
- 🏆 **리더보드**: 다른 사용자들과 점수 경쟁
- 📈 **개인 통계**: 개인별 퀴즈 기록 및 성과 분석
- 🎯 **다양한 난이도**: 쉬움, 보통, 어려움 3단계 난이도
- 💻 **반응형 웹 UI**: 모던한 Streamlit 인터페이스

## 🚀 빠른 시작

### 1. 자동 설치

```bash
# 저장소 클론
git clone [repository-url]
cd ai-quiz-game

# 자동 설치 스크립트 실행
python install_requirements.py
```

### 2. 수동 설치

```bash
# 필요한 패키지 설치
pip install -r requirements.txt
```

### 3. 환경 설정

`.env` 파일을 생성하고 다음 정보를 입력하세요:

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# Firebase Config
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your_project-default-rtdb.firebaseio.com/
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
```

### 4. 앱 실행

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하세요.

## 🔧 필요한 서비스 설정

### OpenAI API 설정

1. [OpenAI 플랫폼](https://platform.openai.com/)에 가입
2. API 키 생성
3. `.env` 파일의 `OPENAI_API_KEY`에 입력

### Firebase 설정

1. [Firebase Console](https://console.firebase.google.com/)에서 새 프로젝트 생성
2. Authentication 활성화 (이메일/비밀번호 로그인)
3. Firestore Database 생성
4. 프로젝트 설정에서 웹 앱 구성 정보 복사
5. `.env` 파일에 Firebase 설정 정보 입력

### Firestore 보안 규칙 설정

Firestore Database에서 다음 보안 규칙을 설정하세요:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 사용자 데이터
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // 퀴즈 결과
    match /quiz_results/{document} {
      allow read, write: if request.auth != null && request.auth.uid == resource.data.uid;
      allow create: if request.auth != null && request.auth.uid == request.resource.data.uid;
    }
    
    // 리더보드 읽기 허용
    match /users/{document} {
      allow read: if request.auth != null;
    }
  }
}
```

## 📁 프로젝트 구조

```
ai-quiz-game/
├── app.py                 # 메인 Streamlit 앱
├── config.py             # 설정 파일
├── firebase_service.py   # Firebase 서비스 클래스
├── quiz_service.py       # 퀴즈 생성 서비스 클래스
├── install_requirements.py # 자동 설치 스크립트
├── requirements.txt      # 필요한 패키지 목록
├── .env                 # 환경변수 (직접 생성)
└── README.md            # 프로젝트 설명서
```

## 🎮 사용 방법

### 1. 회원가입/로그인
- 이메일과 비밀번호로 계정 생성
- 사용자명 설정

### 2. 퀴즈 게임
- 난이도 선택 (쉬움/보통/어려움)
- AI가 생성한 5문제 도전
- 실시간 점수 확인

### 3. 리더보드
- 전체 사용자 순위 확인
- 상위 10명 차트 보기

### 4. 개인 기록
- 개인 퀴즈 기록 조회
- 성과 통계 분석
- 난이도별 성과 확인

## 🔒 보안 기능

- Firebase Authentication을 통한 안전한 사용자 인증
- Firestore 보안 규칙을 통한 데이터 접근 제어
- 환경변수를 통한 API 키 보안 관리

## 🛠️ 기술 스택

- **Frontend**: Streamlit
- **Backend**: Python
- **AI**: OpenAI GPT-3.5 Turbo
- **Authentication**: Firebase Auth
- **Database**: Firebase Firestore
- **Data Visualization**: Plotly
- **Data Processing**: Pandas

## 📊 주요 패키지

- `streamlit`: 웹 앱 프레임워크
- `openai`: OpenAI API 클라이언트
- `firebase-admin`: Firebase Admin SDK
- `pyrebase4`: Firebase 클라이언트 SDK
- `pandas`: 데이터 분석
- `plotly`: 데이터 시각화

## 🐛 문제 해결

### 일반적인 문제들

1. **Firebase 연결 오류**
   - `.env` 파일의 Firebase 설정 확인
   - Firebase 프로젝트 활성화 상태 확인

2. **OpenAI API 오류**
   - API 키 유효성 확인
   - 계정 크레딧 잔액 확인

3. **패키지 설치 오류**
   - Python 버전 확인 (3.8 이상 권장)
   - 가상환경 사용 권장

### 백업 문제 기능

OpenAI API가 작동하지 않을 경우, 미리 준비된 백업 문제들이 자동으로 사용됩니다.

## 📝 라이선스

이 프로젝트는 MIT 라이선스 하에 제공됩니다.

## 🤝 기여하기

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📞 지원

문제가 발생하거나 질문이 있으시면 이슈를 생성해주세요.

---

**즐거운 퀴즈 게임 되세요! 🎉**

## 🎮 온라인 데모

[여기를 클릭하여 플레이하기](https://ai-quiz-game.streamlit.app)

## 🌐 Streamlit Cloud 배포 가이드

1. GitHub에 코드 푸시

2. [Streamlit Cloud](https://share.streamlit.io) 접속
   - GitHub 저장소 연결
   - 새 앱 배포 선택

3. 환경 변수 설정:
   - Streamlit Cloud 대시보드의 앱 설정에서 다음 시크릿 추가:
   ```
   OPENAI_API_KEY=your_openai_api_key
   ```
   - Firebase 자격 증명을 JSON 형식으로 추가:
   ```
   FIREBASE_CREDENTIALS={"type": "service_account", ...}
   ```

4. 배포 시작
   - Streamlit Cloud가 자동으로 앱을 빌드하고 배포 