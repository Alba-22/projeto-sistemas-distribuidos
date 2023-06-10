def decide_chord(identifier: int) -> int:
    """Return chord index to insert a given ID"""
    if identifier % 2 == 0:
        return 0
    return 1
