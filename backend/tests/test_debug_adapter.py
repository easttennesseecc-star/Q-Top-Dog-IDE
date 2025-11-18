"""
Test Suite for Debug Adapter Protocol Implementation
Unit and E2E tests for debugging features

Tests:
- DAP protocol compliance
- Breakpoint management
- Stepping (over, into, out)
- Call stack inspection
- Variable inspection
- Expression evaluation
- Session lifecycle
"""

import pytest
import asyncio
import logging

# Import DAP server
from backend.services.debug_adapter import (
    DAPServer,
    PythonDebuggerAdapter,
    NodeDebuggerAdapter,
    StopReason,
)

logger = logging.getLogger(__name__)


class TestDAPProtocol:
    """Test Debug Adapter Protocol compliance"""

    @pytest.mark.unit
    @pytest.mark.performance
    def test_dap_initialize_response_schema(self):
        """Test that initialize response matches DAP schema"""
        adapter = PythonDebuggerAdapter("test-session")
        
        response = asyncio.run(adapter.initialize(".", "test.py"))
        
        # Verify required fields
        assert "supportsConfigurationDoneRequest" in response
        assert "supportsFunctionBreakpoints" in response
        assert "supportsConditionalBreakpoints" in response
        assert "supportsLogPoints" in response
        assert isinstance(response["supportsConfigurationDoneRequest"], bool)
        
    @pytest.mark.unit
    def test_dap_sequence_numbering(self):
        """Test DAP message sequence numbering"""
        server = DAPServer()
        session_id = asyncio.run(server.create_session("python"))
        
        resp1 = asyncio.run(server.initialize(session_id, ".", "test.py"))
        resp2 = asyncio.run(server.initialize(session_id, ".", "test.py"))
        
        assert resp1["seq"] == 1
        assert resp2["seq"] == 2
        assert resp1["seq"] < resp2["seq"]


class TestBreakpointManagement:
    """Test breakpoint functionality"""

    @pytest.mark.unit
    def test_set_breakpoint(self):
        """Test setting a breakpoint"""
        adapter = PythonDebuggerAdapter("test-session")
        
        bp = asyncio.run(adapter.set_breakpoint("test.py", 42))
        
        assert bp.file == "test.py"
        assert bp.line == 42
        assert bp.verified is True
        assert bp.id >= 0

    @pytest.mark.unit
    def test_set_breakpoint_with_condition(self):
        """Test setting conditional breakpoint"""
        adapter = PythonDebuggerAdapter("test-session")
        
        bp = asyncio.run(adapter.set_breakpoint(
            "test.py",
            42,
            condition="x > 10"
        ))
        
        assert bp.condition == "x > 10"
        assert bp.verified is True

    @pytest.mark.unit
    def test_set_breakpoint_with_logpoint(self):
        """Test setting logpoint"""
        adapter = PythonDebuggerAdapter("test-session")
        
        bp = asyncio.run(adapter.set_breakpoint(
            "test.py",
            42,
            logMessage="x={x}, y={y}"
        ))
        
        assert bp.log_message == "x={x}, y={y}"
        assert bp.verified is True

    @pytest.mark.unit
    def test_multiple_breakpoints_per_file(self):
        """Test setting multiple breakpoints in same file"""
        adapter = PythonDebuggerAdapter("test-session")
        
        bp1 = asyncio.run(adapter.set_breakpoint("test.py", 10))
        bp2 = asyncio.run(adapter.set_breakpoint("test.py", 20))
        bp3 = asyncio.run(adapter.set_breakpoint("test.py", 30))
        
        assert len(adapter.breakpoints["test.py"]) == 3
        assert bp1.id != bp2.id != bp3.id

    @pytest.mark.unit
    def test_breakpoint_tracking(self):
        """Test breakpoint tracking across files"""
        adapter = PythonDebuggerAdapter("test-session")
        
        asyncio.run(adapter.set_breakpoint("file1.py", 10))
        asyncio.run(adapter.set_breakpoint("file2.py", 20))
        
        assert "file1.py" in adapter.breakpoints
        assert "file2.py" in adapter.breakpoints
        assert len(adapter.breakpoints["file1.py"]) == 1
        assert len(adapter.breakpoints["file2.py"]) == 1


