import subprocess
import sys
import os

def install_requirements():
    """requirements.txt의 패키지들을 자동으로 설치"""
    
    print("🔄 AI 퀴즈 게임 패키지 설치를 시작합니다...")
    
    # requirements.txt 파일 존재 확인
    if not os.path.exists('requirements.txt'):
        print("❌ requirements.txt 파일을 찾을 수 없습니다.")
        return False
    
    try:
        # pip 업그레이드
        print("📦 pip를 최신 버전으로 업그레이드 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
        
        # requirements.txt 설치
        print("📥 필요한 패키지들을 설치 중...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        
        print("✅ 모든 패키지가 성공적으로 설치되었습니다!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ 패키지 설치 중 오류가 발생했습니다: {e}")
        return False

def create_env_file():
    """환경변수 파일 생성 안내"""
    
    env_content = """# OpenAI API Key
OPENAI_API_KEY=your_openai_api_key

# Firebase Config
FIREBASE_API_KEY=your_firebase_api_key
FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
FIREBASE_DATABASE_URL=https://your_project-default-rtdb.firebaseio.com/
FIREBASE_PROJECT_ID=your_project_id
FIREBASE_STORAGE_BUCKET=your_project.appspot.com
FIREBASE_MESSAGING_SENDER_ID=your_sender_id
FIREBASE_APP_ID=your_app_id
"""
    
    if not os.path.exists('.env'):
        with open('.env', 'w', encoding='utf-8') as f:
            f.write(env_content)
        print("📝 .env 파일이 생성되었습니다. 필요한 API 키들을 입력해주세요.")
    else:
        print("ℹ️  .env 파일이 이미 존재합니다.")

def main():
    print("🧠 AI 퀴즈 게임 설치 스크립트")
    print("=" * 50)
    
    # 패키지 설치
    if install_requirements():
        print("\n🎉 설치가 완료되었습니다!")
        
        # 환경변수 파일 생성
        create_env_file()
        
        print("\n📋 다음 단계:")
        print("1. .env 파일에 OpenAI API 키와 Firebase 설정을 입력하세요")
        print("2. Firebase 프로젝트를 생성하고 설정하세요")
        print("3. 'streamlit run app.py' 명령어로 앱을 실행하세요")
        
    else:
        print("\n❌ 설치에 실패했습니다. 오류를 확인하고 다시 시도해주세요.")

if __name__ == "__main__":
    main() 