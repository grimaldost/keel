"""Structured, user-facing error messages (the method's own 'format_error' rule)."""


def format_error(*, what: str, why: str, fix: str) -> str:
    """Build a what/why/fix error string."""
    return f'{what}\n\nWhy: {why}\nFix: {fix}'
