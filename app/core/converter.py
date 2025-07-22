"""
PDF 변환 유틸리티 모듈
"""

import os
from PIL import Image


class PDFConverter:
    """PDF 변환기 클래스"""
    
    @staticmethod
    def convert_images_to_pdf(page_count, output_path, input_dir="img"):
        """
        캡처된 이미지들을 하나의 PDF 파일로 변환
        
        Args:
            page_count: 변환할 페이지 수
            output_path: 출력 PDF 파일 경로
            input_dir: 입력 이미지가 저장된 디렉토리
            
        Returns:
            bool: 변환 성공 여부
        """
        try:
            images = []
            for i in range(page_count):
                image_path = os.path.join(input_dir, f"page_{i+1}.png")
                if os.path.exists(image_path):
                    images.append(Image.open(image_path))
            
            if not images:
                return False
                
            # 300 DPI 해상도로 PDF 생성
            images[0].save(
                output_path,
                save_all=True,
                append_images=images[1:],
                resolution=300.0
            )
            
            return True
            
        except Exception as e:
            print(f"PDF 변환 중 오류 발생: {e}")
            return False
    
    @staticmethod
    def cleanup_temp_images(page_count, input_dir="img"):
        """
        임시 이미지 파일들을 정리
        
        Args:
            page_count: 정리할 페이지 수
            input_dir: 이미지가 저장된 디렉토리
        """
        try:
            for i in range(page_count):
                image_path = os.path.join(input_dir, f"page_{i+1}.png")
                if os.path.exists(image_path):
                    os.remove(image_path)
        except Exception as e:
            print(f"임시 파일 정리 중 오류 발생: {e}")