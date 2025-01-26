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
import os
import time
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QSpinBox, QFileDialog, 
                            QHBoxLayout, QLineEdit, QGridLayout, QComboBox,
                            QProgressBar, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
import pyautogui
from PIL import Image
from mss import mss
from PyQt6.QtGui import QFont

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

class MainWindow(QMainWindow):
    """
    메인 프로그램 창
    
    화면 캡처 영역 설정, PDF 변환 등 주요 기능 포함
    """
    
    def __init__(self):
        super().__init__()
        self.output_dir = os.getcwd()
        self.output_filename = 'output.pdf'
        self.coords = {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}
        self.monitor_offset = {'top': 0, 'left': 0}
        self.get_monitors()  # monitors 초기화를 먼저 수행
        self.initUI()
        
    def get_monitors(self):
        """모니터 정보 초기화 및 기본 모니터 자동 설정"""
        with mss() as sct:
            self.monitors = sct.monitors[1:]
            main_monitor = sct.monitors[1]
            self.monitor_offset = {
                'top': main_monitor['top'],
                'left': main_monitor['left']
            }
            
    def create_section(self, title):
        """
        UI 섹션 생성
        
        매개변수:
            title: 섹션 제목
        반환값:
            (섹션 위젯, 컨텐츠 레이아웃) 튜플
        """
        section = QWidget()
        section.setObjectName("section")
        main_layout = QVBoxLayout()
        section.setLayout(main_layout)
        
        if title:
            label = QLabel(title)
            label.setStyleSheet("font-weight: bold; font-size: 13px;")
            main_layout.addWidget(label)
        
        # 내용을 담을 컨테이너
        container = QWidget()
        container_layout = QVBoxLayout()
        container_layout.setContentsMargins(0, 0, 0, 0)
        container.setLayout(container_layout)
        main_layout.addWidget(container)
        
        return section, container_layout

    def initUI(self):
        self.setWindowTitle('eBook PDF 변환기')
        self.setGeometry(100, 100, 500, 400)  # 전체 창 크기 축소
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f5f5f7;
            }
            QLabel {
                font-size: 12px;  /* 폰트 크기 축소 */
                color: #1d1d1f;
            }
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                border-radius: 4px;  /* 반경 축소 */
                padding: 6px 12px;  /* 패딩 축소 */
                font-size: 12px;
                font-weight: 500;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                border: 1px solid #d2d2d7;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                font-size: 12px;
                min-height: 20px;  /* 높이 축소 */
                color: black;
            }
            QSpinBox::up-button, QDoubleSpinBox::up-button {
                subcontrol-origin: border;
                subcontrol-position: top right;
                width: 20px;
                border: none;
                background: #f0f0f0;
                border-top-right-radius: 3px;
            }
            QSpinBox::down-button, QDoubleSpinBox::down-button {
                subcontrol-origin: border;
                subcontrol-position: bottom right;
                width: 20px;
                border: none;
                background: #f0f0f0;
                border-bottom-right-radius: 3px;
            }
            QSpinBox::up-arrow, QDoubleSpinBox::up-arrow {
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-bottom: 6px solid #666;
            }
            QSpinBox::down-arrow, QDoubleSpinBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #666;
            }
            QComboBox {
                padding-right: 20px;
            }
            QComboBox::drop-down {
                border: none;
                width: 20px;
            }
            QComboBox::down-arrow {
                width: 0;
                height: 0;
                border-left: 4px solid transparent;
                border-right: 4px solid transparent;
                border-top: 6px solid #666;
            }
            QProgressBar {
                text-align: center;
                font-weight: bold;
                font-size: 12px;
                color: black;
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f5f5f7;
                min-height: 25px;
                max-height: 25px;
            }
            QProgressBar::chunk {
                background-color: #0071e3;
                border-radius: 3px;
            }
            QWidget#section {
                background-color: white;
                border-radius: 8px;
                padding: 10px;
            }
            QLabel#coord_status {
                background-color: #f5f5f7;
                padding: 10px;
                border-radius: 6px;
                min-height: 60px;  /* 높이 증가 */
                font-size: 12px;
                qproperty-alignment: AlignCenter;
                margin: 5px 0;     /* 상하 여백 추가 */
            }
        """)

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)  # 간격 축소
        main_layout.setContentsMargins(15, 15, 15, 15)  # 여백 축소

        # 모니터 선택 섹션
        monitor_section, monitor_layout = self.create_section("모니터 선택")
        self.monitor_combo = QComboBox()
        self.monitor_combo.setPlaceholderText("모니터를 선택하세요")
        self.monitor_combo.setMinimumWidth(200)
        self.update_monitor_list()
        self.monitor_combo.currentIndexChanged.connect(self.monitor_changed)
        monitor_layout.addWidget(self.monitor_combo)
        main_layout.addWidget(monitor_section)

        # 저장 설정 섹션
        save_section, save_layout = self.create_section("저장 설정")
        
        path_layout = QHBoxLayout()
        path_label = QLabel("저장 경로:")
        path_layout.addWidget(path_label)
        self.path_input = QLineEdit(self.output_dir)
        self.path_input.setReadOnly(True)
        path_layout.addWidget(self.path_input)
        browse_btn = QPushButton('경로 선택')
        browse_btn.setFixedWidth(100)
        browse_btn.clicked.connect(self.select_save_dir)
        path_layout.addWidget(browse_btn)
        save_layout.addLayout(path_layout)
        
        filename_layout = QHBoxLayout()
        filename_label = QLabel("파일 이름:")
        filename_layout.addWidget(filename_label)
        self.filename_input = QLineEdit(os.path.splitext(self.output_filename)[0])
        self.filename_input.setPlaceholderText("파일 이름을 입력하세요")
        self.filename_input.textChanged.connect(self.update_filename)
        filename_layout.addWidget(self.filename_input)
        filename_layout.addWidget(QLabel('.pdf'))
        save_layout.addLayout(filename_layout)
        main_layout.addWidget(save_section)

        # 페이지 설정 섹션
        page_section, page_layout = self.create_section("페이지 설정")
        page_content = QHBoxLayout()
        
        self.page_spin = QSpinBox()
        self.page_spin.setRange(1, 9999)
        self.page_spin.setValue(1)
        self.page_spin.setMinimumWidth(80)
        page_content.addWidget(QLabel('페이지 수:'))
        page_content.addWidget(self.page_spin)
        
        page_content.addSpacing(20)
        
        self.delay_spin = QDoubleSpinBox()
        self.delay_spin.setRange(0.1, 5.0)
        self.delay_spin.setValue(0.5)
        self.delay_spin.setSingleStep(0.1)
        self.delay_spin.setSuffix(' 초')
        self.delay_spin.setMinimumWidth(100)
        page_content.addWidget(QLabel('페이지 넘김 딜레이:'))
        page_content.addWidget(self.delay_spin)
        
        page_layout.addLayout(page_content)
        main_layout.addWidget(page_section)

        # 좌표 설정 섹션
        coord_section, coord_layout = self.create_section("좌표 설정")
        
        # 좌표 입력 그리드
        grid = QGridLayout()
        grid.setSpacing(10)
        self.coord_inputs = {}
        coords = [('x1', '왼쪽 X:'), ('y1', '왼쪽 Y:'),
                 ('x2', '오른쪽 X:'), ('y2', '오른쪽 Y:')]
        for i, (coord, label) in enumerate(coords):
            grid.addWidget(QLabel(label), i//2, (i%2)*2)
            self.coord_inputs[coord] = QLineEdit()
            self.coord_inputs[coord].setPlaceholderText('0')
            self.coord_inputs[coord].textChanged.connect(self.update_coords_from_input)
            grid.addWidget(self.coord_inputs[coord], i//2, (i%2)*2 + 1)
        coord_layout.addLayout(grid)
        
        # 좌표 정보 표시 라벨 수정
        self.coord_label = QLabel('좌표를 설정하세요')
        self.coord_label.setObjectName('coord_status')  # 스타일시트 적용을 위한 ID 설정
        coord_layout.addWidget(self.coord_label)
        
        # 좌표 설정 버튼들
        btn_layout = QHBoxLayout()
        btn_top_left = QPushButton('왼쪽 상단 좌표 설정')
        btn_bottom_right = QPushButton('오른쪽 하단 좌표 설정')
        btn_top_left.clicked.connect(lambda: self.get_coords('top_left'))
        btn_bottom_right.clicked.connect(lambda: self.get_coords('bottom_right'))
        btn_layout.addWidget(btn_top_left)
        btn_layout.addWidget(btn_bottom_right)
        coord_layout.addLayout(btn_layout)
        main_layout.addWidget(coord_section)

        # 실행 버튼과 프로그레스바
        action_section, action_layout = self.create_section("")
        
        self.start_btn = QPushButton('캡처 시작')
        self.start_btn.clicked.connect(self.start_capture)
        self.start_btn.setStyleSheet("""
            QPushButton {
                font-size: 15px;
                padding: 12px;
                min-height: 20px;
            }
        """)
        action_layout.addWidget(self.start_btn)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setFormat("대기 중...")
        self.progress_bar.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.progress_bar.setValue(0)
        
        progress_font = QFont()
        progress_font.setPointSize(11)
        progress_font.setBold(True)
        self.progress_bar.setFont(progress_font)
        
        action_layout.addWidget(self.progress_bar)
        main_layout.addWidget(action_section)

        main_layout.setSpacing(15)
        main_widget.setLayout(main_layout)

    def update_coords_from_input(self):
        try:
            for coord in ['x1', 'y1', 'x2', 'y2']:
                value = self.coord_inputs[coord].text()
                if value:
                    self.coords[coord] = int(value)
            self.update_coord_label()
        except ValueError:
            self.progress_label.setText('좌표는 숫자만 입력 가능합니다!')
            
    def update_monitor_list(self):
        self.monitor_combo.clear()
        with mss() as sct:
            for i, m in enumerate(sct.monitors[1:], 1):
                self.monitor_combo.addItem(f"모니터 {i}: {m['width']}x{m['height']}")
        # 첫 번째 모니터 자동 선택
        self.monitor_combo.setCurrentIndex(0)
                
    def monitor_changed(self, index):
        if index >= 0:
            with mss() as sct:
                monitor = sct.monitors[index + 1]
                self.monitor_offset = {
                    'top': monitor['top'],
                    'left': monitor['left']
                }
                
    def get_coords(self, position):
        """
        마우스로 캡처 영역 좌표 지정
        
        매개변수:
            position: 'top_left' (좌상단) 또는 'bottom_right' (우하단)
        """
        self.hide()
        time.sleep(3)
        if position == 'top_left':
            x, y = pyautogui.position()
            x = x - self.monitor_offset['left']
            y = y - self.monitor_offset['top']
            self.coords['x1'], self.coords['y1'] = x, y
            self.coord_inputs['x1'].setText(str(x))
            self.coord_inputs['y1'].setText(str(y))
        else:
            x, y = pyautogui.position()
            x = x - self.monitor_offset['left']
            y = y - self.monitor_offset['top']
            self.coords['x2'], self.coords['y2'] = x, y
            self.coord_inputs['x2'].setText(str(x))
            self.coord_inputs['y2'].setText(str(y))
        self.show()
        self.update_coord_label()
        
    def update_coord_label(self):
        """좌표, 크기, 비율 정보를 표시하는 라벨 업데이트"""
        width = abs(self.coords['x2'] - self.coords['x1'])
        height = abs(self.coords['y2'] - self.coords['y1'])
        ratio = round(width / height, 2) if height != 0 else 0
        
        self.coord_label.setText(
            f"좌표: ({self.coords['x1']},{self.coords['y1']}) - "
            f"({self.coords['x2']},{self.coords['y2']})\n"
            f"크기: {width}x{height} (픽셀)\n"
            f"비율: {ratio:.2f}:1"
        )
        
        # 좌표 라벨 폰트 크기와 줄간격 조정
        font = self.coord_label.font()
        font.setPointSize(10)
        self.coord_label.setFont(font)
        self.coord_label.setWordWrap(True)  # 자동 줄바꿈 활성화
        self.coord_label.setContentsMargins(0, 5, 0, 5)  # 내부 여백 추가
        
    def start_capture(self):
        """캡처 프로세스 시작 및 진행 상태 표시"""
        if not all(self.coords.values()):
            self.progress_bar.setFormat('좌표를 모두 설정해주세요!')
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 1px solid #ff9999;
                    border-radius: 6px;
                    background-color: #fff0f0;
                    min-height: 30px;
                    font-size: 13px;
                    color: black;
                    text-align: center;
                }
                QProgressBar::chunk {
                    background-color: #ff4444;
                    border-radius: 5px;
                }
            """)
            return
            
        # 정상 상태 스타일로 복구
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 5px;
                text-align: center;
                padding: 1px;
                font-size: 14px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #0d6efd;
                border-radius: 4px;
            }
        """)
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat('캡처 준비 중...')
        # setValue(0)이 중복되어 있어서 하나 제거
        self.capture_thread = CaptureThread(
            self.coords['x1'], 
            self.coords['y1'],
            self.coords['x2'], 
            self.coords['y2'],
            self.page_spin.value(),
            self.monitor_offset,
            self.delay_spin.value()
        )
        
        # 프로그레스바 초기 메시지 설정
        self.progress_bar.setFormat('캡처 준비 중...')
        
        self.capture_thread.progress.connect(self.update_progress)
        self.capture_thread.finished.connect(self.finish_capture)
        self.capture_thread.start()
        self.start_btn.setEnabled(False)
        
    def update_progress(self, value):
        """진행 상황 업데이트"""
        percent = int((value / self.page_spin.value()) * 100)
        self.progress_bar.setValue(percent)
        status_text = f'진행중: {value}/{self.page_spin.value()} 페이지 ({percent}%)'
        self.progress_bar.setFormat(status_text)
        
        # 프로그레스바 색상 설정 - 텍스트 색상 항상 검정색 유지
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f5f5f7;
                min-height: 25px;
                font-size: 12px;
                color: black;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #0071e3;
                border-radius: 3px;
            }
        """)

    def finish_capture(self):
        self.start_btn.setEnabled(True)
        self.progress_bar.setFormat('PDF 변환 중...')
        self.convert_to_pdf()
        
    def convert_to_pdf(self):
        """
        캡처된 이미지들을 하나의 PDF 파일로 변환
        해상도: 300dpi로 설정하여 고품질 유지
        """
        output_pdf = os.path.join(self.output_dir, self.output_filename)
        images = []
        for i in range(self.page_spin.value()):
            # PNG 파일 읽기
            image_path = os.path.join("captures", f"page_{i+1}.png")
            if os.path.exists(image_path):
                images.append(Image.open(image_path))
        
        if images:
            images[0].save(
                output_pdf,
                save_all=True,
                append_images=images[1:],
                resolution=300.0  # PDF 해상도 증가
            )
            self.progress_bar.setFormat(f'완료! {output_pdf} 생성됨')
            
    def select_save_dir(self):
        """저장 경로만 선택"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "저장 경로 선택", self.output_dir
        )
        if dir_path:
            self.output_dir = dir_path
            self.path_input.setText(dir_path)
            
    def update_filename(self, text):
        """파일 이름 업데이트"""
        self.output_filename = f"{text}.pdf"

def main():
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
