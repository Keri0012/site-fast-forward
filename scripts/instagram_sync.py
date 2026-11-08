#!/usr/bin/env python3
"""
Synchronise la page news.html avec le compte Instagram de Fast Forward.

- Récupère les derniers posts via l'API officielle Instagram :
    token « EAA… » (utilisateur système, n'expire pas) → graph.facebook.com
    token « IG… » (connexion Instagram, 60 jours)     → graph.instagram.com
- Télécharge les visuels dans images/instagram/ (les liens Instagram expirent)
- Génère des fiches de réalisation en HTML statique (lisibles par Google)
  entre les balises <!-- IG:START --> et <!-- IG:END --> de news.html
- Détecte une « Fiche technique » dans la légende, complétée si besoin par
  data/details-projets.json

Variables d'environnement :
  IG_TOKEN        jeton d'accès Instagram (obligatoire)
  IG_USER_ID      identifiant numérique du compte Instagram (requis avec un token EAA)
  IG_MAX_POSTS    nombre de posts affichés (défaut : 24)
  IG_REFRESH      "1" le lundi : renouvelle un token IG… et note la date de synchro
  IG_DEMO_FILE    chemin d'un JSON de posts pour tester sans API (optionnel)
"""
import html
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
NEWS = os.path.join(ROOT, "news.html")
IMG_DIR = os.path.join(ROOT, "images", "instagram")
DETAILS = os.path.join(ROOT, "data", "details-projets.json")
API = "https://graph.instagram.com"
FB_API = "https://graph.facebook.com/v23.0"
FIELDS = ("id,caption,media_type,media_url,thumbnail_url,permalink,timestamp,"
          "children{media_type,media_url,thumbnail_url}")
START = "<!-- IG:START"
END = "<!-- IG:END -->"

MOIS = ["janvier", "février", "mars", "avril", "mai", "juin", "juillet",
        "août", "septembre", "octobre", "novembre", "décembre"]


def get_json(url):
    req = urllib.request.Request(url, headers={"User-Agent": "fast-forward-site-sync"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def fetch_posts(token, limit, user_id=""):
    if token.startswith("EAA"):
        if not user_id:
            sys.exit("IG_USER_ID manquant : il est obligatoire avec un token commençant par EAA")
        base = f"{FB_API}/{user_id}/media?"
    else:
        base = f"{API}/me/media?"
    posts, url = [], base + urllib.parse.urlencode(
        {"fields": FIELDS, "limit": min(limit, 50), "access_token": token})
    while url and len(posts) < limit:
        data = get_json(url)
        posts += data.get("data", [])
        url = data.get("paging", {}).get("next")
    return posts[:limit]


def refresh_token(token):
    data = get_json(f"{API}/refresh_access_token?" + urllib.parse.urlencode(
        {"grant_type": "ig_refresh_token", "access_token": token}))
    return data["access_token"], data.get("expires_in")


def shortcode(permalink):
    m = re.search(r"/(?:p|reel|tv)/([^/?#]+)", permalink or "")
    return m.group(1) if m else None


def image_url(post):
    if post.get("media_type") == "VIDEO":
        return post.get("thumbnail_url") or post.get("media_url")
    if post.get("media_type") == "CAROUSEL_ALBUM":
        for c in post.get("children", {}).get("data", []):
            u = c.get("thumbnail_url") if c.get("media_type") == "VIDEO" else c.get("media_url")
            if u:
                return u
    return post.get("media_url")


def download_image(url, code):
    os.makedirs(IMG_DIR, exist_ok=True)
    path = os.path.join(IMG_DIR, f"{code}.jpg")
    if os.path.exists(path) or not url:
        return os.path.exists(path)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "fast-forward-site-sync"})
        with urllib.request.urlopen(req, timeout=60) as r:
            raw = r.read()
        try:
            from io import BytesIO
            from PIL import Image
            im = Image.open(BytesIO(raw)).convert("RGB")
            im.thumbnail((900, 1125))
            im.save(path, "JPEG", quality=82, optimize=True, progressive=True)
        except ImportError:
            with open(path, "wb") as f:
                f.write(raw)
        return True
    except Exception as e:  # une image en échec ne bloque pas la page
        print(f"  ! image {code} non téléchargée : {e}", file=sys.stderr)
        return False


