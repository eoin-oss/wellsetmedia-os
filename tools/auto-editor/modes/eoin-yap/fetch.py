"""Pull web candidates per image key (Bing Images, large + wide) into jobs/yap-assets/cand/<key>_<n>.jpg,
plus a numbered contact sheet per key in cand/_sheets. Usage: python3 fetch.py [key=query ...] (no args = every key in beats.py)"""
import html, io, os, re, sys, concurrent.futures as cf, urllib.parse, urllib.request
from PIL import Image, ImageDraw, ImageFont
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from beats import QUERIES
OUT = os.path.abspath(os.path.join(HERE, "../../jobs/yap-assets/cand")); os.makedirs(OUT + "/_sheets", exist_ok=True)
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130 Safari/537.36"
BAD = re.compile(r"shutterstock|alamy|dreamstime|gettyimages|istockphoto|123rf|depositphotos|freepik|vecteezy|adobe|bigstock|canstock|pond5|pinimg.com/236x", re.I)
Q = dict(QUERIES)
if sys.argv[1:]:
    Q = dict(a.split("=", 1) if "=" in a else (a, Q[a]) for a in sys.argv[1:])


def http(url, t=12):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=t).read()


def one(item):
    k, q = item
    h = http("https://www.bing.com/images/search?" + urllib.parse.urlencode({"q": q, "qft": "+filterui:imagesize-large", "form": "IRFLTR"})).decode("utf8", "ignore")
    urls = [html.unescape(u) for u in re.findall(r'murl&quot;:&quot;(.*?)&quot;', h)]
    ims = []
    for u in urls:
        if len(ims) >= 8: break
        if BAD.search(u): continue
        try:
            im = Image.open(io.BytesIO(http(u))).convert("RGB")
        except Exception:
            continue
        if im.width < 800 or im.width < im.height * 1.05: continue   # landscape, big enough for a 960px card
        ims.append(im)
    for n, im in enumerate(ims):
        im.save(f"{OUT}/{k}_{n}.jpg", quality=93)
    if ims:  # numbered sheet to pick from
        sh = Image.new("RGB", (4 * 400, ((len(ims) + 3) // 4) * 240), "black"); d = ImageDraw.Draw(sh)
        for n, im in enumerate(ims):
            th = im.copy(); th.thumbnail((396, 236)); sh.paste(th, ((n % 4) * 400, (n // 4) * 240))
            d.rectangle([(n % 4) * 400, (n // 4) * 240, (n % 4) * 400 + 34, (n // 4) * 240 + 30], fill="black"); d.text(((n % 4) * 400 + 8, (n // 4) * 240 + 6), str(n), fill="yellow", font=ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 22))
        sh.save(f"{OUT}/_sheets/{k}.jpg", quality=80)
    return k, len(ims)


with cf.ThreadPoolExecutor(6) as ex:
    for k, n in ex.map(one, Q.items()): print(k, n, flush=True)
