FROM runpod/pytorch:2.4.0-py3.11-cuda12.4.1-devel-ubuntu22.04

RUN apt-get update

WORKDIR /app

RUN pip install --no-cache-dir --no-deps qwen-tts

# Install RunPod SDK
RUN pip install --no-cache-dir runpod \
    torchaudio \
    soundfile \
    huggingface_hub \
    gradio \
    numpy \
    scipy \
    transformers \
    accelerate \
    librosa \
    soundfile \
    pydub

# Copy handler
COPY handler.py /app/handler.py

# Start handler

CMD ["python", "-u", "/app/handler.py"]

