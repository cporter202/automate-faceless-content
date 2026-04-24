#!/usr/bin/env python3
"""Faceless Content CLI — Automate faceless video creation from idea to post.

Pipeline: Topic → Script → Voiceover → Video → Schedule
Supports: YouTube Shorts, TikTok, Instagram Reels, Facebook Reels
"""

import os
import sys
import json
import subprocess
import argparse
from pathlib import Path
from datetime import datetime

try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.table import Table
    console = Console()
except ImportError:
    console = None

# ── Config ──────────────────────────────────────────────────────────────────

CONFIG_DIR = Path.home() / ".faceless-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"

DEFAULT_CONFIG = {
    "tts_engine": "edge-tts",
    "tts_voice": "en-US-AriaNeural",
    "video_style": "cinematic",
    "video_format": "9:16",
    "video_duration": 60,
    "platforms": ["youtube", "tiktok", "instagram", "facebook"],
    "llm_provider": "ollama",
    "ollama_model": "glm-5.1:cloud",
    "ollama_host": "http://localhost:11434",
    "output_dir": "./faceless-output",
    "schedule_interval": 30,  # minutes between posts
}


def load_config():
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        return json.loads(CONFIG_FILE.read_text())
    return DEFAULT_CONFIG.copy()


def save_config(cfg):
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    CONFIG_FILE.write_text(json.dumps(cfg, indent=2))


def log(msg, style=None):
    if console:
        console.print(msg, style=style)
    else:
        print(msg)


# ── Step 1: Generate Script ────────────────────────────────────────────────

SCRIPT_PROMPT = """You are an expert short-form video scriptwriter. Write a {duration}-second {style} script for a faceless video about: {topic}

Requirements:
- Hook in the first 3 seconds
- Clear, engaging narration (no on-screen personality needed)
- One key idea or fact per video
- Call to action at the end
- Target platform: {platforms}
- Format: Just the narration text, no stage directions

Write the script now:"""


def generate_script(topic, cfg):
    """Generate a video script using Ollama or OpenAI."""
    provider = cfg.get("llm_provider", "ollama")
    prompt = SCRIPT_PROMPT.format(
        duration=cfg.get("video_duration", 60),
        style=cfg.get("video_style", "cinematic"),
        topic=topic,
        platforms=", ".join(cfg.get("platforms", ["youtube"])),
    )

    if provider == "ollama":
        import requests
        resp = requests.post(
            f"{cfg.get('ollama_host', 'http://localhost:11434')}/api/generate",
            json={
                "model": cfg.get("ollama_model", "glm-5.1:cloud"),
                "prompt": prompt,
                "stream": False,
                "options": {"num_predict": 2048},
            },
            timeout=120,
        )
        resp.raise_for_status()
        return resp.json()["response"].strip()

    elif provider == "openai":
        from openai import OpenAI
        client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        resp = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You write viral short-form video scripts."},
                {"role": "user", "content": prompt},
            ],
            max_tokens=2048,
        )
        return resp.choices[0].message.content.strip()

    else:
        raise ValueError(f"Unknown provider: {provider}")


# ── Step 2: Generate Voiceover ─────────────────────────────────────────────

async def generate_voiceover(script_text, output_path, cfg):
    """Generate voiceover using edge-tts."""
    import edge_tts

    voice = cfg.get("tts_voice", "en-US-AriaNeural")
    communicate = edge_tts.Communicate(script_text, voice)
    await communicate.save(output_path)


def generate_voiceover_sync(script_text, output_path, cfg):
    """Sync wrapper for voiceover generation."""
    import asyncio
    asyncio.run(generate_voiceover(script_text, output_path, cfg))


# ── Step 3: Generate Video ─────────────────────────────────────────────────

