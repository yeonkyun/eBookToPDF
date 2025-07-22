"""
모니터 관리 유틸리티 모듈 (크로스 플랫폼 호환)
"""

import platform
from mss import mss


class MonitorManager:
    """모니터 관리 클래스"""
    
    @staticmethod
    def get_monitors():
        """
        사용 가능한 모니터 정보를 반환 (크로스 플랫폼 호환)
        
        Returns:
            list: 모니터 정보 리스트 (첫 번째 항목 제외)
        """
        try:
            with mss() as sct:
                monitors = sct.monitors[1:]  # 첫 번째는 전체 화면이므로 제외
                
                # 플랫폼별 좌표계 보정
                if platform.system() == "Darwin":  # macOS
                    # macOS는 좌표계가 다를 수 있으므로 추가 처리
                    corrected_monitors = []
                    for monitor in monitors:
                        corrected_monitor = monitor.copy()
                        # macOS에서 음수 좌표 처리
                        if corrected_monitor.get('left', 0) < 0:
                            corrected_monitor['left'] = abs(corrected_monitor['left'])
                        corrected_monitors.append(corrected_monitor)
                    return corrected_monitors
                else:
                    return monitors
                    
        except Exception as e:
            print(f"Monitor detection error: {e}")
            # 기본 모니터 정보 반환
            return [{'left': 0, 'top': 0, 'width': 1920, 'height': 1080}]
    
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
        모니터 정보를 텍스트로 반환 (크로스 플랫폼 호환)
        
        Args:
            monitor_index: 모니터 인덱스
            monitor: 모니터 정보 딕셔너리
            
        Returns:
            str: 모니터 정보 텍스트
        """
        # 플랫폼별 모니터 이름 지정
        if platform.system() == "Darwin":  # macOS
            display_name = f"디스플레이 {monitor_index + 1}"
        elif platform.system() == "Windows":
            display_name = f"모니터 {monitor_index + 1}"
        else:  # Linux
            display_name = f"화면 {monitor_index + 1}"
            
        return f"{display_name}: {monitor['width']}x{monitor['height']}"