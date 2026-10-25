"""
Draws the 3x3 "which picture is missing?" puzzles as SVG files in img/matrix/.

You only need this if you want to change or add a picture puzzle.
Run it from the repo folder with:   python3 tools/make_matrices.py
It prints the correct letter for each puzzle, so you can copy it into
questions.yaml.

Each puzzle is 8 visible cells + the missing one (the answer), plus 5 wrong
options. A cell is a small dict describing what to draw, for example
  cell('circle', 'red', count=2, fill='striped')
"""

import json
import math
import os

OUT = os.path.join(os.path.dirname(__file__), '..', 'img', 'matrix')

COLORS = {
    'red': '#d64541', 'blue': '#2f6fd6', 'green': '#2e9e5b', 'yellow': '#f2c230',
    'orange': '#ef8a24', 'purple': '#8b4fc9', 'navy': '#24324a',
}

CELL, GAP, PAD = 96, 8, 16
GRID = 3 * CELL + 2 * GAP
WIDTH = GRID + 2 * PAD
LETTERS = 'ABCDEF'


def cell(shape, color='navy', fill='solid', count=1, size=1.0, rot=0, **extra):
    return dict(shape=shape, color=color, fill=fill, count=count, size=size, rot=rot, **extra)


# ---------------------------------------------------------------- drawing

def points(cx, cy, pts, rot):
    a = math.radians(rot)
    out = []
    for x, y in pts:
        rx, ry = x * math.cos(a) - y * math.sin(a), x * math.sin(a) + y * math.cos(a)
        out.append(f'{cx + rx:.1f},{cy + ry:.1f}')
    return ' '.join(out)


def regular(n, r, start=-90):
    return [(r * math.cos(math.radians(start + 360 * i / n)),
             r * math.sin(math.radians(start + 360 * i / n))) for i in range(n)]


def star(r):
    pts = []
    for i in range(10):
        rr = r if i % 2 == 0 else r * 0.45
        ang = math.radians(-90 + 36 * i)
        pts.append((rr * math.cos(ang), rr * math.sin(ang)))
    return pts


SIDES = {'triangle': 3, 'square': 4, 'pentagon': 5, 'hexagon': 6, 'heptagon': 7, 'octagon': 8}


def paint(color, fill):
    c = COLORS[color]
    if fill == 'solid':
        return f'fill="{c}" stroke="{c}" stroke-width="2" stroke-linejoin="round"'
    if fill == 'outline':
        return f'fill="#fff" stroke="{c}" stroke-width="4" stroke-linejoin="round"'
    if fill == 'striped':
        return f'fill="url(#stripe-{color})" stroke="{c}" stroke-width="3" stroke-linejoin="round"'
    raise ValueError(fill)


def shape_svg(shape, cx, cy, r, color, fill, rot=0):
    style = paint(color, fill)
    if shape == 'circle':
        return f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r * 0.9:.1f}" {style}/>'
    if shape == 'square':
        pts = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
        return f'<polygon points="{points(cx, cy, [(x * r * .8, y * r * .8) for x, y in pts], rot)}" {style}/>'
    if shape == 'diamond':
        return f'<polygon points="{points(cx, cy, regular(4, r, -90), rot)}" {style}/>'
    if shape == 'star':
        return f'<polygon points="{points(cx, cy, star(r * 1.05), rot)}" {style}/>'
    if shape == 'arrow':
        w = r
        pts = [(0, -w), (w * .8, -w * .1), (w * .3, -w * .1), (w * .3, w), (-w * .3, w), (-w * .3, -w * .1), (-w * .8, -w * .1)]
        return f'<polygon points="{points(cx, cy, pts, rot)}" {style}/>'
    if shape == 'triangle':
        return f'<polygon points="{points(cx, cy + r * .15, regular(3, r * 1.05), rot)}" {style}/>'
    if shape in SIDES:
        return f'<polygon points="{points(cx, cy, regular(SIDES[shape], r * .95), rot)}" {style}/>'
    raise ValueError(shape)


# where to put 1-6 copies of a shape inside a cell (offsets in px, and radius)
LAYOUTS = {
    1: ([(0, 0)], 34),
    2: ([(-18, 0), (18, 0)], 16),
    3: ([(-18, 15), (18, 15), (0, -16)], 15),
    4: ([(-18, -18), (18, -18), (-18, 18), (18, 18)], 15),
    5: ([(-20, -20), (20, -20), (0, 0), (-20, 20), (20, 20)], 11),
    6: ([(-24, -20), (0, -20), (24, -20), (-24, 20), (0, 20), (24, 20)], 11),
}

