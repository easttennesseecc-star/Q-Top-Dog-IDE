"""
Voice Profiling Engine for Q-IDE
Handles voice sample collection, storage, analysis, and accurate voice input recognition
"""

import os
import json
import hashlib
import logging
from datetime import datetime
from dataclasses import dataclass, asdict
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import asyncio

# Audio processing libraries
try:
    import librosa
    import numpy as np
except ImportError:
    librosa = None
    np = None

logger = logging.getLogger(__name__)


@dataclass
class VoiceSample:
    """Voice sample metadata and features"""
    id: str
    user_id: str
    filename: str
    duration: float
    sample_rate: int
    mfcc_features: List[List[float]]  # Mel-frequency cepstral coefficients
    pitch_range: Tuple[float, float]  # (min_pitch, max_pitch)
    energy_level: float
    timestamp: str
    transcription: Optional[str] = None


@dataclass
class VoiceProfile:
    """User voice profile for accurate voice recognition"""
    user_id: str
    profile_name: str
    samples: List[VoiceSample]
    avg_mfcc: List[float]  # Average MFCC across all samples
    pitch_baseline: float  # User's typical pitch
    energy_baseline: float  # User's typical energy level
    voice_characteristics: Dict[str, any]
    created_at: str
    updated_at: str
    accuracy_score: float = 0.0


@dataclass
class VoiceRecognitionResult:
    """Result of voice input recognition"""
    success: bool
    confidence: float  # 0.0-1.0
    matched_profile: Optional[str] = None
    transcription: Optional[str] = None
    voice_characteristics: Optional[Dict] = None
    error_message: Optional[str] = None


class VoiceFeatureExtractor:
    """Extract voice features from audio samples"""

    @staticmethod
    def extract_mfcc(audio_data: np.ndarray, sr: int, n_mfcc: int = 13) -> List[float]:
        """Extract Mel-frequency cepstral coefficients"""
        if librosa is None:
            logger.warning("librosa not available, using placeholder features")
            return [0.0] * n_mfcc
        
        mfcc = librosa.feature.mfcc(y=audio_data, sr=sr, n_mfcc=n_mfcc)
        # Return mean across time
        return mfcc.mean(axis=1).tolist()

    @staticmethod
    def extract_pitch(audio_data: np.ndarray, sr: int) -> Tuple[float, float]:
        """Extract pitch range (min, max) in Hz"""
        if librosa is None:
            logger.warning("librosa not available, using placeholder pitch")
            return (80.0, 250.0)
        
        # Estimate pitch using harmonic-percussive separation
        harmonic = librosa.effects.harmonic(audio_data)
        freqs = librosa.stft(harmonic)
        
        # Simplified pitch estimation
        magnitude = np.abs(freqs)
        pitch_estimate = np.argmax(magnitude, axis=0)
        freqs_hz = librosa.fft_frequencies(sr=sr)
        
        # Get min/max pitch frequencies where there's energy
        voiced_frames = pitch_estimate[magnitude.max(axis=0) > np.mean(magnitude) * 0.1]
        
        if len(voiced_frames) > 0:
            min_pitch = freqs_hz[voiced_frames.min()]
            max_pitch = freqs_hz[voiced_frames.max()]
            return (float(max(min_pitch, 50)), float(min(max_pitch, 500)))
        
        return (80.0, 250.0)

    @staticmethod
    def extract_energy(audio_data: np.ndarray) -> float:
        """Extract energy level (RMS)"""
        if np.size(audio_data) == 0:
            return 0.0
        
        rms = float(np.sqrt(np.mean(audio_data ** 2)))
        return min(rms * 100, 1.0)  # Normalize to 0-1

    @staticmethod
    def extract_all_features(audio_file: str, sr: int = 16000) -> VoiceSample:
        """Extract all voice features from audio file"""
        if librosa is None:
            raise RuntimeError("librosa required for voice feature extraction")
        
        # Load audio
        audio_data, sr_actual = librosa.load(audio_file, sr=sr)
        duration = librosa.get_duration(y=audio_data, sr=sr_actual)
        
        # Extract features
        mfcc = VoiceFeatureExtractor.extract_mfcc(audio_data, sr_actual)
        pitch_range = VoiceFeatureExtractor.extract_pitch(audio_data, sr_actual)
        energy = VoiceFeatureExtractor.extract_energy(audio_data)
        
        # Create sample record
        sample_id = hashlib.md5(f"{audio_file}{datetime.now()}".encode()).hexdigest()[:8]
        
        return VoiceSample(
            id=sample_id,
            user_id="",  # Will be set by caller
            filename=Path(audio_file).name,
            duration=float(duration),
            sample_rate=sr_actual,
            mfcc_features=[mfcc],
            pitch_range=pitch_range,
            energy_level=energy,
            timestamp=datetime.now().isoformat()
        )


