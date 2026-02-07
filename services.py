import os
import requests
from pydub import AudioSegment, effects
import openai
from faster_whisper import WhisperModel

# --- 1. 오디오 최적화 파이프라인 ---
def optimize_audio(input_path, output_folder="data/storage"):
    os.makedirs(output_folder, exist_ok=True)
    filename = os.path.basename(input_path)
    name_without_ext = os.path.splitext(filename)[0]
    output_path = os.path.join(output_folder, f"{name_without_ext}_optimized.mp3")
    
    try:
        audio = AudioSegment.from_file(input_path)
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio = effects.normalize(audio)
        audio = audio.high_pass_filter(200)
        audio.export(output_path, format="mp3", bitrate="64k")
        
        if os.path.exists(input_path):
            os.remove(input_path)
        return output_path
    except Exception as e:
        print(f"❌ Error optimizing audio: {e}")
        return None

# --- 2. AI STT 엔진 (Whisper) ---
def transcribe_audio(model, file_path):
    """
    Faster-Whisper를 사용하여 음성을 텍스트로 변환하고 세그먼트 정보를 반환합니다.
    """
    segments, info = model.transcribe(file_path, beam_size=5)
    
    full_text = ""
    segments_list = []
    
    for segment in segments:
        full_text += segment.text + " "
        segments_list.append({
            "start": round(segment.start, 2),
            "end": round(segment.end, 2),
            "text": segment.text.strip()
        })
    
    return full_text.strip(), segments_list

# --- 3. AI Refiner (Ollama & OpenAI) ---
def refine_text_with_ai(text, config, prompt_type="fix"):
    """
    로컬 Ollama 또는 외부 API를 사용하여 텍스트 분석
    config: { 'ollama_url': ..., 'ollama_model': ..., 'api_key': ... }
    """
    system_prompts = {
        "fix": "너는 전문 에디터야. 아래 텍스트의 오탈자를 수정하고 문맥을 자연스럽게 다듬어줘.",
        "summarize": "너는 문서 요약 전문가야. 아래 내용을 핵심 요약(Bullet point) 해줘.",
        "action_item": "아래 내용에서 주요 키워드나 '중요 사항'을 추출해서 목록으로 만들어줘."
    }
    system_prompt = system_prompts.get(prompt_type, "fix")

    # 1. Ollama 사용 (우선순위)
    if config.get("ollama_url") and config.get("ollama_model"):
        try:
            url = f"{config['ollama_url']}/api/generate"
            payload = {
                "model": config["ollama_model"],
                "prompt": f"{system_prompt}\n\n텍스트: {text}",
                "stream": False
            }
            response = requests.post(url, json=payload, timeout=30)
            if response.status_code == 200:
                return response.json().get("response", "응답 없음")
        except Exception as e:
            print(f"Ollama 호출 실패: {e}")

    # 2. API Key가 있는 경우 OpenAI/Gemini (Fallback)
    if config.get("api_key"):
        client = openai.OpenAI(api_key=config["api_key"])
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"API 호출 오류: {e}"

    return "연결 가능한 AI 엔진(Ollama 또는 API Key)이 없습니다."