CORNERS = {'TL': (-17, -17), 'TR': (17, -17), 'BL': (-17, 17), 'BR': (17, 17)}
# the 8 border squares of a 3x3 mini grid, going clockwise from top-left
RING = [(-1, -1), (0, -1), (1, -1), (1, 0), (1, 1), (0, 1), (-1, 1), (-1, 0)]


def cell_svg(c, x, y):
    cx, cy = x + CELL / 2, y + CELL / 2
    s = c['shape']
    out = []
    if s == 'xor':  # four dot places, some filled
        for name, (dx, dy) in CORNERS.items():
            if name in c['dots']:
                out.append(f'<circle cx="{cx + dx}" cy="{cy + dy}" r="12" fill="{COLORS["navy"]}"/>')
            else:
                out.append(f'<circle cx="{cx + dx}" cy="{cy + dy}" r="12" fill="none" stroke="#d8d1c2" stroke-width="2"/>')
    elif s == 'quad':  # square with one quarter shaded
        h = 28
        qx = {'TL': -h, 'TR': 0, 'BR': 0, 'BL': -h}[c['q']]
        qy = {'TL': -h, 'TR': -h, 'BR': 0, 'BL': 0}[c['q']]
        out.append(f'<rect x="{cx + qx}" y="{cy + qy}" width="{h}" height="{h}" fill="{COLORS[c["color"]]}"/>')
        out.append(f'<rect x="{cx - h}" y="{cy - h}" width="{2 * h}" height="{2 * h}" fill="none" stroke="{COLORS["navy"]}" stroke-width="3"/>')
        out.append(f'<path d="M{cx} {cy - h}V{cy + h}M{cx - h} {cy}H{cx + h}" stroke="{COLORS["navy"]}" stroke-width="1.5"/>')
    elif s == 'inout':  # big outline shape with a small solid shape inside
        out.append(shape_svg(c['outer'], cx, cy, 38, 'navy', 'outline'))
        out.append(shape_svg(c['inner'], cx, cy, 13, c['color'], 'solid'))
    elif s == 'mini':  # 3x3 mini grid with a red and a blue dot
        g = 22
        for i in range(4):
            out.append(f'<line x1="{cx - 1.5 * g}" y1="{cy + (i - 1.5) * g}" x2="{cx + 1.5 * g}" y2="{cy + (i - 1.5) * g}" stroke="#b9b09c" stroke-width="1.5"/>')
            out.append(f'<line x1="{cx + (i - 1.5) * g}" y1="{cy - 1.5 * g}" x2="{cx + (i - 1.5) * g}" y2="{cy + 1.5 * g}" stroke="#b9b09c" stroke-width="1.5"/>')
        for color in ('red', 'blue'):
            gx, gy = RING[c[color]]
            out.append(f'<circle cx="{cx + gx * g}" cy="{cy + gy * g}" r="8" fill="{COLORS[color]}"/>')
    else:
        offsets, r = LAYOUTS[c['count']]
        for dx, dy in offsets:
            out.append(shape_svg(s, cx + dx, cy + dy, r * c['size'], c['color'], c['fill'], c['rot']))
    return '\n'.join(out)


def frame(x, y, missing=False):
    if missing:
        return (f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="10" fill="#fff4cf" stroke="#e7b84a" stroke-width="2.5" stroke-dasharray="6 5"/>'
                f'<text x="{x + CELL / 2}" y="{y + CELL / 2 + 16}" text-anchor="middle" font-size="46" font-weight="700" fill="#c9952b" font-family="Georgia, serif">?</text>')
    return f'<rect x="{x}" y="{y}" width="{CELL}" height="{CELL}" rx="10" fill="#fff" stroke="#d9d0bd" stroke-width="2"/>'


