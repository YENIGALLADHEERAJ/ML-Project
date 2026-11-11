"""Reusable original SVG parts and team data for the SkiaTrace site (logo, ECG rule, joint figure)."""

NAME = "SkiaTrace"

# Mark: a lens ring with a shaded half (skia = shadow) and a three-node trace (hip - knee - shoulder).
LOGO = ('<svg viewBox="0 0 32 32" aria-hidden="true" focusable="false"><rect class="lg-bg" x="1" y="1" width="30" height="30" rx="9"/>'
        '<circle class="lg-ring" cx="16" cy="16" r="9.2"/><path class="lg-shade" d="M16 6.8a9.2 9.2 0 0 0 0 18.4 6.4 9.2 0 0 1 0-18.4z"/>'
        '<path class="lg-trace" d="M9.2 20.6l4.3-4.4 3 2.4 5.6-6.6"/><circle class="lg-node" cx="9.2" cy="20.6" r="1.55"/><circle class="lg-node" cx="16.4" cy="18.4" r="1.55"/><circle class="lg-node" cx="22.1" cy="11.8" r="1.55"/></svg>')
FAVICON = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 32 32"><rect x="1" y="1" width="30" height="30" rx="9" fill="#15120C"/>'
           '<circle cx="16" cy="16" r="9.2" fill="none" stroke="#E8C27A" stroke-width="1.6"/><path d="M16 6.8a9.2 9.2 0 0 0 0 18.4 6.4 9.2 0 0 1 0-18.4z" fill="#E8C27A" opacity=".35"/>'
           '<path d="M9.2 20.6l4.3-4.4 3 2.4 5.6-6.6" fill="none" stroke="#F4F0E6" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round"/>'
           '<circle cx="9.2" cy="20.6" r="1.55" fill="#F4F0E6"/><circle cx="16.4" cy="18.4" r="1.55" fill="#F4F0E6"/><circle cx="22.1" cy="11.8" r="1.55" fill="#F4F0E6"/></svg>')
WORDMARK = 'Skia<em>Trace</em>'


def ecg_path(width=1200, mid=30, beats=3):
    """A stylised ECG trace (P-QRS-T) repeated across the width. Decorative."""
    seg = width / beats; d = f"M0 {mid}"; x = 0
    for _ in range(beats):
        pts = [(0.30, 0), (0.06, -5), (0.06, 5), (0.05, 0), (0.03, 2), (0.025, -26), (0.025, 38), (0.025, -12), (0.04, 0), (0.07, 0), (0.07, -8), (0.07, 8)]
        px = x
        for dx, dy in pts:
            px += dx * seg; d += f" L{px:.1f} {mid + dy:.1f}" if dy else f" L{px:.1f} {mid}"
        d += f" L{x + seg:.1f} {mid}"; x += seg
    return d


def ecg(cls="ecg", height=60):
    return (f'<svg class="{cls}" viewBox="0 0 1200 60" preserveAspectRatio="none" aria-hidden="true" focusable="false" height="{height}">'
            f'<path class="ecg-base" d="{ecg_path()}"/><path class="ecg-line" d="{ecg_path()}"/></svg>')


# Joint figure: original line-art skeleton with the three joints the models are asked to name.
JOINTS = {"Shoulder": [(96, 104), (204, 104)], "Hip": [(120, 292), (180, 292)], "Knee": [(127, 404), (173, 404)]}
SKELETON = '''<svg class="skel-fig" viewBox="0 0 360 540" role="img" aria-label="Line drawing of a human skeleton with the shoulder, hip and knee joints marked">
<g class="bones" fill="none" stroke-linecap="round" stroke-linejoin="round">
<circle cx="150" cy="44" r="23"/><path d="M142 66v22M158 66v22"/>
<path d="M96 104q54-20 108 0"/><path d="M150 88v26M150 114c-7 30 7 54 0 84s7 52 0 80"/>
<path d="M126 120q24 16 48 0M122 146q28 18 56 0M124 172q26 16 52 0M128 198q22 14 44 0" class="ribs"/>
<path d="M96 104l-26 82-10 78M204 104l26 82 10 78"/><circle cx="70" cy="186" r="4"/><circle cx="230" cy="186" r="4"/>
<path d="M102 270q-12 18 18 38q30 14 30-10q0 24 30 10q30-20 18-38"/><path d="M120 292l7 112M180 292l-7 112"/>
<path d="M127 404l4 98M173 404l-4 98"/><circle cx="127" cy="404" r="6"/><circle cx="173" cy="404" r="6"/>
<path d="M118 506h26M156 506h26"/></g>
<g class="markers">''' + "".join(
    f'<g class="mk" data-j="{n}"><circle class="ring" cx="{x}" cy="{y}" r="11"/><circle class="dot" cx="{x}" cy="{y}" r="4.5"/></g>' for n, pts in JOINTS.items() for x, y in pts) + '''</g>
<g class="labels" font-family="JetBrains Mono, monospace" font-size="11" letter-spacing="1.4">
<path class="lead" d="M214 104h42M192 292h64M182 404h74"/>
<text x="262" y="108">SHOULDER</text><text x="262" y="296">HIP</text><text x="262" y="408">KNEE</text></g></svg>'''

TEAM = [("Dheeraj Yenigalla", "RA2411003012126"), ("Kurmadasu Bharat Kumar", "RA2411003012111"), ("Atharva Shrirang Arcotkar", "RA2411003012136"),
        ("Bhuvesh H", "RA2411003012149"), ("Alluri Nithin Varma", "RA2411003012109")]


def initials(n):
    p = n.split(); return (p[0][0] + p[-1][0]).upper() if len(p) > 1 else p[0][:2].upper()


def team_cards():
    return "".join(f'<li class="member"><span class="mono-circle" aria-hidden="true">{initials(n)}</span><div><b>{n}</b><span>{r}</span></div></li>' for n, r in TEAM)
