"""
Customization REST API
Endpoints for theme generation, image upload, and customization features
"""

import os
import contextlib
import logging
from functools import wraps
from flask import Blueprint, request, jsonify
import asyncio
from werkzeug.utils import secure_filename
import json
import uuid
from datetime import datetime

logger = logging.getLogger(__name__)

customization_bp = Blueprint('customization', __name__, url_prefix='/api/v1/customization')

# Configuration: prefer writable locations in containers
_cfg_dir = os.getenv("QIDE_CONFIG_DIR") or \
           os.getenv("XDG_RUNTIME_DIR") or "/tmp/.q-ide"
_base_uploads = os.getenv("UPLOADS_DIR") or os.path.join(_cfg_dir, "uploads")
UPLOAD_FOLDER = os.getenv("THEME_UPLOAD_DIR") or os.path.join(_base_uploads, "themes")
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'svg', 'gif'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

try:
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)
except Exception:
    # Fallback to /tmp if the chosen path isn't writable
    UPLOAD_FOLDER = os.path.join("/tmp", "uploads", "themes")
    with contextlib.suppress(Exception):
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def async_route(rule, **options):
    """Decorator for async Flask routes"""
    def decorator(f):
        @wraps(f)
        def wrapped(*args, **kwargs):
            return asyncio.run(f(*args, **kwargs))
        return customization_bp.route(rule, **options)(wrapped)
    return decorator


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


# ===== Theme Generation Endpoints =====

@async_route('/generate-theme', methods=['POST'])
async def generate_theme():
    """Generate theme using Q-Assistant
    
    Request JSON:
    {
        "prompt": "Dark theme with blue accents and minimalist design",
        "imageSize": "512x512",
        "user_id": "user123" (optional)
    }
    
    Response:
    {
        "success": true,
        "id": "theme_abc123",
        "imageUrl": "https://...",
        "themeData": {
            "colors": {
                "primary": "#...",
                "secondary": "#...",
                ...
            }
        },
        "source": "q-assistant",
        "generatedAt": "2025-10-29T..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'prompt' not in data:
            return jsonify({"error": "Missing prompt"}), 400
        
        prompt = data['prompt']
        image_size = data.get('imageSize', '512x512')
        user_id = data.get('user_id', 'anonymous')
        
        # Call Q-Assistant API or Runway API
        theme_response = await call_theme_generation_service(
            prompt=prompt,
            image_size=image_size,
            user_id=user_id
        )
        
        # Extract colors from generated image using AI vision
        colors = await extract_colors_from_image(theme_response.get('imageUrl', ''))
        
        theme_id = f"theme_{uuid.uuid4().hex[:8]}"
        
        result = {
            "success": True,
            "id": theme_id,
            "imageUrl": theme_response.get('imageUrl', ''),
            "themeData": {
                "colors": colors,
                "metadata": {
                    "prompt": prompt,
                    "source": "q-assistant"
                }
            },
            "source": "q-assistant",
            "generatedAt": datetime.utcnow().isoformat(),
            "message": "Theme generated successfully"
        }
        
        # Store theme for later retrieval
        await store_theme(theme_id, result, user_id)
        
        return jsonify(result), 201
    
    except Exception as e:
        logger.error(f"Error generating theme: {e}")
        return jsonify({"error": str(e)}), 500


@async_route('/generate-avatar', methods=['POST'])
async def generate_avatar():
    """Generate user avatar using Q-Assistant
    
    Request JSON:
    {
        "description": "Professional avatar, blue background, smiling",
        "user_id": "user123"
    }
    
    Response:
    {
        "success": true,
        "id": "avatar_abc123",
        "imageUrl": "https://...",
        "source": "q-assistant",
        "generatedAt": "2025-10-29T..."
    }
    """
    try:
        data = request.get_json()
        
        if not data or 'description' not in data:
            return jsonify({"error": "Missing description"}), 400
        
        description = data['description']
        user_id = data.get('user_id', 'anonymous')
        
        # Build prompt for avatar generation
        full_prompt = f"Generate a professional avatar: {description}"
        
        avatar_response = await call_theme_generation_service(
            prompt=full_prompt,
            image_size='256x256',
            user_id=user_id
        )
        
        avatar_id = f"avatar_{uuid.uuid4().hex[:8]}"
        
        result = {
            "success": True,
            "id": avatar_id,
            "imageUrl": avatar_response.get('imageUrl', ''),
            "source": "q-assistant",
            "generatedAt": datetime.utcnow().isoformat(),
            "description": description,
            "message": "Avatar generated successfully"
        }
        
        # Store avatar
        await store_avatar(avatar_id, result, user_id)
        
        return jsonify(result), 201
    
    except Exception as e:
        logger.error(f"Error generating avatar: {e}")
        return jsonify({"error": str(e)}), 500


# ===== Theme Upload Endpoints =====

@customization_bp.route('/upload-theme', methods=['POST'])
def upload_theme():
    """Upload custom theme image
    
    Multipart form data:
    - file: Theme image (png, jpg, svg, gif)
    - name: Theme name (optional)
    - user_id: User ID (optional)
    
    Response:
    {
        "success": true,
        "id": "theme_abc123",
        "filename": "my-theme.png",
        "url": "/uploads/themes/my-theme.png",
        "uploadedAt": "2025-10-29T..."
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
        
        # Check file size
        file.seek(0, os.SEEK_END)
        file_length = file.tell()
        file.seek(0)
        
        if file_length > MAX_FILE_SIZE:
            return jsonify({"error": f"File too large (max {MAX_FILE_SIZE // 1024 // 1024}MB)"}), 400
        
        # Save file
        filename = secure_filename(f"{uuid.uuid4().hex[:8]}_{file.filename}")
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        
        theme_id = f"theme_{uuid.uuid4().hex[:8]}"
        user_id = request.form.get('user_id', 'anonymous')
        
        result = {
            "success": True,
            "id": theme_id,
            "filename": filename,
            "url": f"/uploads/themes/{filename}",
            "uploadedAt": datetime.utcnow().isoformat(),
            "message": "Theme uploaded successfully"
        }
        
        # Store metadata
        metadata = {
            "id": theme_id,
            "filename": filename,
            "originalName": file.filename,
            "size": file_length,
            "uploadedAt": result["uploadedAt"],
            "user_id": user_id
        }
        
        metadata_path = os.path.join(UPLOAD_FOLDER, f"{theme_id}_meta.json")
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f)
        
        return jsonify(result), 201
    
    except Exception as e:
        logger.error(f"Error uploading theme: {e}")
        return jsonify({"error": str(e)}), 500


