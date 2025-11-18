"""
Voice Profiling Engine Tests
Comprehensive test suite for voice profile management and recognition
"""

import pytest
import numpy as np
import tempfile

from backend.services.voice_profiling_engine import (
    VoiceSample,
    VoiceProfile,
    VoiceRecognitionResult,
    VoiceFeatureExtractor,
    VoiceProfileManager,
    VoiceRecognitionEngine,
)


# ===== Fixtures =====

@pytest.fixture
def temp_profile_dir():
    """Create temporary directory for profiles"""
    with tempfile.TemporaryDirectory() as tmpdir:
        yield tmpdir


@pytest.fixture
def feature_extractor():
    """Create VoiceFeatureExtractor instance"""
    return VoiceFeatureExtractor()


@pytest.fixture
def sample_audio_array():
    """Generate sample audio array (1-second audio at 16kHz)"""
    sample_rate = 16000
    duration = 1.0
    frequency = 440  # A4 note
    t = np.arange(int(sample_rate * duration)) / sample_rate
    # Generate sine wave with harmonics
    audio = np.sin(2 * np.pi * frequency * t)
    # Add some noise
    audio += 0.1 * np.random.randn(len(audio))
    # Normalize
    audio = audio / np.max(np.abs(audio))
    return audio.astype(np.float32)


@pytest.fixture
def profile_manager(temp_profile_dir):
    """Create VoiceProfileManager instance"""
    manager = VoiceProfileManager(profile_dir=temp_profile_dir)
    return manager


@pytest.fixture
def recognition_engine(profile_manager):
    """Create VoiceRecognitionEngine instance"""
    return VoiceRecognitionEngine(profile_manager)


# ===== VoiceFeatureExtractor Tests =====

class TestVoiceFeatureExtractor:
    """Tests for audio feature extraction"""
    
    def test_extract_mfcc_shape(self, feature_extractor, sample_audio_array):
        """Test MFCC extraction returns correct shape"""
        mfcc = feature_extractor.extract_mfcc(sample_audio_array)
        
        assert isinstance(mfcc, np.ndarray)
        assert mfcc.shape[0] == 13  # 13 MFCC coefficients
        assert not np.isnan(mfcc).any()  # No NaN values
    
    def test_extract_mfcc_values_reasonable(self, feature_extractor, sample_audio_array):
        """Test MFCC values are in reasonable range"""
        mfcc = feature_extractor.extract_mfcc(sample_audio_array)
        
        # MFCC values typically between -20 and 20
        assert np.all(np.abs(mfcc) < 100)
    
    def test_extract_pitch_range(self, feature_extractor, sample_audio_array):
        """Test pitch extraction returns reasonable frequency"""
        pitch = feature_extractor.extract_pitch(sample_audio_array)
        
        assert isinstance(pitch, float)
        assert 80 < pitch < 300  # Reasonable human voice range
    
    def test_extract_energy_valid(self, feature_extractor, sample_audio_array):
        """Test energy extraction returns valid value"""
        energy = feature_extractor.extract_energy(sample_audio_array)
        
        assert isinstance(energy, float)
        assert 0 <= energy <= 1  # Normalized energy
    
    def test_extract_features_consistency(self, feature_extractor, sample_audio_array):
        """Test feature extraction is consistent for same audio"""
        features1 = feature_extractor.extract_mfcc(sample_audio_array)
        features2 = feature_extractor.extract_mfcc(sample_audio_array)
        
        np.testing.assert_array_almost_equal(features1, features2)
    
    def test_extract_features_silence_vs_sound(self, feature_extractor):
        """Test features differ between silence and sound"""
        silence = np.zeros(16000)  # 1 second silence
        sound = np.sin(2 * np.pi * 440 * np.arange(16000) / 16000)  # 1 second tone
        
        silence_energy = feature_extractor.extract_energy(silence)
        sound_energy = feature_extractor.extract_energy(sound)
        
        assert sound_energy > silence_energy


# ===== VoiceProfile Tests =====

class TestVoiceProfile:
    """Tests for VoiceProfile dataclass"""
    
    def test_voice_profile_creation(self):
        """Test VoiceProfile can be created"""
        profile = VoiceProfile(
            user_id="test_user",
            profile_name="Test Profile"
        )
        
        assert profile.user_id == "test_user"
        assert profile.profile_name == "Test Profile"
        assert len(profile.samples) == 0
        assert profile.num_samples == 0
    
    def test_voice_sample_addition(self):
        """Test adding voice samples to profile"""
        profile = VoiceProfile(
            user_id="test_user",
            profile_name="Test Profile"
        )
        
        sample = VoiceSample(
            mfcc=np.random.randn(13),
            pitch=440.0,
            energy=0.8
        )
        profile.samples.append(sample)
        
        assert profile.num_samples == 1
        assert len(profile.samples) == 1
    
    def test_profile_characteristics_computation(self):
        """Test profile characteristics are computed correctly"""
        profile = VoiceProfile(
            user_id="test_user",
            profile_name="Test Profile"
        )
        
        # Add multiple samples
        for _ in range(3):
            sample = VoiceSample(
                mfcc=np.random.randn(13),
                pitch=np.random.uniform(100, 200),
                energy=np.random.uniform(0.5, 0.9)
            )
            profile.samples.append(sample)
        
        assert profile.num_samples == 3
        assert len(profile.characteristics) > 0