class TestSteppingOperations:
    """Test stepping through code"""

    @pytest.mark.unit
    @pytest.mark.performance
    def test_step_over_performance(self):
        """Test step over completes within SLA"""
        adapter = PythonDebuggerAdapter("test-session")
        
        import time
        start = time.time()
        asyncio.run(adapter.step_over())
        elapsed = time.time() - start
        
        assert elapsed < 0.2  # Must complete in <200ms

    @pytest.mark.unit
    @pytest.mark.performance
    def test_step_into_performance(self):
        """Test step into completes within SLA"""
        adapter = PythonDebuggerAdapter("test-session")
        
        import time
        start = time.time()
        asyncio.run(adapter.step_into())
        elapsed = time.time() - start
        
        assert elapsed < 0.2

    @pytest.mark.unit
    @pytest.mark.performance
    def test_step_out_performance(self):
        """Test step out completes within SLA"""
        adapter = PythonDebuggerAdapter("test-session")
        
        import time
        start = time.time()
        asyncio.run(adapter.step_out())
        elapsed = time.time() - start
        
        assert elapsed < 0.2

    @pytest.mark.unit
    def test_step_sets_stopped_reason(self):
        """Test that stepping sets correct stopped reason"""
        adapter = PythonDebuggerAdapter("test-session")
        
        asyncio.run(adapter.step_over())
        
        assert adapter.stopped_reason == StopReason.STEP
        assert adapter.paused is True

    @pytest.mark.unit
    def test_continue_clears_paused_state(self):
        """Test that continue clears paused flag"""
        adapter = PythonDebuggerAdapter("test-session")
        adapter.paused = True
        
        asyncio.run(adapter.continue_execution())
        
        assert adapter.paused is False


class TestCallStackInspection:
    """Test call stack functionality"""

    @pytest.mark.unit
    def test_get_stack_trace(self):
        """Test retrieving call stack"""
        adapter = PythonDebuggerAdapter("test-session")
        
        frames = asyncio.run(adapter.get_stack_trace())
        
        assert len(frames) > 0
        assert frames[0].name is not None
        assert frames[0].file is not None
        assert frames[0].line > 0

    @pytest.mark.unit
    def test_stack_frame_structure(self):
        """Test stack frame has required fields"""
        adapter = PythonDebuggerAdapter("test-session")
        
        frames = asyncio.run(adapter.get_stack_trace())
        frame = frames[0]
        
        assert frame.id > 0
        assert len(frame.name) > 0
        assert len(frame.file) > 0
        assert frame.line > 0

    @pytest.mark.unit
    def test_stack_frame_contains_locals(self):
        """Test that stack frame contains local variables"""
        adapter = PythonDebuggerAdapter("test-session")
        
        frames = asyncio.run(adapter.get_stack_trace())
        frame = frames[0]
        
        assert hasattr(frame, 'locals')
        assert isinstance(frame.locals, dict)

    @pytest.mark.unit
    def test_stack_frame_contains_args(self):
        """Test that stack frame contains arguments"""
        adapter = PythonDebuggerAdapter("test-session")
        
        frames = asyncio.run(adapter.get_stack_trace())
        frame = frames[0]
        
        assert hasattr(frame, 'args')
        assert isinstance(frame.args, dict)


class TestVariableInspection:
    """Test variable inspection"""

    @pytest.mark.unit
    def test_get_variables(self):
        """Test retrieving variables"""
        adapter = PythonDebuggerAdapter("test-session")
        
        variables = asyncio.run(adapter.get_variables(1))
        
        assert len(variables) > 0
        assert all(hasattr(v, 'name') for v in variables)
        assert all(hasattr(v, 'value') for v in variables)
        assert all(hasattr(v, 'type') for v in variables)

    @pytest.mark.unit
    def test_variable_to_dict(self):
        """Test variable serialization"""
        from backend.services.debug_adapter import Variable
        
        var = Variable("x", "42", "int", variablesReference=0)
        var_dict = var.to_dict()
        
        assert var_dict["name"] == "x"
        assert var_dict["value"] == "42"
        assert var_dict["type"] == "int"
        assert var_dict["variablesReference"] == 0

    @pytest.mark.unit
    def test_variable_with_children(self):
        """Test variable with nested references"""
        from backend.services.debug_adapter import Variable
        
        var = Variable("obj", "{...}", "object", variablesReference=5)
        
        assert var.variablesReference > 0
        assert var.to_dict()["variablesReference"] == 5

    @pytest.mark.unit
    def test_multiple_variables_returned(self):
        """Test multiple variables per frame"""
        adapter = PythonDebuggerAdapter("test-session")
        
        variables = asyncio.run(adapter.get_variables(1))
        
        # Verify we have multiple distinct variables
        names = [v.name for v in variables]
        assert len(names) == len(set(names))  # All unique


