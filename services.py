import os
from pydub import AudioSegment
import openai
from faster_whisper import WhisperModel

# --- 1. 오디오 최적화 파이프라인 ---
def optimize_audio(input_path, output_folder="data/storage"):
    """
    [명세서 3-2] Optimize: FFmpeg로 mp3 64k mono 변환 -> 원본 삭제 로직 포함
    """
    os.makedirs(output_folder, exist_ok=True)
    
    # 파일명 생성
    filename = os.path.basename(input_path)
    name_without_ext = os.path.splitext(filename)[0]
    output_path = os.path.join(output_folder, f"{name_without_ext}_optimized.mp3")
    
    try:
        audio = AudioSegment.from_file(input_path)
        
        # 64k, mono(1 channel), 22050Hz 변환
        audio = audio.set_channels(1).set_frame_rate(22050)
        audio.export(output_path, format="mp3", bitrate="64k")
        
        # 원본 삭제 (Privacy & Storage Efficient)
        if os.path.exists(input_path):
            os.remove(input_path)
            
        return output_path
    except Exception as e:
        print(f"Error optimizing audio: {e}")
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