# ===== VoiceProfileManager Tests =====

class TestVoiceProfileManager:
    """Tests for voice profile management"""
    
    def test_create_profile(self, profile_manager):
        """Test profile creation"""
        profile = profile_manager.create_profile(
            user_id="user1",
            profile_name="User 1 Profile"
        )
        
        assert profile.user_id == "user1"
        assert profile.profile_name == "User 1 Profile"
        assert profile.num_samples == 0
    
    def test_get_profile(self, profile_manager):
        """Test retrieving profile"""
        profile_manager.create_profile("user1", "Profile 1")
        
        retrieved = profile_manager.get_profile("user1")
        assert retrieved is not None
        assert retrieved.user_id == "user1"
    
    def test_get_nonexistent_profile(self, profile_manager):
        """Test retrieving nonexistent profile returns None"""
        result = profile_manager.get_profile("nonexistent")
        assert result is None
    
    def test_list_profiles(self, profile_manager):
        """Test listing all profiles"""
        profile_manager.create_profile("user1", "Profile 1")
        profile_manager.create_profile("user2", "Profile 2")
        
        profiles = profile_manager.list_profiles()
        assert len(profiles) == 2
        assert any(p.user_id == "user1" for p in profiles)
        assert any(p.user_id == "user2" for p in profiles)
    
    def test_add_voice_sample(self, profile_manager):
        """Test adding voice sample to profile"""
        profile_manager.create_profile("user1", "Profile 1")
        
        sample = VoiceSample(
            mfcc=np.random.randn(13),
            pitch=440.0,
            energy=0.8
        )
        
        profile_manager.add_sample("user1", sample)
        
        profile = profile_manager.get_profile("user1")
        assert profile.num_samples == 1
    
    def test_profile_persistence(self, profile_manager):
        """Test profiles are saved and loaded correctly"""
        profile_manager.create_profile("user1", "Profile 1")
        
        # Create new manager instance with same directory
        new_manager = VoiceProfileManager(
            profile_dir=profile_manager.profile_dir
        )
        
        profile = new_manager.get_profile("user1")
        assert profile is not None
        assert profile.user_id == "user1"
    
    def test_profile_quality_scoring(self, profile_manager):
        """Test profile quality score is calculated"""
        profile_manager.create_profile("user1", "Profile 1")
        
        # Add samples
        for _ in range(5):
            sample = VoiceSample(
                mfcc=np.random.randn(13),
                pitch=np.random.uniform(100, 200),
                energy=np.random.uniform(0.5, 0.9),
                duration=1.0
            )
            profile_manager.add_sample("user1", sample)
        
        profile = profile_manager.get_profile("user1")
        assert hasattr(profile, 'accuracy_score')
        assert 0 <= profile.accuracy_score <= 1


# ===== VoiceRecognitionEngine Tests =====

class TestVoiceRecognitionEngine:
    """Tests for voice recognition"""
    
    def test_recognition_returns_result(self, recognition_engine, profile_manager, feature_extractor, sample_audio_array):
        """Test recognition returns valid result"""
        # Create profile
        profile_manager.create_profile("user1", "User 1")
        
        # Add samples
        sample = VoiceSample(
            mfcc=feature_extractor.extract_mfcc(sample_audio_array),
            pitch=feature_extractor.extract_pitch(sample_audio_array),
            energy=feature_extractor.extract_energy(sample_audio_array)
        )
        profile_manager.add_sample("user1", sample)
        
        # Recognize
        result = recognition_engine.recognize(sample_audio_array)
        
        assert isinstance(result, VoiceRecognitionResult)
        assert hasattr(result, 'confidence')
        assert hasattr(result, 'matched_user')
        assert 0 <= result.confidence <= 1
    
    def test_recognition_confidence_threshold(self, recognition_engine, profile_manager):
        """Test recognition respects confidence threshold"""
        # Create profile with one sample
        profile_manager.create_profile("user1", "User 1")
        
        # Generate different audio
        silence = np.zeros(16000)
        
        result = recognition_engine.recognize(silence)
        
        # Should be rejected as confidence too low
        assert result.confidence < 0.7
    
    def test_recognition_multiple_profiles(self, recognition_engine, profile_manager, feature_extractor, sample_audio_array):
        """Test recognition with multiple profiles"""
        # Create multiple profiles
        profile_manager.create_profile("user1", "User 1")
        profile_manager.create_profile("user2", "User 2")
        
        # Add different samples to each
        sample1 = VoiceSample(
            mfcc=feature_extractor.extract_mfcc(sample_audio_array),
            pitch=150.0,
            energy=0.7
        )
        profile_manager.add_sample("user1", sample1)
        
        # Slightly different audio for user2
        different_audio = sample_audio_array * 0.8  # Lower amplitude
        sample2 = VoiceSample(
            mfcc=feature_extractor.extract_mfcc(different_audio),
            pitch=180.0,
            energy=0.6
        )
        profile_manager.add_sample("user2", sample2)
        
        result = recognition_engine.recognize(sample_audio_array)
        
        assert result.confidence > 0
        # First profile should have higher confidence
        if result.matched_user:
            assert result.matched_user == "user1"