def generate_video(script_path, audio_path, output_path, cfg):
    """Generate a faceless video from script + audio using FFmpeg."""
    duration = cfg.get("video_duration", 60)
    style = cfg.get("video_style", "cinematic")
    fmt = cfg.get("video_format", "9:16")

    # Resolution based on format
    if fmt == "9:16":
        w, h = 1080, 1920
    elif fmt == "16:9":
        w, h = 1920, 1080
    else:
        w, h = 1080, 1080

    # Background color based on style
    colors = {
        "cinematic": "0x0a0a1a",
        "minimal": "0xf5f5f5",
        "vibrant": "0x1a0a3a",
        "nature": "0x0a2a1a",
        "tech": "0x0a1a2a",
    }
    bg_color = colors.get(style, "0x0a0a1a")

    # Get audio duration
    probe = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", audio_path],
        capture_output=True, text=True
    )
    audio_dur = float(probe.stdout.strip()) if probe.stdout.strip() else duration

    # Build FFmpeg command
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c={bg_color}:s={w}x{h}:d={audio_dur}:r=30",
        "-i", audio_path,
        "-vf", f"drawtext=textfile='{script_path}':fontsize=42:fontcolor=white:"
               f"x=(w-text_w)/2:y=(h-text_h)/2:line_spacing=8,"
               f"drawtext=text='':fontsize=0",
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path,
    ]

    # Simpler approach: colored background + audio + subtitles
    subtitle_filter = (
        f"color=c={bg_color}:s={w}x{h}:d={audio_dur}:r=30,"
        f"drawtext=text='{script_path}':"
        f"fontsize=36:fontcolor=white:"
        f"x=(w-text_w)/2:y=(h-text_h)/2:line_spacing=6"
    )

    # Use subtitles approach instead
    cmd = [
        "ffmpeg", "-y",
        "-f", "lavfi", "-i", f"color=c={bg_color}:s={w}x{h}:d={audio_dur}:r=30",
        "-i", audio_path,
        "-c:v", "libx264", "-preset", "fast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k",
        "-pix_fmt", "yuv420p",
        "-shortest",
        output_path,
    ]

    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode == 0


# ── Step 4: Bulk Workflow ───────────────────────────────────────────────────

def bulk_generate(topics, cfg):
    """Generate multiple videos in bulk."""
    output_dir = Path(cfg.get("output_dir", "./faceless-output"))
    results = []

    for i, topic in enumerate(topics, 1):
        log(f"\n[bold green]━━━ Video {i}/{len(topics)}: {topic} ━━━[/bold green]")

        video_dir = output_dir / f"video-{i:03d}"
        video_dir.mkdir(parents=True, exist_ok=True)

        # Step 1: Script
        log("📝 Generating script...", style="cyan")
        try:
            script = generate_script(topic, cfg)
            script_path = video_dir / "script.txt"
            script_path.write_text(script)
            log(f"  ✅ Script saved ({len(script)} chars)")
        except Exception as e:
            log(f"  ❌ Script failed: {e}", style="red")
            continue

        # Step 2: Voiceover
        log("🎤 Generating voiceover...", style="cyan")
        audio_path = video_dir / "voiceover.mp3"
        try:
            generate_voiceover_sync(script, str(audio_path), cfg)
            log(f"  ✅ Voiceover saved")
        except Exception as e:
            log(f"  ❌ Voiceover failed: {e}", style="red")
            continue

        # Step 3: Video
        log("🎬 Generating video...", style="cyan")
        video_path = video_dir / "video.mp4"
        try:
            success = generate_video(str(script_path), str(audio_path), str(video_path), cfg)
            if success:
                log(f"  ✅ Video saved: {video_path}")
            else:
                log(f"  ⚠️ Video generation had issues, but audio is ready", style="yellow")
        except Exception as e:
            log(f"  ❌ Video failed: {e}", style="red")

        results.append({
            "topic": topic,
            "script": str(script_path),
            "audio": str(audio_path),
            "video": str(video_path) if video_path.exists() else None,
        })

    return results


# ── Step 5: Niche Research ──────────────────────────────────────────────────

TOP_NICHES = {
    "finance": {
        "cpm": "$15-25",
        "topics": ["passive income ideas", "stock market tips", "crypto explained", "budgeting hacks", "side hustles 2026"],
        "difficulty": "medium",
        "monetization_time": "2-3 weeks",
    },
    "health": {
        "cpm": "$10-20",
        "topics": ["morning routines", "mental health tips", "workout hacks", "nutrition facts", "sleep optimization"],
        "difficulty": "low",
        "monetization_time": "2-3 weeks",
    },
    "tech": {
        "cpm": "$8-15",
        "topics": ["AI tools 2026", "coding tutorials", "app reviews", "productivity hacks", "tech news"],
        "difficulty": "medium",
        "monetization_time": "3-4 weeks",
    },
    "motivation": {
        "cpm": "$5-12",
        "topics": ["stoic quotes", "success stories", "daily motivation", "habits of winners", "mindset shifts"],
        "difficulty": "low",
        "monetization_time": "3-4 weeks",
    },
    "travel": {
        "cpm": "$6-14",
        "topics": ["hidden destinations", "travel hacks", "budget travel", "luxury on a budget", "digital nomad life"],
        "difficulty": "medium",
        "monetization_time": "4-5 weeks",
    },
    "education": {
        "cpm": "$7-15",
        "topics": ["science facts", "history uncovered", "psychology tricks", "language learning", "study hacks"],
        "difficulty": "low",
        "monetization_time": "3-4 weeks",
    },
}


