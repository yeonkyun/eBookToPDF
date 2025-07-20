"""
모니터 관리 유틸리티 모듈
"""

from mss import mss


class MonitorManager:
    """모니터 관리 클래스"""
    
    @staticmethod
    def get_monitors():
        """
        사용 가능한 모니터 정보를 반환
        
        Returns:
            list: 모니터 정보 리스트 (첫 번째 항목 제외)
        """
        with mss() as sct:
            return sct.monitors[1:]
    
    @staticmethod
    def get_monitor_offset(monitor_index=0):
        """
        지정된 모니터의 오프셋 정보를 반환
        
        Args:
            monitor_index: 모니터 인덱스 (0부터 시작)
            
        Returns:
            dict: {'top': int, 'left': int} 형태의 오프셋 정보
        """
        monitors = MonitorManager.get_monitors()
        if 0 <= monitor_index < len(monitors):
            monitor = monitors[monitor_index]
            return {
                'top': monitor['top'],
                'left': monitor['left']
            }
        return {'top': 0, 'left': 0}
    
    @staticmethod
    def get_monitor_info_text(monitor_index, monitor):
        """
        모니터 정보를 텍스트로 반환
        
        Args:
            monitor_index: 모니터 인덱스
            monitor: 모니터 정보 딕셔너리
            
        Returns:
            str: 모니터 정보 텍스트
        """
        return f"모니터 {monitor_index + 1}: {monitor['width']}x{monitor['height']}"