"""Fusion building blocks for the 16:9 VSL mode (1920x1080, 25fps). Pure comp-text generation, no Resolve calls.
Palette = WellSetMedia tokens (brand/design-system/tokens.css). Type = the soft Helvetica from eoin-yap."""
import math, os, re
from PIL import Image, ImageFont
import fusion
from fusion import Comp, A, AP, P, L, Fu, Raw, q, ramp, ease_out, ease_in_out, clamp01

W, H, FPS = 1920, 1080, 25
fusion.W, fusion.H, fusion.TEXT_DIV = W, H, 1450.0

INK = (0.055, 0.067, 0.075)        # #0E1113
TEAL = (0.180, 0.494, 0.588)       # #2E7E96
TEAL_HI = (0.282, 0.627, 0.737)    # #48A0BC
GREY = (0.494, 0.541, 0.549)       # #7E8A8C
GREY_INK = (0.36, 0.40, 0.41)      # grey for text on white: #7E8A8C reads 2.9 on PAPER, this clears 3.0
WHITE = (1.0, 1.0, 1.0)
PAPER = (0.975, 0.975, 0.968)      # the white scenes (Eoin 26 Oct: white background for the facecam parts)
FONT = "Helvetica"
FONT_FILE, BOLD, REG = "/System/Library/Fonts/Helvetica.ttc", 1, 0


def measure(s, px, spacing=1.0, bold=True):
    f = ImageFont.truetype(FONT_FILE, 100, index=BOLD if bold else REG)
    # x1.047: Fusion's Helvetica Bold sets 4.7% wider than PIL's (measured in Resolve 26 Oct)
    return max(f.getlength(l) for l in s.split("\n")) * px / 100 * (1 + (spacing - 1) * 0.9) * 1.047


def wrap(words, px, width, spacing=1.0):
    """greedy wrap of [(word, t)] into lines that fit width"""
    lines, cur = [], []
    for w in words:
        if cur and measure(" ".join(x[0] for x in cur + [w]), px, spacing) > width:
            lines.append(cur); cur = []
        cur.append(w)
    if cur:
        lines.append(cur)
    return lines


