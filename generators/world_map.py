"""
generators/world_map.py

Generates a procedural SVG world map based on continent and geography data.
No AI model needed — pure Python SVG generation.
Creates a realistic-looking fantasy/sci-fi map with:
  - Ocean background with depth gradient
  - Continent shapes (Bézier blobs)
  - City markers with labels
  - Dangerous region markers
  - Trade route lines
  - Compass rose
  - Grid overlay
"""

import random
import math
from typing import Optional


def _rng(seed: str) -> random.Random:
    return random.Random(abs(hash(seed)) % (2 ** 31))


def _bezier_blob(rng: random.Random, cx: float, cy: float,
                 rx: float, ry: float, points: int = 8) -> str:
    """Generate a smooth closed blob path centered at (cx, cy)."""
    angles = sorted([rng.uniform(0, 2 * math.pi) for _ in range(points)])
    pts = []
    for a in angles:
        r = rng.uniform(0.55, 1.0)
        x = cx + math.cos(a) * rx * r
        y = cy + math.sin(a) * ry * r
        pts.append((x, y))
    pts.append(pts[0])  # close

    path = f"M {pts[0][0]:.1f},{pts[0][1]:.1f} "
    for i in range(len(pts) - 1):
        x0, y0 = pts[i]
        x1, y1 = pts[i + 1]
        mx, my = (x0 + x1) / 2, (y0 + y1) / 2
        cp1x = x0 + (mx - x0) * 0.5
        cp1y = y0 + (my - y0) * 0.5
        path += f"Q {cp1x:.1f},{cp1y:.1f} {mx:.1f},{my:.1f} "
    path += "Z"
    return path


def _color_scheme(theme: str) -> dict:
    """Pick colors based on world theme."""
    t = theme.lower()
    if any(k in t for k in ['cyber', 'neon', 'tech', 'hack', 'robot', 'future']):
        return {
            'ocean': ('1a1a2e', '0f3460'),
            'land': ['2d4a6e', '1a3a5c', '253d5c', '2a4560'],
            'land_stroke': '4a7fa5',
            'mountain': 'a0c4ff',
            'city': 'ff6b9d',
            'city_glow': 'ff6b9d',
            'trade': '00ff88',
            'danger': 'ff0040',
            'text': 'e8f4ff',
            'grid': '1f3a5a',
            'compass': '00bfff',
        }
    elif any(k in t for k in ['hell', 'demon', 'dark', 'shadow', 'void', 'apocal']):
        return {
            'ocean': ('1a0a00', '2d0000'),
            'land': ['3d1a00', '4a2200', '3d1500', '2a1000'],
            'land_stroke': '8b3a00',
            'mountain': 'cc4400',
            'city': 'ff8c00',
            'city_glow': 'ff4500',
            'trade': 'ff6600',
            'danger': 'cc0000',
            'text': 'ffe8d0',
            'grid': '3d1500',
            'compass': 'ff6600',
        }
    elif any(k in t for k in ['space', 'galax', 'star', 'alien', 'cosmic']):
        return {
            'ocean': ('050510', '0a0a2a'),
            'land': ['1a2550', '12203c', '1e2f5a', '152040'],
            'land_stroke': '4a6aaa',
            'mountain': '7090cc',
            'city': 'c0e0ff',
            'city_glow': '80c0ff',
            'trade': '60d0b0',
            'danger': 'ff4060',
            'text': 'd0e8ff',
            'grid': '101030',
            'compass': '8080ff',
        }
    else:
        # Fantasy / default
        return {
            'ocean': ('1a4a6e', '0d3352'),
            'land': ['5a8a3c', '7aaa4c', '4a7a2c', '6a9a40'],
            'land_stroke': '3a6a2c',
            'mountain': 'd4c8a0',
            'city': 'ffe066',
            'city_glow': 'ffb800',
            'trade': 'fff0a0',
            'danger': 'cc2200',
            'text': 'f5f0e0',
            'grid': '1a5070',
            'compass': 'ffd700',
        }


