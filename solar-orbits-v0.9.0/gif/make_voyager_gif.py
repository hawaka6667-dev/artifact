#!/usr/bin/env python3
"""Voyager 2 trajectory animation (1977-08-20 -> Neptune flyby 1989-08-25), top-down ecliptic view.

Method (patched conics, schematic): planet positions come from the JPL approximate Keplerian elements
(Standish, valid 1800-2050); the spacecraft is a Lambert (two-body) arc between consecutive flyby
positions on the real flyby dates. Speed jumps at each flyby are the gravity assists. Not a JPL Horizons
trajectory: errors of a few percent in position are expected.
Usage: python3 make_voyager_gif.py [out.gif]
"""
import sys, math, datetime as dt
import numpy as np
from scipy.optimize import brentq
from PIL import Image, ImageDraw, ImageFont

K = 0.01720209895; MU = K * K                       # AU^3 / day^2
AU_KM = 1.495978707e8
J2000 = dt.datetime(2000, 1, 1, 12)

# a, e, I, L, long.peri, long.node  (value at J2000, rate per Julian century)
EL = {
 "Earth":   [(1.00000261, .00000562), (.01671123, -.00004392), (-.00001531, -.01294668), (100.46457166, 35999.37244981), (102.93768193, .32327364), (0., 0.)],
 "Mars":    [(1.52371034, .00001847), (.09339410, .00007882), (1.84969142, -.00813131), (-4.55343205, 19140.30268499), (-23.94362959, .44441088), (49.55953891, -.29257343)],
 "Jupiter": [(5.20288700, -.00011607), (.04838624, -.00013253), (1.30439695, -.00183714), (34.39644051, 3034.74612775), (14.72847983, .21252668), (100.47390909, .20469106)],
 "Saturn":  [(9.53667594, -.00125060), (.05386179, -.00050991), (2.48599187, .00193609), (49.95424423, 1222.49362201), (92.59887831, -.41897216), (113.66242448, -.28867794)],
 "Uranus":  [(19.18916464, -.00196176), (.04725744, -.00004397), (.77263783, -.00242939), (313.23810451, 428.48202785), (170.95427630, .40805281), (74.01692503, .04240589)],
 "Neptune": [(30.06992276, .00026291), (.00859048, .00005105), (1.77004347, .00035372), (-55.12002969, 218.45945325), (44.96476227, -.32241464), (131.78422574, -.00508664)],
}
PERIOD = {"Earth": 365.25, "Mars": 686.98, "Jupiter": 4332.6, "Saturn": 10759.2, "Uranus": 30688.5, "Neptune": 60182}
COLOR = {"Earth": (70, 160, 255), "Mars": (255, 90, 210), "Jupiter": (40, 225, 80), "Saturn": (50, 230, 230), "Uranus": (255, 215, 40), "Neptune": (255, 80, 40)}

def jd(d): return (d - J2000).total_seconds() / 86400.0       # days since J2000.0

def planet(name, d):
    T = jd(d) / 36525.0
    a, e, I, L, wp, Om = [v0 + v1 * T for v0, v1 in EL[name]]
    w = math.radians(wp - Om); M = math.radians((L - wp) % 360.0)
    E = M
    for _ in range(30): E -= (E - e * math.sin(E) - M) / (1 - e * math.cos(E))
    xo, yo = a * (math.cos(E) - e), a * math.sqrt(1 - e * e) * math.sin(E)
    cw, sw, cO, sO, ci, si = math.cos(w), math.sin(w), math.cos(math.radians(Om)), math.sin(math.radians(Om)), math.cos(math.radians(I)), math.sin(math.radians(I))
    x = (cw * cO - sw * sO * ci) * xo + (-sw * cO - cw * sO * ci) * yo
    y = (cw * sO + sw * cO * ci) * xo + (-sw * sO + cw * cO * ci) * yo
    z = (sw * si) * xo + (cw * si) * yo
    return np.array([x, y, z])

def pvel(name, d):                                                # numeric velocity AU/day
    h = dt.timedelta(hours=6)
    return (planet(name, d + h) - planet(name, d - h)) / .5

def stumpff(z):
    if z > 1e-8: s = math.sqrt(z); return (1 - math.cos(s)) / z, (s - math.sin(s)) / s ** 3
    if z < -1e-8: s = math.sqrt(-z); return (math.cosh(s) - 1) / -z, (math.sinh(s) - s) / s ** 3
    return .5, 1 / 6

