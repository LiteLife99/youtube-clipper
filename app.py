
import os
import subprocess
import streamlit as st
import imageio_ffmpeg

os.environ["PATH"] += os.pathsep + os.path.dirname(imageio_ffmpeg.get_ffmpeg_exe())

# === CONFIG ===
OUTPUT_DIR = "clips"
os.makedirs(OUTPUT_DIR, exist_ok=True)
YTDLP_FORMAT = "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best"


def run_yt_dlp_clip(url, start, end, clip_id):
    section = f"*{start}-{end}"
    output_path = os.path.join(OUTPUT_DIR, f"clip_{clip_id}.mp4")

    command = [
        "yt-dlp",
        "--download-sections", section,
        "--merge-output-format", "mp4",
        "--no-write-subs",
        "-f", YTDLP_FORMAT,
        "-o", output_path,
        url
    ]

    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
        return output_path
    except subprocess.CalledProcessError as e:
        st.error(f"Command Failed: {e.cmd}")
        st.error(f"Stdout: {e.stdout}")
        st.error(f"Stderr: {e.stderr}")
        return None


def main():
    st.title("🎬 YouTube Clip Downloader")

    st.markdown("""
    Enter multiple YouTube video URLs and specify the timestamp ranges (start - end) for each.
    Videos will be clipped and saved as individual files.
    """)

    num_videos = st.number_input("How many videos do you want to process?", min_value=1, max_value=10, value=1)

    clip_counter = 1
    if "results" not in st.session_state:
        st.session_state.results = []

    for i in range(num_videos):
        st.header(f"📽️ Video {i + 1}")
        url = st.text_input(f"Video {i + 1} URL", key=f"url_{i}")
        timestamps_text = st.text_area(f"Timestamps for Video {i + 1} (one per line, format: start - end)", key=f"ts_{i}")

        if st.button(f"Download Clips for Video {i + 1}", key=f"dl_{i}"):
            if not url.strip():
                st.warning("Please enter a valid URL.")
                continue

            timestamps = [line.strip() for line in timestamps_text.strip().splitlines() if "-" in line]
            with st.spinner(f"Processing video {i + 1}..."):
                for ts in timestamps:
                    start, end = map(str.strip, ts.split("-"))
                    clip_path = run_yt_dlp_clip(url, start, end, clip_counter)
                    if clip_path:
                        st.success(f"✅ Clip saved: {clip_path}. Download Below:")
                        with open(clip_path, "rb") as f:
                            st.download_button(
                                label=f"🔽 Download Clip {clip_path}",
                                data=f,
                                file_name=f"clip_{i+1}.mp4",
                                mime="video/mp4",
                                key=f"download_{i}"
                            )
                    else:
                        st.error(f"❌ Failed to download clip from {start} to {end}")
                    clip_counter += 1



if __name__ == "__main__":
    main()