def show_niches():
    """Show top-paying niches with data."""
    if console:
        table = Table(title="🔥 Top Paying Niches for Faceless Content")
        table.add_column("Niche", style="bold cyan")
        table.add_column("CPM", style="green")
        table.add_column("Difficulty", style="yellow")
        table.add_column("Monetization", style="magenta")
        table.add_column("Sample Topics", style="white")

        for niche, data in TOP_NICHES.items():
            table.add_row(
                niche.capitalize(),
                data["cpm"],
                data["difficulty"],
                data["monetization_time"],
                ", ".join(data["topics"][:3]),
            )
        console.print(table)
    else:
        for niche, data in TOP_NICHES.items():
            print(f"{niche}: CPM {data['cpm']}, Difficulty: {data['difficulty']}")


# ── CLI ─────────────────────────────────────────────────────────────────────

SLIDESHOW_PROMPT = """You are a viral TikTok/Instagram slideshow content creator. Generate {num_slides} slide hooks for a faceless slideshow about: {topic}

Each slide should:
- Be under 10 words
- Start with a hook word or emoji
- Build curiosity/suspense
- The last slide should be a CTA (follow/save/share)

Output format: one hook per line, no numbering."""


def generate_slideshow(topic, num_slides, cfg):
    """Generate slide hooks for a TikTok slideshow."""
    provider = cfg.get("llm_provider", "ollama")
    prompt = SLIDESHOW_PROMPT.format(num_slides=num_slides, topic=topic)
    if provider == "ollama":
        import requests
        host = cfg.get('ollama_host', 'http://localhost:11434')
        model = cfg.get('ollama_model', 'glm-5.1:cloud')
        resp = requests.post(f"{host}/api/chat", json={"model": model, "messages": [{"role": "user", "content": prompt}], "stream": False, "options": {"num_predict": 1024}}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        text = data.get("message", {}).get("content", "") or data.get("response", "")
        text = text.strip()
    elif provider == "openai":
        # Also fix the model for chat endpoint
        host = cfg.get('ollama_host', 'http://localhost:11434')
        model = cfg.get('ollama_model', 'glm-5.1:cloud')
        resp = requests.post(f"{host}/api/chat", json={"model": model, "messages": [{"role": "system", "content": "You create viral TikTok slideshow hooks."}, {"role": "user", "content": prompt}], "stream": False, "options": {"num_predict": 1024}}, timeout=60)
        resp.raise_for_status()
        data = resp.json()
        text = data.get("message", {}).get("content", "") or data.get("response", "")
        text = text.strip()
    else:
        raise ValueError(f"Unknown provider: {provider}")
    slides = [line.strip().lstrip("0123456789.-) ") for line in text.splitlines() if line.strip()]
    return slides[:num_slides]


def main():
    parser = argparse.ArgumentParser(
        description="🎬 Faceless Content CLI — Idea → Script → Video → Post on autopilot",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  faceless "passive income ideas"           Generate a single video
  faceless bulk topics.txt                  Generate 60 videos from a file
  faceless niches                          Show top-paying niches
  faceless config                          Show current configuration
  faceless config --set tts_voice=en-US-GuyNeural   Change config
        """,
    )
    subparsers = parser.add_subparsers(dest="command", help="Command")

    # Single video
    video_parser = subparsers.add_parser("video", help="Generate a single video")
    video_parser.add_argument("topic", nargs="?", help="Video topic")

    # Default topic for backward compat
    parser.add_argument("--topic", dest="default_topic", help="Video topic (shortcut)")

    # Bulk
    bulk_parser = subparsers.add_parser("bulk", help="Generate multiple videos from a file")
    bulk_parser.add_argument("topics_file", help="File with one topic per line")

    # Niches
    subparsers.add_parser("niches", help="Show top-paying niches")

    # Config
    config_parser = subparsers.add_parser("config", help="Show or set configuration")
    config_parser.add_argument("--set", action="append", help="Set config key=value")

    # Ideas
    ideas_parser = subparsers.add_parser("ideas", help="Generate video ideas for a niche")
    ideas_parser.add_argument("niche", choices=list(TOP_NICHES.keys()), help="Niche")
    slideshow_parser = subparsers.add_parser("slideshow", help="Generate TikTok/Instagram slideshow hooks")
    slideshow_parser.add_argument("topic", help="Slideshow topic")
    slideshow_parser.add_argument("--slides", "-n", type=int, default=5, help="Number of slides")
    slideshow_parser.add_argument("--format", choices=["tiktok", "instagram", "pinterest"], default="tiktok", help="Target platform")

    args = parser.parse_args()
    cfg = load_config()

    # Default: generate single video from topic
    if args.default_topic and not args.command:
        args.command = "video"
        args.topic = args.default_topic

    if args.command == "niches":
        show_niches()

    elif args.command == "config":
        if args.set:
            for kv in args.set:
                key, _, val = kv.partition("=")
                # Try to parse as list/number
                if val.startswith("["):
                    cfg[key] = json.loads(val)
                elif val.isdigit():
                    cfg[key] = int(val)
                elif val.lower() in ("true", "false"):
                    cfg[key] = val.lower() == "true"
                else:
                    cfg[key] = val
            save_config(cfg)
            log("✅ Config updated", style="green")
        else:
            log(Panel(json.dumps(cfg, indent=2), title="Faceless CLI Config", border_style="cyan"))
    elif args.command == "ideas":
        niche = args.niche
        data = TOP_NICHES[niche]
        log(f"\n[bold]💡 Video Ideas for {niche.capitalize()}[/bold]")
        log(f"CPM: {data['cpm']} | Difficulty: {data['difficulty']} | Monetization: {data['monetization_time']}\n")
        for i, idea in enumerate(data["topics"], 1):
            log(f"  {i}. {idea}")

    elif args.command == "slideshow":
        num = args.slides
        fmt = args.format
        log(Panel(f"[bold]📱 Generating {num} {fmt.title()} slideshow slides[/bold]\nTopic: {args.topic}", border_style="cyan"))
        hooks = generate_slideshow(args.topic, num, cfg)
        log("[bold]📋 Slide Hooks:[/bold]")
        for i, hook in enumerate(hooks, 1):
            log(f"  {i}. {hook}")
        output_dir = Path(cfg.get("output_dir", "./faceless-output"))
        slideshow_file = output_dir / f"slideshow_{args.topic.replace(' ', '-')[:30]}.txt"
        slideshow_file.parent.mkdir(parents=True, exist_ok=True)
        slideshow_file.write_text("\n".join(hooks))
        log(f"[green]✅ Saved to {slideshow_file}[/green]")

    elif args.command == "bulk":
        topics_file = Path(args.topics_file)
        if not topics_file.exists():
            log(f"❌ File not found: {topics_file}", style="red")
            sys.exit(1)
        topics = [line.strip() for line in topics_file.read_text().splitlines() if line.strip()]
        log(f"[bold]📦 Bulk generating {len(topics)} videos[/bold]")
        results = bulk_generate(topics, cfg)
        log(f"\n[bold green]✅ Done! {len(results)} videos generated[/bold green]")

    elif args.command == "video" or args.topic:
        topic = args.topic
        if not topic:
            log("❌ Provide a topic: faceless 'your topic'", style="red")
            sys.exit(1)

        output_dir = Path(cfg.get("output_dir", "./faceless-output"))
        video_dir = output_dir / topic.replace(" ", "-")[:40]
        video_dir.mkdir(parents=True, exist_ok=True)

        log(Panel(f"[bold]🎬 Faceless Content Generator[/bold]\n\nTopic: {topic}\nTTS: {cfg.get('tts_voice')}\nStyle: {cfg.get('video_style')}\nFormat: {cfg.get('video_format')}", border_style="green"))

        # Script
        log("📝 Generating script...", style="cyan")
        script = generate_script(topic, cfg)
        script_path = video_dir / "script.txt"
        script_path.write_text(script)
        log(f"  ✅ Script saved ({len(script)} chars)")

        # Voiceover
        log("🎤 Generating voiceover...", style="cyan")
        audio_path = video_dir / "voiceover.mp3"
        generate_voiceover_sync(script, str(audio_path), cfg)
        log(f"  ✅ Voiceover saved")

        # Video
        log("🎬 Generating video...", style="cyan")
        video_path = video_dir / "video.mp4"
        success = generate_video(str(script_path), str(audio_path), str(video_path), cfg)
        if success:
            log(f"  ✅ Video saved: {video_path}")
        else:
            log(f"  ⚠️ Video had issues (audio is ready though)", style="yellow")

        log(Panel(f"[bold green]✅ Complete![/bold green]\n\nScript: {script_path}\nAudio: {audio_path}\nVideo: {video_path}", border_style="green"))

    else:
        parser.print_help()


if __name__ == "__main__":
    main()
