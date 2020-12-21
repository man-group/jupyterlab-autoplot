"""Module containing utility functions and constants."""


def remove_quotes(text: str) -> str:
    """Return the `text` with any surrounding quotes removed."""
    return text[1:-1] if text[0] + text[-1] in {"''", '""'} else text
