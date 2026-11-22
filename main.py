import json
import asyncio
import os

import edge_tts
from PIL import Image, ImageDraw, ImageFont
from moviepy import AudioFileClip, ImageClip, concatenate_videoclips

# BilimX video üretim sistemi
WIDTH = 1920
HEIGHT = 1080
FPS = 24

os.makedirs("output", exist_ok=True)
os.makedirs("audio", exist_ok=True)


def get_font(size):
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf"
    ]

    for path in paths:
        if os.path.exists(path):
            return ImageFont.truetype(path, size)

    return ImageFont.load_default()


def create_scene_image(scene, index):
    image = Image.new(
        "RGB",
        (WIDTH, HEIGHT),
        (8, 15, 35)
    )

    draw = ImageDraw.Draw(image)

    # Sinematik arka plan çizgileri
    for y in range(0, HEIGHT, 100):
        draw.line(
            (0, y, WIDTH, y),
            fill=(15, 35, 65),
            width=2
        )

    title = scene.get("visual", "BilimX")
    font = get_font(75)

    draw.text(
        (WIDTH // 2, HEIGHT // 2),
        title,
        font=font,
        fill=(255, 255, 255),
        anchor="mm"
    )

    draw.text(
        (70, 70),
        "BILIMX",
        font=get_font(45),
        fill=(0, 200, 255)
    )

    draw.text(
        (WIDTH - 70, HEIGHT - 70),
        f"SAHNE {index}",
        font=get_font(30),
        fill=(180, 200, 220),
        anchor="rs"
    )

    path = f"output/scene_{index}.png"
    image.save(path)

    return path


async def create_voice(text, path):
    voice = edge_tts.Communicate(
        text=text,
        voice="tr-TR-AhmetNeural",
        rate="-5%"
    )

    await voice.save(path)


def main():
    with open("video_plan.json", "r", encoding="utf-8") as file:
        plan = json.load(file)

    clips = []

    for scene in plan["scenes"]:
        index = scene["scene"]
        duration = scene["duration"]

        print(f"Sahne {index} hazırlanıyor...")

        image_path = create_scene_image(scene, index)

        audio_path = f"audio/scene_{index}.mp3"

        asyncio.run(
            create_voice(
                scene["narration"],
                audio_path
            )
        )

        audio = AudioFileClip(audio_path)

        clip = ImageClip(image_path).with_duration(duration)

        clip = clip.with_audio(audio)

        clips.append(clip)

    final_video = concatenate_videoclips(
        clips,
        method="compose"
    )

    final_video.write_videofile(
        "output/bilimx_video.mp4",
        fps=FPS,
        codec="libx264",
        audio_codec="aac"
    )

    print("Video hazır: output/bilimx_video.mp4")


if __name__ == "__main__":
    main()
