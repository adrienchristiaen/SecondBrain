# Graphe: News-Ia
_AST Python, 11 modules, 16 dépendances internes. Généré le 2026-10-14._

## gazette-du-codeur/build.py: Assemble an IA Potter episode: template + episode JSON -> one self-contained HTML page.
- def inline(value)
- def walk(node)
- def main()
## gazette-du-codeur/build_email.py: Version e-mail (Gmail) et message Google Chat d'un épisode, avec le même design que la page.
- def nb(s)
- def md(s)
- def datauri(data, mime)
- def render_images(pw)
- def render_scene_media(pw, page_html)
- def img(imgs, key, alt, width, align)
- def p(s, size)
- def kicker(t)
- def rule(px)
- def codebox(c)
- def build_email(imgs, media)
- def chat_text(url)
- def main()
## pipeline/newsia/__init__.py: News IA — pipeline de veille hebdomadaire.
## pipeline/newsia/align.py: Calcule le minutage (timing.json) : quand chaque séquence et chaque mot apparaît.
- def norm(w)
- def estimate(ep)
- def from_transcript(ep, spoken)
- def align(ep, words_json)
- dépend de: pipeline/newsia/episode.py
## pipeline/newsia/cli.py: Interface en ligne de commande : `newsia <commande>`.
- def main(argv)
- dépend de: pipeline/newsia/__init__.py, pipeline/newsia/align.py, pipeline/newsia/collect.py, pipeline/newsia/draft.py, pipeline/newsia/episode.py, pipeline/newsia/rank.py, pipeline/newsia/transcribe.py, pipeline/newsia/weeks.py
## pipeline/newsia/collect.py: Collecte des flux RSS/Atom → data/raw/<semaine>.json
- def fetch_feed(feed, since)
- def collect(week, sources_file, now)
- dépend de: pipeline/newsia/__init__.py, pipeline/newsia/weeks.py
## pipeline/newsia/draft.py: Brouillon de l'épisode à partir de la shortlist.
- def build_prompt(week)
- def extract_json(text)
- def call_api(prompt, model)
- def draft(week, response_file, model)
- dépend de: pipeline/newsia/__init__.py, pipeline/newsia/episode.py, pipeline/newsia/weeks.py
## pipeline/newsia/episode.py: Chargement / validation d'un épisode (episodes/<id>/episode.json).
- class EpisodeError: -
- def path_of(week)
- def load(week_or_path)
- def units(ep)
- def words(text)
- def estimated_seconds(ep)
- def validate(ep)
- dépend de: pipeline/newsia/__init__.py
## pipeline/newsia/rank.py: Déduplication, regroupement par sujet et classement.
- def tokens(title)
- def jaccard(a, b)
- def cluster(items, threshold)
- def score(members, kw, now)
- def rank(week, top, now)
- dépend de: pipeline/newsia/__init__.py
## pipeline/newsia/transcribe.py: Transcription locale de la voix off → words.json (mot, début, fin).
- def transcribe(audio, out, model, language)
## pipeline/newsia/weeks.py: Identifiants de semaine ISO, ex. 2026-w40.
- def week_id(d)
