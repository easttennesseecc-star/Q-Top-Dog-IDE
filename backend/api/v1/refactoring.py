"""
REST API Routes for Refactoring Operations
Endpoints for extract function, rename symbol, move to file
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
from functools import wraps
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

refactor_bp = Blueprint('refactoring', __name__, url_prefix='/api/v1/refactor')


def async_route(f):
    """Decorator to handle async route functions"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f(*args, **kwargs))
    return wrapped


# Import refactoring operations
try:
    from backend.services.refactoring_engine import (
        get_refactoring_engine,
        extract_function_refactor,
        rename_symbol_refactor,
        move_to_file_refactor,
    )
except ImportError:
    logger.warning("Could not import refactoring engine")


@refactor_bp.route('/extract', methods=['POST'])
@cross_origin()
@async_route
async def extract_function():
    """
    Extract code into function
    
    POST /api/v1/refactor/extract
    {
        "source": "def foo():\n    x = 1\n    y = 2",
        "name": "calculate",
        "start_line": 2,
        "end_line": 3,
        "parameters": ["x"]
    }
    
    Returns:
    {
        "success": true,
        "changes": [...],
        "refactored": "..."
    }
    """
    try:
        data = request.get_json()
        source = data.get('source', '')
        name = data.get('name', 'extracted_function')
        start_line = data.get('start_line', 1)
        end_line = data.get('end_line', 1)
        parameters = data.get('parameters', [])

        result = await extract_function_refactor(
            source=source,
            name=name,
            start_line=start_line,
            end_line=end_line,
            parameters=parameters
        )

        logger.info(f"Extract function: {name} (lines {start_line}-{end_line})")
        return jsonify(result), 200 if result.get('success') else 400

    except Exception as e:
        logger.error(f"Error extracting function: {e}")
        return jsonify({'error': str(e)}), 500


@refactor_bp.route('/rename', methods=['POST'])
@cross_origin()
@async_route
async def rename_symbol():
    """
    Rename symbol throughout file
    
    POST /api/v1/refactor/rename
    {
        "source": "def foo():\n    x = 1\n    return x",
        "old_name": "x",
        "new_name": "result"
    }
    
    Returns:
    {
        "success": true,
        "changes": 2,
        "refactored": "..."
    }
    """
    try:
        data = request.get_json()
        source = data.get('source', '')
        old_name = data.get('old_name', '')
        new_name = data.get('new_name', '')

        if not old_name or not new_name:
            return jsonify({'error': 'old_name and new_name required'}), 400

        result = await rename_symbol_refactor(
            source=source,
            old_name=old_name,
            new_name=new_name
        )

        logger.info(f"Rename symbol: {old_name} → {new_name} ({result.get('changes')} changes)")
        return jsonify(result), 200 if result.get('success') else 400

    except Exception as e:
        logger.error(f"Error renaming symbol: {e}")
        return jsonify({'error': str(e)}), 500


@refactor_bp.route('/move', methods=['POST'])
@cross_origin()
@async_route
async def move_to_file():
    """
    Move symbol to new file
    
    POST /api/v1/refactor/move
    {
        "source": "def foo():\n    return 42",
        "symbol_name": "foo",
        "target_file": "utils.py"
    }
    
    Returns:
    {
        "success": true,
        "source_file_changes": [...],
        "new_file": "..."
    }
    """
    try:
        data = request.get_json()
        source = data.get('source', '')
        symbol_name = data.get('symbol_name', '')
        target_file = data.get('target_file', '')

        if not symbol_name or not target_file:
            return jsonify({'error': 'symbol_name and target_file required'}), 400

        result = await move_to_file_refactor(
            source=source,
            symbol_name=symbol_name,
            target_file=target_file
        )

        logger.info(f"Move to file: {symbol_name} → {target_file}")
        return jsonify(result), 200 if result.get('success') else 400

    except Exception as e:
        logger.error(f"Error moving to file: {e}")
        return jsonify({'error': str(e)}), 500


@refactor_bp.route('/available', methods=['POST'])
@cross_origin()
async def get_available_refactorings():
    """
    Get available refactorings at position
    
    POST /api/v1/refactor/available
    {
        "source": "def foo():\n    pass",
        "line": 1,
        "col": 4
    }
    
    Returns:
    {
        "refactorings": [
            {"type": "extract_function", "name": "Extract Function"},
            {"type": "rename_symbol", "name": "Rename Symbol"}
        ]
    }
    """
    try:
        data = request.get_json()
        source = data.get('source', '')
        line = data.get('line', 1)
        col = data.get('col', 0)

        engine = get_refactoring_engine()
        
        if not engine.parse_source(source):
            return jsonify({
                'refactorings': [],
                'message': 'Could not parse source'
            }), 200

        refactorings = engine.get_available_refactorings(line, col)

        return jsonify({
            'refactorings': refactorings,
            'count': len(refactorings)
        }), 200

    except Exception as e:
        logger.error(f"Error getting available refactorings: {e}")
        return jsonify({'error': str(e)}), 500


@refactor_bp.route('/health', methods=['GET'])
@cross_origin()
def refactoring_health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'refactoring',
        'operations': ['extract', 'rename', 'move', 'available']
    }), 200


def register_refactoring_routes(app):
    """Register refactoring routes with Flask app"""
    app.register_blueprint(refactor_bp)
    logger.info("Refactoring routes registered")
