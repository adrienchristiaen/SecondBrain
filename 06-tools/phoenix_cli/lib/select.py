"""Sélection des repos utiles à un prompt: Blinders si installé, sinon recoupement lexical déterministe."""
import re
import shutil
import subprocess

WORD = re.compile(r"[A-Za-z][A-Za-z0-9]{2,}")


def words(text):
    return {w.lower() for w in WORD.findall(text.replace("_", " ").replace("-", " "))}


def lexical(prompt, docs, limit):
    """docs: {nom: texte}. Un mot dans le nom pèse 5, dans le texte 1."""
    query, scored = words(prompt), []
    for name, text in docs.items():
        score = 5 * len(query & words(name)) + len(query & words(text))
        if score:
            scored.append((-score, name))
    return [name for _, name in sorted(scored)[:limit]]


def via_blinders(prompt, names, runner=subprocess.run, which=shutil.which):
    exe = which("blind")
    if not exe:
        return None
    try:
        res = runner([exe, "select", prompt], capture_output=True, text=True, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None
    if res.returncode:
        return None
    hits = []
    for name in names:
        match = re.search(rf"(?<![\w-]){re.escape(name)}(?![\w-])", res.stdout)
        if match:
            hits.append((match.start(), name))
    return [n for _, n in sorted(hits)] or None


def est_tokens(text):
    return (len(text) + 3) // 4


def pack(sections, max_tokens):
    blocks, used = [], 0
    for title, text in sections:
        room = max_tokens - used
        if room < 50:
            break
        block = f"## {title}\n{text.strip()}\n"
        if est_tokens(block) > room:
            block = block[: room * 4 - 20].rsplit("\n", 1)[0] + "\n…(tronqué)\n"
        blocks.append(block)
        used += est_tokens(block)
    return "\n".join(blocks), used
