"""Client minimal d'un LLM local (API Ollama): les tokens renvoyés sont exacts, donc comptables sans estimation."""
import json
import urllib.request


def generate(cfg, prompt, model="", opener=urllib.request.urlopen):
    llm = cfg["llm"]
    model = model or llm["model"]
    if not model:
        return {"ok": False, "error": "aucun modèle local: renseigner [llm] model dans iris.toml (ex: ollama list)"}
    body = json.dumps({"model": model, "prompt": prompt, "stream": False}).encode()
    req = urllib.request.Request(llm["url"].rstrip("/") + "/api/generate", data=body, headers={"Content-Type": "application/json"})
    try:
        with opener(req, timeout=llm["timeout"]) as res:
            data = json.load(res)
    except (OSError, ValueError) as exc:
        return {"ok": False, "error": f"LLM local injoignable: {exc}"}
    return {"ok": True, "text": data.get("response", ""), "model": model,
            "tin": data.get("prompt_eval_count", 0), "tout": data.get("eval_count", 0)}