def render(grid, options):
    """grid: 9 cells (the last one is hidden). options: 6 cells in display order."""
    parts = []
    y0 = PAD
    for i, c in enumerate(grid):
        x = PAD + (i % 3) * (CELL + GAP)
        y = y0 + (i // 3) * (CELL + GAP)
        if i == 8:
            parts.append(frame(x, y, missing=True))
        else:
            parts.append(frame(x, y))
            parts.append(cell_svg(c, x, y))
    y1 = y0 + GRID + 34
    parts.append(f'<text x="{WIDTH / 2}" y="{y1 - 10}" text-anchor="middle" font-size="16" font-weight="700" fill="#5b6475" font-family="Nunito, system-ui, sans-serif">Which one goes in the ? square</text>')
    for i, c in enumerate(options):
        x = PAD + (i % 3) * (CELL + GAP)
        y = y1 + (i // 3) * (CELL + 30)
        parts.append(frame(x, y))
        parts.append(cell_svg(c, x, y))
        parts.append(f'<text x="{x + CELL / 2}" y="{y + CELL + 21}" text-anchor="middle" font-size="18" font-weight="800" fill="#1d2433" font-family="Nunito, system-ui, sans-serif">{LETTERS[i]}</text>')
    height = y1 + 2 * (CELL + 30) + PAD - 6
    defs = ''.join(
        f'<pattern id="stripe-{n}" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">'
        f'<rect width="7" height="7" fill="#fff"/><rect width="3.5" height="7" fill="{v}"/></pattern>'
        for n, v in COLORS.items())
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {WIDTH} {height}" width="{WIDTH}" height="{height}" role="img" aria-label="A 3 by 3 picture puzzle with one square missing and six options A to F">'
            f'<defs>{defs}</defs><rect width="{WIDTH}" height="{height}" rx="14" fill="#f6f0e2"/>\n'
            + '\n'.join(parts) + '\n</svg>\n')


# ---------------------------------------------------------------- the puzzles

def key(c):
    return json.dumps(c, sort_keys=True)


def build(name, grid, wrong, answer_at):
    assert len(grid) == 9 and len(wrong) == 5, name
    answer = grid[8]
    options = wrong[:answer_at] + [answer] + wrong[answer_at:]
    keys = [key(o) for o in options]
    assert len(set(keys)) == 6, f'{name}: two options are the same'
    assert keys.count(key(answer)) == 1, name
    with open(os.path.join(OUT, name + '.svg'), 'w') as f:
        f.write(render(grid, options))
    print(f'{name}: answer {LETTERS[answer_at]}')


def latin(row_items):
    """Turn [[a,b,c],[d,e,f],[g,h,i]] into a flat list of 9."""
    return [x for row in row_items for x in row]


C, S, T = 'circle', 'square', 'triangle'


def puzzles():
    # ---- Day 12
    shapes = [C, S, T]; cols = ['red', 'blue', 'green']
    g = [cell(shapes[r], cols[k]) for r in range(3) for k in range(3)]
    build('day12-easy', g, [cell(T, 'red'), cell(C, 'green'), cell(T, 'blue'), cell(S, 'green'), cell(T, 'green', 'outline')], 3)

    sh = [[C, S, T], [S, T, C], [T, C, S]]
    co = [['red', 'green', 'blue'], ['blue', 'red', 'green'], ['green', 'blue', 'red']]
    g = [cell(sh[r][k], co[r][k]) for r in range(3) for k in range(3)]
    build('day12-medium', g, [cell(C, 'red'), cell(S, 'blue'), cell(S, 'green'), cell(T, 'red'), cell(S, 'red', 'outline')], 1)

    rs = ['star', 'circle', 'diamond']; cs = ['purple', 'orange', 'blue']
    g = [cell(rs[r], cs[k], count=r + k + 1) for r in range(3) for k in range(3)]
    build('day12-hard', g, [cell('diamond', 'blue', count=4), cell('diamond', 'orange', count=5), cell('circle', 'blue', count=5),
                            cell('diamond', 'blue', count=6), cell('star', 'blue', count=5)], 4)

    # ---- Day 14
    rowcol = ['red', 'blue', 'green']
    g = [cell('arrow', rowcol[r], rot=90 * (r + k)) for r in range(3) for k in range(3)]  # last: rot 360 = up
    g[8]['rot'] = 0
    build('day14-easy', g, [cell('arrow', 'green', rot=90), cell('arrow', 'green', rot=180), cell('arrow', 'green', rot=270),
                            cell('arrow', 'red', rot=0), cell('arrow', 'blue', rot=0)], 2)

    rs = [S, C, 'star']; sizes = [0.5, 0.75, 1.0]
    fills = [['solid', 'striped', 'outline'], ['striped', 'outline', 'solid'], ['outline', 'solid', 'striped']]
    g = [cell(rs[r], 'purple', fills[r][k], size=sizes[k]) for r in range(3) for k in range(3)]
    build('day14-medium', g, [cell('star', 'purple', 'solid'), cell('star', 'purple', 'outline'), cell('star', 'purple', 'striped', size=0.5),
                              cell(C, 'purple', 'striped'), cell('star', 'purple', 'striped', size=0.75)], 5)

    rows = [[{'TL'}, {'TR', 'BL'}], [{'TL', 'BR'}, {'TL', 'TR'}], [{'TR', 'BL', 'BR'}, {'BL', 'TL'}]]
    g = []
    for a, b in rows:
        for d in (a, b, a ^ b):
            g.append(dict(shape='xor', dots=sorted(d)))
    x = lambda *d: dict(shape='xor', dots=sorted(d))
    build('day14-hard', g, [x('TL', 'TR', 'BL', 'BR'), x('BL'), x('TR', 'BR'), x('TL', 'TR', 'BL'), x('TL', 'BL', 'BR')], 0)

    # ---- Day 16
    rs = [S, C, T]; rc = ['red', 'blue', 'yellow']; sizes = [1.0, 0.72, 0.45]
    g = [cell(rs[r], rc[r], size=sizes[k]) for r in range(3) for k in range(3)]
    build('day16-easy', g, [cell(T, 'yellow'), cell(T, 'yellow', size=0.72), cell(C, 'yellow', size=0.45),
                            cell(T, 'red', size=0.45), cell(T, 'yellow', 'outline', size=0.45)], 4)

    names = {3: 'triangle', 4: 'square', 5: 'pentagon', 6: 'hexagon', 7: 'heptagon', 8: 'octagon'}
    cs = ['green', 'orange', 'blue']
    g = []
    for r in range(3):
        for k in range(3):
            n = 3 + r + k
            g.append(cell(names[n], cs[k]))
    build('day16-medium', g, [cell('hexagon', 'blue'), cell('octagon', 'blue'), cell('heptagon', 'orange'),
                              cell('pentagon', 'blue'), cell('heptagon', 'blue', 'outline')], 2)

    sh = [[C, S, T], [S, T, C], [T, C, S]]
    co = [['red', 'blue', 'green'], ['green', 'red', 'blue'], ['blue', 'green', 'red']]
    ct = [[1, 2, 3], [3, 1, 2], [2, 3, 1]]
    g = [cell(sh[r][k], co[r][k], count=ct[r][k]) for r in range(3) for k in range(3)]
    build('day16-hard', g, [cell(S, 'red', count=2), cell(S, 'green'), cell(C, 'red'), cell(S, 'red', count=3), cell(S, 'blue')], 1)

    # ---- Day 18
    co = [['red', 'blue', 'green'], ['blue', 'green', 'red'], ['green', 'red', 'blue']]
    g = [cell('star', co[r][k]) for r in range(3) for k in range(3)]
    build('day18-easy', g, [cell('star', 'red'), cell('star', 'green'), cell('star', 'yellow'), cell(C, 'blue'), cell('star', 'blue', 'outline')], 3)

    outer = ['circle', 'square', 'diamond']; inner = ['star', 'triangle', 'circle']
    io = lambda o, i: dict(shape='inout', outer=o, inner=i, color='red')
    g = [io(outer[r], inner[k]) for r in range(3) for k in range(3)]
    build('day18-medium', g, [io('diamond', 'star'), io('square', 'circle'), io('circle', 'diamond'), io('diamond', 'triangle'),
                              dict(shape='inout', outer='diamond', inner='circle', color='blue')], 0)

    rows = [('triangle', 'green', 1, 2), ('star', 'purple', 2, 2), ('hexagon', 'orange', 2, 3)]
    g = []
    for s, c, a, b in rows:
        g += [cell(s, c, count=a), cell(s, c, count=b), cell(s, c, count=a + b)]
    build('day18-hard', g, [cell('hexagon', 'orange', count=4), cell('hexagon', 'orange', count=6), cell('star', 'orange', count=5),
                            cell('hexagon', 'purple', count=5), cell('hexagon', 'orange', 'outline', count=5)], 2)

    # ---- Day 20
    order = ['TL', 'TR', 'BR', 'BL']
    q = lambda name, color='blue': dict(shape='quad', q=name, color=color)
    g = [q(order[i % 4]) for i in range(9)]
    build('day20-easy', g, [q('TR'), q('BR'), q('BL'), q('TL', 'red'), q('BR', 'red')], 0)

    mix = [('red', 'yellow', 'orange', C), ('blue', 'yellow', 'green', S), ('red', 'blue', 'purple', T)]
    g = []
    for a, b, m, s in mix:
        g += [cell(s, a), cell(s, b), cell(s, m)]
    build('day20-medium', g, [cell(T, 'green'), cell(T, 'orange'), cell(C, 'purple'), cell(T, 'red'), cell(T, 'blue')], 4)

    # red dot walks 1 step clockwise around the edge each square; blue walks 1 step anticlockwise
    mini = lambda r, b: dict(shape='mini', red=r % 8, blue=b % 8)
    g = [mini(k, 5 - k) for k in range(9)]
    build('day20-hard', g, [mini(0, 6), mini(1, 5), mini(0, 1), mini(5, 0), mini(7, 5)], 3)


if __name__ == '__main__':
    os.makedirs(OUT, exist_ok=True)
    puzzles()
