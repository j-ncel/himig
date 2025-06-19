"""
himig: Simple music synthesis and playback package.
"""

from .core import play, save, generate_wav_bytes
from .melodies import happy_birthday, twinkle_twinkle

__all__ = [
    "play",
    "save",
    "generate_wav_bytes",
    "happy_birthday",
    "twinkle_twinkle"
]