# ---------------------------------------------------------------- légendes
FICHE = re.compile(r"^\W*(fiche\s+technique|technique)\s*:?\s*(.*)$", re.I)
LABEL = re.compile(r"^\W{0,3}([A-Za-zÀ-ÿ][A-Za-zÀ-ÿ' /-]{1,28}?)\s*:\s*(.+)$")


def is_tag_line(line):
    words = line.split()
    return bool(words) and all(w.startswith(("#", "@")) for w in words)


def parse_caption(caption):
    """Retourne (titre, paragraphes, fiche) où fiche = {'items': [...], 'pairs': [(label, valeur)]}"""
    lines = [l.strip() for l in (caption or "").replace("\r", "").split("\n")]
    while lines and (not lines[-1] or is_tag_line(lines[-1])):
        lines.pop()
    fiche = {"items": [], "pairs": []}
    body, i = [], 0
    while i < len(lines):
        m = FICHE.match(lines[i])
        if m:
            rest = m.group(2).strip()
            if rest:
                fiche["items"] += [x.strip() for x in re.split(r"\s*[·•|,;]\s*", rest) if x.strip()]
            i += 1
            while i < len(lines) and lines[i]:
                lm = LABEL.match(lines[i])
                if lm:
                    fiche["pairs"].append((lm.group(1).strip(), lm.group(2).strip()))
                else:
                    fiche["items"].append(re.sub(r"^[\W_]+", "", lines[i]).strip())
                i += 1
            continue
        if not is_tag_line(lines[i]):
            body.append(lines[i])
        i += 1
    # retire les hashtags restés en fin de phrase
    body = [re.sub(r"(\s+#[\wÀ-ÿ]+)+\s*$", "", l) for l in body]
    text = "\n".join(body).strip()
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    titre = ""
    if paras:
        first, _, rest = paras[0].partition("\n")
        titre = first.strip()
        paras = ([rest.strip()] if rest.strip() else []) + paras[1:]
    if len(titre) > 110:
        titre = titre[:107].rsplit(" ", 1)[0] + "…"
    return titre, paras, fiche


def date_fr(ts):
    d = datetime.strptime(ts[:19], "%Y-%m-%dT%H:%M:%S")
    return d.strftime("%Y-%m-%d"), f"{MOIS[d.month - 1]} {d.year}"


# ---------------------------------------------------------------- rendu
def e(s):
    return html.escape(s, quote=True)


def render_fiche(fiche):
    if not fiche["items"] and not fiche["pairs"]:
        return ""
    out = ['<div class="fiche-technique">', "<h3>Fiche technique</h3>"]
    if fiche["pairs"]:
        out.append("<dl>" + "".join(f"<dt>{e(k)}</dt><dd>{e(v)}</dd>" for k, v in fiche["pairs"]) + "</dl>")
    if fiche["items"]:
        out.append("<ul>" + "".join(f"<li>{e(x)}</li>" for x in fiche["items"]) + "</ul>")
    out.append("</div>")
    return "".join(out)


