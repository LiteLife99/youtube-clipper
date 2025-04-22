import streamlit as st
import yt_dlp
import os
import uuid
import subprocess
import time

output_dir = "clips"
videos_to_keep = []

st.set_page_config(page_title="🎬 Online Clips Downloader", layout="wide")

st.title("🎬 Online Clips Downloader")
st.caption("Download clips from any open online video be it from intagram reels, youtube shorts, youtube videos, or anything which is publicly available")
st.caption("Fast and efficient! - no need to download full videos and take out clips from them manually anymore!")

st.markdown("""
            <style>
                div[data-testid="stColumn"] {
                    width: fit-content !important;
                    flex: unset;
                }
                div[data-testid="stColumn"] * {
                    width: fit-content !important;
                }
                button[kind="primary"] {
                    margin-top: -5px !important;
                    font-size: 13px;
                    color: white;
                    background-color: red;
                    border: 1px solid red;
                    border-radius: 5px;
                    cursor: pointer;
                    display: inline-flex;  
                    align-items: center;
                    justify-content: center;
                    cursor: pointer;
                }
            </style>
            """, unsafe_allow_html=True)

if "videos" not in st.session_state:
    st.session_state.videos = [{"id": str(uuid.uuid4()), "url": "", "clips": []}]

# Add new video input
if st.button("➕ Add New Video"):
    st.session_state.videos.append({"id": str(uuid.uuid4()), "url": "", "clips": []})

# Display each video input
for i, video in enumerate(st.session_state.videos):
    with st.expander(f"🎥 Video {i + 1}", expanded=True):

        # Create top row: left = title, right = remove button
        top_row = st.columns([1, 1])
        with top_row[0]:
            st.markdown(f"**Open Video {i + 1}**")
        with top_row[1]:
            remove = st.button("Remove", type="primary", key=f"remove_clip_{video['id']}")

        warning_placeholder = st.empty()  # Placeholder for the warning

        if remove:
            # If this is the last video, show a warning
            if len(st.session_state.videos) == 1:
                warning_placeholder.warning("⚠️ You cannot remove the last video. Please keep at least one video.")
                time.sleep(3)  # Wait for 3 seconds
                warning_placeholder.empty()  # Remove the warning after 3 seconds
            else:
                continue  # Skip this video from the list (i.e., remove it)

        video["url"] = st.text_input("Video URL", key=f"url_{video['id']}", value=video.get("url", ""))

        if f"clips_{video['id']}" not in st.session_state:
            st.session_state[f"clips_{video['id']}"] = []

        st.write("Clips (Start and End Times in HH:MM:SS)")
        cols = st.columns([1, 1, 1])
        start_time = cols[0].text_input("Start", key=f"start_{video['id']}")
        end_time = cols[1].text_input("End", key=f"end_{video['id']}")
        custom_name = cols[2].text_input("Custom name (mandatory). Example: phuket_phi-phi-tour_clip1", key=f"name_{video['id']}")


        if st.button("Add Clip", key=f"add_clip_{video['id']}"):
            if start_time and end_time and custom_name:
                safe_name = custom_name.strip().replace(" ", "_").replace("/", "-")
                st.session_state[f"clips_{video['id']}"].append((start_time, end_time, safe_name))
            else:
                st.warning("Start, End, and Custom Name are all required.")

        for idx, (start, end, custom_name) in enumerate(st.session_state[f"clips_{video['id']}"]):
            st.write(f"🔹 Clip {idx + 1}: {start} → {end} -> {custom_name}")

        # Update video object with clips
        video["clips"] = st.session_state[f"clips_{video['id']}"]
        videos_to_keep.append(video)

# Update state
st.session_state.videos = videos_to_keep

def get_direct_video_url(video_url):
    # Step 1: Get the direct video URL using yt-dlp -g
    result = subprocess.run(
        ['yt-dlp', '-g', video_url],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        check=True
    )
    direct_url = result.stdout.strip().splitlines()[0]
    return direct_url

def download_clip_ffmpeg(video_url, start_time, end_time, output_path):
    direct_url = get_direct_video_url(video_url)

    command = [
        'ffmpeg',
        '-y',  # <--- Force overwrite if file already exists in system dir
        '-ss', start_time,
        '-to', end_time,
        '-i', direct_url,
        '-c', 'copy',  # fast, no re-encoding
        output_path
    ]

    try:
        subprocess.run(command, check=True)
        print(f"✅ Clip saved: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed: {e}")
        return False
    
with st.container():
    col1, col2 = st.columns(2)
    with col1:
        download_triggered = st.button("🚀 Download All Clips")
    with col2:
        clear_cache_triggered = st.button("🧹 Clear Server Cache")

# Download Clips
if download_triggered:
    os.makedirs(output_dir, exist_ok=True)

    with st.spinner("📥 Downloading clips on server... Please wait"):
        for video in st.session_state.videos:
            if not video["url"] or not video["clips"]:
                continue

            for idx, (start, end, custom_name) in enumerate(video["clips"]):
                section = f"*{start}-{end}"
                output_path = os.path.join(output_dir, f"{custom_name}.mp4")

                try:
                    downloaded = download_clip_ffmpeg(video["url"], start_time, end_time, output_path)
                    if downloaded:
                        with open(output_path, "rb") as f:
                            st.download_button(
                                label=f"⬇️ Download Clip {custom_name}.mp4",
                                data=f,
                                file_name=f"{custom_name}.mp4",
                                mime="video/mp4",
                            )
                except Exception as e:
                    st.error(f"❌ Error downloading clip {idx + 1}: {e}")

if clear_cache_triggered:
    if os.path.exists(output_dir):
        for filename in os.listdir(output_dir):
            file_path = os.path.join(output_dir, filename)
            try:
                os.remove(file_path)
            except Exception as e:
                st.error(f"Error deleting from server cache {file_path}: {e}")
        st.success("Cache Cleared successfully.")
    else:
        st.warning("Output folder doesn't exist.")
    
    # Clear video inputs and clip states
    st.session_state.videos = [{"id": str(uuid.uuid4()), "url": "", "clips": []}]
    for key in list(st.session_state.keys()):
        if key.startswith("clips_") or key.startswith("start_") or key.startswith("end_") or key.startswith("name_"):
            del st.session_state[key]

    time.sleep(2)

    # Refresh the app view
    st.rerun()

st.info("ℹ️ **Tip:** Remember to clear the cache from time to time to free up server space!")