#!/usr/bin/env python3
"""
Quick test script to verify MP3 conversion functionality
"""
import os
import tempfile
import numpy as np
import soundfile as sf
from pydub import AudioSegment

def test_mp3_conversion():
    """Test the MP3 conversion functionality"""
    print("Testing MP3 conversion...")
    
    # Create a simple test audio (1 second of silence at 24kHz)
    test_audio = np.zeros(24000, dtype=np.float32)
    
    # Create temporary files
    with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_wav:
        temp_wav_path = temp_wav.name
    
    with tempfile.NamedTemporaryFile(suffix='.mp3', delete=False) as temp_mp3:
        temp_mp3_path = temp_mp3.name
    
    try:
        # Write test audio to WAV
        sf.write(temp_wav_path, test_audio, 24000)
        print(f"✓ Created temporary WAV file: {temp_wav_path}")
        
        # Convert to MP3
        audio_segment = AudioSegment.from_wav(temp_wav_path)
        audio_segment.export(temp_mp3_path, format="mp3")
        print(f"✓ Converted to MP3: {temp_mp3_path}")
        
        # Check if MP3 file exists and has content
        if os.path.exists(temp_mp3_path) and os.path.getsize(temp_mp3_path) > 0:
            print(f"✓ MP3 file created successfully (size: {os.path.getsize(temp_mp3_path)} bytes)")
            return True
        else:
            print("✗ MP3 file was not created or is empty")
            return False
            
    except Exception as e:
        print(f"✗ Error during conversion: {e}")
        return False
        
    finally:
        # Clean up temporary files
        for temp_file in [temp_wav_path, temp_mp3_path]:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                print(f"✓ Cleaned up: {temp_file}")

if __name__ == "__main__":
    success = test_mp3_conversion()
    print(f"\nTest {'PASSED' if success else 'FAILED'}")
    exit(0 if success else 1)
