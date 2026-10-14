"""Suggestions proactives déduites de l'état du brain. Fonction pure: état -> liste ordonnée."""


def _s(title, why, action=None, prio=5):
    return {"title": title, "why": why, "action": action, "prio": prio}


def suggest(state):
    out = []
    repos, tok = state["repos"], state["tokens"]
    behind = [r["name"] for r in repos if r["behind"]]
    if behind:
        out.append(_s("Synchroniser les repos en retard", ", ".join(behind), "repos.sync", 1))
    if tok["over_budget"]:
        out.append(_s("Budget dépassé", f"{tok['spent_usd']:.2f} USD dépensés: basculer sur les modèles locaux", None, 0))
    elif tok["projected_usd"] > tok["budget_usd"]:
        out.append(_s("Projection au-dessus du budget", f"{tok['projected_usd']} USD projetés pour {tok['budget_usd']}", None, 1))
    if tok["spent_usd"] == 0 and not tok["split"]["local"]["tin"]:
        out.append(_s("Aucune consommation enregistrée", "Journaliser avec: phoenix tokens add --model … --tin … --tout …", None, 6))
    stale = [r["name"] for r in repos if r["graph"]["stale"]]
    if stale:
        out.append(_s("Régénérer les graphes", ", ".join(stale), "graph.build", 2))
    nocard = [r["name"] for r in repos if not r["card"]]
    if nocard:
        out.append(_s("Créer les fiches wiki manquantes", ", ".join(nocard), "cards.build", 2))
    if state["obsolete"]:
        out.append(_s("Archiver les actifs inutilisés", ", ".join(o["name"] for o in state["obsolete"][:5]), "usage.audit", 3))
    if state["inbox"]:
        out.append(_s("Trier l'inbox", f"{state['inbox']} élément(s) à intégrer au wiki puis archiver", None, 4))
    if not state["has_mining"]:
        out.append(_s("Miner l'historique Gemini", "phoenix mine <dossier-export> alimente le wiki et la purge de l'obsolète", None, 4))
    if not state["datahub_configured"]:
        out.append(_s("Brancher Data Hub", "renseigner [datahub] url dans phoenix.toml (lineage, santé, versions)", None, 7))
    if not state["jira_available"]:
        out.append(_s("Installer Jira-CLI", "pip install -e 05-repos/Jira-CLI pour les plans de release/déploiement depuis le navigateur", None, 7))
    if state["feature_requests"]:
        out.append(_s("Traiter les feature requests", f"{state['feature_requests']} ouverte(s)", None, 5))
    if state["commands_since_retex"] >= 5:
        out.append(_s("Faire le rétex", f"{state['commands_since_retex']} commandes depuis le dernier", "retex.run", 3))
    return sorted(out, key=lambda s: s["prio"])
