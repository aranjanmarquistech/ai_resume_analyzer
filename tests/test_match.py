from resume_analyzer.scoring.match import compute_text_similarity, match_resume_to_jd


def test_compute_text_similarity_basic():
    resume = "I have experience with Python and Flask."
    jd = "Looking for a Python developer with Flask experience."
    sim = compute_text_similarity(resume, jd)
    assert 0.1 < sim <= 1.0


def test_match_resume_to_jd_skill_gap_correct():
    resume = "Skills: Python, Flutter, Git"
    jd = "We need Python, FastAPI, Git"
    result = match_resume_to_jd(resume, jd)

    # matched should include python, git
    assert "python" in result.matched_skills
    assert "git" in result.matched_skills

    # missing should include fastapi (JD - resume)
    assert "fastapi" in result.missing_skills

    # coverage should be 2/3
    assert abs(result.skill_coverage - (2 / 3)) < 1e-6