class VoiceProfileManager:
    """Manage user voice profiles"""

    def __init__(self, profiles_dir: str = "data/voice_profiles"):
        """Initialize voice profile manager"""
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(parents=True, exist_ok=True)
        self._profiles: Dict[str, VoiceProfile] = {}
        self._load_profiles()

    def _load_profiles(self):
        """Load all voice profiles from disk"""
        for profile_file in self.profiles_dir.glob("*.json"):
            try:
                with open(profile_file, 'r') as f:
                    data = json.load(f)
                    # Reconstruct profile from JSON
                    self._profiles[data['user_id']] = data
                    logger.info(f"Loaded voice profile: {data['user_id']}")
            except Exception as e:
                logger.error(f"Failed to load profile {profile_file}: {e}")

    def _save_profile(self, profile: VoiceProfile):
        """Save profile to disk"""
        profile_file = self.profiles_dir / f"{profile.user_id}_profile.json"
        try:
            with open(profile_file, 'w') as f:
                json.dump(asdict(profile), f, indent=2)
            logger.info(f"Saved voice profile: {profile.user_id}")
        except Exception as e:
            logger.error(f"Failed to save profile {profile.user_id}: {e}")

    def create_profile(self, user_id: str, profile_name: str) -> VoiceProfile:
        """Create new voice profile for user"""
        profile = VoiceProfile(
            user_id=user_id,
            profile_name=profile_name,
            samples=[],
            avg_mfcc=[],
            pitch_baseline=0.0,
            energy_baseline=0.0,
            voice_characteristics={},
            created_at=datetime.now().isoformat(),
            updated_at=datetime.now().isoformat(),
            accuracy_score=0.0
        )
        self._profiles[user_id] = profile
        self._save_profile(profile)
        return profile

    def add_voice_sample(self, user_id: str, audio_file: str) -> VoiceSample:
        """Add voice sample to user profile"""
        if user_id not in self._profiles:
            raise ValueError(f"Profile not found for user: {user_id}")
        
        profile = self._profiles[user_id]
        
        # Extract features from audio file
        sample = VoiceFeatureExtractor.extract_all_features(audio_file)
        sample.user_id = user_id
        
        # Add to profile
        profile.samples.append(sample)
        
        # Recalculate profile statistics
        self._update_profile_stats(profile)
        self._save_profile(profile)
        
        return sample

    def _update_profile_stats(self, profile: VoiceProfile):
        """Update average statistics for profile"""
        if not profile.samples:
            return
        
        # Calculate average MFCC
        all_mfccs = [sample.mfcc_features[0] for sample in profile.samples if sample.mfcc_features]
        if all_mfccs:
            profile.avg_mfcc = np.mean(all_mfccs, axis=0).tolist()
        
        # Calculate pitch baseline (average of pitch ranges)
        pitch_ranges = [sample.pitch_range for sample in profile.samples]
        if pitch_ranges:
            avg_min_pitch = np.mean([p[0] for p in pitch_ranges])
            avg_max_pitch = np.mean([p[1] for p in pitch_ranges])
            profile.pitch_baseline = (avg_min_pitch + avg_max_pitch) / 2
        
        # Calculate energy baseline
        energies = [sample.energy_level for sample in profile.samples]
        if energies:
            profile.energy_baseline = np.mean(energies)
        
        # Set voice characteristics
        profile.voice_characteristics = {
            "num_samples": len(profile.samples),
            "total_duration_seconds": sum(s.duration for s in profile.samples),
            "avg_pitch_hz": profile.pitch_baseline,
            "energy_level": profile.energy_baseline,
            "quality_score": self._calculate_quality_score(profile)
        }
        
        profile.updated_at = datetime.now().isoformat()

    @staticmethod
    def _calculate_quality_score(profile: VoiceProfile) -> float:
        """Calculate overall profile quality (0.0-1.0)"""
        score = 0.0
        
        # More samples = higher score
        num_samples = min(len(profile.samples) / 10, 0.3)
        score += num_samples
        
        # Longer total duration = higher score
        total_duration = min(sum(s.duration for s in profile.samples) / 300, 0.3)
        score += total_duration
        
        # Consistent energy levels = higher score
        if len(profile.samples) > 1:
            energies = [s.energy_level for s in profile.samples]
            energy_std = np.std(energies) if len(energies) > 1 else 0
            consistency = max(0, 0.4 * (1 - energy_std))
            score += consistency
        else:
            score += 0.2
        
        return min(score, 1.0)

    def get_profile(self, user_id: str) -> Optional[VoiceProfile]:
        """Get voice profile for user"""
        return self._profiles.get(user_id)

    def list_profiles(self) -> List[VoiceProfile]:
        """List all voice profiles"""
        return list(self._profiles.values())


