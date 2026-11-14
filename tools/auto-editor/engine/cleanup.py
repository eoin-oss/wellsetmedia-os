"""Storage cleanup for finished batches, with a log of everything removed.
Each batch in jobs/RETENTION.json lists:
  drafts       superseded renders and intermediates: safe to delete once the current versions are delivered
  until_posted current masters + the sources needed to re-cut them: delete only after every reel is posted
  keep         never touched (plans, transcripts, EDLs: small, and they're the learning record)
Usage:
  python3 cleanup.py plan                 -> what each batch would free, nothing deleted
  python3 cleanup.py drafts <batch>       -> delete that batch's drafts
  python3 cleanup.py posted <batch>       -> delete drafts + until_posted (run after the batch is all live)
Every deletion is appended to jobs/CLEANUP-LOG.md (date, batch, path, size, why)."""
import datetime, glob, json, os, shutil, sys

HOME = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REG = f"{HOME}/jobs/RETENTION.json"
LOG = f"{HOME}/jobs/CLEANUP-LOG.md"


def size(p):
    if os.path.isfile(p):
        return os.path.getsize(p)
    return sum(os.path.getsize(os.path.join(r, f)) for r, _, fs in os.walk(p) for f in fs)


def human(n):
    for u in ["B", "KB", "MB", "GB"]:
        if n < 1024 or u == "GB":
            return f"{n:.1f}{u}" if u == "GB" else f"{n:.0f}{u}"
        n /= 1024


def expand(patterns, keep):
    out = []
    for pat in patterns:
        for p in sorted(glob.glob(pat)):
            if os.path.basename(p).startswith("._"):
                continue
            if any(os.path.abspath(p) == os.path.abspath(k) or os.path.abspath(k).startswith(os.path.abspath(p) + "/")
                   for k in keep):
                sys.exit(f"refusing: {p} contains a kept path")
            out.append(p)
    return out


def resolve(batch):
    b = json.load(open(REG, encoding="utf-8"))[batch]
    keep = [k for pat in b.get("keep", []) + b.get("until_posted", []) for k in glob.glob(pat)]
    drafts = expand(b.get("drafts", []), keep)
    keep_only = [k for pat in b.get("keep", []) for k in glob.glob(pat)]
    posted = expand(b.get("until_posted", []), keep_only)
    return b, drafts, posted


def delete(batch, paths, why):
    total = 0
    with open(LOG, "a", encoding="utf-8") as log:
        if not os.path.exists(LOG) or os.path.getsize(LOG) == 0:
            log.write("# Cleanup log\n\n| Date | Batch | Path | Size | Why |\n|---|---|---|---|---|\n")
        for p in paths:
            if not os.path.exists(p):
                continue
            n = size(p)
            # exFAT drops a file's ._ twin along with it, which trips rmtree mid-walk: ignore that, then check
            shutil.rmtree(p, ignore_errors=True) if os.path.isdir(p) else os.remove(p)
            if os.path.exists(p):
                shutil.rmtree(p, ignore_errors=True)
            if os.path.exists(p):
                print("could not fully delete", p)
                continue
            ad = os.path.join(os.path.dirname(p), "._" + os.path.basename(p))  # exFAT AppleDouble twin
            if os.path.exists(ad):
                os.remove(ad)
            total += n
            log.write(f"| {datetime.date.today()} | {batch} | `{p}` | {human(n)} | {why} |\n")
            print("deleted", human(n).rjust(8), p)
    print("freed", human(total))


if __name__ == "__main__":
    cmd = sys.argv[1] if len(sys.argv) > 1 else "plan"
    if cmd == "plan":
        for batch in json.load(open(REG, encoding="utf-8")):
            b, drafts, posted = resolve(batch)
            print(f"{batch}: drafts {human(sum(map(size, drafts)))} ({len(drafts)} items) · "
                  f"after posting {human(sum(map(size, posted)))} ({len(posted)} items) · {b.get('status', '')}")
            for p in drafts:
                print("   draft ", human(size(p)).rjust(8), p)
    elif cmd == "drafts":
        b, drafts, _ = resolve(sys.argv[2])
        delete(sys.argv[2], drafts, "superseded draft")
    elif cmd == "posted":
        b, drafts, posted = resolve(sys.argv[2])
        delete(sys.argv[2], drafts + posted, "batch posted")
    else:
        sys.exit(__doc__)
