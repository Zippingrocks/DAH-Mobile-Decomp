import io
import struct
import tempfile
import unittest
import wave
import zipfile
from pathlib import Path

from tools import audio_sanity as audio

class AudioSanityTests(unittest.TestCase):
    def make_wav(self, amplitude=2000, frames=800):
        out=io.BytesIO()
        with wave.open(out,"wb") as w:
            w.setnchannels(1);w.setsampwidth(2);w.setframerate(8000)
            samples=[amplitude if i%2==0 else -amplitude for i in range(frames)]
            w.writeframes(struct.pack("<%dh"%len(samples),*samples))
        return out.getvalue()

    def test_metrics_accept_expected_pcm_shape(self):
        row=audio.metrics(self.make_wav())
        self.assertEqual(row["channels"],1)
        self.assertEqual(row["sample_rate"],8000)
        self.assertEqual(row["sample_width_bytes"],2)
        audio.validate(row)

    def test_silence_is_rejected(self):
        row=audio.metrics(self.make_wav(amplitude=0))
        with self.assertRaises(RuntimeError):
            audio.validate(row)

    def test_clipping_is_rejected(self):
        row=audio.metrics(self.make_wav(amplitude=32767))
        with self.assertRaises(RuntimeError):
            audio.validate(row)

    def test_expected_retail_effect_hash_count(self):
        self.assertEqual(len(audio.EXPECTED_AMR_HASHES),4)

if __name__=="__main__":
    unittest.main()