def generate_svg_map(world: dict, geography: dict) -> str:
    """
    Generate a complete SVG world map.
    Returns the full SVG string to be embedded or served as-is.
    """
    W, H = 900, 500
    world_name = world.get('name', 'Unknown World')
    theme = world.get('theme', 'fantasy')
    continents = world.get('continents', [])
    cities = geography.get('major_cities', [])
    dangerous = geography.get('dangerous_regions', [])
    trade = geography.get('trade_routes', [])

    colors = _color_scheme(theme)
    rng = _rng(world_name)

    oc1, oc2 = colors['ocean']
    lines = []

    # ── SVG header ────────────────────────────────────────────────────────
    lines.append(f'<svg xmlns="http://www.w3.org/2000/svg" '
                 f'viewBox="0 0 {W} {H}" '
                 f'style="border-radius:12px;display:block;width:100%">')

    # ── Defs: gradients / filters ────────────────────────────────────────
    lines.append('<defs>')
    lines.append(f'''<radialGradient id="ocean" cx="50%" cy="40%" r="70%">
  <stop offset="0%"   stop-color="#{oc1}"/>
  <stop offset="100%" stop-color="#{oc2}"/>
</radialGradient>''')
    # Per-continent gradients
    for i, lc in enumerate(colors['land']):
        lines.append(f'''<radialGradient id="land{i}" cx="40%" cy="35%" r="65%">
  <stop offset="0%"   stop-color="#{lc}" stop-opacity="1"/>
  <stop offset="100%" stop-color="#{colors['land_stroke']}" stop-opacity="0.9"/>
</radialGradient>''')
    # Glow filter
    lines.append('''<filter id="glow" x="-30%" y="-30%" width="160%" height="160%">
  <feGaussianBlur stdDeviation="3" result="blur"/>
  <feMerge><feMergeNode in="blur"/><feMergeNode in="SourceGraphic"/></feMerge>
</filter>''')
    lines.append('''<filter id="shadow" x="-20%" y="-20%" width="140%" height="140%">
  <feDropShadow dx="3" dy="4" stdDeviation="5" flood-color="rgba(0,0,0,0.5)"/>
</filter>''')
    lines.append('</defs>')

    # ── Ocean ─────────────────────────────────────────────────────────────
    lines.append(f'<rect width="{W}" height="{H}" fill="url(#ocean)"/>')

    # ── Grid ─────────────────────────────────────────────────────────────
    grid_step = 50
    gc = colors['grid']
    for gx in range(0, W + 1, grid_step):
        lines.append(f'<line x1="{gx}" y1="0" x2="{gx}" y2="{H}" '
                     f'stroke="#{gc}" stroke-width="0.5" stroke-opacity="0.4"/>')
    for gy in range(0, H + 1, grid_step):
        lines.append(f'<line x1="0" y1="{gy}" x2="{W}" y2="{gy}" '
                     f'stroke="#{gc}" stroke-width="0.5" stroke-opacity="0.4"/>')

    # ── Continents ────────────────────────────────────────────────────────
    margin = 80
    n = max(len(continents), 1)
    
    # Generate non-overlapping continent centers based on broad zones
    cont_data = []
    
    # We define distinct zones to force continents to spread out
    # Format: (min_x, max_x, min_y, max_y)
    zones = [
        (margin, W//3, margin, H-margin),                   # Left third
        (W*2//3, W-margin, margin, H-margin),               # Right third
        (W//3, W*2//3, margin, H//2),                       # Top middle
        (W//3, W*2//3, H//2, H-margin),                     # Bottom middle
        (margin, W//2, margin, H//2),                       # Top left fallback
        (W//2, W-margin, H//2, H-margin),                   # Bottom right fallback
    ]
    rng.shuffle(zones)
    
    for i in range(n):
        zone = zones[i % len(zones)]
        zx1, zx2, zy1, zy2 = zone
        
        # Radii
        rx = rng.uniform(W * 0.08, W * 0.15)
        ry = rng.uniform(H * 0.10, H * 0.18)
        
        # Center rigidly within its assigned zone
        cx = rng.uniform(min(zx1 + rx, zx2), max(zx2 - rx, zx1))
        cy = rng.uniform(min(zy1 + ry, zy2), max(zy2 - ry, zy1))
        
        # Enforce basic repulsion
        for attempt in range(20):
            collision = False
            for (ecx, ecy, erx, ery) in cont_data:
                dist = math.hypot(cx - ecx, cy - ecy)
                if dist < (rx + erx + 20):
                    collision = True
                    # Push slightly outward from center
                    cx += 30 if cx > W/2 else -30
                    cy += 30 if cy > H/2 else -30
                    break
            if not collision:
                break
                
        # Constrain to viewbox
        cx = max(margin + rx, min(W - margin - rx, cx))
        cy = max(margin + ry, min(H - margin - ry, cy))
                    
        cont_data.append((cx, cy, rx, ry))
        
    cont_centers = [(d[0], d[1]) for d in cont_data]

    for i, cont in enumerate(continents):
        if i >= len(cont_data): break
        cx, cy, rx, ry = cont_data[i]
        path = _bezier_blob(rng, cx, cy, rx, ry, points=rng.randint(7, 11))
        lgrad = f"url(#land{i % len(colors['land'])})"
        # Shadow
        lines.append(f'<path d="{path}" fill="rgba(0,0,0,0.35)" '
                     f'transform="translate(5,6)" filter="url(#shadow)"/>')
        # Land
        lines.append(f'<path d="{path}" fill="{lgrad}" '
                     f'stroke="#{colors["land_stroke"]}" stroke-width="1.5"/>')
        # Mountain peaks (small triangles)
        for _ in range(rng.randint(2, 5)):
            mx = cx + rng.uniform(-rx * 0.5, rx * 0.5)
            my = cy + rng.uniform(-ry * 0.4, ry * 0.35)
            s = rng.uniform(8, 16)
            lines.append(f'<polygon points="{mx},{my - s} {mx - s * 0.6},{my + s * 0.3} {mx + s * 0.6},{my + s * 0.3}" '
                         f'fill="#{colors["mountain"]}" opacity="0.7"/>')
        # Continent label with shadow for readability
        # Position continent name at the top or bottom of the landmass away from the center where cities go
        cy_label = cy - ry - 15 if (i % 2 == 0) else cy + ry + 25
        name = cont.get('name', f'Land {i+1}') if isinstance(cont, dict) else str(cont)
        # Background shadow/glow
        lines.append(f'<text x="{cx:.0f}" y="{cy_label:.0f}" '
                     f'font-family="serif" font-size="14" font-weight="bold" '
                     f'fill="black" fill-opacity="0.6" '
                     f'stroke="black" stroke-width="4" stroke-linejoin="round" '
                     f'text-anchor="middle" letter-spacing="2">{name.upper()}</text>')
        # Foreground text
        lines.append(f'<text x="{cx:.0f}" y="{cy_label:.0f}" '
                     f'font-family="serif" font-size="14" font-weight="bold" '
                     f'fill="#{colors["text"]}" '
                     f'text-anchor="middle" letter-spacing="2">{name.upper()}</text>')

    # ── Trade routes (dashed lines between random continent pairs) ────────
    if len(cont_centers) > 1:
        for tr in trade[:5]:
            i1, i2 = rng.sample(range(len(cont_centers)), 2)
            x1, y1 = cont_centers[i1]
            x2, y2 = cont_centers[i2]
            tc = colors['trade']
            lines.append(f'<line x1="{x1:.0f}" y1="{y1:.0f}" '
                         f'x2="{x2:.0f}" y2="{y2:.0f}" '
                         f'stroke="#{tc}" stroke-width="1.2" stroke-opacity="0.45" '
                         f'stroke-dasharray="6,5"/>')

    # Keep track of all placed points to prevent cluster overlaps
    placed_points = []

    # ── Dangerous regions (red X markers) ────────────────────────────────
    for dr in dangerous[:5]:
        ci = rng.randint(0, len(cont_data) - 1)
        cx2, cy2, rx2, ry2 = cont_data[ci]
        
        # Try to find an empty spot with generous padding
        for _ in range(50):
            dx = cx2 + rng.uniform(-rx2 * 0.8, rx2 * 0.8)
            dy = cy2 + rng.uniform(-ry2 * 0.8, ry2 * 0.8)
            # Increase padding from 45 to 70 to radically prevent text overlaps
            if not any(math.hypot(dx - ex, dy - ey) < 70 for (ex, ey) in placed_points):
                break
                
        placed_points.append((dx, dy))
        dc = colors['danger']
        s = 7
        lines.append(f'<line x1="{dx - s}" y1="{dy - s}" x2="{dx + s}" y2="{dy + s}" '
                     f'stroke="#{dc}" stroke-width="2.5" stroke-linecap="round" opacity="0.8"/>')
        lines.append(f'<line x1="{dx + s}" y1="{dy - s}" x2="{dx - s}" y2="{dy + s}" '
                     f'stroke="#{dc}" stroke-width="2.5" stroke-linecap="round" opacity="0.8"/>')
        name = (dr.get('name', '') if isinstance(dr, dict) else str(dr))[:16]
        # Shadow/glow for visibility
        lines.append(f'<text x="{dx}" y="{dy - 12}" '
                     f'font-family="sans-serif" font-size="9" font-weight="bold" '
                     f'fill="black" stroke="black" stroke-width="2" '
                     f'text-anchor="middle" opacity="0.6">{name}</text>')
        lines.append(f'<text x="{dx}" y="{dy - 12}" '
                     f'font-family="sans-serif" font-size="9" font-weight="bold" '
                     f'fill="#{dc}" text-anchor="middle">{name}</text>')

    # ── Cities ────────────────────────────────────────────────────────────
    for ci_idx, city in enumerate(cities[:8]):
        cont_i = ci_idx % len(cont_data)
        cx3, cy3, rx3, ry3 = cont_data[cont_i]
        
        # Try to find an empty spot with generous padding
        for _ in range(50):
            px = cx3 + rng.uniform(-rx3 * 0.6, rx3 * 0.6)
            py = cy3 + rng.uniform(-ry3 * 0.6, ry3 * 0.6)
            # Extremely large padding to guarantee city names don't overlap danger names
            if not any(math.hypot(px - ex, py - ey) < 70 for (ex, ey) in placed_points):
                break
                
        placed_points.append((px, py))
        
        cc = colors['city']
        cg = colors['city_glow']
        # Glow ring
        lines.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="8" '
                     f'fill="#{cg}" opacity="0.25" filter="url(#glow)"/>')
        # Dot
        lines.append(f'<circle cx="{px:.0f}" cy="{py:.0f}" r="4" '
                     f'fill="#{cc}" stroke="white" stroke-width="1" opacity="0.95"/>')
        # City name with shadow
        cname = (city.get('name', '') if isinstance(city, dict) else str(city))
        cname = cname[:20]
        # Position label slightly above or below to avoid point overlap
        label_y_off = 14 if py < cy3 else -10
        lines.append(f'<text x="{px:.0f}" y="{py + label_y_off:.0f}" '
                     f'font-family="sans-serif" font-size="10" font-weight="bold" '
                     f'fill="black" stroke="black" stroke-width="2.5" '
                     f'text-anchor="middle" opacity="0.5">{cname}</text>')
        lines.append(f'<text x="{px:.0f}" y="{py + label_y_off:.0f}" '
                     f'font-family="sans-serif" font-size="10" font-weight="bold" '
                     f'fill="#{colors["text"]}" text-anchor="middle">{cname}</text>')

    # ── Compass Rose (bottom-right) ───────────────────────────────────────
    cx_c, cy_c = W - 55, H - 55
    cc2 = colors['compass']
    for ang, lbl in [(0, 'N'), (90, 'E'), (180, 'S'), (270, 'W')]:
        rad = math.radians(ang - 90)
        tx = cx_c + math.cos(rad) * 32
        ty = cy_c + math.sin(rad) * 32
        is_n = lbl == 'N'
        lines.append(f'<text x="{tx:.0f}" y="{ty + 4:.0f}" '
                     f'font-family="sans-serif" font-size="{11 if is_n else 9}" '
                     f'font-weight="bold" fill="#{cc2}" '
                     f'fill-opacity="{1.0 if is_n else 0.7}" '
                     f'text-anchor="middle">{lbl}</text>')
    lines.append(f'<circle cx="{cx_c}" cy="{cy_c}" r="18" '
                 f'fill="none" stroke="#{cc2}" stroke-width="1" opacity="0.5"/>')
    lines.append(f'<circle cx="{cx_c}" cy="{cy_c}" r="3" fill="#{cc2}" opacity="0.8"/>')

    # ── Title / legend ────────────────────────────────────────────────────
    tc = colors['text']
    lines.append(f'<text x="16" y="26" '
                 f'font-family="serif" font-size="16" font-weight="bold" '
                 f'fill="#{tc}" fill-opacity="0.9" letter-spacing="1">'
                 f'{world_name}</text>')
    lines.append(f'<text x="16" y="42" '
                 f'font-family="sans-serif" font-size="9" '
                 f'fill="#{tc}" fill-opacity="0.5" letter-spacing="2">'
                 f'WORLD MAP — {theme.upper()}</text>')

    # ── Border ────────────────────────────────────────────────────────────
    lines.append(f'<rect width="{W}" height="{H}" fill="none" '
                 f'stroke="#{tc}" stroke-width="1.5" stroke-opacity="0.2" '
                 f'rx="12"/>')

    lines.append('</svg>')
    return '\n'.join(lines)
