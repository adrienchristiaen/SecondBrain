# Carte du code

```
iris                      lanceur (fixe IRIS_ROOT, path)
iris.toml                 configuration (budget, prix, Data Hub)
06-tools/iris_cli/
  cli.py registry.py         dispatch + découverte des commandes
  core/                      paths, config, context, jsonl
  commands/                  une commande par fichier (NAME + register)
  lib/                       logique pure: tokenmath, gitrun, graphast, select,
                             miningparse, assets, network, datahubclient, dashstate, dashserver
  web/index.html             dashboard
  tests/                     unittest (stdlib)
```
Dépendances: `commands/* → lib/* → core/*`; `lib/dashstate → commands/{tokens,usage,fr}` (agrégation).
Régénérer les graphes des repos suivis: `./iris graph`.
