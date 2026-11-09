from src.reranker import confidence_from_logit, gate_status
from src.schemas import RetrievedChunk


def test_sigmoid_logit_normalization():
    positive = confidence_from_logit(4.2)
    negative = confidence_from_logit(-3.8)
    zero = confidence_from_logit(0.0)
    assert 0.0 <= positive <= 1.0
    assert 0.0 <= negative <= 1.0
    assert 0.0 <= zero <= 1.0
    assert positive > 0.5
    assert negative < 0.5
    assert zero == 0.5


def test_threshold_gating_logic():
    low = [
        RetrievedChunk(chunk_id="a", content="unrelated", score=0.42, source="internal_doc"),
        RetrievedChunk(chunk_id="b", content="also weak", score=0.21, source="internal_doc"),
    ]
    high = [
        RetrievedChunk(chunk_id="c", content="strong match", score=0.81, source="internal_doc"),
        RetrievedChunk(chunk_id="d", content="backup", score=0.60, source="internal_doc"),
    ]
    assert gate_status(max(item.score for item in low)) == "LOW_CONFIDENCE"
    assert gate_status(max(item.score for item in high)) == "HIGH_CONFIDENCE"