# ===== Theme List/Retrieval Endpoints =====

@customization_bp.route('/themes/<user_id>', methods=['GET'])
def get_user_themes(user_id):
    """Get all themes for a user
    
    Response:
    {
        "success": true,
        "themes": [
            {
                "id": "theme_abc123",
                "name": "Dark Blue",
                "type": "generated" | "uploaded",
                "url": "...",
                "createdAt": "2025-10-29T..."
            },
            ...
        ],
        "total": 5
    }
    """
    try:
        themes = []
        
        # Get metadata files
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename.endswith('_meta.json'):
                metadata_path = os.path.join(UPLOAD_FOLDER, filename)
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                if metadata.get('user_id') == user_id:
                    themes.append({
                        "id": metadata['id'],
                        "name": metadata.get('originalName', 'Unnamed'),
                        "type": "uploaded",
                        "url": f"/uploads/themes/{metadata['filename']}",
                        "createdAt": metadata.get('uploadedAt')
                    })
        
        return jsonify({
            "success": True,
            "themes": themes,
            "total": len(themes)
        }), 200
    
    except Exception as e:
        logger.error(f"Error getting themes: {e}")
        return jsonify({"error": str(e)}), 500


@customization_bp.route('/theme/<theme_id>', methods=['GET'])
def get_theme(theme_id):
    """Get specific theme details
    
    Response:
    {
        "success": true,
        "theme": {
            "id": "theme_abc123",
            "url": "...",
            "colors": {...},
            "metadata": {...}
        }
    }
    """
    try:
        # Look for metadata file
        for filename in os.listdir(UPLOAD_FOLDER):
            if filename == f"{theme_id}_meta.json":
                metadata_path = os.path.join(UPLOAD_FOLDER, filename)
                with open(metadata_path, 'r') as f:
                    metadata = json.load(f)
                
                return jsonify({
                    "success": True,
                    "theme": {
                        "id": theme_id,
                        "url": f"/uploads/themes/{metadata['filename']}",
                        "metadata": metadata
                    }
                }), 200
        
        return jsonify({"error": "Theme not found"}), 404
    
    except Exception as e:
        logger.error(f"Error getting theme: {e}")
        return jsonify({"error": str(e)}), 500


# ===== Preset Themes Endpoint =====

