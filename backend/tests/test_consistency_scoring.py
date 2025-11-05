from backend.services.consistency_scoring import ConsistencyScoringAgent


def test_consistency_scoring_basic():
    agent = ConsistencyScoringAgent()

    def mock_llm(p: str) -> str:
        # Simple echo with minor variation
        if p.endswith('.'):
            return "answer is stable"
        return "the answer is stable"

    res = agent.evaluate("What is the answer?", mock_llm, n=3)
    assert 0.0 <= res.score <= 1.0
    # Expect reasonably high similarity for our mock
    assert res.score > 0.5
