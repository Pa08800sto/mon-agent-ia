"""
Outils disponibles pour l'agent IA.
Chaque fonction est automatiquement reconnue par le SDK google-genai
via son docstring et ses annotations de type.
"""

import math
import os
import subprocess
import sys
import urllib.parse
import urllib.request
import json
import tempfile


# ──────────────────────────────────────────────
# 1. RECHERCHE WEB (DuckDuckGo Instant Answer API)
# ──────────────────────────────────────────────

def recherche_web(query: str) -> str:
    """Effectue une recherche sur le web et retourne un résumé des résultats.

    Args:
        query: La question ou le sujet à rechercher.
    """
    try:
        encoded = urllib.parse.quote_plus(query)
        url = f"https://api.duckduckgo.com/?q={encoded}&format=json&no_redirect=1&no_html=1&skip_disambig=1"
        req = urllib.request.Request(url, headers={"User-Agent": "mon-agent-ia/1.0"})
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        parts = []

        # Réponse directe (AbstractText)
        if data.get("AbstractText"):
            parts.append(f"📖 Résumé : {data['AbstractText']}")
            if data.get("AbstractURL"):
                parts.append(f"   Source : {data['AbstractURL']}")

        # Réponse immédiate (Answer)
        if data.get("Answer"):
            parts.append(f"✅ Réponse directe : {data['Answer']}")

        # Résultats associés (RelatedTopics)
        topics = data.get("RelatedTopics", [])[:3]
        if topics:
            parts.append("\n🔗 Sujets connexes :")
            for t in topics:
                if isinstance(t, dict) and t.get("Text"):
                    parts.append(f"  - {t['Text'][:200]}")

        if not parts:
            return (
                f"Aucun résultat Instant Answer pour « {query} ».\n"
                "Conseil : reformulez ou posez une question plus précise."
            )

        return "\n".join(parts)

    except Exception as e:
        return f"Erreur lors de la recherche : {e}"


# ──────────────────────────────────────────────
# 2. EXÉCUTION DE CODE PYTHON
# ──────────────────────────────────────────────

def executer_code_python(code: str) -> str:
    """Exécute un extrait de code Python et retourne sa sortie standard et les erreurs.

    Args:
        code: Le code Python à exécuter (chaîne multiligne acceptée).
    """
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".py", delete=False, encoding="utf-8"
        ) as f:
            f.write(code)
            tmp_path = f.name

        result = subprocess.run(
            [sys.executable, tmp_path],
            capture_output=True,
            text=True,
            timeout=30,
        )

        os.unlink(tmp_path)

        output = ""
        if result.stdout:
            output += f"📤 Sortie :\n{result.stdout}"
        if result.stderr:
            output += f"\n⚠️  Erreurs :\n{result.stderr}"
        if not output:
            output = "✅ Code exécuté sans sortie ni erreur."

        return output.strip()

    except subprocess.TimeoutExpired:
        return "⏱️ Timeout : le code a mis trop de temps à s'exécuter (> 30s)."
    except Exception as e:
        return f"❌ Erreur d'exécution : {e}"


# ──────────────────────────────────────────────
# 3. LECTURE DE FICHIERS
# ──────────────────────────────────────────────

def lire_fichier(chemin: str, debut_ligne: int = 1, fin_ligne: int = 0) -> str:
    """Lit le contenu d'un fichier texte local.

    Args:
        chemin: Chemin absolu ou relatif vers le fichier à lire.
        debut_ligne: Première ligne à lire (1 = début du fichier).
        fin_ligne: Dernière ligne à lire (0 = jusqu'à la fin).
    """
    try:
        path = os.path.expanduser(chemin)
        if not os.path.exists(path):
            return f"❌ Fichier introuvable : {path}"

        with open(path, "r", encoding="utf-8", errors="replace") as f:
            lines = f.readlines()

        total = len(lines)
        start = max(0, debut_ligne - 1)
        end = total if fin_ligne <= 0 else min(fin_ligne, total)
        selected = lines[start:end]

        if not selected:
            return f"⚠️ Aucune ligne dans la plage [{debut_ligne}, {fin_ligne}] (fichier = {total} lignes)."

        content = "".join(selected)
        header = f"📄 {path}  (lignes {start+1}–{start+len(selected)} / {total})\n{'─'*60}\n"
        return header + content

    except PermissionError:
        return f"🚫 Permission refusée pour lire : {chemin}"
    except Exception as e:
        return f"❌ Erreur : {e}"


# ──────────────────────────────────────────────
# 4. CALCULS MATHÉMATIQUES
# ──────────────────────────────────────────────

