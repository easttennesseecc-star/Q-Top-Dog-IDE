from __future__ import annotations
"""
Lightweight Voice Profiling Engine

This implementation is optimized for unit tests that operate on in-memory
numpy arrays (no external audio libs). It provides:
- Simple MFCC-like feature extraction (DCT of log power spectrum)
- Pitch estimation via autocorrelation
- Energy via RMS
- Minimal profile management with JSON persistence
- Recognition based on cosine similarity of MFCCs with pitch/energy cues
"""

import json
import logging
from datetime import datetime
from dataclasses import dataclass, field
from typing import Dict, List, Optional
from pathlib import Path

import numpy as np

logger = logging.getLogger(__name__)


# =====================
# Data Model
# =====================

@dataclass
class VoiceSample:
    mfcc: np.ndarray
    pitch: float
    energy: float
    duration: float = 1.0


@dataclass
class VoiceProfile:
    user_id: str
    profile_name: str
    samples: List[VoiceSample] = field(default_factory=list)
    accuracy_score: float = 0.0
    created_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    @property
    def num_samples(self) -> int:
        return len(self.samples)

    @property
    def characteristics(self) -> Dict[str, float]:
        if not self.samples:
            return {}
        energies = [s.energy for s in self.samples]
        return {
            "num_samples": self.num_samples,
            "avg_energy": float(np.mean(energies)),
        }


@dataclass
class VoiceRecognitionResult:
    success: bool
    confidence: float
    matched_user: Optional[str] = None
    error_message: Optional[str] = None


# =====================
# Feature Extraction
# =====================

