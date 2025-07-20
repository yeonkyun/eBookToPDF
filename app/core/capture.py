"""
스크린샷 자동 캡처 스레드 모듈
"""

import os
import time
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
        """지정된 영역을 순차적으로 캡처하고 PNG 이미지로 저장"""
        output_dir = "img"
        os.makedirs(output_dir, exist_ok=True)
        
        with mss() as sct:
            for i in range(self.page_num):
                monitor = {
                    "top": self.y1,
                    "left": self.x1,
                    "width": self.x2 - self.x1,
                    "height": self.y2 - self.y1
                }
                
                screenshot = sct.grab(monitor)
                
                # PNG 형식으로 저장하여 무손실 화질 유지
                image_path = os.path.join(output_dir, f"page_{i+1}.png")
                img = Image.frombytes("RGB", screenshot.size, screenshot.rgb)
                img.save(image_path, "PNG")
                
                pyautogui.press('right')
                time.sleep(self.delay)
                self.progress.emit(i + 1)
                
        self.finished.emit()