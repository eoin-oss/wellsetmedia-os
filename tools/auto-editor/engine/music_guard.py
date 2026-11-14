"""Banned music guard (SOP 06/07). Fails a timeline that has a banned track anywhere on its audio tracks.
Banned list = every mode's music.never (modes/*/mode.json) + the `banned-music:` list in a client's CONTENT-RULES.md
(AE_RULES=<path>, or the `client` named by the AE_MODE mode). Matching is case-insensitive on the clip name and file path.
Usage: python3 music_guard.py [timeline name suffix]   (checks the open project; exit 1 if anything is banned)"""
import glob, json, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
MODES = os.path.join(HERE, "..", "modes")
CLIENTS = os.path.join(HERE, "..", "..", "..", "clients")


def rules_file():
    if os.environ.get("AE_RULES"):
        return os.environ["AE_RULES"]
    mode = os.environ.get("AE_MODE")
    if mode and os.path.exists(os.path.join(MODES, mode, "mode.json")):
        client = json.load(open(os.path.join(MODES, mode, "mode.json"))).get("client")
        if client:   # a slug ("kyle-ritchie") or a description naming the client ("Kyle Ritchie clips from ...")
            hits = [(client.lower().find(s.replace("-", " ")), s) for s in os.listdir(CLIENTS)
                    if s == client or s.replace("-", " ") in client.lower()]
            if hits:   # the client named first wins ("Kyle Ritchie clips from The James Hempton Show" = kyle-ritchie)
                return os.path.join(CLIENTS, min(hits)[1], "CONTENT-RULES.md")
    return None


def banned():
    out = set()
    for f in glob.glob(os.path.join(MODES, "*", "mode.json")):
        try:
            m = json.load(open(f))
        except ValueError:
            continue
        out |= {x.lower() for x in (m.get("music") or {}).get("never", []) if isinstance(x, str)}
    rf = rules_file()
    if rf and os.path.exists(rf):
        text = open(rf).read()
        block = re.search(r"^banned-music:\s*\n((?:\s*-\s*.+\n?)+)", text, re.M)
        if block:
            out |= {x.strip().lower() for x in re.findall(r"-\s*(.+)", block.group(1)) if not x.strip().startswith("<")}
    return sorted(out)


def check_timeline(t, ban=None):
    """List of (track, clip name) on the timeline's audio that match the banned list."""
    ban = banned() if ban is None else ban
    hits = []
    for i in range(1, t.GetTrackCount("audio") + 1):
        for it in t.GetItemListInTrack("audio", i) or []:
            name = it.GetName() or ""
            mpi = it.GetMediaPoolItem()
            path = (mpi.GetClipProperty("File Path") or "") if mpi else ""
            hay = f"{name} {path}".lower()
            if any(b in hay for b in ban):
                hits.append((i, name or os.path.basename(path)))
    return hits


if __name__ == "__main__":
    sys.path.insert(0, HERE)
    from resolve import connect
    suffix = sys.argv[1] if len(sys.argv) > 1 else ""
    p = connect().GetProjectManager().GetCurrentProject()
    ban, bad = banned(), 0
    print("banned:", ", ".join(ban))
    for i in range(1, p.GetTimelineCount() + 1):
        t = p.GetTimelineByIndex(i)
        if not t.GetName().endswith(suffix):
            continue
        for tr, n in check_timeline(t, ban):
            bad += 1
            print(f"FAIL  {t.GetName()}: banned music on A{tr}: {n}")
    print(f"{bad} banned clip(s)")
    sys.exit(1 if bad else 0)
