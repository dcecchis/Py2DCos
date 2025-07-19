class PlotCache:
    """Store figures on demand; reuse if settings unchanged."""
    def __init__(self):
        self._store: dict[tuple[str, str], object] = {}   # (proj, which) → fig

    def get(self, proj: bool, which: str):
        return self._store.get((proj, which))

    def set(self, proj: bool, which: str, fig):
        self._store[(proj, which)] = fig

    def clear(self):
        self._store.clear()             # call when math settings change
