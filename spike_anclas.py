#!/usr/bin/env python3
"""spike_anclas.py — arnés de medición para R-03 (03_SPIKE_anclas.md).

No es código de producto. Prioridad única: que la medición sea correcta y
auditable. Toda decisión de diseño no trivial está anotada donde se toma,
con referencia a la sección de 03_SPIKE_anclas.md que la motiva.

Dependencias: diff-match-patch (pip) + stdlib. Nada más.
"""

import argparse
import bisect
import difflib
import hashlib
import html
import json
import os
import random
import re
import ssl
import sys
import unicodedata
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import asdict, dataclass, field
from typing import Dict, List, Optional, Set, Tuple

from diff_match_patch import diff_match_patch as DMP

# ---------------------------------------------------------------------------
# Constantes de diseño (no se leen de config: son las decisiones del spike)
# ---------------------------------------------------------------------------

# 03_SPIKE §4.6 — las dos trampas de la librería, no negociables.
def make_dmp() -> DMP:
    dmp = DMP()
    dmp.Diff_Timeout = 0     # sin esto, diff_main sobre una obra entera degrada en silencio
    dmp.Match_MaxBits = 0    # sin esto, match_main revienta: el patrón (prefijo+cita+sufijo) pasa de 32 chars siempre
    return dmp

# 08_RULES R-030 — "por debajo de umbral, huérfana; empate, huérfana". El
# epsilon de empate es una decisión de instrumento, no del producto: dos
# candidatos "empatan" si sus confianzas no se pueden distinguir de forma
# confiable con el ratio de difflib.
EMPATE_EPSILON = 0.02

# 03_SPIKE §2 — criterio de fracaso, textual, no inventado acá.
CRITERIO_FP_DESVIO_MAYOR_50_PCT = 1.0
CRITERIO_HUERFANAS_EVITABLES_PCT = 10.0

CATEGORIAS = [
    "migrada_bien",
    "migrada_mal_fp",
    "migrada_mal_ambiguedad",
    "huerfana_evitable",
    "huerfana_correcta",
    "migro_tocado",
]

ETIQUETAS = {
    "migrada_bien": "migrada bien",
    "migrada_mal_fp": "migrada mal (falso positivo)",
    "migrada_mal_ambiguedad": "migrada mal por ambigüedad literal",
    "huerfana_evitable": "huérfana evitable",
    "huerfana_correcta": "huérfana correcta",
    "migro_tocado": "migró en caso tocado",
}


# ---------------------------------------------------------------------------
# BLOQUE 1 — verdad de campo (03_SPIKE §4.1)
# ---------------------------------------------------------------------------

def build_char_map(text_a: str, text_b: str, dmp: DMP) -> List[Optional[int]]:
    """Mapa carácter a carácter de A -> B.

    Derivado de diff_main SIN diff_cleanupSemantic: la limpieza semántica
    agrupa ediciones para que un humano las lea mejor y al hacerlo destruye
    la correspondencia carácter a carácter (03_SPIKE §4.1). No se llama acá
    a propósito.
    """
    diffs = dmp.diff_main(text_a, text_b)
    char_map: List[Optional[int]] = [None] * len(text_a)
    a_pos = 0
    b_pos = 0
    for op, data in diffs:
        length = len(data)
        if op == dmp.DIFF_EQUAL:
            for i in range(length):
                char_map[a_pos + i] = b_pos + i
            a_pos += length
            b_pos += length
        elif op == dmp.DIFF_DELETE:
            a_pos += length
        elif op == dmp.DIFF_INSERT:
            b_pos += length
    return char_map


# ---------------------------------------------------------------------------
# BLOQUE 2 — bloques e identificadores (03_SPIKE §4.2)
# ---------------------------------------------------------------------------

def normalize_text(s: str) -> str:
    """Unicode NFC, saltos de línea uniformes, sin espacios colgando."""
    s = unicodedata.normalize("NFC", s)
    s = s.replace("\r\n", "\n").replace("\r", "\n")
    s = "\n".join(line.rstrip() for line in s.split("\n"))
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip("\n")


@dataclass
class Block:
    id: Optional[str]
    order: int
    start: int  # offset global en el texto de SU versión
    end: int
    text: str
    hash: str


