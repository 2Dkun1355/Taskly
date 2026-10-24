BG = (0.055, 0.067, 0.10, 1)
SIDEBAR = (0.075, 0.09, 0.13, 1)
SURFACE = (0.105, 0.125, 0.17, 1)
SURFACE_ALT = (0.15, 0.175, 0.23, 1)
FIELD = (0.07, 0.085, 0.12, 1)
FIELD_FOCUS = (0.09, 0.11, 0.16, 1)

TEXT = (0.93, 0.94, 0.97, 1)
MUTED = (0.62, 0.67, 0.75, 1)
DIM = (0.42, 0.47, 0.56, 1)
WHITE = (1, 1, 1, 1)

ACCENT = (0.30, 0.48, 0.95, 1)
GREEN = (0.22, 0.68, 0.48, 1)
RED = (0.90, 0.38, 0.40, 1)
ORANGE = (0.95, 0.65, 0.25, 1)

# Колір смужки на картці залежно від пріоритету.
PRIORITY_COLORS = {
    "LOW": (0.45, 0.60, 0.80, 1),
    "MEDIUM": ORANGE,
    "HIGH": RED,
}

STATE_COLORS = {
    "inbox": MUTED,
    "planned": ACCENT,
    "completed": GREEN,
    "not_completed": ORANGE,
    "cancelled": DIM,
}