def lambert(r1, r2, tof):                                         # prograde, Bate-Mueller-White
    n1, n2 = np.linalg.norm(r1), np.linalg.norm(r2)
    c = np.dot(r1, r2) / (n1 * n2); dn = math.acos(max(-1, min(1, c)))
    if np.cross(r1, r2)[2] < 0: dn = 2 * math.pi - dn
    A = math.sin(dn) * math.sqrt(n1 * n2 / (1 - math.cos(dn)))
    def tz(z):
        C, S = stumpff(z); y = n1 + n2 + A * (z * S - 1) / math.sqrt(C)
        return (math.sqrt(y / C) ** 3 * S + A * math.sqrt(y)) / math.sqrt(MU) - tof
    def yz(z):
        C, S = stumpff(z); return n1 + n2 + A * (z * S - 1) / math.sqrt(C)
    hi_ok, bad = 0.0, -1.0                                         # find the y = 0 edge of the hyperbolic branch
    while yz(bad) > 0 and bad > -1e6: hi_ok, bad = bad, bad * 2
    if yz(bad) <= 0:
        for _ in range(200):
            mid = (hi_ok + bad) / 2
            if yz(mid) > 0: hi_ok = mid
            else: bad = mid
        lo = hi_ok + 1e-9
    else: lo = bad
    z = brentq(tz, lo, (2 * math.pi) ** 2 - 1e-3)
    C, S = stumpff(z); y = n1 + n2 + A * (z * S - 1) / math.sqrt(C)
    f, g, gd = 1 - y / n1, A * math.sqrt(y / MU), 1 - y / n2
    return (r2 - f * r1) / g, (gd * r2 - r1) / g

def propagate(r0, v0, dtm):                                       # universal variables
    r0n = np.linalg.norm(r0); vr0 = np.dot(r0, v0) / r0n; alpha = 2 / r0n - np.dot(v0, v0) / MU
    chi = math.sqrt(MU) * abs(alpha) * dtm
    for _ in range(80):
        z = alpha * chi * chi; C, S = stumpff(z)
        F = r0n * vr0 / math.sqrt(MU) * chi * chi * C + (1 - alpha * r0n) * chi ** 3 * S + r0n * chi - math.sqrt(MU) * dtm
        dF = r0n * vr0 / math.sqrt(MU) * chi * (1 - z * S) + (1 - alpha * r0n) * chi * chi * C + r0n
        chi -= F / dF
    z = alpha * chi * chi; C, S = stumpff(z)
    f = 1 - chi * chi / r0n * C; g = dtm - chi ** 3 / math.sqrt(MU) * S
    r = f * r0 + g * v0; rn = np.linalg.norm(r)
    fd = math.sqrt(MU) / (rn * r0n) * chi * (z * S - 1); gd = 1 - chi * chi / rn * C
    return r, fd * r0 + gd * v0

# ---------------- mission ----------------
EVENTS = [("Earth", dt.datetime(1977, 8, 20, 14, 29), "Launch"), ("Jupiter", dt.datetime(1979, 7, 9, 22, 29), "Jupiter flyby"),
          ("Saturn", dt.datetime(1981, 8, 26, 3, 24), "Saturn flyby"), ("Uranus", dt.datetime(1986, 1, 24, 17, 59), "Uranus flyby"),
          ("Neptune", dt.datetime(1989, 8, 25, 3, 56), "Neptune flyby")]
legs = []
for (p1, d1, _), (p2, d2, _) in zip(EVENTS, EVENTS[1:]):
    r1, r2 = planet(p1, d1), planet(p2, d2); tof = (d2 - d1).total_seconds() / 86400
    v1, v2 = lambert(r1, r2, tof); legs.append((d1, d2, r1, v1, v2))
    print(f"{p1:8s}->{p2:8s} tof {tof/365.25:5.2f} yr  v_dep {np.linalg.norm(v1)*AU_KM/86400:5.1f} km/s  "
          f"v_inf(dep) {np.linalg.norm(v1-pvel(p1,d1))*AU_KM/86400:5.1f}  v_inf(arr) {np.linalg.norm(v2-pvel(p2,d2))*AU_KM/86400:5.1f} km/s")

def craft(d):
    for d1, d2, r1, v1, v2 in legs:
        if d1 <= d <= d2:
            r, v = propagate(r1, v1, (d - d1).total_seconds() / 86400); return r, v
    raise ValueError(d)

