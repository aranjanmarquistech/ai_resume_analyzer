

from resume_analyzer.skills.taxonomy import load_taxonomy
from resume_analyzer.skills.extract import extract_skills


def test_load_taxonomy_ok():
    tax = load_taxonomy("data/skills_taxonomy.json")
    assert "python" in tax.canonical_to_aliases
    assert tax.alias_to_canonical["py"] == "python"


def test_extract_skills_basic():
    text = "Worked with Python, Py, Flutter, SpringBoot, ReactJS and GitHub."
    skills = extract_skills(text)
    assert "python" in skills
    assert "flutter" in skills
    assert "spring boot" in skills
    assert "react" in skills
    assert "git" in skills


def test_extract_skills_word_boundaries():
    # "sql" should not match inside "sequel" (word boundary check)
    text = "I love sequel databases (not really)."
    skills = extract_skills(text)
    assert "sql" not in skills
