"""Instagram Reels safe zone on a 1080x1920 frame, HARD RULE (feedback 23 Oct 2026, SOP 07). Same numbers as
modes/eoin-yap/build_yap.py. Builders call check() on every text box they place; it never moves anything, it only
says what broke so the builder can fail loudly."""

SAFE_TOP, SAFE_BOTTOM, SAFE_LEFT = 250, 1440, 60
SAFE_RIGHT_TOP, SAFE_RIGHT_LOW = 1020, 940      # the like/comment rail sits on the right below ~y 1000


def check(name, x0, y0, x1, y1):
    """None if the box is inside the safe zone, else a one-line reason."""
    right = SAFE_RIGHT_TOP if y1 <= 1000 else SAFE_RIGHT_LOW
    if x0 < SAFE_LEFT or y0 < SAFE_TOP or y1 > SAFE_BOTTOM or x1 > right:
        return f"IG safe zone broken by {name}: ({x0:.0f},{y0:.0f})-({x1:.0f},{y1:.0f})"
    return None
