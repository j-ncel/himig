import numpy as np
import wave
import tempfile
import sys
import subprocess
import os
import io

from .constants import BASE_FREQUENCIES


def get_frequency(note_name):
    """Return frequency for note string like 'C4', 'C#5', etc."""
    try:
        if note_name.upper() == "R":
            return 0.0
        for idx, char in enumerate(note_name):
            if char.isdigit():
                note, octave = note_name[:idx], int(note_name[idx:])
                break
        else:
            note, octave = note_name, 4
        if note not in BASE_FREQUENCIES:
            raise ValueError(f"Unknown note: {note_name}")
        return BASE_FREQUENCIES[note] * 2 ** (octave - 4)
    except Exception as e:
        raise ValueError(f"Invalid note format '{note_name}': {e}")


def apply_adsr_envelop(waveform, sample_rate):
    """Apply a piano-style ADSR (Attack, Decay, Sustain, Release) envelope to a waveform."""
    attack = int(0.01 * sample_rate)
    decay = int(0.1 * sample_rate)
    sustain_level = 0.7
    release = int(0.2 * sample_rate)
    total = len(waveform)

    envelope = np.ones(total)
    if total < attack + decay + release:
        return waveform

    envelope[:attack] = np.linspace(0, 1, attack)
    envelope[attack:attack+decay] = np.linspace(1, sustain_level, decay)
    envelope[attack+decay:total-release] = sustain_level
    envelope[total-release:] = np.linspace(sustain_level, 0, release)

    return waveform * envelope


def synthesize_waveform(note_names, durations, sample_rate=44100, amplitude=32767):
    """Generate the full waveform for the melody."""
    waveforms = []
    for note, duration in zip(note_names, durations):
        try:
            freq = get_frequency(note)
        except ValueError as e:
            print(f"Warning: {e}. Skipping note.")
            continue
        t = np.linspace(0, duration, int(
            sample_rate * duration), endpoint=False)
        if freq == 0.0:
            waveform = np.zeros_like(t)
        else:
            waveform = (
                1.0 * np.sin(2 * np.pi * freq * t) +
                0.5 * np.sin(2 * np.pi * 2 * freq * t) +
                0.25 * np.sin(2 * np.pi * 3 * freq * t)
            )
            waveform *= np.exp(-3 * t)
            waveform = apply_adsr_envelop(waveform, sample_rate)
            waveform /= np.max(np.abs(waveform)) + 1e-6
        waveforms.append(waveform)
    if not waveforms:
        raise ValueError("No valid notes to synthesize.")
    return (np.concatenate(waveforms) * amplitude).astype(np.int16)


def parse_note_and_duration(note_duration_str):
    """Parse 'C4:0.5' into ('C4', 0.5)."""
    try:
        if ':' in note_duration_str:
            note, duration = note_duration_str.split(':')
            return note, float(duration)
        return note_duration_str, 1.0
    except Exception as e:
        raise ValueError(
            f"Invalid note-duration string '{note_duration_str}': {e}")


def parse_melody(melody):
    """Convert a melody list into separate note and duration lists."""
    try:
        notes, durations = zip(*(parse_note_and_duration(item)
                                 for item in melody))
        return notes, durations
    except Exception as e:
        raise ValueError(f"Error parsing melody: {e}")


def save_waveform_to_wav(audio_data, sample_rate=44100, filename=None):
    """Save waveform to a WAV file and return its path."""
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
        raise IOError(f"Failed to save WAV file: {e}")


def play_wav_file(wav_path):
    """Play a WAV file using the system's audio player."""
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
        raise RuntimeError(f"Failed to play WAV file: {e}")


def play(melody: list[str], sample_rate: int = 44100, amplitude: int = 32767) -> None:
    """
    Play a melody directly through your system's audio output.

    Args:
        melody (list of str): A list of note-duration strings, e.g. ["C4:0.5", "G4:1.0"].
            Each string should be in the format "NOTE:DURATION", where NOTE is a note name
            (e.g., "C4", "F#5", "Bb3", or "R" for rest) and DURATION is the note length in seconds.
        sample_rate (int, optional): Audio sample rate in Hz. Default is 44100.
        amplitude (int, optional): Peak amplitude of the waveform. Default is 32767.

    Example:
        >>> from himig import play
        >>> melody = ["C4:0.5", "C4:0.5", "G4:1.0"]
        >>> play(melody)
    """
    try:
        notes, durations = parse_melody(melody)
        audio_data = synthesize_waveform(
            notes, durations, sample_rate, amplitude)
        wav_path = save_waveform_to_wav(audio_data, sample_rate)
        play_wav_file(wav_path)
    except Exception as e:
        print(f"Error during playback: {e}")
    finally:
        if 'wav_path' in locals() and os.path.exists(wav_path):
            os.remove(wav_path)


def save(melody: list[str], filename: str, sample_rate: int = 44100, amplitude: int = 32767) -> None:
    """
    Save a melody as a WAV file.

    Args:
        melody (list of str): A list of note-duration strings, e.g. ["C4:0.5", "G4:1.0"].
            Each string should be in the format "NOTE:DURATION", where NOTE is a note name
            (e.g., "C4", "F#5", "Bb3", or "R" for rest) and DURATION is the note length in seconds.
        filename (str): The path where the WAV file will be saved.
        sample_rate (int, optional): Audio sample rate in Hz. Default is 44100.
        amplitude (int, optional): Peak amplitude of the waveform. Default is 32767.

    Example:
        >>> from himig import save
        >>> melody = ["C4:0.5", "C4:0.5", "G4:1.0"]
        >>> save(melody, "twinkle.wav")
    """
    try:
        notes, durations = parse_melody(melody)
        audio_data = synthesize_waveform(
            notes, durations, sample_rate, amplitude)
        save_waveform_to_wav(audio_data, sample_rate, filename)
        print(f"Melody saved to {filename}")
    except Exception as e:
        print(f"Error saving melody: {e}")


def generate_wav_bytes(melody: list[str], sample_rate: int = 44100, amplitude: int = 32767):
    """
    Generate a WAV audio file as bytes for a given melody.

    Args:
        melody (list of str): List of note-duration strings, e.g. ["C4:0.5", "G4:1.0"].
        sample_rate (int, optional): Audio sample rate in Hz. Default is 44100.
        amplitude (int, optional): Peak amplitude of the waveform. Default is 32767.

    Returns:
        BytesIO: In-memory WAV file suitable for web apps (e.g., Streamlit st.audio).

    Example:
        >>> from himig import generate_wav_bytes
        >>> wav_bytes = generate_wav_bytes(["C4:0.5", "G4:1.0"])
    """
    try:
        notes, durations = parse_melody(melody)
        audio_data = synthesize_waveform(
            notes, durations, sample_rate, amplitude)
        buffer = io.BytesIO()
        with wave.open(buffer, "wb") as wav_file:
            wav_file.setnchannels(1)
            wav_file.setsampwidth(2)
            wav_file.setframerate(sample_rate)
            wav_file.writeframes(audio_data.tobytes())
        buffer.seek(0)
        return buffer
    except Exception as e:
        raise RuntimeError(f"Error generating WAV bytes: {e}")