class VoiceRecognitionEngine:
    """Recognize voice input and match to user profile"""

    def __init__(self, profile_manager: VoiceProfileManager):
        """Initialize recognition engine"""
        self.profile_manager = profile_manager
        self.feature_extractor = VoiceFeatureExtractor()

    def _calculate_similarity(self, sample_features: List[float], 
                            profile_features: List[float]) -> float:
        """Calculate similarity between voice features (0.0-1.0)"""
        if not sample_features or not profile_features:
            return 0.0
        
        sample_array = np.array(sample_features)
        profile_array = np.array(profile_features)
        
        # Use cosine similarity
        dot_product = np.dot(sample_array, profile_array)
        norms = np.linalg.norm(sample_array) * np.linalg.norm(profile_array)
        
        if norms == 0:
            return 0.0
        
        similarity = dot_product / norms
        # Normalize to 0-1
        return max(0.0, min(1.0, (similarity + 1) / 2))

    def recognize_voice_input(self, audio_file: str) -> VoiceRecognitionResult:
        """Recognize voice input against user profiles"""
        try:
            # Extract features from input
            if librosa is None:
                return VoiceRecognitionResult(
                    success=False,
                    confidence=0.0,
                    error_message="librosa not available"
                )
            
            input_sample = self.feature_extractor.extract_all_features(audio_file)
            
            if not input_sample.mfcc_features or not input_sample.mfcc_features[0]:
                return VoiceRecognitionResult(
                    success=False,
                    confidence=0.0,
                    error_message="Failed to extract voice features"
                )
            
            # Compare against all profiles
            best_match = None
            best_confidence = 0.0
            
            for profile in self.profile_manager.list_profiles():
                if not profile.avg_mfcc:
                    continue
                
                # Calculate MFCC similarity
                mfcc_similarity = self._calculate_similarity(
                    input_sample.mfcc_features[0],
                    profile.avg_mfcc
                )
                
                # Calculate pitch similarity
                input_pitch = sum(input_sample.pitch_range) / 2
                profile_pitch = profile.pitch_baseline
                pitch_diff = abs(input_pitch - profile_pitch) / max(profile_pitch, 100)
                pitch_similarity = 1.0 - min(1.0, pitch_diff)
                
                # Calculate energy similarity
                energy_diff = abs(input_sample.energy_level - profile.energy_baseline)
                energy_similarity = 1.0 - min(1.0, energy_diff)
                
                # Weighted combination
                confidence = (
                    0.6 * mfcc_similarity +  # MFCC is most important
                    0.2 * pitch_similarity +
                    0.2 * energy_similarity
                )
                
                if confidence > best_confidence:
                    best_confidence = confidence
                    best_match = profile.user_id
            
            # Return result
            if best_confidence > 0.7:  # 70% threshold
                profile = self.profile_manager.get_profile(best_match)
                return VoiceRecognitionResult(
                    success=True,
                    confidence=best_confidence,
                    matched_profile=best_match,
                    voice_characteristics=profile.voice_characteristics if profile else None
                )
            else:
                return VoiceRecognitionResult(
                    success=False,
                    confidence=best_confidence,
                    error_message="No matching voice profile found"
                )
        
        except Exception as e:
            logger.error(f"Voice recognition error: {e}")
            return VoiceRecognitionResult(
                success=False,
                confidence=0.0,
                error_message=str(e)
            )


