import os
from moviepy import VideoFileClip

def batch_process_audio():
    """
    Scans student folders, extracts audio from various video formats (mp4, mov, mkv, etc.), 
    and compresses it to high-efficiency MP3s for transcription.
    
    Includes a check to skip files that have already been processed.
    """
    # Get all items in the current directory
    items = os.listdir(".")
    
    # Filter for student directories
    student_dirs = [d for d in items if os.path.isdir(d) and not d.startswith(".") and d not in ["__pycache__", ".venv"]]
    
    print(f"Found {len(student_dirs)} student directories.")
    
    # Supported video formats
    VIDEO_EXTENSIONS = ('.mp4', '.mov', '.mkv', '.avi', '.wmv', '.flv', '.webm')
    
    processed_count = 0
    skipped_count = 0
    
    for student_dir in student_dirs:
        # Check for presentation folder
        presentation_dir = os.path.join(student_dir, "presentation")
        if not os.path.exists(presentation_dir):
            presentation_dir = os.path.join(student_dir, "Presentation")
            if not os.path.exists(presentation_dir):
                continue
                
        print(f"\n--- Checking Folder: {student_dir} ---")
        
        # Find original videos
        videos = [f for f in os.listdir(presentation_dir) if f.lower().endswith(VIDEO_EXTENSIONS)]
        
        if not videos:
            print(f"   No supported videos found.")
            continue
            
        for video in videos:
            video_path = os.path.join(presentation_dir, video)
            base_name, _ = os.path.splitext(video)
            
            # Generate audio filename
            audio_output = os.path.join(presentation_dir, f"{base_name}_audio.mp3")
            
            # CRITICAL CHECK: Skip if the output audio file already exists
            if os.path.exists(audio_output):
                print(f"   >>> SKIPPING: {video} (Audio already exists)")
                skipped_count += 1
                continue
            
            print(f"   Processing: {video} -> {os.path.basename(audio_output)}")
            try:
                clip = VideoFileClip(video_path)
                if clip.audio:
                    # Compress audio to 64k for efficient transcription
                    clip.audio.write_audiofile(audio_output, bitrate="64k", logger=None)
                    processed_count += 1
                else:
                    print(f"   Warning: No audio track found in {video}")
                clip.close()
            except Exception as e:
                print(f"   Error processing {video}: {e}")

    print(f"\n--- Batch Process Summary ---")
    print(f"New files processed: {processed_count}")
    print(f"Files skipped (already exist): {skipped_count}")
    print("Done!")

if __name__ == "__main__":
    batch_process_audio()