class Scene:
    """one comp that starts at timeline second `a`; lf(t) = local frame of second t"""
    def __init__(self, a, b):
        self.a, self.b = a, b
        self.n = max(1, round(b * FPS) - round(a * FPS))
        self.c = Comp(self.n)
        self.k = 0

    def lf(self, t):
        return (t - self.a) * FPS

    def nm(self, base):
        self.k += 1
        return re.sub(r"\W", "", base)[:14] + str(self.k)

    # ---- timing curves ---------------------------------------------------------------------------------------
    def fade(self, t_in, t_out=None, din=0.3, dout=0.3, lo=0.0):
        a, b = self.lf(t_in), self.lf(t_out) if t_out is not None else None
        def fn(f):
            v = ease_out(ramp(f, a, a + din * FPS))
            if b is not None:
                v *= 1 - ease_in_out(ramp(f, b - dout * FPS, b)) * (1 - lo)
            return v
        return fn

    def rise(self, t_in, px=26, dur=0.45):
        a = self.lf(t_in)
        return lambda f: px * (1 - ease_out(ramp(f, a, a + dur * FPS)))

    def end_words(self, words):
        """Text+ End for a line built from [(word, t)]: each word lands on its spoken frame"""
        s = " ".join(w for w, _ in words)
        marks, acc = [], 0
        for w, t in words:
            acc += len(w) + 1
            # Text+ rounds the revealed count up: stop half a character short of the space so no next letter leaks
            marks.append((self.lf(t) - 1, 1.0 if acc >= len(s) else (acc - 1.5) / len(s)))
        def fn(f):
            v = 0.0
            for fr, e in marks:
                if f >= fr:
                    v = e
            return v
        return fn

    # ---- drawing ---------------------------------------------------------------------------------------------
    def canvas(self):
        return self.c.canvas(self.nm("Canvas"))

    def paper(self, bg, blend=None):
        s = self.c.solid(self.nm("Paper"), PAPER)
        return self.c.merge(self.nm("PaperM"), bg, s, blend=A(blend) if blend else None)

    def put(self, bg, fg, blend=None, dx=None, dy=None):
        """merge a full-frame layer with optional animated opacity and offset"""
        center = None
        if dx or dy:
            center = AP(lambda f: (W / 2 + (dx(f) if dx else 0), H / 2 + (dy(f) if dy else 0)))
        return self.c.merge(self.nm("Put"), bg, fg, blend=A(blend) if blend else None, center=center)

    def text(self, s, x, y, px, rgb=WHITE, spacing=1.0, end=None, soft=True, style="Bold", left=False, angle=0):
        """soft Helvetica (slight blur + glow) on its own layer; x is the left edge when left=True"""
        c = self.c
        if left:
            x = x + measure(s, px, spacing, style == "Bold") / 2
        n = self.nm("T" + s)
        lay = c.canvas(n + "C")
        e = A(end) if end else None
        tx = c.text(n, s, x, y, px, rgb=rgb, style=style, font=FONT, spacing=spacing, end=e, angle=angle)
        if not soft:
            return c.merge(n + "M", lay, tx)
        tb = c.tool(n + "B", "Blur", {"Input": L(tx), "XBlurSize": 0.35})
        tg = c.tool(n + "G", "SoftGlow", {"Input": L(tb), "Gain": 0.12, "XGlowSize": 3})
        return c.merge(n + "M", lay, tg)

    def halo(self, s, x, y, px, spacing=1.0, end=None, a=0.85, line=0.14, blur=1.4, left=False, style="Bold"):
        """soft dark halo behind white text on camera (readable everywhere, engine/readable.py)"""
        c = self.c
        if left:
            x = x + measure(s, px, spacing, style == "Bold") / 2
        n = self.nm("H" + s)
        lay = c.canvas(n + "C")
        tx = c.text(n, s, x, y, px, rgb=(0, 0, 0), a=a, style=style, font=FONT, spacing=spacing, end=A(end) if end else None)
        extra = (f"Enabled2 = Input {{ Value = 1, }},\n\t\t\t\tThickness2 = Input {{ Value = {line}, }},\n\t\t\t\t"
                 f"Red2 = Input {{ Value = 0, }},\n\t\t\t\tGreen2 = Input {{ Value = 0, }},\n\t\t\t\tBlue2 = Input {{ Value = 0, }},\n\t\t\t\t"
                 f"Alpha2 = Input {{ Value = {a}, }},\n\t\t\t\t")
        for k, (nn, t) in enumerate(c.tools):
            if nn == tx:
                c.tools[k] = (nn, t.replace("Inputs = {\n\t\t\t\t", "Inputs = {\n\t\t\t\t" + extra, 1))
        return c.merge(n + "M", lay, c.tool(n + "B", "Blur", {"Input": L(tx), "XBlurSize": blur}))

    def box(self, rgb, a, cx, cy, w, h, radius=0.0, soft=0.0, border=None):
        """filled (or outlined) rect layer"""
        c = self.c
        n = self.nm("Box")
        m = c.rect(n + "M", cx, cy, w, h, radius, soft, border=border)
        s = c.solid(n + "F", rgb, a)
        c.tools[-1] = (s, c.tools[-1][1].replace("\n\t\t\t},", ",\n\t\t\t\tEffectMask = Input { SourceOp = " + q(m) + ", Source = \"Mask\", },\n\t\t\t},", 1))
        return s

    def shadow(self, cx, cy, w, h, radius=0.02, a=0.22, blur=28, off=14):
        s = self.box(INK, a, cx, cy + off, w, h, radius)
        return self.c.tool(self.nm("Shd"), "Blur", {"Input": L(s), "XBlurSize": blur})

    def image(self, path, cx, cy, w, h, radius=0.0, crop=None, scale=1.0, dx=None, dy=None, sc=None, angle=None):
        """image covering a w x h window centred on (cx, cy); crop = (x0, y0, x1, y1) in image px picks what fills it.
        dx/dy/sc animate the whole window (fn of frame); returns a full-frame layer"""
        c = self.c
        pw, ph = Image.open(path).size
        x0, y0, x1, y1 = crop or (0, 0, pw, ph)
        n = self.nm("Img")
        ld = c.tool(n + "L", "Loader", {})
        c.tools[-1] = (ld, c.tools[-1][1].replace("Inputs = {", "Clips = {\n\t\t\t\tClip {\n\t\t\t\t\tFilename = " + q(path) +
                       ",\n\t\t\t\t\tFormatID = \"JpegFormat\",\n\t\t\t\t\tLength = 1,\n\t\t\t\t\tLoop = 1,\n\t\t\t\t}\n\t\t\t},\n\t\t\tInputs = {", 1))
        k = max(w / (x1 - x0), h / (y1 - y0)) * scale            # image px -> screen px
        # the loader's image is centred on the merge centre: shift so the crop centre lands on (cx, cy)
        ox, oy = (pw / 2 - (x0 + x1) / 2) * k, (ph / 2 - (y0 + y1) / 2) * k
        lay = c.canvas(n + "C")
        def ctr(f):
            s_ = sc(f) if sc else 1.0
            return (cx + ox * s_ + (dx(f) if dx else 0), cy + oy * s_ + (dy(f) if dy else 0))
        # Merge Size = screen px per image px (same as eoin-yap put_image)
        mg = c.merge(n + "M", lay, ld, center=AP(ctr), size=A(lambda f: k * sc(f)) if sc else k, angle=angle)
        def mctr(f):
            return (cx + (dx(f) if dx else 0), cy + (dy(f) if dy else 0))
        if sc:
            wfn = lambda f: w * sc(f) / W
            hfn = lambda f: h * sc(f) / H
            m = c.tool(n + "Mk", "RectangleMask", {"Center": AP(mctr), "Width": A(wfn), "Height": A(hfn), "CornerRadius": radius, "OutputSize": 0})
        else:
            m = c.tool(n + "Mk", "RectangleMask", {"Center": AP(mctr) if (dx or dy) else P(cx, cy), "Width": w / W, "Height": h / H, "CornerRadius": radius, "OutputSize": 0})
        c.tools[[x[0] for x in c.tools].index(mg)] = (mg, c.tools[[x[0] for x in c.tools].index(mg)][1].replace(
            "\n\t\t\t},", ",\n\t\t\t\tEffectMask = Input { SourceOp = " + q(m) + ", Source = \"Mask\", },\n\t\t\t},", 1))
        return mg

    def arc(self, cx, cy, r, a0, a1, width, rgb, alpha=1.0, write=None, steps=96):
        """circular arc from angle a0 to a1 (degrees, clockwise from 12 o'clock) as an outlined polyline mask;
        write(f) -> 0..1 draws it on (Fusion WriteLength)"""
        c = self.c
        n = self.nm("Arc")
        pts = []
        for i in range(steps + 1):
            th = math.radians(a0 + (a1 - a0) * i / steps)
            x, y = cx + r * math.sin(th), cy - r * math.cos(th)
            pts.append(f"{{ Linear = true, X = {(x - cx) / W:.6f}, Y = {-(y - cy) / H:.6f}, LX = 0, LY = 0, RX = 0, RY = 0 }}")
        wl = f"WriteLength = Input {{ SourceOp = {q(n + 'WL')}, Source = \"Value\", }},\n\t\t\t\t" if write else ""
        if write:
            c._spline(n + "WL", write)
        mask = (f"{n}M = PolylineMask {{\n\t\t\tDrawMode = \"ModifyOnly\",\n\t\t\tDrawMode2 = \"ModifyOnly\",\n\t\t\tInputs = {{\n\t\t\t\t"
                f"MaskWidth = Input {{ Value = {W}, }},\n\t\t\t\tMaskHeight = Input {{ Value = {H}, }},\n\t\t\t\t"
                f"PixelAspect = Input {{ Value = {{ 1, 1 }}, }},\n\t\t\t\tOutputSize = Input {{ Value = 0, }},\n\t\t\t\t"
                f"Solid = Input {{ Value = 0, }},\n\t\t\t\tBorderWidth = Input {{ Value = {width / W:.6f}, }},\n\t\t\t\t"
                f"Center = Input {{ Value = {{ {cx / W:.6f}, {1 - cy / H:.6f} }}, }},\n\t\t\t\t{wl}"
                f"Polyline = Input {{\n\t\t\t\t\tValue = Polyline {{\n\t\t\t\t\t\tPoints = {{\n\t\t\t\t\t\t\t" + ",\n\t\t\t\t\t\t\t".join(pts) +
                f"\n\t\t\t\t\t\t}}\n\t\t\t\t\t}},\n\t\t\t\t}},\n\t\t\t\tPolyline2 = Input {{ Value = Polyline {{ }}, }},\n\t\t\t}},\n\t\t}}")
        c.tools.append((n + "M", mask))
        s = c.solid(n + "F", rgb, alpha)
        c.tools[-1] = (s, c.tools[-1][1].replace("\n\t\t\t},", ",\n\t\t\t\tEffectMask = Input { SourceOp = " + q(n + "M") + ", Source = \"Mask\", },\n\t\t\t},", 1))
        return s

    def chain_mask(self, base, cx, cy, w, h, radius, mode="Subtract", invert=False):
        """a rounded-rect mask combined with mask `base` (Fusion mask chaining via EffectMask + PaintMode)"""
        c = self.c
        n = self.nm("Cm")
        i = {"Center": P(cx, cy), "Width": w / W, "Height": h / H, "CornerRadius": radius, "OutputSize": 0,
             "PaintMode": Fu(mode), "EffectMask": L(base, "Mask")}
        if invert:
            i["Invert"] = 1
        return c.tool(n, "RectangleMask", i)

    def masked_solid(self, rgb, a, mask):
        c = self.c
        s = c.solid(self.nm("Ms"), rgb, a)
        c.tools[-1] = (s, c.tools[-1][1].replace("\n\t\t\t},", ",\n\t\t\t\tEffectMask = Input { SourceOp = " + q(mask) + ", Source = \"Mask\", },\n\t\t\t},", 1))
        return s

    def window_frame(self, cx, cy, w, h, radius=0.07, shadow=True):
        """PAPER everywhere except a rounded w x h hole (the facecam shows through from the track below),
        with a soft shadow that only falls outside the hole"""
        c = self.c
        full = c.tool(self.nm("Full"), "RectangleMask", {"Center": P(W / 2, H / 2), "Width": 1.2, "Height": 1.2, "OutputSize": 0})
        hole = self.chain_mask(full, cx, cy, w, h, radius)
        top = self.masked_solid(PAPER, 1.0, hole)
        if shadow:
            sm = c.tool(self.nm("ShM"), "RectangleMask", {"Center": P(cx, cy + 16), "Width": (w + 10) / W, "Height": (h + 10) / H,
                                                         "CornerRadius": radius, "SoftEdge": 0.022, "OutputSize": 0})
            sh = self.chain_mask(sm, cx, cy, w, h, radius)
            top = self.c.merge(self.nm("ShP"), top, self.masked_solid(INK, 0.20, sh))
        return top

    def dot(self, cx, cy, d, rgb, a=1.0, border=None):
        return self.box(rgb, a, cx, cy, d, d, radius=1.0, border=border)

    def out(self, top):
        return self.c.text_out(top)