def render_post(post, details):
    code = shortcode(post.get("permalink"))
    if not code:
        return None
    titre, paras, fiche = parse_caption(post.get("caption"))
    extra = details.get(code, {})
    titre = extra.get("titre") or titre or "Réalisation Fast Forward"
    if extra.get("description"):
        paras = [p.strip() for p in extra["description"].split("\n\n") if p.strip()]
    for k, v in (extra.get("fiche_technique") or {}).items():
        fiche["pairs"] = [(a, b) for a, b in fiche["pairs"] if a.lower() != k.lower()] + [(k, str(v))]
    iso, lisible = date_fr(post.get("timestamp", "1970-01-01T00:00:00"))
    has_img = download_image(image_url(post), code)
    href = e(post.get("permalink"))
    alt = extra.get("alt") or f"{titre} – réalisation vidéo Fast Forward"
    badge = {"VIDEO": "Vidéo", "CAROUSEL_ALBUM": "Album"}.get(post.get("media_type"), "")
    media = ""
    if has_img:
        media = (f'<a class="projet-media" href="{href}" target="_blank" rel="noopener">'
                 f'<img src="images/instagram/{e(code)}.jpg" alt="{e(alt)}" loading="lazy">'
                 + (f'<span class="projet-badge">{badge}</span>' if badge else "") + "</a>")
    texte = "".join(f"<p>{e(p).replace(chr(10), '<br>')}</p>" for p in paras)
    return (f'<article class="projet" id="{e(code)}">{media}<div class="projet-body">'
            f'<time class="projet-date" datetime="{iso}">{lisible}</time>'
            f"<h2>{e(titre)}</h2>"
            + (f'<div class="projet-texte">{texte}</div>' if texte else "")
            + render_fiche(fiche)
            + f'<a class="projet-lien" href="{href}" target="_blank" rel="noopener">Voir sur Instagram →</a>'
            "</div></article>")


def update_news(articles):
    page = open(NEWS, encoding="utf-8").read()
    a, b = page.find(START), page.find(END)
    if a < 0 or b < 0:
        sys.exit("Balises IG:START / IG:END introuvables dans news.html")
    a = page.index("-->", a) + 3
    block = '\n<div class="projets">\n' + "\n".join(articles) + "\n</div>\n"
    new = page[:a] + block + page[b:]
    if new != page:
        open(NEWS, "w", encoding="utf-8").write(new)
        print(f"news.html mis à jour ({len(articles)} réalisations)")
    else:
        print("Aucun changement")


def main():
    limit = int(os.environ.get("IG_MAX_POSTS", "24"))
    demo = os.environ.get("IG_DEMO_FILE")
    token = os.environ.get("IG_TOKEN", "").strip()
    if demo:
        posts = json.load(open(demo, encoding="utf-8"))
    else:
        if not token:
            sys.exit("IG_TOKEN manquant : ajoute le secret IG_TOKEN dans GitHub (voir GUIDE-INSTAGRAM.md)")
        if os.environ.get("IG_REFRESH") == "1":
            # trace hebdomadaire : garde le dépôt « actif » pour que GitHub
            # ne suspende pas la synchronisation automatique au bout de 60 jours
            os.makedirs(os.path.dirname(DETAILS), exist_ok=True)
            with open(os.path.join(ROOT, "data", "instagram-sync.json"), "w") as f:
                json.dump({"derniere_verification": datetime.now(timezone.utc).strftime("%Y-%m-%d")}, f)
            if token.startswith("IG"):  # les tokens EAA utilisateur système n'expirent pas
                try:
                    new, exp = refresh_token(token)
                    out = os.path.join(os.environ.get("RUNNER_TEMP", "/tmp"), "new_token")
                    with open(out, "w") as f:
                        f.write(new)
                    print(f"Jeton renouvelé (valable {int(exp or 0) // 86400} jours)")
                except Exception as ex:
                    print(f"::warning::Renouvellement du jeton impossible : {ex}")
        try:
            posts = fetch_posts(token, limit, os.environ.get("IG_USER_ID", "").strip())
        except urllib.error.HTTPError as ex:
            detail = ex.read().decode("utf-8", "replace")[:500]
            sys.exit(f"Erreur de l'API Instagram ({ex.code}) : {detail}")
    details = {}
    if os.path.exists(DETAILS):
        details = {k: v for k, v in json.load(open(DETAILS, encoding="utf-8")).items() if not k.startswith("_")}
    articles = [x for x in (render_post(p, details) for p in posts) if x]
    if not articles:
        sys.exit("Aucun post récupéré : la page n'a pas été modifiée")
    update_news(articles)


if __name__ == "__main__":
    main()
