"""tinyetl — a tiny invented ETL package the adversarial spec corpus anchors into.

Nothing here is imported by keel. It exists so `clean-series.md` can carry real
`path:line` anchors, a real concept→module map, and a real reuse target — a corpus
of anchors into nothing would prove nothing about a check that resolves anchors.
"""

__all__ = ['REGION_CODES', 'load_orders', 'rollup_by_region']

from tinyetl.orders import load_orders, rollup_by_region
from tinyetl.regions import REGION_CODES
