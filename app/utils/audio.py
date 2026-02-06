import os
import subprocess
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def optimize_audio(input_path: str, output_dir: str = None) -> str:
    """
    오디오 파일을 최적화된 MP3 포맷(Mono, 16kHz, 64k)으로 변환하고 원본은 삭제합니다.
    """
    if not os.path.exists(input_path):
        raise FileNotFoundError(f"파일을 찾을 수 없습니다: {input_path}")

    # 파일명 및 경로 설정
    base_name = os.path.splitext(os.path.basename(input_path))[0]
    if output_dir is None:
        output_dir = os.path.dirname(input_path)
    
    output_path = os.path.join(output_dir, f"{base_name}_optimized.mp3")

    # FFmpeg 명령어 구성 (N100 CPU 부하를 줄이기 위해 가벼운 옵션 사용)
    # -ac 1: 모노 채널 (회의록은 스테레오 불필요)
    # -ar 16000: 16kHz 샘플링 (Whisper에 최적화된 주파수)
    # -b:a 64k: 비트레이트 64kbps (용량 절약)
    command = [
        "ffmpeg",
        "-y",               # 덮어쓰기 허용
        "-i", input_path,   # 입력 파일
        "-ac", "1",
        "-ar", "16000",
        "-b:a", "64k",
        output_path
    ]

    try:
        logger.info(f"🔄 오디오 변환 시작: {input_path} -> {output_path}")
        # FFmpeg 실행 (출력 숨김)
        subprocess.run(command, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        
        # 변환 성공 시 원본 삭제 (용량 확보)
        if os.path.exists(output_path) and os.path.getsize(output_path) > 0:
            os.remove(input_path)
            logger.info(f"✅ 변환 완료 및 원본 삭제됨: {base_name}")
            return output_path
        else:
            raise Exception("변환된 파일이 비어있습니다.")

    except subprocess.CalledProcessError as e:
        logger.error(f"❌ FFmpeg 변환 오류: {e}")
        return input_path # 실패 시 원본 경로 반환
    except Exception as e:
        logger.error(f"❌ 알 수 없는 오류: {e}")
        return input_path