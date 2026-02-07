import os
from pydub import AudioSegment
import openai
from faster_whisper import WhisperModel

# --- 1. 오디오 최적화 파이프라인 (업그레이드 버전) ---
def optimize_audio(input_path, output_folder="data/storage"):
    """
    [기능 개선]
    1. 16kHz Mono 변환 (Whisper 최적화)
    2. Normalize (볼륨 평준화)
    3. High-pass Filter (200Hz 이하 잡음 제거)
    4. MP3 64k 저장 (용량 최적화)
    """
    os.makedirs(output_folder, exist_ok=True)
    
    # 파일명 생성
    filename = os.path.basename(input_path)
    name_without_ext = os.path.splitext(filename)[0]
    output_path = os.path.join(output_folder, f"{name_without_ext}_optimized.mp3")
    
    try:
        # 오디오 로드
        audio = AudioSegment.from_file(input_path)
        
        # [최적화 1] 채널을 Mono로, 샘플링 레이트를 16000Hz로 변경 (Whisper 표준)
        audio = audio.set_channels(1).set_frame_rate(16000)
        
        # [최적화 2] 볼륨 정규화 (너무 작거나 큰 소리 평준화)
        audio = effects.normalize(audio)
        
        # [최적화 3] High-pass Filter (200Hz 이하의 웅웅거리는 저음 노이즈 제거)
        # 사람 목소리는 보통 300Hz~3400Hz 대역에 있습니다.
        audio = audio.high_pass_filter(200)

        # [최적화 4] 압축 저장 (64k는 음성 인식에 충분한 음질)
        audio.export(output_path, format="mp3", bitrate="64k")
        
        # 원본 삭제 (Privacy & Storage Efficient)
        if os.path.exists(input_path):
            os.remove(input_path)
            
        print(f"✅ Audio optimized: {output_path}")
        return output_path

    except Exception as e:
        print(f"❌ Error optimizing audio: {e}")
        return None
# --- 2. AI Refiner (검토 요청) ---
def refine_text_with_ai(text, api_key, prompt_type="fix"):
    """
    [명세서 1. AI Engine] Refiner: Gemini/OpenAI API 연동
    """
    if not api_key:
        return "API Key가 설정되지 않았습니다."

    client = openai.OpenAI(api_key=api_key) # OpenAI 호환 클라이언트
    
    system_prompts = {
        "fix": "너는 전문 에디터야. 아래 텍스트의 오탈자를 수정하고 문맥을 자연스럽게 다듬어줘.",
        "summarize": "너는 회의록 서기야. 아래 내용을 핵심 요약(Bullet point) 해줘.",
        "action_item": "아래 내용에서 '할 일(Action Item)'만 추출해서 목록으로 만들어줘."
    }

    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini", # 또는 Gemini 모델명
            messages=[
                {"role": "system", "content": system_prompts.get(prompt_type, "fix")},
                {"role": "user", "content": text}
            ]
        )
        return response.choices[0].message.content
    except Exception as e:
        return f"AI 호출 오류: {e}"