class TestExpressionEvaluation:
    """Test expression evaluation"""

    @pytest.mark.unit
    def test_evaluate_simple_expression(self):
        """Test evaluating simple expression"""
        adapter = PythonDebuggerAdapter("test-session")
        
        result = asyncio.run(adapter.evaluate("1 + 1"))
        
        assert result == "2"

    @pytest.mark.unit
    def test_evaluate_arithmetic(self):
        """Test arithmetic evaluation"""
        adapter = PythonDebuggerAdapter("test-session")
        
        result = asyncio.run(adapter.evaluate("10 * 5"))
        
        assert result == "50"

    @pytest.mark.unit
    def test_evaluate_returns_string(self):
        """Test evaluation returns string result"""
        adapter = PythonDebuggerAdapter("test-session")
        
        result = asyncio.run(adapter.evaluate("42"))
        
        assert isinstance(result, str)
        assert result == "42"

    @pytest.mark.unit
    def test_evaluate_handles_errors(self):
        """Test evaluation error handling"""
        adapter = PythonDebuggerAdapter("test-session")
        
        result = asyncio.run(adapter.evaluate("1 / 0"))
        
        assert isinstance(result, str)
        assert "Error" in result


class TestSessionLifecycle:
    """Test debug session creation and termination"""

    @pytest.mark.unit
    def test_create_python_session(self):
        """Test creating Python debug session"""
        server = DAPServer()
        
        session_id = asyncio.run(server.create_session("python"))
        
        assert session_id in server.sessions
        assert isinstance(server.sessions[session_id], PythonDebuggerAdapter)

    @pytest.mark.unit
    def test_create_node_session(self):
        """Test creating Node.js debug session"""
        server = DAPServer()
        
        session_id = asyncio.run(server.create_session("javascript"))
        
        assert session_id in server.sessions
        assert isinstance(server.sessions[session_id], NodeDebuggerAdapter)

    @pytest.mark.unit
    def test_unsupported_language_raises_error(self):
        """Test that unsupported language raises error"""
        server = DAPServer()
        
        with pytest.raises(ValueError):
            asyncio.run(server.create_session("cobol"))

    @pytest.mark.unit
    def test_terminate_session(self):
        """Test terminating a session"""
        server = DAPServer()
        session_id = asyncio.run(server.create_session("python"))
        
        asyncio.run(server.terminate_session(session_id))
        
        assert session_id not in server.sessions

    @pytest.mark.unit
    def test_multiple_concurrent_sessions(self):
        """Test multiple concurrent debug sessions"""
        server = DAPServer()
        
        s1 = asyncio.run(server.create_session("python"))
        s2 = asyncio.run(server.create_session("javascript"))
        s3 = asyncio.run(server.create_session("python"))
        
        assert len(server.sessions) == 3
        assert s1 != s2 != s3


class TestDAPServerOperations:
    """Test DAPServer operations"""

    @pytest.mark.unit
    @pytest.mark.performance
    def test_initialize_performance(self):
        """Test initialize completes within SLA"""
        server = DAPServer()
        session_id = asyncio.run(server.create_session("python"))
        
        import time
        start = time.time()
        asyncio.run(server.initialize(session_id, ".", "test.py"))
        elapsed = time.time() - start
        
        assert elapsed < 0.05  # Must complete in <50ms

    @pytest.mark.unit
    def test_set_breakpoint_through_server(self):
        """Test setting breakpoint through server"""
        server = DAPServer()
        session_id = asyncio.run(server.create_session("python"))
        
        response = asyncio.run(server.set_breakpoint(
            session_id,
            "test.py",
            42
        ))
        
        assert response["success"] is True
        assert len(response["body"]["breakpoints"]) == 1

    @pytest.mark.unit
    def test_stack_trace_through_server(self):
        """Test getting stack trace through server"""
        server = DAPServer()
        session_id = asyncio.run(server.create_session("python"))
        asyncio.run(server.initialize(session_id, ".", "test.py"))
        
        response = asyncio.run(server.stack_trace(session_id))
        
        assert response["success"] is True
        assert "stackFrames" in response["body"]
        assert len(response["body"]["stackFrames"]) > 0

    @pytest.mark.unit
    def test_variables_through_server(self):
        """Test getting variables through server"""
        server = DAPServer()
        session_id = asyncio.run(server.create_session("python"))
        asyncio.run(server.initialize(session_id, ".", "test.py"))
        
        response = asyncio.run(server.variables(session_id, 1))
        
        assert response["success"] is True
        assert "variables" in response["body"]

    @pytest.mark.unit
    def test_evaluate_through_server(self):
        """Test evaluating expression through server"""
        server = DAPServer()
        session_id = asyncio.run(server.create_session("python"))
        asyncio.run(server.initialize(session_id, ".", "test.py"))
        
        response = asyncio.run(server.evaluate(session_id, "1 + 1"))
        
        assert response["success"] is True
        assert response["body"]["result"] == "2"


