# Voice Clone Serverless (Qwen3-TTS)

[![RunPod](https://img.shields.io/badge/RunPod-Serverless-purple?style=flat-square&logo=runpod)](https://runpod.io/console/serverless)

RunPod Serverless worker for Qwen3-TTS with voice cloning capabilities.

## Capabilities

- **Text-to-Speech** - High-quality speech synthesis using Qwen3-TTS-12Hz-1.7B-Base.
- **Voice Cloning** - Clone any voice from a reference audio sample (URL or Base64).
- **Auto Language Detection** - Automatically detects language from input text.

## Deployment on RunPod

### 1. Build & Push Docker Image

```bash
docker build -t your-username/voice-clone-serverless .
docker push your-username/voice-clone-serverless
```

### 2. Create Serverless Endpoint

1. Go to **Serverless > New Endpoint** on RunPod.
2. **Container Image**: Your pushed image (e.g., `your-username/voice-clone-serverless`).
3. **GPU**: Recommended **RTX 3090** or **RTX 4090** (24GB VRAM recommended for 1.7B model inference).
4. **Container Disk**: 10GB+ (Model is downloaded at runtime/build).
5. **Environment Variables**: None required (Model is standard Qwen3-TTS).

## API Usage



### Voice Cloning (via URL)

**Required**: When using reference audio, you MUST provide `reference_text` matching the audio content.

```json
{
  "input": {
    "text": "This is my cloned voice speaking a new sentence.",
    "reference_audio_url": "https://example.com/audio/sample_voice.wav",
    "reference_text": "The content of the sample voice audio file."
  }
}
```

### Voice Cloning (via Base64)

```json
{
  "input": {
    "text": "This is my cloned voice speaking a new sentence.",
    "reference_audio_base64": "UklGRi...",
    "reference_text": "The content of the sample voice audio file."
  }
}
```

## Response Format

The worker returns the generated audio as a Base64 encoded WAV file.

```json
{
  "audio_base64": "UklGRi...",
  "sample_rate": 24000,
  "duration": 5.25,
  "text": "This is my cloned voice speaking a new sentence."
}
```

## Error Handling

If `reference_audio` is provided without `reference_text` (or vice-versa), the API will return an error:

```json
{
  "error": "reference_text is required when using reference audio"
}
```

## Local Development

### Prerequisites

- NVIDIA GPU with CUDA support
- Docker with NVIDIA Container Toolkit

### Build & Run

```bash
# Build the image
docker build -t voice-clone-serverless .

# Run the container
docker run --gpus all -p 8000:8000 voice-clone-serverless
```