def calculer(expression: str) -> str:
    """Évalue une expression mathématique et retourne le résultat.
    Supporte : +, -, *, /, **, sqrt, sin, cos, tan, log, pi, e, etc.

    Args:
        expression: L'expression mathématique à évaluer, ex: "sqrt(2) * pi".
    """
    # Contexte sécurisé : uniquement les fonctions math
    safe_env = {name: getattr(math, name) for name in dir(math) if not name.startswith("_")}
    safe_env["abs"] = abs
    safe_env["round"] = round
    safe_env["__builtins__"] = {}

    try:
        result = eval(expression, safe_env)  # noqa: S307
        # Formatage intelligent du résultat
        if isinstance(result, float):
            if result == int(result) and abs(result) < 1e15:
                return f"🧮 {expression} = {int(result)}"
            return f"🧮 {expression} = {result:.10g}"
        return f"🧮 {expression} = {result}"
    except ZeroDivisionError:
        return "❌ Division par zéro."
    except Exception as e:
        return f"❌ Expression invalide : {e}\nHint : utilisez ** pour la puissance, sqrt(x) pour la racine carrée."


# ──────────────────────────────────────────────
# 5. MÉTÉO (Open-Meteo, gratuit, sans clé API)
# ──────────────────────────────────────────────

# Geocoding via Open-Meteo geocoding API
def _geocode(ville: str) -> tuple[float, float, str] | None:
    """Retourne (lat, lon, nom_complet) pour une ville."""
    encoded = urllib.parse.quote_plus(ville)
    url = f"https://geocoding-api.open-meteo.com/v1/search?name={encoded}&count=1&language=fr&format=json"
    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())
        results = data.get("results", [])
        if not results:
            return None
        r = results[0]
        nom = r.get("name", ville)
        pays = r.get("country", "")
        return r["latitude"], r["longitude"], f"{nom}, {pays}"
    except Exception:
        return None


def meteo(ville: str) -> str:
    """Retourne la météo actuelle et les prévisions sur 3 jours pour une ville.

    Args:
        ville: Nom de la ville (ex: "Paris", "Lyon", "New York").
    """
    geo = _geocode(ville)
    if not geo:
        return f"❌ Ville introuvable : « {ville} »"

    lat, lon, nom_complet = geo

    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        f"&current=temperature_2m,relative_humidity_2m,wind_speed_10m,"
        f"weather_code,apparent_temperature"
        f"&daily=temperature_2m_max,temperature_2m_min,weather_code,precipitation_sum"
        f"&timezone=auto&forecast_days=4"
    )

    WMO = {
        0: "☀️ Ciel dégagé", 1: "🌤 Peu nuageux", 2: "⛅ Partiellement nuageux",
        3: "☁️ Couvert", 45: "🌫 Brouillard", 48: "🌫 Brouillard givrant",
        51: "🌦 Bruine légère", 53: "🌦 Bruine", 55: "🌧 Bruine forte",
        61: "🌧 Pluie légère", 63: "🌧 Pluie", 65: "🌧 Pluie forte",
        71: "🌨 Neige légère", 73: "🌨 Neige", 75: "❄️ Neige forte",
        80: "🌦 Averses légères", 81: "🌧 Averses", 82: "⛈ Fortes averses",
        95: "⛈ Orage", 96: "⛈ Orage avec grêle", 99: "⛈ Orage violent",
    }

    try:
        with urllib.request.urlopen(url, timeout=10) as resp:
            data = json.loads(resp.read().decode())

        cur = data["current"]
        daily = data["daily"]

        wmo_cur = cur.get("weather_code", 0)
        desc_cur = WMO.get(wmo_cur, f"Code {wmo_cur}")

        lines = [
            f"🌍 Météo pour {nom_complet}",
            f"{'─'*45}",
            f"🌡  Température    : {cur['temperature_2m']}°C (ressenti {cur['apparent_temperature']}°C)",
            f"💧 Humidité       : {cur['relative_humidity_2m']}%",
            f"💨 Vent           : {cur['wind_speed_10m']} km/h",
            f"🌤 Conditions     : {desc_cur}",
            f"",
            f"📅 Prévisions sur 3 jours :",
        ]

        for i in range(1, 4):
            date = daily["time"][i]
            tmax = daily["temperature_2m_max"][i]
            tmin = daily["temperature_2m_min"][i]
            pluie = daily["precipitation_sum"][i]
            wmo_d = daily["weather_code"][i]
            desc_d = WMO.get(wmo_d, f"Code {wmo_d}")
            lines.append(
                f"  {date} : {desc_d}  {tmin}°C→{tmax}°C  🌧{pluie}mm"
            )

        return "\n".join(lines)

    except Exception as e:
        return f"❌ Erreur météo : {e}"


# Liste exportée de tous les outils
TOUS_LES_OUTILS = [
    recherche_web,
    executer_code_python,
    lire_fichier,
    calculer,
    meteo,
]
