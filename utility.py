
def get_difficulty_string(diff: int) -> str:
    if diff == 0:
        return "easy"
    elif diff == 1:
        return "medium"
    elif diff == 2:
        return "hard"
    else:
        raise ValueError("Only integers 0, 1, or 2 allowed")