# Singleton instances
_profile_manager = None
_recognition_engine = None


def get_voice_profile_manager() -> VoiceProfileManager:
    """Get singleton voice profile manager"""
    global _profile_manager
    if _profile_manager is None:
        _profile_manager = VoiceProfileManager()
    return _profile_manager


def get_voice_recognition_engine() -> VoiceRecognitionEngine:
    """Get singleton voice recognition engine"""
    global _recognition_engine
    if _recognition_engine is None:
        manager = get_voice_profile_manager()
        _recognition_engine = VoiceRecognitionEngine(manager)
    return _recognition_engine


# Async wrappers for API integration
async def create_user_voice_profile(user_id: str, profile_name: str) -> Dict:
    """Create voice profile for user"""
    try:
        manager = get_voice_profile_manager()
        profile = manager.create_profile(user_id, profile_name)
        return {
            "success": True,
            "profile_id": profile.user_id,
            "profile_name": profile.profile_name,
            "message": "Voice profile created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating voice profile: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def add_voice_sample_to_profile(user_id: str, audio_file: str) -> Dict:
    """Add voice sample to user's profile"""
    try:
        manager = get_voice_profile_manager()
        sample = manager.add_voice_sample(user_id, audio_file)
        
        profile = manager.get_profile(user_id)
        
        return {
            "success": True,
            "sample_id": sample.id,
            "duration": sample.duration,
            "profile_quality": profile.voice_characteristics if profile else {},
            "message": f"Voice sample added ({sample.duration:.1f}s)"
        }
    except Exception as e:
        logger.error(f"Error adding voice sample: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def recognize_voice_input(audio_file: str) -> Dict:
    """Recognize voice input against profiles"""
    try:
        engine = get_voice_recognition_engine()
        result = engine.recognize_voice_input(audio_file)
        
        return {
            "success": result.success,
            "confidence": result.confidence,
            "matched_user": result.matched_profile,
            "voice_characteristics": result.voice_characteristics,
            "error": result.error_message
        }
    except Exception as e:
        logger.error(f"Error recognizing voice: {e}")
        return {
            "success": False,
            "error": str(e)
        }


async def get_user_voice_profile_details(user_id: str) -> Dict:
    """Get detailed profile information"""
    try:
        manager = get_voice_profile_manager()
        profile = manager.get_profile(user_id)
        
        if not profile:
            return {
                "success": False,
                "error": f"Profile not found for user: {user_id}"
            }
        
        return {
            "success": True,
            "profile": {
                "user_id": profile.user_id,
                "profile_name": profile.profile_name,
                "num_samples": len(profile.samples),
                "characteristics": profile.voice_characteristics,
                "accuracy_score": profile.accuracy_score,
                "created_at": profile.created_at,
                "updated_at": profile.updated_at
            }
        }
    except Exception as e:
        logger.error(f"Error getting profile details: {e}")
        return {
            "success": False,
            "error": str(e)
        }
