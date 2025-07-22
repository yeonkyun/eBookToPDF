"""
스크린샷 자동 캡처 스레드 모듈
"""

import os
import time
import platform
from PyQt6.QtCore import QThread, pyqtSignal
import pyautogui
from PIL import Image
from mss import mss


class CaptureThread(QThread):
    """
    스크린샷 자동 캡처 스레드
    
    시그널:
        progress: 현재 캡처 진행 상태 (페이지 번호)
        finished: 캡처 작업 완료 알림
    """
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    
    def __init__(self, x1, y1, x2, y2, page_num, monitor_offset, delay):
        """
        Args:
            x1, y1: 캡처 영역의 좌상단 좌표
            x2, y2: 캡처 영역의 우하단 좌표
            page_num: 총 페이지 수
            monitor_offset: 모니터 오프셋 {'top': int, 'left': int}
            delay: 페이지 넘김 딜레이 (초)
        """
        super().__init__()
        self.x1 = x1 + monitor_offset['left']
        self.y1 = y1 + monitor_offset['top']
        self.x2 = x2 + monitor_offset['left']
        self.y2 = y2 + monitor_offset['top']
        self.page_num = page_num
        self.delay = delay
        
    def run(self):
        """지정된 영역을 순차적으로 캡처하고 PNG 이미지로 저장 (크로스 플랫폼 호환)"""
        output_dir = "img"
        os.makedirs(output_dir, exist_ok=True)
        
        # 플랫폼별 pyautogui 설정
        if platform.system() == "Darwin":  # macOS
            # macOS에서 보안 권한 처리
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
        elif platform.system() == "Windows":
            # Windows에서 DPI 인식 설정
            pyautogui.FAILSAFE = True
            pyautogui.PAUSE = 0.1
        
        try:
            with mss() as sct:
                for i in range(self.page_num):
                    monitor = {
                        "top": self.y1,
                        "left": self.x1,
                        "width": self.x2 - self.x1,
                        "height": self.y2 - self.y1
                    }
                    
                    # 캡처 영역 유효성 검사
                    if monitor["width"] <= 0 or monitor["height"] <= 0:
                        print(f"Invalid capture area: {monitor}")
                        continue
                    
                    screenshot = sct.grab(monitor)
                    
                    # PNG 형식으로 저장하여 무손실 화질 유지
                    image_path = os.path.join(output_dir, f"page_{i+1}.png")
                    img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                    img.save(image_path, "PNG")
                    
                    # 플랫폼별 키 입력 방식
                    if platform.system() == "Darwin":  # macOS
                        pyautogui.press('right')
                    else:  # Windows, Linux
                        pyautogui.press('right')
                        
                    time.sleep(self.delay)
                    self.progress.emit(i + 1)
                    
        except Exception as e:
            print(f"Capture error: {e}")
                
        self.finished.emit()