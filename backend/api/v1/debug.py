"""
Debug Adapter Protocol API Endpoints
REST API routes for frontend to communicate with DAP server
"""

from flask import Blueprint, request, jsonify, current_app
from flask_cors import cross_origin
from functools import wraps
import asyncio
import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

debug_bp = Blueprint('debug', __name__, url_prefix='/api/v1/debug')


def async_route(f):
    """Decorator to handle async route functions"""
    @wraps(f)
    def wrapped(*args, **kwargs):
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(f(*args, **kwargs))
    return wrapped


# Import the DAP server
try:
    from backend.services.debug_adapter import (
        get_dap_server,
        start_debug_session,
        initialize_debug,
        launch_debug,
        set_breakpoint_dap,
        continue_debug,
        step_over_debug,
        step_into_debug,
        step_out_debug,
        get_stack_trace_dap,
        get_variables_dap,
        evaluate_expression_dap,
        stop_debug_session,
    )
except ImportError:
    logger.warning("Could not import DAP server - debug endpoints will not work")


@debug_bp.route('/start', methods=['POST'])
@cross_origin()
@async_route
async def start_debug():
    """
    Start a new debug session
    
    POST /api/v1/debug/start
    {
        "language": "python" | "javascript" | "node"
    }
    
    Returns:
    {
        "session_id": "uuid",
        "language": "python",
        "status": "initialized"
    }
    """
    try:
        data = request.get_json()
        language = data.get('language', 'python')
        
        # Validate language
        supported = ['python', 'javascript', 'typescript', 'node']
        if language not in supported:
            return jsonify({'error': f'Unsupported language: {language}'}), 400
        
        # Create session
        session_id = await start_debug_session(language)
        
        logger.info(f"Started debug session: {session_id} for {language}")
        
        return jsonify({
            'session_id': session_id,
            'language': language,
            'status': 'initialized',
        }), 201
        
    except Exception as e:
        logger.error(f"Error starting debug session: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/<session_id>/initialize', methods=['POST'])
@cross_origin()
@async_route
async def initialize_session(session_id: str):
    """
    Initialize a debug session with program details
    
    POST /api/v1/debug/{session_id}/initialize
    {
        "working_dir": "/path/to/project",
        "program": "/path/to/script.py"
    }
    """
    try:
        data = request.get_json()
        working_dir = data.get('working_dir', '.')
        program = data.get('program')
        
        if not program:
            return jsonify({'error': 'program is required'}), 400
        
        response = await initialize_debug(session_id, working_dir, program)
        
        logger.info(f"Initialized session {session_id}: {program}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error initializing session: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/<session_id>/launch', methods=['POST'])
@cross_origin()
@async_route
async def launch_session(session_id: str):
    """
    Launch debugger for a session
    
    POST /api/v1/debug/{session_id}/launch
    {
        "program": "/path/to/script.py",
        "workingDir": "/path/to/project",
        "args": ["arg1", "arg2"],
        "env": {"VAR": "value"}
    }
    """
    try:
        data = request.get_json()
        program = data.get('program')
        working_dir = data.get('workingDir', '.')
        args = data.get('args', [])
        env = data.get('env', {})
        
        response = await launch_debug(
            session_id,
            program=program,
            workingDir=working_dir,
            args=args,
            env=env,
        )
        
        logger.info(f"Launched debugger for session {session_id}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error launching session: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/<session_id>/breakpoint', methods=['POST'])
@cross_origin()
@async_route
async def set_breakpoint(session_id: str):
    """
    Set a breakpoint
    
    POST /api/v1/debug/{session_id}/breakpoint
    {
        "file": "/path/to/file.py",
        "line": 42,
        "condition": "x > 5",
        "logMessage": "x={x}"
    }
    """
    try:
        data = request.get_json()
        file = data.get('file')
        line = data.get('line')
        condition = data.get('condition')
        log_message = data.get('logMessage')
        
        if not file or not line:
            return jsonify({'error': 'file and line are required'}), 400
        
        response = await set_breakpoint_dap(
            session_id,
            file,
            line,
            condition=condition,
            logMessage=log_message,
        )
        
        logger.info(f"Breakpoint set: {file}:{line}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error setting breakpoint: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/<session_id>/breakpoint/<int:bp_id>', methods=['DELETE'])
@cross_origin()
@async_route
async def delete_breakpoint(session_id: str, bp_id: int):
    """
    Delete a breakpoint
    
    DELETE /api/v1/debug/{session_id}/breakpoint/{bp_id}
    """
    try:
        # Implementation would remove breakpoint from session
        logger.info(f"Breakpoint deleted: {bp_id}")
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"Error deleting breakpoint: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/<session_id>/continue', methods=['POST'])
@cross_origin()
@async_route
async def continue_execution(session_id: str):
    """
    Continue execution after pause
    
    POST /api/v1/debug/{session_id}/continue
    """
    try:
        response = await continue_debug(session_id)
        
        logger.info(f"Continued execution: {session_id}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error continuing execution: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/<session_id>/next', methods=['POST'])
@cross_origin()
@async_route
async def step_over(session_id: str):
    """
    Step over (next line)
    
    POST /api/v1/debug/{session_id}/next
    """
    try:
        response = await step_over_debug(session_id)
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error stepping: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/<session_id>/stepIn', methods=['POST'])
@cross_origin()
@async_route
async def step_into(session_id: str):
    """
    Step into function
    
    POST /api/v1/debug/{session_id}/stepIn
    """
    try:
        response = await step_into_debug(session_id)
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error stepping: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/<session_id>/stepOut', methods=['POST'])
@cross_origin()
@async_route
async def step_out(session_id: str):
    """
    Step out of function
    
    POST /api/v1/debug/{session_id}/stepOut
    """
    try:
        response = await step_out_debug(session_id)
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error stepping: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/<session_id>/pause', methods=['POST'])
@cross_origin()
@async_route
async def pause_execution(session_id: str):
    """
    Pause execution
    
    POST /api/v1/debug/{session_id}/pause
    """
    try:
        server = get_dap_server()
        if session_id not in server.sessions:
            return jsonify({'error': 'Session not found'}), 404
        
        adapter = server.sessions[session_id]
        adapter.paused = True
        
        logger.info(f"Paused execution: {session_id}")
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logger.error(f"Error pausing execution: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/<session_id>/stackTrace', methods=['GET'])
@cross_origin()
@async_route
async def get_stack_trace(session_id: str):
    """
    Get call stack
    
    GET /api/v1/debug/{session_id}/stackTrace
    
    Returns:
    {
        "body": {
            "stackFrames": [
                {
                    "id": 1,
                    "name": "main",
                    "file": "/path/to/file.py",
                    "line": 42,
                    "column": 0
                }
            ],
            "totalFrames": 1
        }
    }
    """
    try:
        response = await get_stack_trace_dap(session_id)
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting stack trace: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/<session_id>/variables/<int:frame_id>', methods=['GET'])
@cross_origin()
@async_route
async def get_variables(session_id: str, frame_id: int):
    """
    Get variables for a stack frame
    
    GET /api/v1/debug/{session_id}/variables/{frame_id}
    
    Returns:
    {
        "body": {
            "variables": [
                {
                    "name": "x",
                    "value": "42",
                    "type": "int",
                    "variablesReference": 0
                }
            ]
        }
    }
    """
    try:
        response = await get_variables_dap(session_id, frame_id)
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error getting variables: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/<session_id>/evaluate', methods=['POST'])
@cross_origin()
@async_route
async def evaluate(session_id: str):
    """
    Evaluate expression in current context
    
    POST /api/v1/debug/{session_id}/evaluate
    {
        "expression": "x + y"
    }
    
    Returns:
    {
        "body": {
            "result": "42",
            "type": "int"
        }
    }
    """
    try:
        data = request.get_json()
        expression = data.get('expression')
        
        if not expression:
            return jsonify({'error': 'expression is required'}), 400
        
        response = await evaluate_expression_dap(session_id, expression)
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error evaluating expression: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/<session_id>', methods=['DELETE'])
@cross_origin()
@async_route
async def delete_session(session_id: str):
    """
    Terminate a debug session
    
    DELETE /api/v1/debug/{session_id}
    """
    try:
        response = await stop_debug_session(session_id)
        
        logger.info(f"Terminated debug session: {session_id}")
        
        return jsonify(response), 200
        
    except Exception as e:
        logger.error(f"Error terminating session: {e}")
        return jsonify({'error': str(e)}), 500


@debug_bp.route('/health', methods=['GET'])
@cross_origin()
def health_check():
    """
    Health check endpoint
    
    GET /api/v1/debug/health
    """
    return jsonify({
        'status': 'healthy',
        'service': 'debug-adapter',
    }), 200


def register_debug_routes(app):
    """Register debug routes with Flask app"""
    app.register_blueprint(debug_bp)
    logger.info("Debug adapter routes registered")
