import argparse
from moviepy.editor import AudioFileClip, ImageClip, CompositeVideoClip
import os

def audio_with_static_image(audio_file, image_file, output_video):
    # Check the file extension to determine the audio format
    if audio_file.lower().endswith('.wav'):
        audio = AudioFileClip(audio_file, fps=44100)  # Adjust the FPS as needed for WAV
    elif audio_file.lower().endswith('.m4a'):
        audio = AudioFileClip(audio_file)
    else:
        print("Unsupported audio file format. Please provide a WAV or M4A file.")
        return

    # Create a static image video clip
    image = ImageClip(image_file, duration=audio.duration)

    # Set the audio of the image clip
    video = CompositeVideoClip([image.set_audio(audio)])

    # Determine the output video file path
    if output_video is None:
        base_name, _ = os.path.splitext(audio_file)
        output_video = base_name + "_with_image.mp4"

    # Write the video to the output file with YouTube-compatible settings
    video.write_videofile(
        output_video, 
        codec="libx264",              # H.264 codec
        audio_codec="aac",            # AAC audio codec
        fps=24,                       # Frame rate (24fps is common for YouTube)
        preset='ultrafast',           # Encoding preset (adjust as needed)
        threads=4                     # Number of CPU threads to use for encoding
    )

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Create a video with audio and a static image.")
    parser.add_argument("audio_file", type=str, help="Path to the input audio file (WAV or M4A format).")
    parser.add_argument("image_file", type=str, help="Path to the input image file (PNG or JPG).")
    parser.add_argument("output_video", type=str, nargs='?', default=None, help="Path to the output video file (MP4 format).")
    args = parser.parse_args()

    audio_file = args.audio_file
    image_file = args.image_file
    output_video = args.output_video

    audio_with_static_image(audio_file, image_file, output_video)
