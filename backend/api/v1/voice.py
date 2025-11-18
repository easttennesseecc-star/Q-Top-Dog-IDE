"""
Voice Profiling REST API
Endpoints for voice profile management and recognition
"""

import os
import logging
from functools import wraps
from flask import Blueprint, request, jsonify
import asyncio
from werkzeug.utils import secure_filename

from backend.services.voice_profiling_engine import (
    get_voice_profile_manager,
    create_user_voice_profile,
    add_voice_sample_to_profile,
    recognize_voice_input,
    get_user_voice_profile_details
)

logger = logging.getLogger(__name__)

voice_bp = Blueprint('voice', __name__, url_prefix='/api/v1/voice')

# Configuration
UPLOAD_FOLDER = 'uploads/voice_samples'
ALLOWED_EXTENSIONS = {'wav', 'mp3', 'ogg', 'm4a', 'flac'}

os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def async_route(rule, **options):
    """Decorator for async Flask routes"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            return asyncio.run(f(*args, **kwargs))
        return voice_bp.route(rule, **options)(wrapped)
    return decorator


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ===== Profile Management Endpoints =====

@async_route('/profile/create', methods=['POST'])
async def create_profile():
    """Create new voice profile for user
    
    Request JSON:
    {
        "user_id": "user123",
        "profile_name": "My Voice Profile"
    }
    
    Response:
    {
        "success": true,
        "profile_id": "user123",
        "profile_name": "My Voice Profile",
        "message": "Voice profile created successfully"
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'user_id' not in data:
            return jsonify({"error": "Missing user_id"}), 400
        
        user_id = data['user_id']
        profile_name = data.get('profile_name', f"Profile for {user_id}")
        
        result = await create_user_voice_profile(user_id, profile_name)
        
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
    
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        return jsonify({"error": str(e)}), 500


@async_route('/profile/<user_id>', methods=['GET'])
async def get_profile(user_id):
    """Get voice profile details
    
    Response:
    {
        "success": true,
        "profile": {
            "user_id": "user123",
            "profile_name": "My Voice Profile",
            "num_samples": 5,
            "characteristics": {...},
            "accuracy_score": 0.85,
            "created_at": "2025-10-29T...",
            "updated_at": "2025-10-29T..."
        }
    }
    """
    try:
        result = await get_user_voice_profile_details(user_id)
        status_code = 200 if result['success'] else 404
        return jsonify(result), status_code
    
    except Exception as e:
        logger.error(f"Error getting profile: {e}")
        return jsonify({"error": str(e)}), 500


@async_route('/profile/list', methods=['GET'])
async def list_profiles():
    """List all voice profiles
    
    Response:
    {
        "success": true,
        "profiles": [
            {
                "user_id": "user123",
                "profile_name": "Profile 1",
                "num_samples": 5,
                "accuracy_score": 0.85
            },
            ...
        ],
        "total": 3
    }
    """
    try:
        manager = get_voice_profile_manager()
        profiles = manager.list_profiles()
        
        profile_data = [
            {
                "user_id": p.user_id,
                "profile_name": p.profile_name,
                "num_samples": len(p.samples),
                "accuracy_score": p.accuracy_score,
                "created_at": p.created_at
            }
            for p in profiles
        ]
        
        return jsonify({
            "success": True,
            "profiles": profile_data,
            "total": len(profile_data)
        }), 200
    
    except Exception as e:
        logger.error(f"Error listing profiles: {e}")
        return jsonify({"error": str(e)}), 500


# ===== Voice Sample Endpoints =====

@async_route('/sample/add/<user_id>', methods=['POST'])
async def add_voice_sample(user_id):
    """Add voice sample to user's profile
    
    Multipart form data:
    - file: Audio file (wav, mp3, ogg, m4a, flac)
    - transcription (optional): Text transcription
    
    Response:
    {
        "success": true,
        "sample_id": "abc123",
        "duration": 3.5,
        "profile_quality": {
            "num_samples": 6,
            "total_duration_seconds": 21.5,
            "quality_score": 0.82
        },
        "message": "Voice sample added (3.5s)"
    }
    """
    try:
        # Check if file exists in request
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "error": f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # Save uploaded file
        filename = secure_filename(f"{user_id}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        # Add to profile
        result = await add_voice_sample_to_profile(user_id, filepath)
        
        status_code = 201 if result['success'] else 400
        return jsonify(result), status_code
    
    except Exception as e:
        logger.error(f"Error adding voice sample: {e}")
        return jsonify({"error": str(e)}), 500


# ===== Voice Recognition Endpoints =====

@async_route('/recognize', methods=['POST'])
async def recognize():
    """Recognize voice input against profiles
    
    Multipart form data:
    - file: Audio file to recognize
    
    Response:
    {
        "success": true,
        "confidence": 0.92,
        "matched_user": "user123",
        "voice_characteristics": {
            "num_samples": 5,
            "avg_pitch_hz": 165.5,
            "energy_level": 0.65,
            ...
        }
    }
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file uploaded"}), 400
        
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No file selected"}), 400
        
        if not allowed_file(file.filename):
            return jsonify({
                "error": f"File type not allowed. Supported: {', '.join(ALLOWED_EXTENSIONS)}"
            }), 400
        
        # Save temporarily
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, f"temp_{filename}")
        file.save(filepath)
        
        # Recognize
        result = await recognize_voice_input(filepath)
        
        # Clean up
        try:
            os.remove(filepath)
        except:
            pass
        
        return jsonify(result), 200
    
    except Exception as e:
        logger.error(f"Error recognizing voice: {e}")
        return jsonify({"error": str(e)}), 500


# ===== Health Check =====

@voice_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


# ===== Registration =====

def register_voice_routes(app):
    """Register voice profiling routes with Flask app"""
    app.register_blueprint(voice_bp)
    logger.info("Voice profiling routes registered")
