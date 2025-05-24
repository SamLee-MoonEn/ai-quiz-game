# 🔧 AI 퀴즈 게임 설정 가이드

## 1. 환경변수 설정

프로젝트 루트 디렉토리에 `.env` 파일을 생성하고 다음 내용을 복사한 후 실제 값들을 입력하세요:

```env
# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key_here

# Firebase Config
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your_project-default-rtdb.firebaseio.com/
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
```

## 2. OpenAI API 키 설정

1. [OpenAI 플랫폼](https://platform.openai.com/)에 로그인
2. 좌측 메뉴에서 "API keys" 클릭
3. "Create new secret key" 버튼 클릭
4. 생성된 키를 복사하여 `.env` 파일의 `OPENAI_API_KEY`에 입력

## 3. Firebase 프로젝트 설정

### 3.1 Firebase 프로젝트 생성
1. [Firebase Console](https://console.firebase.google.com/)에 접속
2. "프로젝트 추가" 클릭
3. 프로젝트 이름 입력 (예: ai-quiz-game)
4. Google Analytics 설정 (선택사항)

### 3.2 Authentication 설정
1. Firebase Console에서 "Authentication" 메뉴 선택
2. "Sign-in method" 탭 클릭
3. "이메일/비밀번호" 활성화
4. "사용자" 탭에서 테스트 계정 생성 (선택사항)

### 3.3 Firestore Database 설정
1. "Firestore Database" 메뉴 선택
2. "데이터베이스 만들기" 클릭
3. "테스트 모드에서 시작" 선택
4. 지역 선택 (asia-northeast1 권장)

### 3.4 웹 앱 설정 정보 복사
1. 프로젝트 설정 (⚙️ 아이콘) 클릭
2. "일반" 탭에서 스크롤 다운
3. "내 앱" 섹션에서 "웹" 아이콘 (</>) 클릭
4. 앱 닉네임 입력
5. Firebase SDK 구성 정보 복사
6. `.env` 파일에 각 값들을 입력:
   - `apiKey` → `FIREBASE_API_KEY`
   - `authDomain` → `FIREBASE_AUTH_DOMAIN`
   - `databaseURL` → `FIREBASE_DATABASE_URL`
   - `projectId` → `FIREBASE_PROJECT_ID`
   - `storageBucket` → `FIREBASE_STORAGE_BUCKET`
   - `messagingSenderId` → `FIREBASE_MESSAGING_SENDER_ID`
   - `appId` → `FIREBASE_APP_ID`

## 4. Firestore 보안 규칙 설정

Firestore Database > 규칙 탭에서 다음 규칙을 설정하세요:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // 사용자 데이터: 본인만 읽기/쓰기 가능
    match /users/{userId} {
      allow read, write: if request.auth != null && request.auth.uid == userId;
    }
    
    // 퀴즈 결과: 본인 것만 생성/읽기/쓰기 가능
    match /quiz_results/{document} {
      allow read, write: if request.auth != null && request.auth.uid == resource.data.uid;
      allow create: if request.auth != null && request.auth.uid == request.resource.data.uid;
    }
    
    // 리더보드를 위한 사용자 데이터 읽기 허용
    match /users/{document} {
      allow read: if request.auth != null;
    }
  }
}
```

## 5. 앱 실행

모든 설정이 완료되면 다음 명령어로 앱을 실행하세요:

```bash
streamlit run app.py
```

브라우저에서 `http://localhost:8501`로 접속하면 AI 퀴즈 게임을 즐길 수 있습니다!

## 6. 문제 해결

### API 키 관련 오류
- OpenAI API 키가 올바른지 확인
- 계정에 충분한 크레딧이 있는지 확인

### Firebase 연결 오류
- 모든 Firebase 설정값이 올바른지 확인
- Authentication과 Firestore가 활성화되어 있는지 확인
- 보안 규칙이 올바르게 설정되어 있는지 확인

### 패키지 설치 오류
- Python 3.8 이상 버전 사용 확인
- 가상환경 사용 권장
- `pip install -r requirements.txt` 재실행

## 7. 데모 계정 (테스트용)

Firebase Authentication에서 테스트 계정을 미리 생성해두면 바로 테스트할 수 있습니다:
- 이메일: test@example.com
- 비밀번호: test123456

즐거운 퀴즈 게임 되세요! 🎉 