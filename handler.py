import runpod
import torch
import soundfile as sf
import base64
import tempfile
import os
import io
import numpy as np

tts_model = None

def load_model():

    global tts_model

    if tts_model is not None:
        return tts_model

    print("[Handler] Loading Qwen3-TTS model...")

    from qwen_tts import Qwen3TTSModel

    tts_model = Qwen3TTSModel.from_pretrained(
        "Qwen/Qwen3-TTS-12Hz-1.7B-Base",
        device_map="cuda:0",
        dtype=torch.bfloat16,
        attn_implementation="flash_attention_2",
    )
    return tts_model

def base64_to_audio_file(b64_data: str) -> str:
    """Convert base64 audio to temp file."""
    # Remove data URL prefix if present
    if "," in b64_data:
        b64_data = b64_data.split(",")[1]

    audio_bytes = base64.b64decode(b64_data)
    temp_file = tempfile.NamedTemporaryFile(suffix=".wav", delete=False)
    temp_file.write(audio_bytes)
    temp_file.close()
    return temp_file.name


def audio_to_base64(audio_array: np.ndarray, sample_rate: int = 24000) -> str:
    """Convert audio array to base64 encoded WAV."""
    buffer = io.BytesIO()
    sf.write(buffer, audio_array, sample_rate, format="WAV")
    buffer.seek(0)
    return base64.b64encode(buffer.read()).decode("utf-8")

def handler(job: dict) -> dict:
    
    job_input = job.get("input", {})
    
    if job_input.get("health_check"):
        return {
            "status": "healthy",
            "message": "Qwen3-TTS handler ready",
            "model_loaded": tts_model is not None
        }

    text = job_input.get("text")

    if not text:
        return {"error": "No text provided"}

    reference_audio_url = job_input.get("reference_audio_url")
    reference_audio_base64 = job_input.get("reference_audio_base64")
    reference_text = job_input.get("reference_text")
    
    # Validate reference audio requirements
    has_reference_audio = bool(reference_audio_url or reference_audio_base64)
    
    if has_reference_audio and not reference_text:
        return {"error": "reference_text is required when using reference audio"}
    
    if not has_reference_audio and reference_text:
        return {"error": "reference_audio_url or reference_audio_base64 is required when providing reference_text"}
    
    ref_audio = None
    temp_audio_file = None
    
    try:
        model = load_model()

        # Handle reference audio
        if reference_audio_url:
            print(f"[Handler] Using reference audio from URL...")
            ref_audio = reference_audio_url
        elif reference_audio_base64:
            print(f"[Handler] Decoding reference audio from base64...")
            temp_audio_file = base64_to_audio_file(reference_audio_base64)
            ref_audio = temp_audio_file

        print(f"[Handler] Generating speech for: {text[:50]}...")

        wavs, sr = model.generate_voice_clone(
            text=text,
            language="auto",
            ref_audio=ref_audio,
            ref_text=reference_text,
        )

        # Convert to base64
        audio_b64 = audio_to_base64(wavs[0], sr)

        return {
            "audio_base64": audio_b64,
            "sample_rate": sr,
            "duration": len(wavs[0]) / sr,
            "text": text,
        }

    except Exception as e:
        print(f"[Handler] Error generating speech: {e}")
        return {"error": str(e)}
    
    finally:
        # Cleanup temp files in finally block to ensure it always runs
        if temp_audio_file and os.path.exists(temp_audio_file):
            try:
                os.unlink(temp_audio_file)
                print(f"[Handler] Cleaned up temp file: {temp_audio_file}")
            except Exception as e:
                print(f"[Handler] Warning: Could not clean up temp file {temp_audio_file}: {e}")

# Pre-load model on worker start
print("[Handler] Pre-loading model...")
try:
    load_model()
except Exception as e:
    print(f"[Handler] Warning: Could not pre-load model: {e}")

# RunPod serverless entry point
runpod.serverless.start({"handler": handler})
