"""
좌표 선택 오버레이 모듈
드래그 선택과 십자선, 실시간 픽셀 표시 기능 제공
"""

import platform
from PyQt6.QtWidgets import (QWidget, QApplication, QLabel, QVBoxLayout, 
                            QHBoxLayout, QFrame)
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal, QTimer
from PyQt6.QtGui import QPainter, QPen, QColor, QPixmap, QFont, QCursor


class CoordinateSelector(QWidget):
    """좌표 선택 오버레이 위젯"""
    
    coordinates_selected = pyqtSignal(int, int, int, int)  # x1, y1, x2, y2
    
    def __init__(self, all_monitors, selected_monitor_index=0):
        super().__init__()
        self.all_monitors = all_monitors
        self.selected_monitor_index = selected_monitor_index
        self.selection_start = None
        self.selection_end = None
        self.current_pos = QPoint(0, 0)
        self.is_selecting = False
        self.zoom_factor = 3
        
        # 선택된 모니터 정보 설정
        self.setup_monitor_info()
        
        self.init_ui()
        self.setup_timer()
        
    def setup_monitor_info(self):
        """선택된 모니터 정보 설정"""
        if not self.all_monitors or self.selected_monitor_index >= len(self.all_monitors):
            # 기본 모니터 정보
            self.current_monitor = {'left': 0, 'top': 0, 'width': 1920, 'height': 1080}
        else:
            self.current_monitor = self.all_monitors[self.selected_monitor_index]
            
        print(f"Selected monitor {self.selected_monitor_index}: {self.current_monitor}")
        
    def calculate_full_screen_area(self):
        """현재 선택된 모니터의 전체 영역 계산"""
        return QRect(
            self.current_monitor['left'],
            self.current_monitor['top'],
            self.current_monitor['width'],
            self.current_monitor['height']
        )
        
    def init_ui(self):
        """UI 초기화 (크로스 플랫폼 호환)"""
        # 플랫폼별 윈도우 플래그 설정
        if platform.system() == "Windows":
            # Windows: Tool 플래그 제거로 태스크바 표시 방지
            self.setWindowFlags(
                Qt.WindowType.WindowStaysOnTopHint | 
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.WindowSystemMenuHint
            )
        elif platform.system() == "Darwin":  # macOS
            # macOS: 기본 설정 유지
            self.setWindowFlags(
                Qt.WindowType.WindowStaysOnTopHint | 
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.Tool
            )
        else:  # Linux 등
            self.setWindowFlags(
                Qt.WindowType.WindowStaysOnTopHint | 
                Qt.WindowType.FramelessWindowHint |
                Qt.WindowType.Tool
            )
            
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setAttribute(Qt.WidgetAttribute.WA_DeleteOnClose)
        
        # 포커스 설정
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        
        # 선택된 모니터 영역으로 설정
        monitor_geometry = self.calculate_full_screen_area()
        self.setGeometry(monitor_geometry)
        
        # 디버깅을 위한 출력
        print(f"Monitor geometry: {monitor_geometry}")
        print(f"Selected monitor index: {self.selected_monitor_index}")
        print(f"Monitor info: {self.current_monitor}")
        
        # 더 투명한 배경 (검정색 문제 완화)
        self.setStyleSheet("background-color: rgba(0, 0, 0, 30);")
        
        # 커서 변경
        self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        
        # 윈도우 활성화 및 포커스
        self.activateWindow()
        self.raise_()
        
        # 정보 패널 생성
        self.create_info_panel()
        
        # macOS 호환성을 위한 추가 설정
        if platform.system() == "Darwin":
            self.setWindowOpacity(0.95)  # 투명도 조정으로 렌더링 개선
        
    def create_info_panel(self):
        """정보 표시 패널 생성"""
        self.info_panel = QFrame(self)
        
        # macOS와 Windows에서 다른 크기 설정
        if platform.system() == "Darwin":  # macOS
            self.info_panel.setFixedSize(300, 250)
            panel_style = """
                QFrame {
                    background-color: rgba(30, 30, 30, 240);
                    border: 1px solid rgba(255, 255, 255, 0.3);
                    border-radius: 10px;
                    color: white;
                    padding: 12px;
                }
                QLabel {
                    color: white;
                    font-size: 11px;
                    background: transparent;
                    padding: 2px;
                }
            """
        else:  # Windows, Linux
            self.info_panel.setFixedSize(280, 230)
            panel_style = """
                QFrame {
                    background-color: rgba(40, 40, 40, 220);
                    border: 1px solid #555;
                    border-radius: 8px;
                    color: white;
                    padding: 8px;
                }
                QLabel {
                    color: white;
                    font-size: 11px;
                    background: transparent;
                }
            """
        
        self.info_panel.setStyleSheet(panel_style)
        
        layout = QVBoxLayout(self.info_panel)
        if platform.system() == "Darwin":  # macOS
            layout.setSpacing(6)
            layout.setContentsMargins(12, 12, 12, 12)
        else:
            layout.setSpacing(4)
            layout.setContentsMargins(10, 10, 10, 10)
        
        # 좌표 정보
        self.coord_label = QLabel("마우스 위치: (0, 0)")
        if platform.system() == "Darwin":  # macOS
            self.coord_label.setFont(QFont("SF Pro Text", 11, QFont.Weight.Bold))
            self.coord_label.setStyleSheet("color: white; background: transparent; min-height: 16px;")
        else:
            self.coord_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
            self.coord_label.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(self.coord_label)
        
        # 선택 영역 정보
        self.selection_label = QLabel("선택 영역: 없음")
        if platform.system() == "Darwin":  # macOS
            self.selection_label.setFont(QFont("SF Pro Text", 10))
            self.selection_label.setStyleSheet("color: white; background: transparent; min-height: 16px;")
        else:
            self.selection_label.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(self.selection_label)
        
        # 크기 정보
        self.size_label = QLabel("크기: 0 x 0")
        if platform.system() == "Darwin":  # macOS
            self.size_label.setFont(QFont("SF Pro Text", 10))
            self.size_label.setStyleSheet("color: white; background: transparent; min-height: 16px;")
        else:
            self.size_label.setStyleSheet("color: white; background: transparent;")
        layout.addWidget(self.size_label)
        
        # 사용법 안내
        help_layout = QHBoxLayout()
        self.help_label = QLabel("드래그: 영역 선택 | ESC: 취소")
        self.help_label.setStyleSheet("color: #aaa; font-size: 9px;")
        help_layout.addWidget(self.help_label)
        layout.addLayout(help_layout)
        
        # 확대 영역 (픽셀 단위 정확도)
        self.zoom_label = QLabel()
        self.zoom_label.setFixedSize(100, 100)  # 확대 영역 크기 증가
        self.zoom_label.setStyleSheet("""
            border: 2px solid #0071e3;
            background-color: rgba(60, 60, 60, 200);
        """)
        layout.addWidget(self.zoom_label)
        
        # 패널 위치 설정 (우상단)
        self.info_panel.move(self.width() - 300, 20)
        
    def setup_timer(self):
        """마우스 추적 타이머 설정"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_mouse_info)
        self.timer.start(16)  # 60 FPS
        
    def update_mouse_info(self):
        """마우스 정보 업데이트"""
        if not self.isVisible():
            return
            
        # 전역 마우스 위치
        global_pos = QCursor.pos()
        
        # 위젯 상대 좌표로 변환
        widget_pos = self.mapFromGlobal(global_pos)
        local_x = widget_pos.x()
        local_y = widget_pos.y()
        
        # 모니터 상대 좌표 계산 (실제 캡처에 사용될 좌표)
        monitor_relative_x = global_pos.x() - self.current_monitor['left']
        monitor_relative_y = global_pos.y() - self.current_monitor['top']
        
        self.current_pos = QPoint(local_x, local_y)
        
        # 좌표 표시 업데이트
        if hasattr(self, 'coord_label'):
            self.coord_label.setText(f"모니터 좌표: ({monitor_relative_x}, {monitor_relative_y}) | 전역: ({global_pos.x()}, {global_pos.y()})")
        
        # 선택 영역 정보 업데이트
        if hasattr(self, 'selection_label') and hasattr(self, 'size_label'):
            if self.is_selecting and self.selection_start:
                width = abs(local_x - self.selection_start.x())
                height = abs(local_y - self.selection_start.y())
                self.selection_label.setText(f"선택 중: ({self.selection_start.x()}, {self.selection_start.y()}) → ({local_x}, {local_y})")
                self.size_label.setText(f"크기: {width} x {height}")
            elif self.selection_start and self.selection_end:
                x1, y1 = self.selection_start.x(), self.selection_start.y()
                x2, y2 = self.selection_end.x(), self.selection_end.y()
                width = abs(x2 - x1)
                height = abs(y2 - y1)
                self.selection_label.setText(f"선택됨: ({min(x1,x2)}, {min(y1,y2)}) → ({max(x1,x2)}, {max(y1,y2)})")
                self.size_label.setText(f"크기: {width} x {height}")
            else:
                self.selection_label.setText("선택 영역: 없음")
                self.size_label.setText("크기: 0 x 0")
        
        # 확대 영역 업데이트
        if hasattr(self, 'zoom_label'):
            self.update_zoom_view(global_pos.x(), global_pos.y())
        
        # 정보 패널 위치 조정 (마우스 근처에 표시하되 화면 밖으로 나가지 않게)
        if hasattr(self, 'info_panel'):
            panel_x = min(local_x + 20, self.width() - self.info_panel.width() - 10)
            panel_y = max(local_y - self.info_panel.height() - 20, 10)
            
            # 마우스가 패널과 겹치지 않도록 조정
            if (panel_x <= local_x <= panel_x + self.info_panel.width() and
                panel_y <= local_y <= panel_y + self.info_panel.height()):
                panel_y = local_y + 20
                
            self.info_panel.move(panel_x, panel_y)
        
        self.update()
        
    def update_zoom_view(self, global_x, global_y):
        """확대 뷰 업데이트 (크로스 플랫폼 호환)"""
        try:
            # 마우스 위치에 해당하는 스크린 찾기
            target_screen = None
            for screen in QApplication.screens():
                if screen.geometry().contains(global_x, global_y):
                    target_screen = screen
                    break
            
            # 해당하는 스크린이 없으면 primary 사용
            if not target_screen:
                target_screen = QApplication.primaryScreen()
            
            if target_screen:
                zoom_size = 50  # 확대 영역 크기 증가
                
                # 캡처 영역 계산 (스크린 상대 좌표로)
                screen_geometry = target_screen.geometry()
                relative_x = global_x - screen_geometry.x()
                relative_y = global_y - screen_geometry.y()
                
                capture_rect = QRect(
                    relative_x - zoom_size//2,
                    relative_y - zoom_size//2,
                    zoom_size,
                    zoom_size
                )
                
                # 화면 경계 체크
                screen_rect = QRect(0, 0, screen_geometry.width(), screen_geometry.height())
                capture_rect = capture_rect.intersected(screen_rect)
                
                if not capture_rect.isEmpty():
                    # 해당 스크린에서 스크린샷 캡처
                    pixmap = target_screen.grabWindow(
                        0, 
                        capture_rect.x(), 
                        capture_rect.y(),
                        capture_rect.width(), 
                        capture_rect.height()
                    )
                    
                    if not pixmap.isNull():
                        # 정확한 크기로 스케일링 (잘림 방지)
                        label_size = self.zoom_label.size()
                        
                        # 테두리를 고려한 실제 표시 영역
                        display_width = label_size.width() - 4
                        display_height = label_size.height() - 4
                        
                        # 픽셀 경계를 명확하게 하기 위해 FastTransformation 사용
                        scaled_pixmap = pixmap.scaled(
                            display_width, 
                            display_height,
                            Qt.AspectRatioMode.KeepAspectRatio,
                            Qt.TransformationMode.FastTransformation
                        )
                        
                        self.zoom_label.setPixmap(scaled_pixmap)
                    else:
                        self.zoom_label.clear()
                        self.zoom_label.setText("캡처\n실패")
            
        except Exception as e:
            # 에러 발생 시 빈 이미지로 설정
            if hasattr(self, 'zoom_label'):
                self.zoom_label.clear()
                self.zoom_label.setText(f"확대뷰\n오류")
    
    def mousePressEvent(self, event):
        """마우스 클릭 시작"""
        # 모든 마우스 이벤트를 받아서 처리
        event.accept()
        
        if event.button() == Qt.MouseButton.LeftButton:
            # 정보 패널 클릭 무시
            if hasattr(self, 'info_panel') and self.info_panel.geometry().contains(event.pos()):
                return
                
            self.selection_start = event.pos()
            self.selection_end = None
            self.is_selecting = True
            self.grabMouse()  # 마우스 캡처
            
    def mouseMoveEvent(self, event):
        """마우스 이동 중"""
        event.accept()
        
        if self.is_selecting and self.selection_start:
            self.selection_end = event.pos()
            self.update()
            
    def mouseReleaseEvent(self, event):
        """마우스 클릭 종료"""
        event.accept()
        
        if hasattr(self, 'is_selecting') and self.is_selecting:
            self.releaseMouse()  # 마우스 캡처 해제
            
        if event.button() == Qt.MouseButton.LeftButton and self.is_selecting:
            self.selection_end = event.pos()
            self.is_selecting = False
            self.update()
            
            # 드래그가 완료되면 자동으로 확정 (최소 크기 체크)
            if self.selection_start and self.selection_end:
                # 최소 5x5 픽셀 이상일 때만 자동 확정
                width = abs(self.selection_end.x() - self.selection_start.x())
                height = abs(self.selection_end.y() - self.selection_start.y())
                if width >= 5 and height >= 5:
                    # 0.5초 후 자동 확정 (사용자가 결과를 볼 수 있도록)
                    QTimer.singleShot(500, self.confirm_selection)
                else:
                    # 너무 작은 영역은 선택 취소
                    self.selection_start = None
                    self.selection_end = None
                    self.update()
            
    def keyPressEvent(self, event):
        """키보드 이벤트"""
        if event.key() == Qt.Key.Key_Escape:
            event.accept()
            # ESC 시 좌표 선택 취소 시그널 발생
            self.coordinates_selected.emit(-1, -1, -1, -1)  # 취소를 나타내는 특수 값
            self.close()
        else:
            event.ignore()
            
    def confirm_selection(self):
        """선택 확정"""
        if self.selection_start and self.selection_end:
            # 위젯 상대 좌표를 전역 좌표로 변환
            start_global = self.mapToGlobal(self.selection_start)
            end_global = self.mapToGlobal(self.selection_end)
            
            # 모니터 상대 좌표로 변환 (실제 캡처에 사용될 좌표)
            x1 = start_global.x() - self.current_monitor['left']
            y1 = start_global.y() - self.current_monitor['top']
            x2 = end_global.x() - self.current_monitor['left']
            y2 = end_global.y() - self.current_monitor['top']
            
            # 좌표 정규화 (좌상단이 더 작은 값이 되도록)
            min_x, max_x = min(x1, x2), max(x1, x2)
            min_y, max_y = min(y1, y2), max(y1, y2)
            
            print(f"Confirmed selection: ({min_x}, {min_y}) to ({max_x}, {max_y}) on monitor {self.selected_monitor_index}")
            
            self.coordinates_selected.emit(min_x, min_y, max_x, max_y)
            self.close()
            
    def paintEvent(self, event):
        """화면 그리기"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # 십자선 그리기
        self.draw_crosshair(painter)
        
        # 선택 영역 그리기
        if self.selection_start and (self.selection_end or self.is_selecting):
            self.draw_selection(painter)
            
    def draw_crosshair(self, painter):
        """십자선 그리기"""
        pen = QPen(QColor(0, 113, 227), 1, Qt.PenStyle.DotLine)
        painter.setPen(pen)
        
        # 세로선
        painter.drawLine(self.current_pos.x(), 0, self.current_pos.x(), self.height())
        # 가로선  
        painter.drawLine(0, self.current_pos.y(), self.width(), self.current_pos.y())
        
    def draw_selection(self, painter):
        """선택 영역 그리기"""
        if not self.selection_start:
            return
            
        end_pos = self.selection_end if self.selection_end else self.current_pos
        
        # 선택 영역 사각형
        rect = QRect(self.selection_start, end_pos).normalized()
        
        # 선택 영역 테두리
        pen = QPen(QColor(0, 113, 227), 2, Qt.PenStyle.SolidLine)
        painter.setPen(pen)
        painter.drawRect(rect)
        
        # 선택 영역 반투명 채우기
        painter.fillRect(rect, QColor(0, 113, 227, 30))
        
        # 모서리 핸들 그리기
        handle_size = 6
        handle_color = QColor(0, 113, 227)
        painter.fillRect(rect.topLeft().x() - handle_size//2, 
                        rect.topLeft().y() - handle_size//2, 
                        handle_size, handle_size, handle_color)
        painter.fillRect(rect.bottomRight().x() - handle_size//2, 
                        rect.bottomRight().y() - handle_size//2, 
                        handle_size, handle_size, handle_color)
        painter.fillRect(rect.topRight().x() - handle_size//2, 
                        rect.topRight().y() - handle_size//2, 
                        handle_size, handle_size, handle_color)
        painter.fillRect(rect.bottomLeft().x() - handle_size//2, 
                        rect.bottomLeft().y() - handle_size//2, 
                        handle_size, handle_size, handle_color)
    
    def closeEvent(self, event):
        """창 닫기 시 정리"""
        # 마우스 캡처 해제
        if hasattr(self, 'is_selecting') and self.is_selecting:
            self.releaseMouse()
            
        # 타이머 정리
        if hasattr(self, 'timer'):
            self.timer.stop()
            
        super().closeEvent(event)