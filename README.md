# 📚 eBook PDF 변환기

eBook 리더 화면을 자동으로 캡처하여 고품질 PDF 파일로 변환하는 Python 애플리케이션입니다.

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![PyQt6](https://img.shields.io/badge/PyQt6-6.9.1-green.svg)
![Platform](https://img.shields.io/badge/Platform-macOS%20%7C%20Windows-lightgrey.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## ✨ 주요 기능

### 🎯 **정밀한 좌표 선택**
- **드래그 선택**: 마우스 드래그로 직관적인 캡처 영역 지정
- **실시간 픽셀뷰**: 50×50 픽셀 영역을 2배 확대하여 정확한 좌표 선택
- **십자선 가이드**: 정밀한 위치 조정을 위한 시각적 가이드
- **자동 영역 확정**: 드래그 완료 후 0.5초 자동 확정

### 📸 **스마트 캡처 시스템**
- **무손실 품질**: PNG 형식으로 캡처 후 300 DPI PDF 변환
- **자동 페이지 넘김**: 설정 가능한 딜레이로 우 화살표 키 자동 입력
- **진행률 표시**: 실시간 캡처 진행 상황 모니터링
- **임시 파일 자동 정리**: 변환 완료 후 임시 이미지 파일 자동 삭제

### 🖥️ **멀티 플랫폼 지원**
- **macOS 최적화**: SF Pro 폰트, 시스템 색상, 보안 권한 처리
- **Windows 호환**: DPI 인식, 태스크바 숨김 최적화
- **멀티 모니터**: 모니터 간 자유로운 이동 및 정확한 좌표 변환

## 🚀 설치 및 실행

### 📋 요구사항
- Python 3.8 이상
- macOS 10.14+ 또는 Windows 10+

### 💿 설치 방법

```bash
# 1. 저장소 클론
git clone https://github.com/yourusername/EbookToPDF.git
cd EbookToPDF

# 2. 가상 환경 생성
python -m venv venv

# 3. 가상 환경 활성화
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. 의존성 설치
pip install -r requirements.txt

# 5. 애플리케이션 실행
python main.py
```

### 🔧 macOS 추가 설정

macOS에서는 화면 녹화 및 접근성 권한이 필요합니다:

1. **시스템 환경설정** → **보안 및 개인 정보 보호**
2. **개인 정보 보호** 탭 → **화면 녹화**
3. Python 또는 터미널 앱에 권한 부여
4. **접근성** 섹션에서도 동일하게 권한 부여

## 📖 사용 방법

### 1️⃣ **모니터 선택**
멀티 모니터 환경에서 캡처할 모니터를 선택합니다.

### 2️⃣ **저장 경로 설정**
- 저장할 폴더 경로 지정
- PDF 파일 이름 입력

### 3️⃣ **페이지 설정**
- 총 페이지 수 입력
- 페이지 넘김 딜레이 설정 (초)

### 4️⃣ **영역 선택**
1. **"영역 선택 (드래그)"** 버튼 클릭
2. 오버레이 화면에서 캡처할 영역을 마우스로 드래그
3. 실시간 픽셀뷰를 참고하여 정확한 좌표 조정
4. 드래그 완료 후 자동으로 영역 확정
5. ESC 키로 언제든 취소 가능

### 5️⃣ **캡처 시작**
**"캡처 시작"** 버튼을 클릭하면:
- 지정된 영역을 순차적으로 캡처
- 자동으로 우 화살표 키를 눌러 페이지 넘김
- 진행률 표시로 현재 상황 확인
- 완료 후 자동으로 PDF 파일 생성

## 🏗️ 프로젝트 구조

```
EbookToPDF/
├── main.py              # 애플리케이션 진입점
├── requirements.txt     # Python 의존성
├── README.md           # 프로젝트 문서
├── CLAUDE.md          # 개발 가이드
├── .gitignore         # Git 무시 파일
│
├── app/                # 메인 애플리케이션 패키지
│   ├── __init__.py
│   ├── core/           # 핵심 로직
│   │   ├── __init__.py
│   │   ├── capture.py  # 화면 캡처 스레드
│   │   └── converter.py # PDF 변환 유틸리티
│   ├── gui/            # UI 컴포넌트
│   │   ├── __init__.py
│   │   ├── main_window.py        # 메인 윈도우
│   │   ├── coordinate_selector.py # 좌표 선택 오버레이
│   │   └── components.py         # UI 컴포넌트 및 스타일
│   └── utils/          # 유틸리티
│       ├── __init__.py
│       └── monitor.py   # 모니터 관리
│
└── img/                # 임시 이미지 저장 (자동 생성)
```

## 🛠️ 기술 스택

- **GUI 프레임워크**: PyQt6 6.9.1
- **화면 캡처**: MSS (Multi-Screen-Shot) 9.0.1
- **자동화**: PyAutoGUI 0.9.53
- **이미지 처리**: Pillow 9.5.0
- **PDF 생성**: PyMuPDF 1.22.5
- **macOS 시스템 API**: pyobjc 11.1

## 🎨 주요 특징

### 🔍 **정밀한 좌표 선택 시스템**
- 드래그 기반 직관적 인터페이스
- 실시간 십자선 및 좌표 표시
- 50×50 픽셀 영역 2배 확대 뷰
- 모니터 상대 좌표 정확한 변환

### ⚡ **최적화된 성능**
- 멀티스레드 기반 백그라운드 캡처
- 메모리 효율적인 이미지 처리
- 자동 임시 파일 정리

### 🌍 **크로스 플랫폼 호환성**
- macOS/Windows 플랫폼별 최적화
- 플랫폼 감지 및 자동 설정 조정
- 멀티 모니터 환경 완벽 지원

---

<div align="center">
Made with ❤️ by JeongYeonKyun
</div>
