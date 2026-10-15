"""
Agent IA principal — interface CLI interactive.
Utilise le SDK google-genai avec function calling automatique.
"""

import os
import sys
from google import genai
from google.genai import types
from tools import TOUS_LES_OUTILS

# ──────────────────────────────────────────────
# Configuration
# ──────────────────────────────────────────────

MODEL = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = """Tu es un assistant IA intelligent et serviable.
Tu peux utiliser plusieurs outils à ta disposition :

1. recherche_web(query) — cherche des informations sur Internet (DuckDuckGo)
2. executer_code_python(code) — exécute du code Python et retourne le résultat
3. lire_fichier(chemin, debut_ligne, fin_ligne) — lit un fichier texte local
4. calculer(expression) — évalue une expression mathématique (sqrt, sin, cos, pi, e...)
5. meteo(ville) — affiche la météo actuelle et les prévisions pour une ville

Règles :
- Utilise les outils quand c'est pertinent, sans le demander à l'utilisateur.
- Sois concis mais complet dans tes réponses.
- Réponds toujours en français sauf si l'utilisateur parle une autre langue.
- Si tu n'as pas la réponse, dis-le honnêtement.
"""

COULEURS = {
    "reset": "\033[0m",
    "cyan": "\033[96m",
    "vert": "\033[92m",
    "jaune": "\033[93m",
    "rouge": "\033[91m",
    "gris": "\033[90m",
    "bold": "\033[1m",
}


def c(couleur: str, texte: str) -> str:
    """Applique une couleur ANSI à un texte."""
    return f"{COULEURS.get(couleur, '')}{texte}{COULEURS['reset']}"


# ──────────────────────────────────────────────
# Bannière
# ──────────────────────────────────────────────

BANNIERE = f"""
{c('cyan', '╔══════════════════════════════════════════════════╗')}
{c('cyan', '║')}  {c('bold', '🤖  Mon Agent IA — Propulsé par Gemini 3.8 Flash')}  {c('cyan', '║')}
{c('cyan', '╠══════════════════════════════════════════════════╣')}
{c('cyan', '║')}  {c('gris', 'Outils : web · code · fichiers · calculs · météo')}  {c('cyan', '║')}
{c('cyan', '║')}  {c('gris', 'Tapez  : /aide  /outils  /reset  /quitter')}         {c('cyan', '║')}
{c('cyan', '╚══════════════════════════════════════════════════╝')}
"""

AIDE = f"""
{c('jaune', '📋 Commandes disponibles :')}
  {c('vert', '/aide')}     — Affiche cette aide
  {c('vert', '/outils')}   — Liste les outils disponibles
  {c('vert', '/reset')}    — Réinitialise la conversation
  {c('vert', '/quitter')}  — Quitte l'agent

{c('jaune', '💡 Exemples de questions :')}
  "Quel est le carré de 1234 ?"
  "Météo à Paris demain ?"
  "Cherche des infos sur Python 3.13"
  "Exécute : print(sum(range(100)))"
  "Lis le fichier C:/mon/fichier.txt"
"""

LISTE_OUTILS = f"""
{c('jaune', '🛠️  Outils disponibles :')}
  {c('vert', '1.')} {c('bold', 'recherche_web')}      — Recherche DuckDuckGo
  {c('vert', '2.')} {c('bold', 'executer_code_python')} — Exécute du Python
  {c('vert', '3.')} {c('bold', 'lire_fichier')}       — Lit un fichier local
  {c('vert', '4.')} {c('bold', 'calculer')}           — Calculs mathématiques
  {c('vert', '5.')} {c('bold', 'meteo')}              — Météo en temps réel
"""


# ──────────────────────────────────────────────
# Agent
# ──────────────────────────────────────────────

class AgentIA:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            print(c("rouge", "❌ GEMINI_API_KEY non définie."))
            print(c("jaune", "   Définissez-la avec : $env:GEMINI_API_KEY = 'votre-clé'"))
            print(c("gris",  "   Obtenez une clé sur : https://aistudio.google.com/apikey"))
            sys.exit(1)

        self.client = genai.Client(api_key=api_key)
        self.previous_interaction_id: str | None = None
        self.tour = 0

    def reset(self):
        self.previous_interaction_id = None
        self.tour = 0
        print(c("jaune", "🔄 Conversation réinitialisée.\n"))

    def envoyer(self, message: str) -> str:
        """Envoie un message à l'agent et retourne sa réponse."""
        self.tour += 1

        kwargs = {
            "model": MODEL,
            "input": message,
            "tools": TOUS_LES_OUTILS,
            "system_instruction": SYSTEM_INSTRUCTION,
        }

        if self.previous_interaction_id:
            kwargs["previous_interaction_id"] = self.previous_interaction_id

        # Affichage des étapes de raisonnement
        print(c("gris", "⏳ Réflexion en cours..."), end="\r")

        interaction = self.client.interactions.create(**kwargs)
        self.previous_interaction_id = interaction.id

        # Affiche les appels d'outils effectués
        tool_calls = [
            s for s in (interaction.steps or [])
            if getattr(s, "type", None) == "function_call"
        ]
        if tool_calls:
            print(" " * 40, end="\r")  # efface le spinner
            for tc in tool_calls:
                print(c("gris", f"  🔧 Outil utilisé : {tc.name}"))

        return interaction.output_text or "(Pas de réponse textuelle)"

    def run(self):
        """Boucle principale de l'agent."""
        print(BANNIERE)
        print(c("gris", f"Modèle : {MODEL} | Tapez /aide pour l'aide\n"))

        while True:
            try:
                user_input = input(c("cyan", f"Vous [{self.tour+1}]> ")).strip()
            except (KeyboardInterrupt, EOFError):
                print(f"\n{c('jaune', 'Au revoir ! 👋')}")
                break

            if not user_input:
                continue

            # Commandes spéciales
            match user_input.lower():
                case "/quitter" | "/exit" | "/quit":
                    print(c("jaune", "Au revoir ! 👋"))
                    break
                case "/aide" | "/help":
                    print(AIDE)
                    continue
                case "/outils" | "/tools":
                    print(LISTE_OUTILS)
                    continue
                case "/reset":
                    self.reset()
                    continue

            # Envoi à l'agent
            try:
                reponse = self.envoyer(user_input)
                print(" " * 40, end="\r")  # efface le spinner
                print(f"\n{c('vert', 'Agent')} > {reponse}\n")
            except Exception as e:
                print(c("rouge", f"\n❌ Erreur : {e}\n"))


# ──────────────────────────────────────────────
# Point d'entrée
# ──────────────────────────────────────────────

if __name__ == "__main__":
    agent = AgentIA()
    agent.run()
