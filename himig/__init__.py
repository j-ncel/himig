"""
himig is a python music synthesis module that lets you compose, play, and save melodies.
"""

from ._core import play, save, generate_wav_bytes
from .melodies import happy_birthday, twinkle_twinkle

__all__ = [
    "play",
    "save",
    "generate_wav_bytes",
    "happy_birthday",
    "twinkle_twinkle"
]
