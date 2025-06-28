import wave
import tempfile
import os
import sys
import subprocess


def save_waveform_to_wav(audio_data, sample_rate=44100, filename=None):
    """
    Save audio data to a WAV file and return its path.
    """
    try:
        if filename is None:
            fd, filename = tempfile.mkstemp(suffix=".wav")
            os.close(fd)
        with wave.open(filename, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        return filename
    except Exception as e:
        raise IOError(f"Failed to save WAV file '{filename}': {e}")


def play_wav_file(wav_path):
    """
    Play a WAV file using the system's audio player.
    """
    try:
        if sys.platform.startswith("win"):
            import winsound
            winsound.PlaySound(wav_path, winsound.SND_FILENAME)
        elif sys.platform.startswith("darwin"):
            subprocess.run(["afplay", wav_path], check=True)
        elif sys.platform.startswith("linux"):
            for player in ("aplay", "paplay", "play"):
                if subprocess.call(["which", player], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) == 0:
                    subprocess.run([player, wav_path], check=True)
                    break
            else:
                raise RuntimeError("No audio player found.")
        else:
            raise RuntimeError("Unsupported OS.")
    except Exception as e:
        raise RuntimeError(f"Failed to play WAV file '{wav_path}': {e}")
