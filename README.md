<div align="center">

# 🤖 Mon Agent IA

**Agent conversationnel intelligent propulsé par Google Gemini 3.8 Flash**

[![Python](https://img.shields.io/badge/Python-3.12+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Gemini](https://img.shields.io/badge/Gemini-3.8_Flash-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev)
[![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)](LICENSE)

*Parle, demande, explore — ton agent s'occupe du reste.*

</div>

---

## ✨ Fonctionnalités

| Outil | Description | API requise |
|-------|-------------|-------------|
| 🌐 `recherche_web` | Recherche sur le web via DuckDuckGo | ❌ Gratuit |
| 🐍 `executer_code_python` | Exécute du code Python en temps réel | ❌ Gratuit |
| 📄 `lire_fichier` | Lit n'importe quel fichier texte local | ❌ Gratuit |
| 🧮 `calculer` | Calculs mathématiques avancés (sqrt, sin, pi…) | ❌ Gratuit |
| 🌤 `meteo` | Météo actuelle + prévisions 3 jours | ❌ Gratuit |

- **Mémoire conversationnelle** : l'agent se souvient du contexte entre les messages
- **Function calling automatique** : il choisit lui-même l'outil adapté
- **Interface CLI colorée** avec commandes intégrées
- **Aucune dépendance externe** sauf `google-genai`

---

## 🚀 Installation rapide

### 1. Cloner le dépôt

```bash
git clone https://github.com/TON_USERNAME/mon-agent-ia.git
cd mon-agent-ia
```

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

### 3. Configurer la clé API Gemini

Obtiens ta clé gratuite sur [Google AI Studio](https://aistudio.google.com/apikey).

**Linux / macOS :**
```bash
export GEMINI_API_KEY="ta-clé-ici"
```

**Windows (PowerShell) :**
```powershell
$env:GEMINI_API_KEY = "ta-clé-ici"
```

**Permanent (Windows) :**
```powershell
[System.Environment]::SetEnvironmentVariable("GEMINI_API_KEY", "ta-clé-ici", "User")
```

### 4. Lancer l'agent

```bash
python agent.py
```

---

## 💬 Utilisation

```
╔══════════════════════════════════════════════════╗
║  🤖  Mon Agent IA — Propulsé par Gemini 3.8 Flash  ║
╠══════════════════════════════════════════════════╣
║  Outils : web · code · fichiers · calculs · météo  ║
║  Tapez  : /aide  /outils  /reset  /quitter          ║
╚══════════════════════════════════════════════════╝

Vous [1]> Quel est le carré de 1234 ?
Agent > 1234² = 1 523 756 🧮

Vous [2]> Météo à Paris demain ?
Agent > 🌍 Météo pour Paris, France
        🌡 Température : 18°C (ressenti 16°C)
        ...

Vous [3]> Cherche des infos sur Python 3.13
Agent > 📖 Python 3.13 est sorti en octobre 2024...
```

### Commandes disponibles

| Commande | Description |
|----------|-------------|
| `/aide` | Affiche l'aide |
| `/outils` | Liste les outils |
| `/reset` | Réinitialise la conversation |
| `/quitter` | Quitte l'agent |

---

## 📁 Structure du projet

```
mon-agent-ia/
├── agent.py          # 🧠 Agent principal (CLI, historique, couleurs)
├── tools.py          # 🛠️ Les 5 outils (web, code, fichiers, calculs, météo)
├── requirements.txt  # 📦 Dépendances Python
├── .gitignore        # 🙈 Fichiers ignorés par Git
└── README.md         # 📖 Ce fichier
```

---

## 🛠️ Comment ajouter un outil ?

C'est simple ! Dans [`tools.py`](tools.py), ajoute une fonction Python avec un docstring clair :

```python
def mon_outil(parametre: str) -> str:
    """Description de ce que fait l'outil.

    Args:
        parametre: Description du paramètre.
    """
    # Ta logique ici
    return "résultat"
```

Puis ajoute-la à la liste `TOUS_LES_OUTILS` en bas du fichier. C'est tout ! 🎉

---

## 🔧 Prérequis

- **Python 3.12+** → [python.org](https://www.python.org/downloads/)
- **Clé API Gemini** (gratuite) → [aistudio.google.com](https://aistudio.google.com/apikey)

---

## 📄 Licence

Ce projet est sous licence **MIT** — libre de l'utiliser, modifier et distribuer.

---

<div align="center">

Fait avec ❤️ et [Google Gemini](https://ai.google.dev)

</div>
