"""Order loading and the region rollup."""

from collections.abc import Iterable

ORDER_COLUMNS = (
    'order_id',
    'region_code',
    'placed_at',
    'amount_cents',
)


def load_orders(rows: Iterable[dict[str, object]]) -> list[dict[str, object]]:
    """Return the rows that carry every required order column."""
    return [row for row in rows if all(column in row for column in ORDER_COLUMNS)]


def rollup_by_region(orders: list[dict[str, object]]) -> dict[str, int]:
    """Total amount_cents per region_code, one entry per region seen."""
    totals: dict[str, int] = {}
    for order in orders:
        code = str(order['region_code'])
        totals[code] = totals.get(code, 0) + int(order['amount_cents'])  # type: ignore[call-overload]
    return totals
