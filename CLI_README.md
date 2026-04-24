# 🎬 Faceless Content CLI

**Automate faceless video creation: idea → script → voiceover → video → scheduled posts**

Built on top of [cporter202/automate-faceless-content](https://github.com/cporter202/automate-faceless-content) — the open-source course with 1.8K⭐. This CLI turns the course's manual workflow into a fully automated pipeline.

## Install

```bash
pip install faceless-content-cli[tts]
```

Requires [FFmpeg](https://ffmpeg.org/) for video generation and [Ollama](https://ollama.ai) for local LLM scripts.

## Quick Start

```bash
# Generate a single video
faceless "passive income ideas for 2026"

# Bulk generate 60 videos from a topics file
faceless bulk topics.txt

# Browse top-paying niches
faceless niches

# Get video ideas for a specific niche
faceless ideas finance

# Configure TTS voice, video style, etc.
faceless config --set tts_voice=en-US-GuyNeural
faceless config --set video_format=9:16
```

## Pipeline

```
Topic → LLM Script → Edge-TTS Voiceover → FFmpeg Video → Output
```

1. **Script**: Ollama (local) or OpenAI generates a viral short-form script
2. **Voiceover**: Edge-TTS creates natural narration
3. **Video**: FFmpeg composes background + text + audio
4. **Output**: Ready-to-upload MP4 for YouTube, TikTok, Instagram, Facebook

## Top Niches

| Niche | CPM | Difficulty | Monetization Time |
|-------|-----|-----------|-------------------|
| Finance | $15-25 | Medium | 2-3 weeks |
| Health | $10-20 | Low | 2-3 weeks |
| Tech | $8-15 | Medium | 3-4 weeks |
| Motivation | $5-12 | Low | 3-4 weeks |
| Education | $7-15 | Low | 3-4 weeks |

## Features

- ✅ Local LLM (Ollama) — no API key needed
- ✅ Edge-TTS — free, natural-sounding voices
- ✅ FFmpeg video composition
- ✅ Bulk workflow — 2 hours for 60 videos
- ✅ 6 niche databases with CPM data
- ✅ Configurable voices, styles, formats
- ✅ 9:16 (Shorts/Reels), 16:9, 1:1 formats

## Configuration

```bash
faceless config                              # Show current config
faceless config --set tts_voice=en-US-GuyNeural
faceless config --set video_style=cinematic
faceless config --set video_format=9:16
faceless config --set llm_provider=openai    # Switch to OpenAI
faceless config --set ollama_model=gemma3:12b
```

Config stored at `~/.faceless-cli/config.json`

## Related

- [automate-faceless-content](https://github.com/cporter202/automate-faceless-content) — The full course (1.8K⭐)
- [bonanza-labs](https://pypi.org/project/bonanza-labs/) — AI tools for builders
- [fork-doctor](https://pypi.org/project/fork-doctor/) — Repo health checker

## License

MIT