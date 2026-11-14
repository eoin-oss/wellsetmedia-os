"""Write Fusion .comp files from Python so every graphic is a native, editable Fusion comp inside Resolve.
Positions are in timeline pixels (1920x1080, y down); they are converted to Fusion's normalized, y-up space here.
Animation is baked as BezierSpline keys (linear, one per frame where the value changes) so it's visible and
editable in the Fusion spline editor."""
import math

W, H = 1920, 1080
TEXT_DIV = 1450.0  # Text+ Size = px / TEXT_DIV (calibrated on 1920x1080; vertical jobs set their own)


def px(x, y):
    return (x / W, 1 - y / H)


class Fu:  # FuID value
    def __init__(self, v): self.v = v


class P:  # static point, pixels
    def __init__(self, x, y): self.x, self.y = x, y


class L:  # link to another tool's output
    def __init__(self, op, src="Output"): self.op, self.src = op, src


class A:  # animated number: f(frame) -> value
    def __init__(self, fn): self.fn = fn


class AP:  # animated point: f(frame) -> (x, y) pixels
    def __init__(self, fn): self.fn = fn


class Txt:  # StyledText
    def __init__(self, s): self.s = s


class Raw:
    def __init__(self, s): self.s = s


def q(s):
    return '"' + str(s).replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n") + '"'


def f6(v):
    return f"{v:.6g}"


