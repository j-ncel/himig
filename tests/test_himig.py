import pytest
from himig import play, save, generate_wav_bytes
from himig import happy_birthday, twinkle_twinkle


@pytest.fixture
def simple_melody():
    return ["C4:0.5", "G4:0.5"]


def test_generate_wav_bytes(simple_melody):
    """Test that generate_wav_bytes returns a readable buffer with data."""
    wav_bytes = generate_wav_bytes(["C4:0.5", "G4:0.5"])
    assert hasattr(wav_bytes, "read")
    wav_bytes.seek(0)
    assert len(wav_bytes.read()) > 0


def test_save(tmp_path, simple_melody):
    """Test that save creates a valid WAV file."""
    filename = tmp_path / "test_output.wav"
    save(simple_melody, str(filename))
    assert filename.exists()


def test_play(simple_melody):
    """Test that play runs without raising exceptions."""
    try:
        play(simple_melody)
    except Exception as e:
        pytest.fail(f"play() raised an exception: {e}")


def test_invalid_note_raises():
    """Test that an invalid note raises an exception."""
    with pytest.raises(Exception):
        generate_wav_bytes(["Z9:1.0"])


def test_empty_melody_raises():
    """Test that an empty melody raises an exception."""
    with pytest.raises(Exception):
        generate_wav_bytes([])


def test_rest_note():
    """Test that a rest note ('R') produces silence (all zeros)."""
    wav_bytes = generate_wav_bytes(["R:1.0"])
    wav_bytes.seek(0)
    data = wav_bytes.read()
    assert set(data[44:]) == {0}


def test_long_melody(tmp_path):
    """Test saving a long melody does not raise errors."""
    melody = ["C4:0.1", "D4:0.1", "E4:0.1", "F4:0.1", "G4:0.1"] * 20
    filename = tmp_path / "long_melody.wav"
    save(melody, str(filename))
    assert filename.exists()
    wav_bytes = generate_wav_bytes(melody)
    assert hasattr(wav_bytes, "read")
    wav_bytes.seek(0)
    assert len(wav_bytes.read()) > 0


def test_malformed_note_format_raises():
    """Test that an invalid note format raises an exception."""
    with pytest.raises(Exception):
        generate_wav_bytes(["C4-0.5"])


def test_multiple_rest_notes():
    """Test that multiple rest notes produce silence."""
    wav_bytes = generate_wav_bytes(["R:0.5", "R:0.5", "R:0.5"])
    wav_bytes.seek(0)
    data = wav_bytes.read()
    assert set(data[44:]) == {0}