class TestEventEmission:
    """Test event system"""

    @pytest.mark.unit
    def test_register_event_callback(self):
        """Test registering event callback"""
        server = DAPServer()
        callback_called = []
        
        def callback(body):
            callback_called.append(body)
        
        server.register_event_callback("stopped", callback)
        asyncio.run(server.emit_event("stopped", {"reason": "breakpoint"}))
        
        assert len(callback_called) == 1
        assert callback_called[0]["reason"] == "breakpoint"

    @pytest.mark.unit
    def test_event_emission_with_multiple_listeners(self):
        """Test event emitted to multiple listeners"""
        server = DAPServer()
        results = []
        
        def callback1(body):
            results.append("callback1")
        
        def callback2(body):
            results.append("callback2")
        
        server.register_event_callback("stopped", callback1)
        server.register_event_callback("stopped", callback2)
        asyncio.run(server.emit_event("stopped", {}))
        
        assert len(results) == 2
        assert "callback1" in results
        assert "callback2" in results


class TestErrorHandling:
    """Test error handling"""

    @pytest.mark.unit
    def test_invalid_session_id(self):
        """Test handling of invalid session ID"""
        server = DAPServer()
        
        with pytest.raises(ValueError):
            asyncio.run(server.stack_trace("invalid-session-id"))

    @pytest.mark.unit
    def test_missing_required_fields(self):
        """Test validation of required fields"""
        adapter = PythonDebuggerAdapter("test-session")
        
        # Missing required fields should be handled gracefully
        bp = asyncio.run(adapter.set_breakpoint("", 0))
        
        # Should still create breakpoint even with empty values
        assert bp is not None


class TestLanguageAdapters:
    """Test language-specific adapters"""

    @pytest.mark.unit
    def test_python_adapter_launch(self):
        """Test Python adapter launch"""
        adapter = PythonDebuggerAdapter("test-session")
        
        # Note: actual launch will fail without debugpy, but structure is tested
        result = asyncio.run(adapter.initialize(".", "test.py"))
        
        assert "supportsConfigurationDoneRequest" in result

    @pytest.mark.unit
    def test_node_adapter_initialization(self):
        """Test Node.js adapter initialization"""
        adapter = NodeDebuggerAdapter("test-session")
        
        result = asyncio.run(adapter.initialize(".", "test.js"))
        
        assert "supportsFunctionBreakpoints" in result
        assert result["supportsFunctionBreakpoints"] is True

    @pytest.mark.unit
    def test_python_vs_node_capabilities(self):
        """Test differences in language adapter capabilities"""
        py_adapter = PythonDebuggerAdapter("py-session")
        node_adapter = NodeDebuggerAdapter("node-session")
        
        py_result = asyncio.run(py_adapter.initialize(".", "test.py"))
        node_result = asyncio.run(node_adapter.initialize(".", "test.js"))
        
        # Both should have core capabilities
        assert "supportsConfigurationDoneRequest" in py_result
        assert "supportsConfigurationDoneRequest" in node_result


# Integration tests
class TestDebuggerIntegration:
    """Integration tests for complete debug workflows"""

    @pytest.mark.e2e
    def test_complete_debug_workflow_python(self):
        """Test complete Python debugging workflow"""
        server = DAPServer()
        
        # 1. Create session
        session_id = asyncio.run(server.create_session("python"))
        assert session_id is not None
        
        # 2. Initialize
        resp = asyncio.run(server.initialize(session_id, ".", "test.py"))
        assert resp["success"] is True
        
        # 3. Set breakpoint
        resp = asyncio.run(server.set_breakpoint(session_id, "test.py", 10))
        assert resp["success"] is True
        
        # 4. Get stack trace
        resp = asyncio.run(server.stack_trace(session_id))
        assert resp["success"] is True
        
        # 5. Terminate
        resp = asyncio.run(server.terminate_session(session_id))
        assert resp["success"] is True

    @pytest.mark.e2e
    def test_complete_debug_workflow_node(self):
        """Test complete Node.js debugging workflow"""
        server = DAPServer()
        
        session_id = asyncio.run(server.create_session("javascript"))
        
        asyncio.run(server.initialize(session_id, ".", "test.js"))
        asyncio.run(server.set_breakpoint(session_id, "test.js", 15))
        resp = asyncio.run(server.step_over(session_id))
        
        assert resp["success"] is True
        
        asyncio.run(server.terminate_session(session_id))


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
