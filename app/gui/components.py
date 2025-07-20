"""
UI 컴포넌트 모듈
"""

from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel


class UISection:
    """UI 섹션 생성 유틸리티"""
    
    @staticmethod
    def create_section(title):
        """
        UI 섹션 생성
        
        Args:
            title: 섹션 제목
            
        Returns:
            tuple: (섹션 위젯, 컨텐츠 레이아웃) 튜플
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


class StyleManager:
    """스타일 관리 클래스"""
    
    @staticmethod
    def get_main_stylesheet():
        """메인 윈도우 스타일시트 반환"""
        return """
            QMainWindow {
                background-color: #f5f5f7;
            }
            QLabel {
                font-size: 12px;
                color: #1d1d1f;
            }
            QPushButton {
                background-color: #0071e3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                font-size: 12px;
                font-weight: 500;
            }
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox {
                border: 1px solid #d2d2d7;
                border-radius: 4px;
                padding: 4px 8px;
                background-color: white;
                font-size: 12px;
                min-height: 20px;
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
                min-height: 60px;
                font-size: 12px;
                qproperty-alignment: AlignCenter;
                margin: 5px 0;
            }
        """
    
    @staticmethod
    def get_error_progressbar_style():
        """오류 상태 프로그레스바 스타일 반환"""
        return """
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
        """
    
    @staticmethod
    def get_normal_progressbar_style():
        """정상 상태 프로그레스바 스타일 반환"""
        return """
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
        """