class Comp:
    def __init__(self, frames):
        self.n = frames
        self.tools = []  # (name, text)
        self.order = []

    def _spline(self, name, fn):
        keys, prev = [], None
        vals = [fn(f) for f in range(self.n + 1)]
        for f, v in enumerate(vals):
            # keep a key where the slope changes (linear segments in between are exact)
            if f in (0, self.n) or abs((vals[f - 1] + vals[f + 1]) / 2 - v) > 1e-5 or (prev is not None and f == 1):
                keys.append(f"[{f}] = {{ {f6(v)}, Flags = {{ Linear = true }} }}")
            prev = v
        self.tools.append((name, f"{name} = BezierSpline {{\n\t\t\tSplineColor = {{ Red = 240, Green = 200, Blue = 60 }},\n\t\t\tKeyFrames = {{\n\t\t\t\t" + ",\n\t\t\t\t".join(keys) + "\n\t\t\t}\n\t\t}"))

    def tool(self, name, typ, inputs=None, extra=""):
        lines = []
        for k, v in (inputs or {}).items():
            if isinstance(v, bool):
                v = int(v)
            if isinstance(v, (int, float)):
                lines.append(f"{k} = Input {{ Value = {f6(v)}, }}")
            elif isinstance(v, str):
                lines.append(f"{k} = Input {{ Value = {q(v)}, }}")
            elif isinstance(v, Fu):
                lines.append(f'{k} = Input {{ Value = FuID {{ {q(v.v)} }}, }}')
            elif isinstance(v, P):
                x, y = px(v.x, v.y)
                lines.append(f"{k} = Input {{ Value = {{ {f6(x)}, {f6(y)} }}, }}")
            elif isinstance(v, L):
                lines.append(f"{k} = Input {{ SourceOp = {q(v.op)}, Source = {q(v.src)}, }}")
            elif isinstance(v, A):
                sp = f"{name}{k.replace('.', '')}"
                self._spline(sp, v.fn)
                lines.append(f"{k} = Input {{ SourceOp = {q(sp)}, Source = \"Value\", }}")
            elif isinstance(v, AP):
                pth = f"{name}{k}Path"
                self._spline(pth + "X", lambda f, fn=v.fn: px(*fn(f))[0])
                self._spline(pth + "Y", lambda f, fn=v.fn: px(*fn(f))[1])
                self.tools.append((pth, f'{pth} = XYPath {{\n\t\t\tShowKeyPoints = false,\n\t\t\tDrawMode = "ModifyOnly",\n\t\t\tInputs = {{\n\t\t\t\tX = Input {{ SourceOp = {q(pth + "X")}, Source = "Value", }},\n\t\t\t\tY = Input {{ SourceOp = {q(pth + "Y")}, Source = "Value", }},\n\t\t\t}},\n\t\t}}'))
                lines.append(f"{k} = Input {{ SourceOp = {q(pth)}, Source = \"Value\", }}")
            elif isinstance(v, Txt):
                lines.append(f"{k} = Input {{ Value = StyledText {{ Value = {q(v.s)} }}, }}")
            elif isinstance(v, Raw):
                lines.append(f"{k} = Input {{ {v.s} }},")
        body = ",\n\t\t\t\t".join(l.rstrip(",") for l in lines)
        self.tools.append((name, f"{name} = {typ} {{\n\t\t\tInputs = {{\n\t\t\t\t{body}\n\t\t\t}},{extra}\n\t\t}}"))
        self.order.append(name)
        return name

    # ---- building blocks -------------------------------------------------------------------------------------
    def canvas(self, name="Canvas"):
        """transparent 1920x1080 base"""
        return self.tool(name, "Background", {"Width": W, "Height": H, "UseFrameFormatSettings": 0, "TopLeftAlpha": 0,
                                              "TopLeftRed": 0, "TopLeftGreen": 0, "TopLeftBlue": 0})

    def solid(self, name, rgb, a=1.0):
        """flat colour; premultiplied (rgb*a) or a 14% white line draws at full brightness"""
        return self.tool(name, "Background", {"Width": W, "Height": H, "UseFrameFormatSettings": 0, "TopLeftRed": rgb[0] * a,
                                              "TopLeftGreen": rgb[1] * a, "TopLeftBlue": rgb[2] * a, "TopLeftAlpha": a})

    def merge(self, name, bg, fg, blend=None, center=None, size=None, angle=None, operator=None):
        i = {"Background": L(bg), "Foreground": L(fg)}
        if blend is not None: i["Blend"] = blend
        if center is not None: i["Center"] = center
        if size is not None: i["Size"] = size
        if angle is not None: i["Angle"] = angle
        if operator is not None: i["ApplyMode"] = Fu(operator)
        return self.tool(name, "Merge", i)

    def rect(self, name, cx, cy, w, h, radius=0.0, soft=0.0, border=None, center=None):
        """rounded-rect mask; w/h in pixels (Fusion measures both against the image width)"""
        i = {"Center": center or P(cx, cy), "Width": w / W, "Height": h / H, "CornerRadius": radius, "SoftEdge": soft,
             "OutputSize": 0}
        if border is not None:
            i.update({"Solid": 0, "BorderWidth": border / W})
        return self.tool(name, "RectangleMask", i)

    def card(self, name, rgb, a, cx, cy, w, h, radius=0.12, center=None, border_rgb=None, border_a=0.14):
        """filled rounded card (+ hairline border) -> image"""
        m = self.rect(name + "M", cx, cy, w, h, radius, center=center)
        bg = self.solid(name + "Fill", rgb, a)
        self.tools[-1] = (bg, self.tools[-1][1].replace("\n\t\t\t},", ",\n\t\t\t\tEffectMask = Input { SourceOp = " + q(m) + ", Source = \"Mask\", },\n\t\t\t},", 1))
        if border_rgb is None:
            return bg
        bm = self.rect(name + "BM", cx, cy, w, h, radius, border=2, center=center)
        bb = self.solid(name + "Line", border_rgb, border_a)
        self.tools[-1] = (bb, self.tools[-1][1].replace("\n\t\t\t},", ",\n\t\t\t\tEffectMask = Input { SourceOp = " + q(bm) + ", Source = \"Mask\", },\n\t\t\t},", 1))
        return self.merge(name, bg, bb)

    def text(self, name, s, x, y, px_size, rgb=(1, 1, 1), a=1.0, style="Bold", font="Helvetica", align="center",
             spacing=1.0, center=None, end=None, angle=0, expr=None):
        """Text+; (x,y) is the anchor in pixels: centre for align=center, left edge for align=left"""
        i = {"Width": W, "Height": H, "UseFrameFormatSettings": 0, "StyledText": Txt(s), "Font": font, "Style": style,
             "Size": px_size / TEXT_DIV, "Center": center or P(x, y), "HorizontalJustificationNew": 3,
             "VerticalJustificationNew": 3, "CharacterSpacing": spacing,
             "Red1": rgb[0], "Green1": rgb[1], "Blue1": rgb[2], "Alpha1": a}
        if end is not None:
            i["End"] = end
        if angle:
            i["AngleZ"] = angle
        if expr:
            i["StyledText"] = Raw(f"Value = StyledText {{ Value = {q(s)} }}, Expression = {q(expr)},")
        return self.tool(name, "TextPlus", i)

    def text_out(self, out):
        tools = "\n\t\t" + ",\n\t\t".join(t for _, t in self.tools)
        saver = f'MediaOut1 = Saver {{\n\t\t\tInputs = {{\n\t\t\t\tIndex = Input {{ Value = "0", }},\n\t\t\t\tInput = Input {{ SourceOp = {q(out)}, Source = "Output", }},\n\t\t\t}},\n\t\t}}'
        return ("Composition {\n\tCurrentTime = 0,\n\tRenderRange = { 0, " + str(self.n - 1) + " },\n\tGlobalRange = { 0, " + str(self.n - 1) +
                " },\n\tHiQ = true,\n\tVersion = \"DaVinci Resolve Studio 21.1.1.0010\",\n\tTools = {" + tools + ",\n\t\t" + saver + "\n\t}\n}\n")


# ---- easing helpers (frame-domain) ----------------------------------------------------------------------------
def clamp01(v): return max(0.0, min(1.0, v))
def ramp(f, a, b): return clamp01((f - a) / (b - a)) if b != a else float(f >= a)
def ease_out(t): return 1 - (1 - t) ** 3
def ease_in_out(t): return 4 * t ** 3 if t < 0.5 else 1 - (-2 * t + 2) ** 3 / 2


def spring(f, start, fps=25, damping=14, stiffness=130, mass=1.0):
    """damped spring 0 -> 1 (same feel as UI springs)"""
    if f < start:
        return 0.0
    t = (f - start) / fps
    w0 = math.sqrt(stiffness / mass)
    z = damping / (2 * math.sqrt(stiffness * mass))
    if z < 1:
        wd = w0 * math.sqrt(1 - z * z)
        return 1 - math.exp(-z * w0 * t) * (math.cos(wd * t) + z * w0 / wd * math.sin(wd * t))
    return 1 - math.exp(-w0 * t) * (1 + w0 * t)
