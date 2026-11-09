from src.rewriter import rewrite_query


def test_conversational_pronoun_resolution():
    rewritten = rewrite_query(
        "What are its system requirements?",
        conversation_history=["We were looking at Kubernetes Worker Nodes"],
    )
    assert "Kubernetes Worker Nodes" in rewritten
