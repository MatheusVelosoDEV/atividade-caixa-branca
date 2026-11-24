"""Gera SVGs dos grafos do original. Nós e arestas são os dados-fonte."""
from html import escape
from pathlib import Path

OUT = Path(__file__).resolve().parent

GRAPHS = {
    "consultarQuantidade": {
        "size": (900, 900),
        "nodes": {
            1: (360, 55, "Entrada; quantidade = 0"),
            2: (360, 145, "try; abrir leitor"),
            3: (360, 240, "readLine() != null?"),
            4: (360, 335, "split(';')"),
            5: (360, 430, "colunas[0] == codigo?"),
            6: (360, 525, "parseInt(colunas[1])"),
            7: (360, 620, "break"),
            9: (720, 240, "catch IOException"),
            10: (360, 750, "return quantidade"),
            11: (360, 845, "Saída normal / abrupta"),
        },
        "edges": [
            (1, 2, "", [(360, 80), (360, 120)]),
            (2, 3, "normal", [(360, 170), (360, 215)]),
            (2, 9, "IOException", [(465, 145), (610, 145), (610, 220), (615, 220)]),
            (3, 4, "sim", [(360, 265), (360, 310)]),
            (3, 10, "não", [(255, 240), (95, 240), (95, 750), (255, 750)]),
            (3, 9, "IOException", [(465, 240), (615, 240)]),
            (4, 5, "", [(360, 360), (360, 405)]),
            (5, 6, "sim", [(360, 455), (360, 500)]),
            (5, 3, "não", [(255, 430), (175, 430), (175, 200), (255, 200), (255, 220)]),
            (6, 7, "normal", [(360, 550), (360, 595)]),
            (6, 11, "exceção não tratada", [(465, 525), (840, 525), (840, 845), (465, 845)]),
            (7, 10, "", [(360, 645), (360, 725)]),
            (9, 10, "", [(720, 265), (720, 700), (465, 700), (465, 750)]),
            (10, 11, "", [(360, 775), (360, 820)]),
        ],
    },
    "registrarSaida": {
        "size": (900, 840),
        "nodes": {
            1: (360, 55, "Entrada; consultarQuantidade"),
            2: (360, 160, "quantidade <= disponível?"),
            3: (360, 265, "try; abrir FileWriter"),
            4: (360, 365, "write(...)"),
            5: (360, 465, "ultimaMovimentacao = codigo"),
            6: (360, 565, "return true"),
            7: (710, 365, "catch IOException"),
            8: (710, 675, "return false"),
            9: (360, 785, "Saída normal / abrupta"),
        },
        "edges": [
            (1, 2, "normal", [(360, 80), (360, 135)]),
            (1, 9, "exceção propagada", [(255, 55), (105, 55), (105, 785), (255, 785)]),
            (2, 3, "sim", [(360, 185), (360, 240)]),
            (2, 8, "não", [(465, 160), (850, 160), (850, 675), (815, 675)]),
            (3, 4, "normal", [(360, 290), (360, 340)]),
            (3, 7, "IOException", [(465, 265), (580, 265), (580, 340), (605, 340)]),
            (4, 5, "normal", [(360, 390), (360, 440)]),
            (4, 7, "IOException", [(465, 365), (605, 365)]),
            (5, 6, "", [(360, 490), (360, 540)]),
            (6, 9, "", [(360, 590), (360, 760)]),
            (7, 8, "", [(710, 390), (710, 650)]),
            (8, 9, "", [(710, 700), (710, 735), (465, 735), (465, 785)]),
        ],
    },
}


def render(name, graph):
    width, height = graph["size"]
    nodes, edges = graph["nodes"], graph["edges"]
    assert all(a in nodes and b in nodes for a, b, _, _ in edges)
    assert len(edges) - len(nodes) + 2 == (6 if name == "consultarQuantidade" else 5)
    parts = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
             '<defs><marker id="arrow" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#263445"/></marker><marker id="error" markerWidth="8" markerHeight="8" refX="7" refY="4" orient="auto"><path d="M0,0 L8,4 L0,8 Z" fill="#ae3642"/></marker></defs>',
             '<rect width="100%" height="100%" fill="#ffffff"/>',
             f'<text x="20" y="25" font-family="Arial" font-size="18" font-weight="bold" fill="#172b4d">{name} — código original</text>']
    for a, b, label, points in edges:
        exceptional = "IOException" in label or "exceção" in label
        color = "#ae3642" if exceptional else "#263445"
        marker = "error" if exceptional else "arrow"
        data = " ".join(f"{x},{y}" for x, y in points)
        parts.append(f'<polyline points="{data}" fill="none" stroke="{color}" stroke-width="2" marker-end="url(#{marker})"/>')
        if label:
            x1, y1 = points[0]
            x2, y2 = points[1]
            x, y = (x1 + x2) / 2, (y1 + y2) / 2 - 7
            parts.append(f'<text x="{x}" y="{y}" text-anchor="middle" font-family="Arial" font-size="11" fill="{color}">{escape(label)}</text>')
    for number, (x, y, label) in nodes.items():
        fill = "#fff1f2" if number in (9, 7) and name == "registrarSaida" or number == 9 and name == "consultarQuantidade" else "#eaf2fb"
        parts.append(f'<rect x="{x-105}" y="{y-25}" width="210" height="50" rx="9" fill="{fill}" stroke="#326397" stroke-width="2"/>')
        parts.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" font-family="Arial" font-size="13" fill="#172b4d">{number}. {escape(label)}</text>')
    parts.append('</svg>')
    (OUT / (name + ".svg")).write_text("\n".join(parts), encoding="utf-8")
    print(f"{name}: N={len(nodes)}, E={len(edges)}, P=1, V={len(edges)-len(nodes)+2}")


if __name__ == "__main__":
    for name, graph in GRAPHS.items():
        render(name, graph)
