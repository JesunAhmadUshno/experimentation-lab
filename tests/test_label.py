from explab.label import is_question


def test_is_question_rule():
    assert is_question("Why Did This Happen?")
    assert is_question("  Padded question?  ")
    assert not is_question("A statement.")
    assert not is_question("What? A follow-up statement")
    assert not is_question("")
    assert not is_question(None)