class VoiceFeatureExtractor:
    """Extract audio features from numpy arrays."""

    @staticmethod
    def extract_mfcc(audio: np.ndarray, sr: int = 16000, n_mfcc: int = 13) -> np.ndarray:
        """Compute simple MFCC-like features using DCT of log power spectrum.

        This is not a full MFCC implementation but is stable, fast, and
        returns n_mfcc coefficients suitable for tests.
        """
        if audio is None or audio.size == 0:
            return np.zeros(n_mfcc, dtype=np.float32)
        # Pre-emphasis (no amplitude normalization to preserve gain differences)
        emphasized = np.append(audio[0], audio[1:] - 0.97 * audio[:-1])

        # Frame into a single window large enough for a coarse spectrum
        n_fft = 1024
        if emphasized.size < n_fft:
            pad = n_fft - emphasized.size
            emphasized = np.pad(emphasized, (0, pad), mode="constant")
        frame = emphasized[:n_fft]

        # Hamming window and power spectrum
        windowed = frame * np.hamming(n_fft)
        spectrum = np.fft.rfft(windowed)
        power = (np.abs(spectrum) ** 2) / n_fft

        # Simple mel-like band aggregation: split into n_mfcc+2 bands and sum
        n_bands = n_mfcc + 2
        band_edges = np.linspace(0, power.size, n_bands + 1, dtype=int)
        mel_energies_list: List[float] = []
        for i in range(n_bands):
            start, end = band_edges[i], band_edges[i + 1]
            if end > start:
                mel_energies_list.append(float(power[start:end].mean()))
            else:
                mel_energies_list.append(0.0)
        mel_energies_arr = np.array(mel_energies_list, dtype=np.float32) + 1e-10

        # Log and DCT (take first n_mfcc coefficients)
        log_mel = np.log(mel_energies_arr)
        # DCT type-II via cosine transform matrix
        k = np.arange(n_mfcc)[:, None]
        n = np.arange(log_mel.size)[None, :]
        dct_basis = np.cos(np.pi * (n + 0.5) * k / log_mel.size)
        mfcc = dct_basis @ log_mel
        return mfcc.astype(np.float32)

    @staticmethod
    def extract_pitch(audio: np.ndarray, sr: int = 16000) -> float:
        """Estimate fundamental frequency using autocorrelation in human range."""
        if audio is None or audio.size == 0:
            return 0.0

        # Autocorrelation
        audio = audio - np.mean(audio)
        corr = np.correlate(audio, audio, mode="full")
        corr = corr[corr.size // 2:]

        # Search in range 80-300 Hz
        min_lag = int(sr / 300)
        max_lag = int(sr / 80)
        if max_lag <= min_lag or max_lag >= corr.size:
            return 0.0

        segment = corr[min_lag:max_lag]
        peak_lag = np.argmax(segment) + min_lag
        if peak_lag == 0:
            return 0.0
        return float(sr / peak_lag)

    @staticmethod
    def extract_energy(audio: np.ndarray) -> float:
        if audio is None or audio.size == 0:
            return 0.0
        rms = float(np.sqrt(np.mean(audio.astype(np.float32) ** 2)))
        return float(max(0.0, min(1.0, rms)))


# =====================
# Profile Management
# =====================

class VoiceProfileManager:
    def __init__(self, profile_dir: str = "data/voice_profiles"):
        self.profile_dir = Path(profile_dir)
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        self._profiles: Dict[str, VoiceProfile] = {}
        self._load_profiles()

    def _profile_path(self, user_id: str) -> Path:
        return self.profile_dir / f"{user_id}.json"

    def _load_profiles(self) -> None:
        for p in self.profile_dir.glob("*.json"):
            try:
                data = json.load(p.open("r", encoding="utf-8"))
                # Minimal reconstruction for tests
                prof = VoiceProfile(
                    user_id=data.get("user_id", p.stem),
                    profile_name=data.get("profile_name", p.stem),
                )
                prof.accuracy_score = float(data.get("accuracy_score", 0.0))
                self._profiles[prof.user_id] = prof
            except Exception as e:
                logger.warning(f"Failed to load profile {p}: {e}")

    def _save(self, profile: VoiceProfile) -> None:
        data = {
            "user_id": profile.user_id,
            "profile_name": profile.profile_name,
            "accuracy_score": profile.accuracy_score,
            "characteristics": profile.characteristics,
            "created_at": profile.created_at,
            "updated_at": profile.updated_at,
        }
        with self._profile_path(profile.user_id).open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

    def create_profile(self, user_id: str, profile_name: str) -> VoiceProfile:
        prof = VoiceProfile(user_id=user_id, profile_name=profile_name)
        self._profiles[user_id] = prof
        self._save(prof)
        return prof

    def add_sample(self, user_id: str, sample: VoiceSample) -> None:
        if user_id not in self._profiles:
            raise KeyError(f"No profile for user_id={user_id}")
        prof = self._profiles[user_id]
        prof.samples.append(sample)
        # Update lightweight stats
        prof.accuracy_score = float(min(1.0, prof.num_samples / 10.0))
        prof.updated_at = datetime.utcnow().isoformat()
        self._save(prof)

    def get_profile(self, user_id: str) -> Optional[VoiceProfile]:
        return self._profiles.get(user_id)

    def list_profiles(self) -> List[VoiceProfile]:
        return list(self._profiles.values())


# =====================
# Recognition
# =====================

class VoiceRecognitionEngine:
    def __init__(self, profile_manager: VoiceProfileManager):
        self.profile_manager = profile_manager
        self.extractor = VoiceFeatureExtractor()

    def _cosine(self, a: np.ndarray, b: np.ndarray) -> float:
        if a is None or b is None or a.size == 0 or b.size == 0:
            return 0.0
        na = np.linalg.norm(a)
        nb = np.linalg.norm(b)
        if na == 0 or nb == 0:
            return 0.0
        return float(np.dot(a, b) / (na * nb))

    def recognize(self, audio: np.ndarray, sr: int = 16000) -> VoiceRecognitionResult:
        try:
            mfcc = self.extractor.extract_mfcc(audio, sr=sr)
            pitch = self.extractor.extract_pitch(audio, sr=sr)
            energy = self.extractor.extract_energy(audio)

            best_user = None
            best_conf = 0.0

            for prof in self.profile_manager.list_profiles():
                # Build a simple reference MFCC as average of stored samples
                if prof.samples:
                    ref = np.mean([s.mfcc for s in prof.samples], axis=0)
                else:
                    ref = np.zeros_like(mfcc)

                # Combine cosine similarity (scale-invariant) with inverse Euclidean distance
                cos_sim = (self._cosine(mfcc, ref) + 1) / 2
                euclid = float(np.linalg.norm(mfcc - ref))
                euclid_sim = 1.0 / (1.0 + euclid)
                mfcc_sim = 0.6 * cos_sim + 0.4 * euclid_sim

                # Pitch similarity
                if prof.samples:
                    ref_pitch = float(np.mean([s.pitch for s in prof.samples]))
                else:
                    ref_pitch = 150.0
                pitch_diff = abs(pitch - ref_pitch) / max(ref_pitch, 100.0)
                pitch_sim = 1.0 - float(min(1.0, pitch_diff))

                # Energy similarity
                if prof.samples:
                    ref_energy = float(np.mean([s.energy for s in prof.samples]))
                else:
                    ref_energy = 0.5
                energy_diff = abs(energy - ref_energy)
                energy_sim = 1.0 - float(min(1.0, energy_diff))

                # Heavier weight on MFCC and energy; pitch has minimal influence
                conf = 0.6 * mfcc_sim + 0.35 * energy_sim + 0.05 * pitch_sim
                if conf > best_conf:
                    best_conf = conf
                    best_user = prof.user_id

            return VoiceRecognitionResult(
                success=best_conf >= 0.7,
                confidence=float(max(0.0, min(1.0, best_conf))),
                matched_user=best_user,
            )
        except Exception as e:
            logger.error(f"recognize error: {e}")
            return VoiceRecognitionResult(success=False, confidence=0.0, error_message=str(e))


# =====================
# Singletons and Async wrappers
# =====================

_PROFILE_MGR: Optional[VoiceProfileManager] = None
_RECOG_ENG: Optional[VoiceRecognitionEngine] = None


def get_voice_profile_manager() -> VoiceProfileManager:
    global _PROFILE_MGR
    if _PROFILE_MGR is None:
        _PROFILE_MGR = VoiceProfileManager()
    return _PROFILE_MGR


def get_voice_recognition_engine() -> VoiceRecognitionEngine:
    global _RECOG_ENG
    if _RECOG_ENG is None:
        _RECOG_ENG = VoiceRecognitionEngine(get_voice_profile_manager())
    return _RECOG_ENG


async def create_user_voice_profile(user_id: str, profile_name: str) -> Dict:
    try:
        mgr = get_voice_profile_manager()
        prof = mgr.create_profile(user_id, profile_name)
        return {"success": True, "profile_id": prof.user_id, "profile_name": prof.profile_name}
    except Exception as e:
        logger.error(f"create_user_voice_profile error: {e}")
        return {"success": False, "error": str(e)}


