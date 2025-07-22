"""
이북 PDF 변환기
이북 리더 화면을 자동으로 캡처하여 PDF로 변환하는 프로그램

기능:
- 멀티 모니터 지원
- 고품질 PNG 캡처
- 자동 페이지 넘김
- 사용자 지정 딜레이
- 고해상도 PDF 출력
"""

import sys
from PyQt6.QtWidgets import QApplication
from app.gui import MainWindow


def main():
    """메인 애플리케이션 실행"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == '__main__':
    main()