@customization_bp.route('/presets', methods=['GET'])
def get_preset_themes():
    """Get available preset themes
    
    Response:
    {
        "success": true,
        "presets": [
            {
                "id": "dark-blue",
                "name": "Dark Blue",
                "colors": {...},
                "preview": "..."
            },
            ...
        ]
    }
    """
    presets = [
        {
            "id": "dark-blue",
            "name": "Dark Blue",
            "type": "dark",
            "colors": {
                "primary": "#3b82f6",
                "secondary": "#8b5cf6",
                "background": "#1f2937",
                "text": "#f3f4f6",
                "accent": "#ec4899"
            }
        },
        {
            "id": "light-minimal",
            "name": "Light Minimal",
            "type": "light",
            "colors": {
                "primary": "#2563eb",
                "secondary": "#7c3aed",
                "background": "#ffffff",
                "text": "#1f2937",
                "accent": "#db2777"
            }
        },
        {
            "id": "neon-dark",
            "name": "Neon Dark",
            "type": "dark",
            "colors": {
                "primary": "#00ff00",
                "secondary": "#ff00ff",
                "background": "#0a0e27",
                "text": "#00ff00",
                "accent": "#00ffff"
            }
        },
        {
            "id": "ocean-breeze",
            "name": "Ocean Breeze",
            "type": "dark",
            "colors": {
                "primary": "#06b6d4",
                "secondary": "#0891b2",
                "background": "#0f172a",
                "text": "#e0f2fe",
                "accent": "#7dd3fc"
            }
        },
        {
            "id": "sunset",
            "name": "Sunset",
            "type": "dark",
            "colors": {
                "primary": "#f97316",
                "secondary": "#fb923c",
                "background": "#1c1410",
                "text": "#fef3c7",
                "accent": "#fbbf24"
            }
        }
    ]
    
    return jsonify({
        "success": True,
        "presets": presets,
        "total": len(presets)
    }), 200


# ===== Health Check =====

@customization_bp.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({"status": "healthy"}), 200


# ===== Helper Functions =====

async def call_theme_generation_service(prompt: str, image_size: str, user_id: str) -> dict:
    """
    Call Q-Assistant or Runway API to generate theme/avatar
    
    In production, this would call actual API. For now, returns placeholder.
    """
    try:
        # Placeholder implementation
        # In production, call Q-Assistant API or Runway API
        logger.info(f"Generating theme for {user_id}: {prompt}")
        
        # Simulate API call
        return {
            "imageUrl": f"https://placeholder-images.example.com/{image_size}?prompt={prompt}",
            "success": True
        }
    except Exception as e:
        logger.error(f"Error calling generation service: {e}")
        raise


async def extract_colors_from_image(image_url: str) -> dict:
    """
    Extract dominant colors from image using AI vision
    
    Placeholder that returns default colors.
    In production, would use image analysis API.
    """
    try:
        # Placeholder implementation
        # In production, call vision API to extract colors
        default_colors = {
            "primary": "#3b82f6",
            "secondary": "#8b5cf6",
            "background": "#1f2937",
            "text": "#f3f4f6",
            "accent": "#ec4899"
        }
        return default_colors
    except Exception as e:
        logger.error(f"Error extracting colors: {e}")
        return {}


async def store_theme(theme_id: str, theme_data: dict, user_id: str) -> None:
    """Store generated theme for persistence"""
    try:
        metadata_path = os.path.join(UPLOAD_FOLDER, f"{theme_id}_meta.json")
        
        metadata = {
            "id": theme_id,
            "user_id": user_id,
            "imageUrl": theme_data.get('imageUrl'),
            "colors": theme_data.get('themeData', {}).get('colors'),
            "source": "q-assistant",
            "generatedAt": theme_data.get('generatedAt')
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    except Exception as e:
        logger.error(f"Error storing theme: {e}")


async def store_avatar(avatar_id: str, avatar_data: dict, user_id: str) -> None:
    """Store generated avatar for persistence"""
    try:
        metadata_path = os.path.join(UPLOAD_FOLDER, f"{avatar_id}_meta.json")
        
        metadata = {
            "id": avatar_id,
            "user_id": user_id,
            "imageUrl": avatar_data.get('imageUrl'),
            "description": avatar_data.get('description'),
            "source": "q-assistant",
            "generatedAt": avatar_data.get('generatedAt')
        }
        
        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)
    
    except Exception as e:
        logger.error(f"Error storing avatar: {e}")


# ===== Registration =====

def register_customization_routes(app):
    """Register customization routes with Flask app"""
    app.register_blueprint(customization_bp)
    logger.info("Customization routes registered")