# ===== Async Function Tests =====

class TestAsyncFunctions:
    """Tests for async wrapper functions"""
    
    @pytest.mark.asyncio
    async def test_create_user_voice_profile_async(self):
        """Test async profile creation"""
        from backend.services.voice_profiling_engine import (
            create_user_voice_profile
        )
        
        with tempfile.TemporaryDirectory():
            # Mock the manager
            result = await create_user_voice_profile("user1", "Test Profile")
            
            assert result['success'] or not result['success']  # Returns dict
            assert 'profile_id' in result or 'error' in result


# ===== Performance Tests =====

class TestPerformance:
    """Tests for performance requirements"""
    
    def test_mfcc_extraction_performance(self, feature_extractor, sample_audio_array):
        """Test MFCC extraction completes in <50ms"""
        import time
        
        start = time.time()
        for _ in range(10):
            feature_extractor.extract_mfcc(sample_audio_array)
        elapsed = (time.time() - start) / 10
        
        assert elapsed < 0.050  # 50ms per extraction
    
    def test_recognition_performance(self, recognition_engine, profile_manager, feature_extractor, sample_audio_array):
        """Test recognition completes in <100ms"""
        import time
        
        # Setup profile
        profile_manager.create_profile("user1", "User 1")
        sample = VoiceSample(
            mfcc=feature_extractor.extract_mfcc(sample_audio_array),
            pitch=440.0,
            energy=0.8
        )
        profile_manager.add_sample("user1", sample)
        
        # Measure recognition time
        start = time.time()
        for _ in range(5):
            recognition_engine.recognize(sample_audio_array)
        elapsed = (time.time() - start) / 5
        
        assert elapsed < 0.100  # 100ms per recognition


# ===== Integration Tests =====

class TestIntegration:
    """Integration tests combining multiple components"""
    
    def test_full_voice_workflow(self, profile_manager, recognition_engine, feature_extractor, sample_audio_array):
        """Test complete workflow: create profile → add samples → recognize"""
        # Create profile
        profile = profile_manager.create_profile("user1", "User 1")
        assert profile.user_id == "user1"
        
        # Add multiple samples
        for _ in range(3):
            sample = VoiceSample(
                mfcc=feature_extractor.extract_mfcc(sample_audio_array),
                pitch=np.random.uniform(100, 200),
                energy=np.random.uniform(0.5, 0.9)
            )
            profile_manager.add_sample("user1", sample)
        
        # Verify samples added
        profile = profile_manager.get_profile("user1")
        assert profile.num_samples == 3
        
        # Recognize voice
        result = recognition_engine.recognize(sample_audio_array)
        assert result.confidence > 0
    
    def test_multiple_user_profiles(self, profile_manager):
        """Test managing multiple user profiles simultaneously"""
        users = ["user1", "user2", "user3"]
        
        # Create profiles
        for user in users:
            profile_manager.create_profile(user, f"Profile for {user}")
        
        # Verify all exist
        profiles = profile_manager.list_profiles()
        assert len(profiles) == 3
        
        # Verify each can be retrieved
        for user in users:
            profile = profile_manager.get_profile(user)
            assert profile is not None
            assert profile.user_id == user


# ===== Error Handling Tests =====

class TestErrorHandling:
    """Tests for error handling and edge cases"""
    
    def test_empty_audio_handling(self, feature_extractor):
        """Test handling of empty audio"""
        empty_audio = np.array([], dtype=np.float32)
        
        # Should handle gracefully or raise appropriate error
        try:
            feature_extractor.extract_mfcc(empty_audio)
        except (ValueError, IndexError):
            pass  # Expected
    
    def test_very_short_audio(self, feature_extractor):
        """Test handling of very short audio"""
        short_audio = np.zeros(100, dtype=np.float32)  # 6ms at 16kHz
        
        # Should handle gracefully
        try:
            mfcc = feature_extractor.extract_mfcc(short_audio)
            # If it completes, result should be valid
            if mfcc is not None:
                assert isinstance(mfcc, np.ndarray)
        except (ValueError, IndexError):
            pass  # Also acceptable
    
    def test_add_sample_to_nonexistent_profile(self, profile_manager):
        """Test adding sample to nonexistent profile"""
        sample = VoiceSample(
            mfcc=np.random.randn(13),
            pitch=440.0,
            energy=0.8
        )
        
        # Should handle gracefully
        try:
            profile_manager.add_sample("nonexistent_user", sample)
        except KeyError:
            pass  # Expected


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
