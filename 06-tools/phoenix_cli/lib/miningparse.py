"""Lecture d'exports de chats Gemini (Takeout, historique Gemini CLI, jsonl, markdown) et extraction de motifs."""
import json
import re
from collections import Counter
from pathlib import Path

PREFIXES = ("Prompted ", "Asked ", "Vous avez demandé ", "Vous avez posé la question ")
STOP = set("avec dans pour cette cette comme mais plus sans sont être faire that this with from have what when your quel quoi tout fait peut très donc alors aussi vous nous elle ils leur the and not are you can".split())
FILE = re.compile(r"[\w./-]+\.(?:py|java|scala|kt|ya?ml|json|toml|md|sh|sql|tf|ts|js|xml|gradle|conf)\b")
BACKTICK = re.compile(r"`([^`\n]{3,80})`")


def _text_of(msg):
    content = msg.get("content", msg.get("text", ""))
    if isinstance(content, list):
        content = " ".join(c.get("text", "") for c in content if isinstance(c, dict))
    return content if isinstance(content, str) else ""


def _from_json(data, source):
    items = data.get("messages", []) if isinstance(data, dict) else data
    out = []
    for item in items if isinstance(items, list) else []:
        if not isinstance(item, dict):
            continue
        if "title" in item and item["title"].startswith(PREFIXES):
            title = item["title"]
            text = next(title[len(p):] for p in PREFIXES if title.startswith(p))
            out.append({"text": text, "ts": item.get("time", ""), "source": source})
        elif item.get("type") in ("user", None) and item.get("role", "user") == "user" and _text_of(item):
            out.append({"text": _text_of(item), "ts": item.get("timestamp", ""), "source": source})
    return out


def load_prompts(folder):
    prompts = []
    for path in sorted(Path(folder).rglob("*")):
        if not path.is_file():
            continue
        src = path.relative_to(folder).as_posix()
        try:
            raw = path.read_text(encoding="utf-8", errors="replace")
            if path.suffix == ".json":
                prompts += _from_json(json.loads(raw), src)
            elif path.suffix == ".jsonl":
                prompts += [p for line in raw.splitlines() if line.strip() for p in _from_json([json.loads(line)], src)]
            elif path.suffix in (".md", ".txt"):
                prompts.append({"text": raw, "ts": "", "source": src})
        except ValueError:
            continue
    return prompts


def _command_key(span):
    tokens = span.lstrip("$ ").split()
    if not tokens or not re.match(r"^[a-z][\w.-]*$", tokens[0]):
        return None
    return " ".join(tokens[:1] if len(tokens) < 2 or tokens[1].startswith("-") else tokens[:2])


def analyze(prompts, repo_names, asset_names):
    repos, files, commands, assets, topics = (Counter() for _ in range(5))
    for prompt in prompts:
        text = prompt["text"]
        low = text.lower()
        for name in repo_names:
            if re.search(rf"(?<![\w-]){re.escape(name.lower())}(?![\w-])", low):
                repos[name] += 1
        for name in asset_names:
            if re.search(rf"(?<![\w-]){re.escape(name.lower())}(?![\w-])", low):
                assets[name] += 1
        files.update(FILE.findall(text))
        spans = BACKTICK.findall(text) + [l for l in text.splitlines() if l.startswith("$ ")]
        commands.update(k for k in map(_command_key, spans) if k)
        ws = [w for w in re.findall(r"[a-zà-ÿ]{4,}", low) if w not in STOP]
        topics.update(" ".join(p) for p in zip(ws, ws[1:]))
    return {"n": len(prompts), "repos": repos, "files": files, "commands": commands, "assets": assets,
            "topics": Counter({k: v for k, v in topics.items() if v >= 3})}


def render(result, asset_names, top=15):
    out = [f"# Mining des chats Gemini ({result['n']} prompts)", ""]
    for title, key in (("Repos les plus sollicités", "repos"), ("Fichiers récurrents", "files"),
                       ("Commandes récurrentes", "commands"), ("Skills/MCP cités", "assets"), ("Sujets récurrents", "topics")):
        out.append(f"## {title}")
        out += [f"- {k}: {v}" for k, v in result[key].most_common(top)] or ["- (rien)"]
        out.append("")
    unused = sorted(set(asset_names) - set(result["assets"]))
    out += ["## Skills/MCP jamais cités (candidats à l'archivage)"] + ([f"- {n}" for n in unused] or ["- (aucun)"])
    return "\n".join(out) + "\n"