# ---------------- drawing ----------------
SS = 2; W, H = 720, 540
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"; FB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
f_title = ImageFont.truetype(FONT, 26 * SS); f_s = ImageFont.truetype(FONT, 15 * SS); f_t = ImageFont.truetype(FONT, 13 * SS); f_b = ImageFont.truetype(FB, 17 * SS)
CX, CY, SCALE = W * SS / 2, H * SS * .52, H * SS * .43 / 30.07

def px(p): return (CX + p[0] * SCALE, CY - p[1] * SCALE)

def frame(d, ev_text):
    im = Image.new("RGB", (W * SS, H * SS), (0, 0, 0)); g = ImageDraw.Draw(im)
    for n in COLOR:
        win = min(PERIOD[n], 6000.0); pts = [px(planet(n, d - dt.timedelta(days=win * (1 - i / 80)))) for i in range(81)]
        g.line(pts, fill=tuple(int(c * .85) for c in COLOR[n]), width=2 * SS, joint="curve")
    g.ellipse([CX - 5 * SS, CY - 5 * SS, CX + 5 * SS, CY + 5 * SS], fill=(255, 220, 40))
    for n in COLOR:
        x, y = px(planet(n, d)); r = (4 if n in ("Earth", "Mars") else 5.5) * SS
        g.ellipse([x - r, y - r, x + r, y + r], fill=COLOR[n])
        if n != "Mars": g.text((x + r + 4 * SS, y - 9 * SS), n, font=f_t, fill=tuple(int(c * .75 + 40) for c in COLOR[n]))
    # spacecraft trail + marker
    t0 = EVENTS[0][1]; n = max(2, int((d - t0).days / 8) + 2)
    trail = [px(craft(min(d, t0 + (d - t0) * i / (n - 1)))[0]) for i in range(n)]
    g.line(trail, fill=(255, 255, 255), width=2 * SS, joint="curve")
    r, v = craft(d); x, y = px(r); g.ellipse([x - 5 * SS, y - 5 * SS, x + 5 * SS, y + 5 * SS], fill=(255, 255, 255))
    g.ellipse([x - 9 * SS, y - 9 * SS, x + 9 * SS, y + 9 * SS], outline=(255, 255, 255), width=SS)
    # text
    g.text((W * SS / 2, 14 * SS), "Voyager 2", font=f_title, fill=(255, 255, 255), anchor="ma")
    g.text((14 * SS, 10 * SS), d.strftime("%Y-%m-%d"), font=f_s, fill=(255, 255, 255))
    if ev_text: g.text((W * SS / 2, 54 * SS), ev_text, font=f_b, fill=(255, 235, 140), anchor="ma")
    g.text((14 * SS, (H - 30) * SS), f"{np.linalg.norm(v) * AU_KM / 86400:.1f} km/s", font=f_s, fill=(255, 255, 255))
    g.text(((W - 14) * SS, (H - 30) * SS), f"{np.linalg.norm(r) * AU_KM:,.0f} km from Sun", font=f_s, fill=(255, 255, 255), anchor="ra")
    g.text((14 * SS, (H - 52) * SS), "speed relative to the Sun", font=f_t, fill=(130, 130, 130))
    g.text(((W - 14) * SS, 10 * SS), "top-down view of the ecliptic", font=f_t, fill=(130, 130, 130), anchor="ra")
    return im.resize((W, H), Image.LANCZOS)

if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "voyager2.gif"
    start, end = EVENTS[0][1], EVENTS[-1][1]; total = (end - start).total_seconds() / 86400
    frames, durs = [], []
    nf = 170
    for i in range(nf + 1):
        d = start + dt.timedelta(days=total * i / nf)
        ev = ""
        for _, de, label in EVENTS:
            if abs((d - de).days) < 45: ev = f"{label} · {de.strftime('%Y-%m-%d')}"
        frames.append(frame(d, ev)); durs.append(70)
    durs[0] = 1200; durs[-1] = 2500
    # one shared palette (built from a montage of sample frames) keeps the planet colours stable
    pick = frames[::8] + [frames[-1]]
    mont = Image.new("RGB", (W, H * len(pick)))
    for i, f in enumerate(pick): mont.paste(f, (0, i * H))
    gp = mont.quantize(colors=255, method=Image.MEDIANCUT, dither=Image.NONE)
    pal = [f.quantize(palette=gp, dither=Image.NONE) for f in frames]
    pal[0].save(out, save_all=True, append_images=pal[1:], duration=durs, loop=0, optimize=True, disposal=1)
    print("saved", out, len(frames), "frames")
