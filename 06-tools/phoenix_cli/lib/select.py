"""Sélection des repos utiles à un prompt: Blinders si installé, sinon recoupement lexical déterministe."""
import re
import shutil
import subprocess

WORD = re.compile(r"[A-Za-z][A-Za-z0-9]{2,}")


def words(text):
    return {w.lower() for w in WORD.findall(text.replace("_", " ").replace("-", " "))}


def lexical(prompt, docs, limit):
    """docs: {nom: texte}. Mot du nom: 5; mot du texte: 1/df (un mot présent partout ne prouve rien).
    Seuls les repos à au moins 40 % du meilleur score sont gardés."""
    query = words(prompt)
    doc_words = {name: words(text) for name, text in docs.items()}
    scored = []
    for name, found in doc_words.items():
        score = 5 * len(query & words(name))
        for w in query & found:
            df = sum(w in other for other in doc_words.values())
            score += 0 if df == len(docs) > 1 else 1 / df
        if score:
            scored.append((-score, name))
    scored.sort()
    return [n for s, n in scored[:limit] if -s >= 0.4 * -scored[0][0]]


def find_card(folder, name):
    """Fiche wiki d'un repo, insensible à la casse; None si absente."""
    if folder.is_dir():
        for path in folder.glob("*.md"):
            if path.stem.lower() == name.lower():
                return path
    return None


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
