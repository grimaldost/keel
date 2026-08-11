"""Region codes and their display names."""

REGION_CODES = {
    'emea': 'Europe, Middle East and Africa',
    'amer': 'Americas',
    'apac': 'Asia-Pacific',
}


def region_name(code: str) -> str:
    """The display name for a region code, or the code itself when unknown."""
    return REGION_CODES.get(code, code)
