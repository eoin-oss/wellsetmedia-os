import json, os, sys
HOME = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
sys.path.insert(0, os.path.join(HOME, "engine"))
FPS = 24


def job_dir():
    j = sys.argv[1] if len(sys.argv) > 1 else sys.exit("usage: <tool>.py <job_dir>")
    return os.path.abspath(j if os.path.isdir(j) else os.path.join(HOME, "jobs", j))


def extras(job):
    p = os.path.join(job, "extras.json")
    return json.load(open(p)) if os.path.exists(p) else {}