def _hash_block(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def split_blocks(text: str) -> List[Block]:
    """Partición por párrafo (una o más líneas en blanco separan bloques)."""
    seps = list(re.finditer(r"\n\s*\n+", text))
    bounds = []
    start = 0
    for m in seps:
        bounds.append((start, m.start()))
        start = m.end()
    bounds.append((start, len(text)))

    blocks: List[Block] = []
    for s, e in bounds:
        t = text[s:e]
        if t.strip() == "":
            continue
        blocks.append(Block(id=None, order=len(blocks), start=s, end=e, text=t, hash=_hash_block(t)))
    return blocks


def assign_ids(blocks: List[Block], prefix: str = "b") -> None:
    """Ids opacos, asignados una vez sobre A. Nunca derivados de la posición
    en el sentido prohibido por I-IB-2: son un contador opaco, no una
    coordenada (capitulo-3-parrafo-14 sería la prohibición; b0001 como mera
    etiqueta de asignación-única no lo es, porque nunca se reusa ni se
    recalcula al insertar un bloque nuevo)."""
    for i, b in enumerate(blocks, start=1):
        b.id = f"{prefix}{i:04d}"


def align_blocks(blocks_a: List[Block], blocks_b: List[Block]) -> None:
    """Transporta ids de A a B por alineación (03_SPIKE §4.2 / I-IB-3).

    Paso 1 — hash exacto: SequenceMatcher sobre la secuencia de hashes,
    que encuentra las corridas contiguas idénticas sin ambigüedad.
    Paso 2 — similitud: dentro de cada tramo no resuelto por hash (un
    'replace' de difflib), empareja por similitud de texto (ratio) los
    bloques que sobrevivieron editados.
    Un bloque de B que no se pudo emparejar es nuevo: recibe un id nuevo
    que nunca se reusa (I-IB-1).
    """
    a_hashes = [b.hash for b in blocks_a]
    b_hashes = [b.hash for b in blocks_b]
    sm = difflib.SequenceMatcher(a=a_hashes, b=b_hashes, autojunk=False)

    id_of_b: List[Optional[str]] = [None] * len(blocks_b)

    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for k in range(i2 - i1):
                id_of_b[j1 + k] = blocks_a[i1 + k].id

    SIM_THRESHOLD = 0.6
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            continue
        a_cands = list(range(i1, i2))
        b_cands = [j for j in range(j1, j2) if id_of_b[j] is None]
        pairs = []
        for ai in a_cands:
            for bj in b_cands:
                ratio = difflib.SequenceMatcher(None, blocks_a[ai].text, blocks_b[bj].text, autojunk=False).ratio()
                pairs.append((ratio, ai, bj))
        pairs.sort(key=lambda x: -x[0])
        used_a: Set[int] = set()
        used_b: Set[int] = set()
        for ratio, ai, bj in pairs:
            if ratio < SIM_THRESHOLD:
                break
            if ai in used_a or bj in used_b:
                continue
            used_a.add(ai)
            used_b.add(bj)
            id_of_b[bj] = blocks_a[ai].id

    next_num = len(blocks_a) + 1
    for j, b in enumerate(blocks_b):
        if id_of_b[j] is None:
            b.id = f"n{next_num:04d}"
            next_num += 1
        else:
            b.id = id_of_b[j]


def find_block(blocks: List[Block], offset: int) -> Block:
    starts = [b.start for b in blocks]
    idx = bisect.bisect_right(starts, offset) - 1
    if idx < 0:
        idx = 0
    return blocks[idx]


# ---------------------------------------------------------------------------
# BLOQUE 3 — anclas
# ---------------------------------------------------------------------------

@dataclass
class Anchor:
    idx: int
    start: int
    end: int
    block_inicio_id: str
    offset_inicio: int
    block_fin_id: str
    offset_fin: int
    cruza_bloques: bool
    prefijo: str
    cita: str
    sufijo: str
    tipo_generacion: str


def build_anchor(blocks_a: List[Block], text_a: str, start: int, end: int, contexto: int, tipo: str, idx: int) -> Anchor:
    b_ini = find_block(blocks_a, start)
    b_fin = find_block(blocks_a, max(start, end - 1))
    return Anchor(
        idx=idx,
        start=start,
        end=end,
        block_inicio_id=b_ini.id,
        offset_inicio=start - b_ini.start,
        block_fin_id=b_fin.id,
        offset_fin=end - b_fin.start,
        cruza_bloques=(b_ini.id != b_fin.id),
        prefijo=text_a[max(0, start - contexto):start],
        cita=text_a[start:end],
        sufijo=text_a[end:end + contexto],
        tipo_generacion=tipo,
    )


VOCAB_HUMO = [
    "la", "casa", "el", "gato", "dijo", "noche", "camino", "luz", "tiempo", "agua",
    "mano", "puerta", "viento", "sombra", "mesa", "libro", "ojos", "voz", "silencio", "calle",
]


def _pick_single_word(text_a: str, block: Block, rng: random.Random) -> Optional[Tuple[int, int]]:
    words = list(re.finditer(r"\b\w+\b", block.text))
    if not words:
        return None
    w = rng.choice(words)
    return block.start + w.start(), block.start + w.end()


def _pick_half_sentence(block: Block, rng: random.Random) -> Optional[Tuple[int, int]]:
    sentences = re.split(r"(?<=[.!?])\s+", block.text)
    candidatas = [s for s in sentences if len(s) > 10]
    if not candidatas:
        return None
    s = rng.choice(candidatas)
    local_start = block.text.find(s)
    if local_start < 0:
        return None
    half_len = max(5, len(s) // 2)
    max_off = max(0, len(s) - half_len)
    local_off = rng.randint(0, max_off)
    start = block.start + local_start + local_off
    return start, start + half_len


def _pick_repeated_fragment(text_a: str, rng: random.Random) -> Optional[Tuple[int, int]]:
    from collections import Counter
    words = re.findall(r"\b\w+\b", text_a)
    freq = Counter(w.lower() for w in words if len(w) >= 3)
    common = [w for w, c in freq.items() if c >= 3]
    if not common:
        return None
    word = rng.choice(common)
    occ = [m.span() for m in re.finditer(r"\b" + re.escape(word) + r"\b", text_a, re.IGNORECASE)]
    if len(occ) < 2:
        return None
    return rng.choice(occ)


def _pick_cross_block(blocks: List[Block], idx: int, rng: random.Random) -> Optional[Tuple[int, int]]:
    b1, b2 = blocks[idx], blocks[idx + 1]
    if len(b1.text) < 5 or len(b2.text) < 5:
        return None
    tail_len = rng.randint(5, min(20, len(b1.text)))
    head_len = rng.randint(5, min(20, len(b2.text)))
    return b1.end - tail_len, b2.start + head_len


def _pick_random_span(block: Block, rng: random.Random, min_len=3, max_len=80) -> Optional[Tuple[int, int]]:
    L = len(block.text)
    if L < min_len:
        return None
    length = rng.randint(min_len, min(max_len, L))
    start_local = rng.randint(0, L - length)
    return block.start + start_local, block.start + start_local + length


def generate_anchors(
    text_a: str,
    blocks_a: List[Block],
    n: int,
    seed: int,
    contexto: int,
    dificiles_ids: Set[str],
) -> List[Anchor]:
    """Genera anclas de prueba, cargadas a propósito de casos difíciles
    (02_RISKS §R-03 paso 3): palabra única, media frase, fragmento repetido
    (ambigüedad literal), fragmento a caballo de dos bloques, y una cuota
    alta dentro de los bloques que efectivamente cambiaron ('tocado').

    `dificiles_ids` es la unión de bloques editados y bloques borrados: los
    dos casos en los que "efectivamente cambió" algo entre A y B. Sesgar
    sólo hacia los editados dejaría casi sin cobertura la huérfana correcta
    (03_SPIKE §4.3), que es justamente el caso de los bloques borrados.
    """
    rng = random.Random(seed)
    estrategias = ["palabra", "media_frase", "repetido", "cruce", "tocado", "normal"]
    pesos = [0.15, 0.20, 0.15, 0.15, 0.20, 0.15]

    pool_tocado = [b for b in blocks_a if b.id in dificiles_ids]

    anchors: List[Anchor] = []
    intentos = 0
    max_intentos = max(2000, n * 80)
    while len(anchors) < n and intentos < max_intentos:
        intentos += 1
        estrategia = rng.choices(estrategias, weights=pesos, k=1)[0]
        span = None
        if estrategia == "palabra":
            b = rng.choice(blocks_a)
            span = _pick_single_word(text_a, b, rng)
        elif estrategia == "media_frase":
            b = rng.choice(blocks_a)
            span = _pick_half_sentence(b, rng)
        elif estrategia == "repetido":
            span = _pick_repeated_fragment(text_a, rng)
        elif estrategia == "cruce":
            if len(blocks_a) < 2:
                continue
            i = rng.randint(0, len(blocks_a) - 2)
            span = _pick_cross_block(blocks_a, i, rng)
        elif estrategia == "tocado":
            b = rng.choice(pool_tocado) if pool_tocado else rng.choice(blocks_a)
            span = _pick_random_span(b, rng)
        else:
            b = rng.choice(blocks_a)
            span = _pick_random_span(b, rng)

        if span is None:
            continue
        start, end = span
        if start < 0 or end > len(text_a) or start >= end:
            continue
        anchors.append(build_anchor(blocks_a, text_a, start, end, contexto, estrategia, len(anchors)))

    return anchors


# ---------------------------------------------------------------------------
# BLOQUE 4 — reanclaje
# ---------------------------------------------------------------------------

@dataclass
class ReanchorResult:
    estado: str            # 'migrada' | 'huerfana'
    metodo: str            # 'posicion' | 'difusa'
    confianza: float
    empate: bool
    intento_posicion_aplicable: bool
    pred_start: Optional[int]
    pred_end: Optional[int]
    nota: str


def _find_all_literal(haystack: str, needle: str) -> List[int]:
    positions = []
    start = 0
    while True:
        idx = haystack.find(needle, start)
        if idx == -1:
            break
        positions.append(idx)
        start = idx + 1
    return positions


def reanchor(
    anchor: Anchor,
    text_b: str,
    len_text_a: int,
    id_to_block_b: Dict[str, Block],
    stable_ids: Set[str],
    dmp: DMP,
    umbral: float,
) -> ReanchorResult:
    # Paso 1 (03_SPIKE §6 / R-029): posición transportada por el id de
    # bloque, sólo válida si el/los bloque(s) no cambiaron de hash.
    posicion_aplicable = anchor.block_inicio_id in stable_ids and anchor.block_fin_id in stable_ids
    if posicion_aplicable:
        b_ini = id_to_block_b[anchor.block_inicio_id]
        pred_start = b_ini.start + anchor.offset_inicio
        pred_end = pred_start + (anchor.end - anchor.start)
        return ReanchorResult(
            estado="migrada", metodo="posicion", confianza=1.0, empate=False,
            intento_posicion_aplicable=True, pred_start=pred_start, pred_end=pred_end,
            nota="bloque(s) sin cambio de hash: offset transportado tal cual",
        )

    # Paso 2: concordancia difusa sobre prefijo+cita+sufijo (match_main).
    needle = anchor.prefijo + anchor.cita + anchor.sufijo

    exactas = _find_all_literal(text_b, needle)
    if len(exactas) == 1:
        idx = exactas[0]
        pred_start = idx + len(anchor.prefijo)
        pred_end = pred_start + len(anchor.cita)
        return ReanchorResult(
            estado="migrada", metodo="difusa", confianza=1.0, empate=False,
            intento_posicion_aplicable=False, pred_start=pred_start, pred_end=pred_end,
            nota="coincidencia exacta y única de prefijo+cita+sufijo",
        )
    if len(exactas) > 1:
        # Empate real entre >=2 candidatos idénticos al patrón completo.
        # R-030 / I-MI-3: ante empate, huérfana. (Distinto de la
        # "ambigüedad literal" de clasificación, que compara sólo la cita
        # contra la verdad de campo, no el patrón completo con contexto.)
        return ReanchorResult(
            estado="huerfana", metodo="difusa", confianza=1.0, empate=True,
            intento_posicion_aplicable=False, pred_start=None, pred_end=None,
            nota=f"{len(exactas)} coincidencias exactas idénticas del patrón completo",
        )

    if anchor.block_inicio_id in id_to_block_b:
        b = id_to_block_b[anchor.block_inicio_id]
        loc_hint = min(max(0, b.start + anchor.offset_inicio), max(0, len(text_b) - 1))
    else:
        loc_hint = int(anchor.start / len_text_a * len(text_b)) if len_text_a else 0
        loc_hint = min(max(0, loc_hint), max(0, len(text_b) - 1))

    idx1 = dmp.match_main(text_b, needle, loc_hint)
    if idx1 == -1:
        return ReanchorResult(
            estado="huerfana", metodo="difusa", confianza=0.0, empate=False,
            intento_posicion_aplicable=False, pred_start=None, pred_end=None,
            nota="match_main sin candidato dentro del umbral interno de la librería",
        )

    ventana1 = text_b[idx1: idx1 + len(needle)]
    conf1 = difflib.SequenceMatcher(None, needle, ventana1).ratio()

    # Chequeo de empate: enmascarar la región encontrada y volver a buscar.
    fin_repl = min(idx1 + len(needle), len(text_b))
    repl_len = fin_repl - idx1
    masked = text_b[:idx1] + ("\x00" * repl_len) + text_b[fin_repl:]
    idx2 = dmp.match_main(masked, needle, loc_hint)
    empate = False
    if idx2 != -1:
        ventana2 = masked[idx2: idx2 + len(needle)]
        conf2 = difflib.SequenceMatcher(None, needle, ventana2).ratio()
        if abs(conf1 - conf2) < EMPATE_EPSILON:
            empate = True

    if empate:
        return ReanchorResult(
            estado="huerfana", metodo="difusa", confianza=conf1, empate=True,
            intento_posicion_aplicable=False, pred_start=None, pred_end=None,
            nota="empate entre dos candidatos difusos de confianza indistinguible",
        )

    if conf1 < umbral:
        return ReanchorResult(
            estado="huerfana", metodo="difusa", confianza=conf1, empate=False,
            intento_posicion_aplicable=False, pred_start=None, pred_end=None,
            nota=f"confianza {conf1:.3f} < umbral {umbral}",
        )

    pred_start = idx1 + len(anchor.prefijo)
    pred_end = pred_start + len(anchor.cita)
    return ReanchorResult(
        estado="migrada", metodo="difusa", confianza=conf1, empate=False,
        intento_posicion_aplicable=False, pred_start=pred_start, pred_end=pred_end,
        nota="match difuso sobre prefijo+cita+sufijo",
    )


# ---------------------------------------------------------------------------
# BLOQUE 5 — clasificación contra la verdad de campo
# ---------------------------------------------------------------------------

def _existio_en_b(anchor: Anchor, char_map: List[Optional[int]]) -> Tuple[bool, Optional[int]]:
    mapped = [char_map[i] for i in range(anchor.start, anchor.end)]
    if not mapped or any(m is None for m in mapped):
        return False, None
    for i in range(len(mapped) - 1):
        if mapped[i + 1] != mapped[i] + 1:
            return False, None
    return True, mapped[0]


def _es_ambiguedad_literal(anchor: Anchor, text_b: str, pred_start: Optional[int]) -> bool:
    if pred_start is None:
        return False
    L = len(anchor.cita)
    candidata = text_b[pred_start:pred_start + L]
    if candidata != anchor.cita:
        return False
    return len(_find_all_literal(text_b, anchor.cita)) > 1


def _bucket_desvio(dev: int) -> str:
    if dev <= 5:
        return "≤5"
    if dev <= 50:
        return "6–50"
    return ">50"


def classify(
    anchor: Anchor,
    char_map: List[Optional[int]],
    text_b: str,
    r: ReanchorResult,
    tocado_ids: Set[str],
) -> Tuple[str, Optional[int], bool, Optional[int]]:
    """Devuelve (categoria, desvio_en_chars_o_None, existio_en_b, true_start_b)."""
    existio, true_start = _existio_en_b(anchor, char_map)
    tocado = anchor.block_inicio_id in tocado_ids or anchor.block_fin_id in tocado_ids

    if not existio:
        if r.estado == "huerfana":
            return "huerfana_correcta", None, existio, true_start
        if _es_ambiguedad_literal(anchor, text_b, r.pred_start):
            return "migrada_mal_ambiguedad", None, existio, true_start
        return "migrada_mal_fp", None, existio, true_start

    # existio == True
    if r.estado == "huerfana":
        return "huerfana_evitable", None, existio, true_start

    dev = abs(r.pred_start - true_start)
    if dev == 0:
        return ("migro_tocado" if tocado else "migrada_bien"), 0, existio, true_start

    if _es_ambiguedad_literal(anchor, text_b, r.pred_start):
        return "migrada_mal_ambiguedad", dev, existio, true_start
    return "migrada_mal_fp", dev, existio, true_start


# ---------------------------------------------------------------------------
# BLOQUE 7 — salida (resumen, tabla, JSON) — definido antes de "correr"
# porque run_experiment lo usa.
# ---------------------------------------------------------------------------

def summarize(records: List[dict]) -> dict:
    """03_SPIKE §1: un ancla migrada cuyo texto no existía en B (existio_en_b
    False) no tiene un desvío nulo, tiene un desvío no medible por arriba —
    el reanclaje difuso la migró igual, con confianza alta, sobre un pasaje
    que no está. Excluirla del histograma y del criterio de fracaso (como
    hacía la versión anterior, filtrando por `desvio is not None`) es la
    falla de contabilidad que 03_SPIKE §1 llama "la única que decide": el
    arnés reportaba CUMPLE con anclas colgadas de un pasaje inexistente.
    Estas anclas van al bucket ">50" y, si son falsos positivos, cuentan en
    fp_desvio_mayor_50 igual que un desvío medido y grande.
    """
    n = len(records)
    conteos = {c: 0 for c in CATEGORIAS}
    hist = {"≤5": 0, "6–50": 0, ">50": 0}
    cruza = 0
    fp_desvio_mayor_50 = 0
    sobre_texto_inexistente_en_b = {"migrada_mal_fp": 0, "migrada_mal_ambiguedad": 0}

    for r in records:
        conteos[r["categoria"]] += 1
        if r["cruza_bloques"]:
            cruza += 1
        if r["categoria"] in ("migrada_mal_fp", "migrada_mal_ambiguedad"):
            if r["desvio"] is not None:
                hist[_bucket_desvio(r["desvio"])] += 1
            else:
                hist[">50"] += 1
                sobre_texto_inexistente_en_b[r["categoria"]] += 1
        if r["categoria"] == "migrada_mal_fp":
            if (r["desvio"] is not None and r["desvio"] > 50) or r["desvio"] is None:
                fp_desvio_mayor_50 += 1

    hist_total = hist["≤5"] + hist["6–50"] + hist[">50"]
    esperado = conteos["migrada_mal_fp"] + conteos["migrada_mal_ambiguedad"]
    assert hist_total == esperado, (
        f"histograma de desvío ({hist_total}) no cierra contra "
        f"migrada_mal_fp + migrada_mal_ambiguedad ({esperado}): "
        "quedó alguna ancla migrada_mal_* fuera del histograma"
    )

    porcentajes = {c: (round(100 * conteos[c] / n, 2) if n else 0.0) for c in CATEGORIAS}
    fp_pct = round(100 * fp_desvio_mayor_50 / n, 2) if n else 0.0
    evitable_pct = porcentajes["huerfana_evitable"]

    return {
        "n": n,
        "conteos": conteos,
        "porcentajes": porcentajes,
        "histograma_desvio_migraciones_malas": hist,
        "sobre_texto_inexistente_en_b": sobre_texto_inexistente_en_b,
        "anclas_cruzan_bloques": cruza,
        "criterio_fracaso": {
            "fp_desvio_mayor_50_pct": fp_pct,
            "fp_desvio_mayor_50_umbral_pct": CRITERIO_FP_DESVIO_MAYOR_50_PCT,
            "fp_desvio_mayor_50_cumple": fp_pct <= CRITERIO_FP_DESVIO_MAYOR_50_PCT,
            "huerfanas_evitables_pct": evitable_pct,
            "huerfanas_evitables_umbral_pct": CRITERIO_HUERFANAS_EVITABLES_PCT,
            "huerfanas_evitables_cumple": evitable_pct <= CRITERIO_HUERFANAS_EVITABLES_PCT,
        },
    }


def format_table(summary: dict) -> str:
    n = summary["n"]
    lines = ["| Resultado | n | % |", "|---|---|---|"]
    for cat in CATEGORIAS:
        label = ETIQUETAS[cat]
        if cat == "migrada_mal_fp":
            label = f"**{label}**"
        lines.append(f"| {label} | {summary['conteos'][cat]} | {summary['porcentajes'][cat]}% |")
        if cat in ("migrada_mal_fp", "migrada_mal_ambiguedad"):
            sub_n = summary["sobre_texto_inexistente_en_b"][cat]
            sub_pct = round(100 * sub_n / n, 2) if n else 0.0
            lines.append(
                f"| &nbsp;&nbsp;de las cuales, sobre texto inexistente en B | {sub_n} | {sub_pct}% |"
            )
    return "\n".join(lines)


def format_reporte(result: dict) -> str:
    meta = result.get("meta", {})
    estructura = result["estructura"]
    resumen = result["resumen"]
    hist = resumen["histograma_desvio_migraciones_malas"]
    cf = resumen["criterio_fracaso"]

    out = []
    out.append("| | |")
    out.append("|---|---|")
    out.append(f"| Obra | {meta.get('obra', '[desconocida]')} |")
    out.append(f"| Revisiones (A → A+k) | {meta.get('revisiones', '[desconocido]')} |")
    out.append(f"| Comentario de edición | {meta.get('comentario', '[desconocido]')} |")
    out.append(
        f"| Bloques totales / cambiados / perdidos | "
        f"{estructura['bloques_totales_a']} / {estructura['bloques_cambiados']} / {estructura['bloques_perdidos']} |"
    )
    out.append(f"| Anclas generadas | {resumen['n']} |")
    out.append(f"| Umbral de confianza | {result['parametros']['umbral']} |")
    out.append("")
    out.append(format_table(resumen))
    out.append("")
    out.append(f"Desvío de las migraciones malas: `≤5 chars {hist['≤5']} / 6–50 {hist['6–50']} / >50 {hist['>50']}`")
    out.append(f"Anclas que cruzan bloques (ventana de dos bloques, 03_SPIKE §4.5): {resumen['anclas_cruzan_bloques']}")
    out.append("")
    out.append(
        f"Criterio de fracaso — FP con desvío >50: {cf['fp_desvio_mayor_50_pct']}% "
        f"(umbral ≤{cf['fp_desvio_mayor_50_umbral_pct']}%) -> "
        f"{'CUMPLE' if cf['fp_desvio_mayor_50_cumple'] else 'NO CUMPLE'}"
    )
    out.append(
        f"Criterio de fracaso — huérfanas evitables: {cf['huerfanas_evitables_pct']}% "
        f"(umbral ≤{cf['huerfanas_evitables_umbral_pct']}%) -> "
        f"{'CUMPLE' if cf['huerfanas_evitables_cumple'] else 'NO CUMPLE'}"
    )
    return "\n".join(out)


def write_json(path: str, data: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Orquestación de un experimento completo (usado por humo, correr, barrido)
# ---------------------------------------------------------------------------

def run_experiment(text_a_raw: str, text_b_raw: str, n: int, umbral: float, seed: int, contexto: int) -> dict:
    text_a = normalize_text(text_a_raw)
    text_b = normalize_text(text_b_raw)

    dmp = make_dmp()
    char_map = build_char_map(text_a, text_b, dmp)

    blocks_a = split_blocks(text_a)
    assign_ids(blocks_a)
    blocks_b = split_blocks(text_b)
    align_blocks(blocks_a, blocks_b)

    id_to_block_a = {b.id: b for b in blocks_a}
    id_to_block_b = {b.id: b for b in blocks_b}

    stable_ids = {i for i in id_to_block_a if i in id_to_block_b and id_to_block_a[i].hash == id_to_block_b[i].hash}
    tocado_ids = {i for i in id_to_block_a if i in id_to_block_b and id_to_block_a[i].hash != id_to_block_b[i].hash}
    perdido_ids = {i for i in id_to_block_a if i not in id_to_block_b}
    nuevo_ids_b = {b.id for b in blocks_b if b.id not in id_to_block_a}

    anchors = generate_anchors(text_a, blocks_a, n, seed, contexto, tocado_ids | perdido_ids)

    records = []
    for a in anchors:
        r = reanchor(a, text_b, len(text_a), id_to_block_b, stable_ids, dmp, umbral)
        categoria, desvio, existio, true_start = classify(a, char_map, text_b, r, tocado_ids)
        records.append({
            "idx": a.idx,
            "block_inicio_id": a.block_inicio_id,
            "offset_inicio": a.offset_inicio,
            "block_fin_id": a.block_fin_id,
            "offset_fin": a.offset_fin,
            "cruza_bloques": a.cruza_bloques,
            "tipo_generacion": a.tipo_generacion,
            "prefijo": a.prefijo,
            "cita": a.cita,
            "sufijo": a.sufijo,
            "existio_en_b": existio,
            "true_start_b": true_start,
            "reanclaje": asdict(r),
            "categoria": categoria,
            "desvio": desvio,
        })

    resumen = summarize(records)

    return {
        "anclas": records,
        "resumen": resumen,
        "estructura": {
            "bloques_totales_a": len(blocks_a),
            "bloques_totales_b": len(blocks_b),
            "bloques_cambiados": len(tocado_ids),
            "bloques_perdidos": len(perdido_ids),
            "bloques_nuevos_en_b": len(nuevo_ids_b),
        },
    }


# ---------------------------------------------------------------------------
# BLOQUE 6 — CLI: humo
# ---------------------------------------------------------------------------

def _apply_edit_humo(paragraph: str, rng: random.Random) -> str:
    original = paragraph
    for _ in range(10):
        words = original.split(" ")
        if len(words) < 2:
            return original + " extra."
        pos = rng.randrange(len(words))
        choice = rng.random()
        candidate = list(words)
        if choice < 0.4:
            candidate[pos] = rng.choice(VOCAB_HUMO)
        elif choice < 0.7:
            candidate.insert(pos, rng.choice(VOCAB_HUMO))
        elif len(candidate) > 3:
            del candidate[pos]
        else:
            candidate[pos] = rng.choice(VOCAB_HUMO)
        joined = " ".join(candidate)
        if joined != original:
            return joined
    return original + " cambiado."


def build_humo_textos(seed: int) -> Tuple[str, str, dict]:
    """Texto sintético con erratas fabricadas (03_SPIKE §2, humo).

    Vocabulario de veinte palabras a propósito: es el peor caso para el
    selector de contexto (mucha ambigüedad literal) y el mejor para la
    alineación de bloques por hash. Calibra el instrumento, no mide R-03.
    """
    rng = random.Random(seed)

    def gen_sentence() -> str:
        n = rng.randint(5, 12)
        words = [rng.choice(VOCAB_HUMO) for _ in range(n)]
        s = " ".join(words)
        return s[0:1].upper() + s[1:] + "."

    def gen_paragraph() -> str:
        n = rng.randint(2, 5)
        return " ".join(gen_sentence() for _ in range(n))

    paragraphs = [gen_paragraph() for _ in range(60)]
    text_a = "\n\n".join(paragraphs)

    deleted_idx = set(rng.sample(range(60), 3))
    remaining = [i for i in range(60) if i not in deleted_idx]
    changed_idx = set(rng.sample(remaining, 9))

    paragraphs_b = []
    for i, p in enumerate(paragraphs):
        if i in deleted_idx:
            continue
        if i in changed_idx:
            paragraphs_b.append(_apply_edit_humo(p, rng))
        else:
            paragraphs_b.append(p)

    insert_pos = rng.randint(0, len(paragraphs_b))
    paragraphs_b.insert(insert_pos, gen_paragraph())

    text_b = "\n\n".join(paragraphs_b)

    ficha = {
        "bloques_generados_esperado": 60,
        "bloques_cambiados_esperado": 9,
        "bloques_borrados_esperado": 3,
        "parrafos_insertados_esperado": 1,
    }
    return text_a, text_b, ficha


def cmd_humo(args: argparse.Namespace) -> None:
    text_a, text_b, ficha = build_humo_textos(args.semilla)
    result = run_experiment(text_a, text_b, n=200, umbral=0.75, seed=args.semilla, contexto=args.contexto)
    result["meta"] = {
        "obra": "texto sintético (humo) — calibración del instrumento, NO mide R-03",
        "revisiones": "A (generada) -> B (con erratas fabricadas)",
        "comentario": "n/a: no hay edición humana real",
    }
    result["parametros"] = {"n": 200, "umbral": 0.75, "semilla": args.semilla, "contexto": args.contexto}
    result["ficha_generacion_humo"] = ficha
    write_json(args.json, result)

    e = result["estructura"]
    print("=== PRUEBA DE HUMO — calibra el instrumento, no mide nada del proyecto (03_SPIKE §2) ===\n")
    print(format_reporte(result))
    print()
    print(
        "Verificación de construcción vs. lo detectado por align_blocks: "
        f"generados 60 (medidos {e['bloques_totales_a']}), "
        f"cambiados esperados 9 (detectados por hash {e['bloques_cambiados']}), "
        f"borrados esperados 3 (detectados {e['bloques_perdidos']}), "
        f"párrafo insertado esperado 1 (nuevos en B detectados {e['bloques_nuevos_en_b']})."
    )
    print(f"\nJSON completo en: {args.json}")


# ---------------------------------------------------------------------------
# BLOQUE 6 — CLI: traer (Wikisource real)
# ---------------------------------------------------------------------------

CA_BUNDLE_CANDIDATES = ["/root/.ccr/ca-bundle.crt"]


def _ssl_context() -> ssl.SSLContext:
    for path in CA_BUNDLE_CANDIDATES:
        if os.path.exists(path):
            return ssl.create_default_context(cafile=path)
    return ssl.create_default_context()


def http_get_json(url: str, params: dict) -> dict:
    qs = urllib.parse.urlencode(params)
    full = f"{url}?{qs}"
    req = urllib.request.Request(full, headers={"User-Agent": "artHUB-spike-anclas/0.1 (investigacion R-03, ver CLAUDE.md del repo)"})
    with urllib.request.urlopen(req, context=_ssl_context(), timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def get_revision_list(site: str, titulo: str, want_at_least: int) -> List[dict]:
    revs: List[dict] = []
    cont = None
    for _ in range(6):
        params = {
            "action": "query", "format": "json", "formatversion": "2",
            "prop": "revisions", "titles": titulo,
            "rvprop": "ids|timestamp|comment", "rvlimit": "500", "rvdir": "newer",
        }
        if cont:
            params["rvcontinue"] = cont
        data = http_get_json(f"https://{site}/w/api.php", params)
        pages = data.get("query", {}).get("pages")
        if not pages or pages[0].get("missing"):
            raise SystemExit(f"No se encontró la página '{titulo}' en {site}")
        revs.extend(pages[0].get("revisions", []))
        cont = data.get("continue", {}).get("rvcontinue")
        if not cont or len(revs) >= want_at_least:
            break
    return revs


def get_revision_content(site: str, revid: int) -> Tuple[str, str, str]:
    params = {
        "action": "query", "format": "json", "formatversion": "2",
        "prop": "revisions", "revids": str(revid),
        "rvprop": "content|comment|timestamp", "rvslots": "main",
    }
    data = http_get_json(f"https://{site}/w/api.php", params)
    page = data["query"]["pages"][0]
    rev = page["revisions"][0]
    content = rev["slots"]["main"]["content"]
    return content, rev.get("comment", ""), rev.get("timestamp", "")


def wikitext_to_plain(wt: str) -> str:
    """El conversor más tonto posible: suficiente para medir reanclaje,
    nada más. No es (ni pretende ser) la ingesta real de 04_MVP."""
    s = wt
    s = re.sub(r"<!--.*?-->", "", s, flags=re.S)
    s = re.sub(r"<ref[^>]*/>", "", s)
    s = re.sub(r"<ref[^>]*>.*?</ref>", "", s, flags=re.S)
    for _ in range(3):  # un par de pasadas para plantillas con un nivel de anidamiento
        s = re.sub(r"\{\{[^{}]*\}\}", "", s)
    s = re.sub(r"\[\[(?:[^\]|]*\|)?([^\]]*)\]\]", r"\1", s)
    s = re.sub(r"'''''([^']*)'''''", r"\1", s)
    s = re.sub(r"'''([^']*)'''", r"\1", s)
    s = re.sub(r"''([^']*)''", r"\1", s)
    s = re.sub(r"<br\s*/?>", "\n", s)
    s = re.sub(r"<[^>]+>", "", s)
    s = re.sub(r"^=+\s*(.*?)\s*=+$", r"\1", s, flags=re.M)
    s = re.sub(r"^[:;*#]+\s?", "", s, flags=re.M)
    s = html.unescape(s)
    return s.strip("\n")


def cmd_traer(args: argparse.Namespace) -> None:
    revs = get_revision_list(args.sitio, args.titulo, args.saltos + 2)
    if len(revs) < args.saltos + 1:
        raise SystemExit(
            f"'{args.titulo}' en {args.sitio} tiene sólo {len(revs)} revisiones registradas; "
            f"--saltos {args.saltos} es demasiado."
        )
    idx_b = len(revs) - 1
    idx_a = idx_b - args.saltos
    if idx_a < 0:
        raise SystemExit(f"--saltos {args.saltos} excede el historial disponible ({len(revs)} revisiones).")

    rev_a, rev_b = revs[idx_a], revs[idx_b]
    content_a, comment_a, ts_a = get_revision_content(args.sitio, rev_a["revid"])
    content_b, comment_b, ts_b = get_revision_content(args.sitio, rev_b["revid"])

    plano_a = wikitext_to_plain(content_a)
    plano_b = wikitext_to_plain(content_b)

    with open(args.salida_a, "w", encoding="utf-8") as f:
        f.write(plano_a)
    with open(args.salida_b, "w", encoding="utf-8") as f:
        f.write(plano_b)

    meta = {
        "titulo": args.titulo,
        "sitio": args.sitio,
        "saltos_pedidos": args.saltos,
        "saltos_reales": idx_b - idx_a,
        "revid_a": rev_a["revid"], "timestamp_a": ts_a, "comentario_a": comment_a,
        "revid_b": rev_b["revid"], "timestamp_b": ts_b, "comentario_b": comment_b,
        "archivo_a": args.salida_a, "archivo_b": args.salida_b,
    }
    write_json("rev_meta.json", meta)

    print(f"Obra: {args.titulo} ({args.sitio})")
    print(f"Revisión A: {rev_a['revid']} ({ts_a}) — \"{comment_a}\" -> {args.salida_a}")
    print(f"Revisión B: {rev_b['revid']} ({ts_b}) — \"{comment_b}\" -> {args.salida_b}")
    print(f"Saltos reales entre A y B: {idx_b - idx_a} (pedidos: {args.saltos})")
    print("Metadata en rev_meta.json")


# ---------------------------------------------------------------------------
# BLOQUE 6 — CLI: correr (+ BLOQUE 8 — barrido)
# ---------------------------------------------------------------------------

def load_meta_if_present(a_path: str) -> dict:
    meta_path = os.path.join(os.path.dirname(os.path.abspath(a_path)) or ".", "rev_meta.json")
    if os.path.exists(meta_path):
        with open(meta_path, encoding="utf-8") as f:
            m = json.load(f)
        return {
            "obra": m.get("titulo", "[desconocida]"),
            "revisiones": f"{m.get('revid_a')} -> {m.get('revid_b')} ({m.get('saltos_reales')} ediciones)",
            "comentario": m.get("comentario_b", "[desconocido]"),
        }
    return {"obra": "[desconocida: no hay rev_meta.json junto a --a]", "revisiones": "[desconocido]", "comentario": "[desconocido]"}


def run_barrido(text_a: str, text_b: str, n: int, contexto: int, base_seed: int, meta: dict, json_path: str) -> None:
    umbrales = [0.6, 0.7, 0.75, 0.8, 0.9]
    semillas = [base_seed, base_seed + 1, base_seed + 2]

    filas = []
    detalle = {}
    for u in umbrales:
        for s in semillas:
            res = run_experiment(text_a, text_b, n, u, s, contexto)
            cf = res["resumen"]["criterio_fracaso"]
            filas.append({
                "umbral": u, "semilla": s,
                "fp_desvio_mayor_50_pct": cf["fp_desvio_mayor_50_pct"],
                "huerfanas_evitables_pct": cf["huerfanas_evitables_pct"],
            })
            detalle[f"umbral={u}_semilla={s}"] = res["resumen"]

    print("=== BARRIDO --umbral x --semilla (03_SPIKE §6 / BLOQUE 8) ===\n")
    print("| umbral | semilla | %FP desvío>50 | %huérfanas evitables |")
    print("|---|---|---|---|")
    for fila in filas:
        print(f"| {fila['umbral']} | {fila['semilla']} | {fila['fp_desvio_mayor_50_pct']}% | {fila['huerfanas_evitables_pct']}% |")

    print("\n| umbral | media %FP desvío>50 | media %huérfanas evitables |")
    print("|---|---|---|")
    for u in umbrales:
        filas_u = [f for f in filas if f["umbral"] == u]
        media_fp = round(sum(f["fp_desvio_mayor_50_pct"] for f in filas_u) / len(filas_u), 2)
        media_ev = round(sum(f["huerfanas_evitables_pct"] for f in filas_u) / len(filas_u), 2)
        print(f"| {u} | {media_fp}% | {media_ev}% |")

    write_json(json_path, {
        "meta": meta,
        "parametros": {"n": n, "contexto": contexto, "umbrales": umbrales, "semillas": semillas},
        "barrido": filas,
        "detalle_por_celda": detalle,
    })
    print(f"\nJSON completo (todas las celdas) en: {json_path}")


def cmd_correr(args: argparse.Namespace) -> None:
    with open(args.a, encoding="utf-8") as f:
        text_a = f.read()
    with open(args.b, encoding="utf-8") as f:
        text_b = f.read()
    meta = load_meta_if_present(args.a)

    if args.barrido:
        run_barrido(text_a, text_b, args.n, args.contexto, args.semilla, meta, args.json)
        return

    result = run_experiment(text_a, text_b, args.n, args.umbral, args.semilla, args.contexto)
    result["meta"] = meta
    result["parametros"] = {"n": args.n, "umbral": args.umbral, "semilla": args.semilla, "contexto": args.contexto}
    write_json(args.json, result)

    print(format_reporte(result))
    print(f"\nJSON completo (cada ancla, categoría, confianza, desvío) en: {args.json}")


# ---------------------------------------------------------------------------
# BLOQUE 6 — CLI: sondeo (R-04, 02_RISKS §3)
# ---------------------------------------------------------------------------

def _slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_") or "obra"


def _residual_markup(text: str) -> int:
    patrones = [r"\{\{", r"\}\}", r"\[\[", r"\]\]", r"<[^>]+>", r"&[a-zA-Z]+;", r"^=+", r"''"]
    total = 0
    for p in patrones:
        total += len(re.findall(p, text, flags=re.M))
    return total


def get_latest_revision(site: str, titulo: str) -> Tuple[str, str, str, int]:
    params = {
        "action": "query", "format": "json", "formatversion": "2",
        "prop": "revisions", "titles": titulo,
        "rvprop": "ids|content|comment|timestamp", "rvslots": "main", "rvlimit": "1",
    }
    data = http_get_json(f"https://{site}/w/api.php", params)
    pages = data.get("query", {}).get("pages")
    if not pages or pages[0].get("missing"):
        raise SystemExit(f"No se encontró la página '{titulo}' en {site}")
    rev = pages[0]["revisions"][0]
    content = rev["slots"]["main"]["content"]
    return content, rev.get("comment", ""), rev.get("timestamp", ""), rev["revid"]


def cmd_sondeo(args: argparse.Namespace) -> None:
    resultados = []
    print("=== SONDEO R-04 — conversor más tonto posible, cuenta candidatas (02_RISKS §3) ===\n")
    for titulo in args.titulos:
        try:
            content, comment, ts, revid = get_latest_revision(args.sitio, titulo)
        except (urllib.error.URLError, SystemExit) as e:
            resultados.append({"titulo": titulo, "error": str(e)})
            print(f"{titulo}: ERROR — {e}")
            continue

        plano = wikitext_to_plain(content)
        norm = normalize_text(plano)
        blocks = split_blocks(norm)
        residual = _residual_markup(norm)
        ratio = residual / max(1, len(blocks))
        heuristica_usable = ratio < 0.3

        slug = _slugify(titulo)
        out_path = f"sondeo_{slug}.txt"
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(norm)

        fila = {
            "titulo": titulo, "revid": revid, "timestamp": ts,
            "caracteres": len(norm), "bloques": len(blocks),
            "marcado_residual": residual, "marcado_residual_por_bloque": round(ratio, 3),
            "heuristica_usable_menos_1h": heuristica_usable,
            "archivo": out_path,
        }
        resultados.append(fila)
        print(
            f"{titulo}: {len(blocks)} bloques, {len(norm)} chars, "
            f"marcado residual {residual} ({round(ratio,3)}/bloque) -> "
            f"heurística: {'usable' if heuristica_usable else 'revisar a mano'} (-> {out_path})"
        )

    print("\nLa heurística no reemplaza la mirada humana: abrir cada .txt y contar minutos reales de limpieza.")
    write_json(args.json, resultados)
    print(f"JSON en: {args.json}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="spike_anclas.py",
        description="Arnés de medición para R-03 (03_SPIKE_anclas.md). No es código de producto.",
    )
    sub = p.add_subparsers(dest="comando", required=True)

    p_humo = sub.add_parser("humo", help="calibrar el instrumento con texto sintético, sin red")
    p_humo.add_argument("--semilla", type=int, default=42)
    p_humo.add_argument("--contexto", type=int, default=32)
    p_humo.add_argument("--json", default="humo_resultado.json")
    p_humo.set_defaults(func=cmd_humo)

    p_traer = sub.add_parser("traer", help="bajar dos revisiones reales de Wikisource")
    p_traer.add_argument("--titulo", required=True)
    p_traer.add_argument("--saltos", type=int, required=True)
    p_traer.add_argument("--sitio", default="es.wikisource.org")
    p_traer.add_argument("--salida-a", default="rev_A.txt", dest="salida_a")
    p_traer.add_argument("--salida-b", default="rev_B.txt", dest="salida_b")
    p_traer.set_defaults(func=cmd_traer)

    p_correr = sub.add_parser("correr", help="medir el reanclaje sobre dos revisiones reales")
    p_correr.add_argument("--a", required=True)
    p_correr.add_argument("--b", required=True)
    p_correr.add_argument("--n", type=int, default=200)
    p_correr.add_argument("--umbral", type=float, default=0.75)
    p_correr.add_argument("--semilla", type=int, default=1)
    p_correr.add_argument("--contexto", type=int, default=32)
    p_correr.add_argument("--json", default="resultado.json")
    p_correr.add_argument("--barrido", action="store_true", help="BLOQUE 8: matriz --umbral x 3 semillas en vez de una corrida sola")
    p_correr.set_defaults(func=cmd_correr)

    p_sondeo = sub.add_parser("sondeo", help="R-04: sondeo de obras candidatas de Wikisource")
    p_sondeo.add_argument("titulos", nargs="+")
    p_sondeo.add_argument("--sitio", default="es.wikisource.org")
    p_sondeo.add_argument("--json", default="sondeo_resultado.json")
    p_sondeo.set_defaults(func=cmd_sondeo)

    return p


def main(argv: Optional[List[str]] = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
