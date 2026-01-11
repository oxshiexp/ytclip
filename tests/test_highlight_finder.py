from app.core.highlight_finder import score_candidates, select_top


def test_select_top_diversity():
    analysis = {"rms": [0.1] * 100, "duration": 50}
    candidates = [
        {"start": 0, "end": 20},
        {"start": 5, "end": 25},
        {"start": 30, "end": 45},
    ]
    scored = score_candidates(candidates, analysis)
    selected = select_top(scored, analysis, count=2)
    assert len(selected) == 2
    assert selected[0]["start"] == 0
    assert selected[1]["start"] == 30


def test_score_candidates_order():
    analysis = {"rms": [0.1] * 10 + [0.9] * 10, "duration": 10}
    candidates = [
        {"start": 0, "end": 2.5},
        {"start": 5, "end": 10},
    ]
    scored = score_candidates(candidates, analysis)
    assert scored[0]["start"] == 5
