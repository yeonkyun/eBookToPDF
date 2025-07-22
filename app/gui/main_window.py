"""
메인 윈도우 UI 모듈
"""

import os
import time
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, 
                            QPushButton, QLabel, QSpinBox, QFileDialog, 
                            QHBoxLayout, QLineEdit, QGridLayout, QComboBox,
                            QProgressBar, QDoubleSpinBox)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import pyautogui

from ..core import CaptureThread, PDFConverter
from ..utils import MonitorManager
from .components import UISection, StyleManager
from .coordinate_selector import CoordinateSelector


class MainWindow(QMainWindow):
    """메인 프로그램 창"""
    
    def __init__(self):
        super().__init__()
        self.output_dir = os.getcwd()
        self.output_filename = 'output.pdf'
        self.coords = {'x1': 0, 'y1': 0, 'x2': 0, 'y2': 0}
        self.monitor_offset = {'top': 0, 'left': 0}
        self.monitors = MonitorManager.get_monitors()
        self.monitor_offset = MonitorManager.get_monitor_offset(0)
        self.initUI()
        
    def initUI(self):
        """UI 초기화"""
        self.setWindowTitle('eBook PDF 변환기')
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet(StyleManager.get_main_stylesheet())

        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(15, 15, 15, 15)

        self._setup_monitor_section(main_layout)
        self._setup_save_section(main_layout)
        self._setup_page_section(main_layout)
        self._setup_coord_section(main_layout)
        self._setup_action_section(main_layout)

        main_layout.setSpacing(15)
        main_widget.setLayout(main_layout)

    def _setup_monitor_section(self, main_layout):
        """모니터 선택 섹션 설정"""
        monitor_section, monitor_layout = UISection.create_section("모니터 선택")
        self.monitor_combo = QComboBox()
        self.monitor_combo.setPlaceholderText("모니터를 선택하세요")
        self.monitor_combo.setMinimumWidth(200)
        self.update_monitor_list()
        self.monitor_combo.currentIndexChanged.connect(self.monitor_changed)
        monitor_layout.addWidget(self.monitor_combo)
        main_layout.addWidget(monitor_section)

    def _setup_save_section(self, main_layout):
        """저장 설정 섹션 설정"""
        save_section, save_layout = UISection.create_section("저장 설정")
        save_layout.setSpacing(5)  # 저장 섹션 내부 간격 줄이기
        
        # 저장 경로
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
        
        # 파일 이름
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

    def _setup_page_section(self, main_layout):
        """페이지 설정 섹션 설정"""
        page_section, page_layout = UISection.create_section("페이지 설정")
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

    def _setup_coord_section(self, main_layout):
        """좌표 설정 섹션 설정"""
        coord_section, coord_layout = UISection.create_section("좌표 설정")
        
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
        
        # 좌표 정보 표시 라벨
        self.coord_label = QLabel('좌표를 설정하세요')
        self.coord_label.setObjectName('coord_status')
        coord_layout.addWidget(self.coord_label)
        
        # 좌표 설정 버튼들
        btn_layout = QHBoxLayout()
        coord_select_btn = QPushButton('영역 선택 (드래그)')
        coord_select_btn.setStyleSheet("""
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }
            QPushButton:hover {
                background-color: #005bb5;
            }
        """)
        coord_select_btn.clicked.connect(self.start_coordinate_selection)
        btn_layout.addWidget(coord_select_btn)
        
        # 기존 개별 버튼들도 유지 (호환성)
        btn_top_left = QPushButton('좌상단')
        btn_bottom_right = QPushButton('우하단')
        btn_top_left.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        btn_bottom_right.setStyleSheet("""
            QPushButton {
                padding: 8px 16px;
                font-size: 13px;
                font-weight: 600;
            }
        """)
        btn_top_left.setMaximumWidth(80)
        btn_bottom_right.setMaximumWidth(80)
        btn_top_left.clicked.connect(lambda: self.get_coords('top_left'))
        btn_bottom_right.clicked.connect(lambda: self.get_coords('bottom_right'))
        btn_layout.addWidget(btn_top_left)
        btn_layout.addWidget(btn_bottom_right)
        coord_layout.addLayout(btn_layout)
        main_layout.addWidget(coord_section)

    def _setup_action_section(self, main_layout):
        """실행 버튼과 프로그레스바 섹션 설정"""
        action_section, action_layout = UISection.create_section("")
        
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

    def update_coords_from_input(self):
        """입력 필드에서 좌표 업데이트"""
        try:
            for coord in ['x1', 'y1', 'x2', 'y2']:
                value = self.coord_inputs[coord].text()
                if value:
                    self.coords[coord] = int(value)
            self.update_coord_label()
        except ValueError:
            pass
            
    def update_monitor_list(self):
        """모니터 목록 업데이트"""
        self.monitor_combo.clear()
        for i, m in enumerate(self.monitors):
            self.monitor_combo.addItem(MonitorManager.get_monitor_info_text(i, m))
        self.monitor_combo.setCurrentIndex(0)
                
    def monitor_changed(self, index):
        """모니터 변경 시 오프셋 업데이트"""
        if index >= 0 and index < len(self.monitors):
            self.monitor_offset = MonitorManager.get_monitor_offset(index)
                
    def start_coordinate_selection(self):
        """새로운 드래그 기반 좌표 선택 시작"""
        # 현재 선택된 모니터 인덱스 가져오기
        selected_monitor_index = self.monitor_combo.currentIndex()
        print(f"Starting coordinate selection on monitor {selected_monitor_index}")
        
        # 선택된 모니터 정보 전달
        self.coordinate_selector = CoordinateSelector(self.monitors, selected_monitor_index)
        self.coordinate_selector.coordinates_selected.connect(self.on_coordinates_selected)
        
        # 일반 창으로 표시 (showFullScreen 대신)
        self.coordinate_selector.show()
        
        # 포커스 확실히 가져오기
        self.coordinate_selector.activateWindow()
        self.coordinate_selector.raise_()
        self.coordinate_selector.setFocus()
        
        # 메인 윈도우 임시 숨김
        self.hide()
    
    def on_coordinates_selected(self, x1, y1, x2, y2):
        """좌표 선택 완료 시 호출 (모니터 상대 좌표를 받음)"""
        # 메인 윈도우 다시 표시 (취소든 확정이든 항상)
        self.show()
        self.raise_()
        self.activateWindow()
        
        # ESC 취소 처리
        if x1 == -1 and y1 == -1 and x2 == -1 and y2 == -1:
            print("Coordinate selection cancelled")
            return
            
        print(f"Received coordinates: ({x1}, {y1}) to ({x2}, {y2})")
        
        # 이미 모니터 상대 좌표이므로 바로 사용
        self.coords['x1'], self.coords['y1'] = x1, y1
        self.coords['x2'], self.coords['y2'] = x2, y2
        
        # UI 업데이트
        self.coord_inputs['x1'].setText(str(x1))
        self.coord_inputs['y1'].setText(str(y1))
        self.coord_inputs['x2'].setText(str(x2))
        self.coord_inputs['y2'].setText(str(y2))
        
        self.update_coord_label()

    def get_coords(self, position):
        """기존 방식 마우스로 캡처 영역 좌표 지정 (호환성 유지)"""
        self.hide()
        time.sleep(3)
        x, y = pyautogui.position()
        x = x - self.monitor_offset['left']
        y = y - self.monitor_offset['top']
        
        if position == 'top_left':
            self.coords['x1'], self.coords['y1'] = x, y
            self.coord_inputs['x1'].setText(str(x))
            self.coord_inputs['y1'].setText(str(y))
        else:
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
        
        font = self.coord_label.font()
        font.setPointSize(10)
        self.coord_label.setFont(font)
        self.coord_label.setWordWrap(True)
        self.coord_label.setContentsMargins(0, 5, 0, 5)
        
    def start_capture(self):
        """캡처 프로세스 시작"""
        if not all(self.coords.values()):
            self.progress_bar.setFormat('좌표를 모두 설정해주세요!')
            self.progress_bar.setStyleSheet(StyleManager.get_error_progressbar_style())
            return
            
        self.progress_bar.setStyleSheet(StyleManager.get_normal_progressbar_style())
        self.progress_bar.setValue(0)
        self.progress_bar.setFormat('캡처 준비 중...')
        
        self.capture_thread = CaptureThread(
            self.coords['x1'], 
            self.coords['y1'],
            self.coords['x2'], 
            self.coords['y2'],
            self.page_spin.value(),
            self.monitor_offset,
            self.delay_spin.value()
        )
        
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
        self.progress_bar.setStyleSheet(StyleManager.get_normal_progressbar_style())

    def finish_capture(self):
        """캡처 완료 후 PDF 변환"""
        self.start_btn.setEnabled(True)
        self.progress_bar.setFormat('PDF 변환 중...')
        self.convert_to_pdf()
        
    def convert_to_pdf(self):
        """캡처된 이미지들을 PDF로 변환"""
        output_pdf = os.path.join(self.output_dir, self.output_filename)
        success = PDFConverter.convert_images_to_pdf(
            self.page_spin.value(), 
            output_pdf
        )
        
        if success:
            self.progress_bar.setFormat(f'완료! {output_pdf} 생성됨')
        else:
            self.progress_bar.setFormat('PDF 변환 실패')
            
    def select_save_dir(self):
        """저장 경로 선택"""
        dir_path = QFileDialog.getExistingDirectory(
            self, "저장 경로 선택", self.output_dir
        )
        if dir_path:
            self.output_dir = dir_path
            self.path_input.setText(dir_path)
            
    def update_filename(self, text):
        """파일 이름 업데이트"""
        self.output_filename = f"{text}.pdf"