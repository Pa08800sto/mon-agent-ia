"""
Interface web pour l'Agent IA — propulsé par Streamlit + Gemini 3.8 Flash
"""

import os
import streamlit as st
from google import genai
from tools import TOUS_LES_OUTILS

# ──────────────────────────────────────────────
# Config de la page
# ──────────────────────────────────────────────
st.set_page_config(
    page_title="Mon Agent IA 🤖",
    page_icon="🤖",
    layout="centered",
    initial_sidebar_state="expanded",
)

MODEL = "gemini-3.8-flash"

SYSTEM_INSTRUCTION = """Tu es un assistant IA intelligent et serviable.
Tu peux utiliser plusieurs outils à ta disposition :
1. recherche_web(query) — cherche des informations sur Internet
2. executer_code_python(code) — exécute du code Python
3. lire_fichier(chemin) — lit un fichier texte local
4. calculer(expression) — calculs mathématiques avancés
5. meteo(ville) — météo en temps réel pour n'importe quelle ville

Règles :
- Utilise les outils quand c'est pertinent, sans le demander.
- Sois concis mais complet.
- Réponds toujours en français sauf si l'utilisateur parle une autre langue.
"""

# ──────────────────────────────────────────────
# CSS personnalisé
# ──────────────────────────────────────────────
st.markdown("""
<style>
    /* Fond général */
    .stApp { background-color: #0f1117; }

    /* Bulle utilisateur */
    .user-bubble {
        background: linear-gradient(135deg, #4285F4, #0F9D58);
        color: white;
        padding: 12px 18px;
        border-radius: 18px 18px 4px 18px;
        margin: 8px 0 8px 15%;
        box-shadow: 0 2px 8px rgba(66,133,244,0.3);
    }

    /* Bulle agent */
    .agent-bubble {
        background: #1e2130;
        color: #e0e0e0;
        padding: 12px 18px;
        border-radius: 18px 18px 18px 4px;
        margin: 8px 15% 8px 0;
        border-left: 3px solid #4285F4;
        box-shadow: 0 2px 8px rgba(0,0,0,0.3);
    }

    /* Badge outil */
    .tool-badge {
        display: inline-block;
        background: #2d2f3e;
        color: #a0a8c0;
        font-size: 0.75rem;
        padding: 3px 10px;
        border-radius: 12px;
        margin: 2px 2px;
        border: 1px solid #3a3d52;
    }

    /* Input chat */
    .stChatInput > div { border-radius: 24px !important; }

    /* Sidebar */
    [data-testid="stSidebar"] { background: #16192a; }

    /* Titres */
    h1 { color: #4285F4 !important; }
</style>
""", unsafe_allow_html=True)

# ──────────────────────────────────────────────
# Sidebar
# ──────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ Configuration")

    api_key = st.text_input(
        "🔑 Clé API Gemini",
        type="password",
        placeholder="AIza...",
        help="Obtiens ta clé gratuite sur https://aistudio.google.com/apikey",
        value=os.getenv("GEMINI_API_KEY", ""),
    )

    st.markdown("---")
    st.markdown("### 🛠️ Outils disponibles")
    outils_info = {
        "🌐 Recherche web": "DuckDuckGo",
        "🐍 Code Python": "Exécution sécurisée",
        "📄 Lecture fichiers": "Texte local",
        "🧮 Calculs": "sqrt, sin, pi…",
        "🌤 Météo": "Open-Meteo (temps réel)",
    }
    for nom, desc in outils_info.items():
        st.markdown(f"**{nom}** — {desc}")

    st.markdown("---")

    if st.button("🗑️ Réinitialiser la conversation", use_container_width=True):
        st.session_state.messages = []
        st.session_state.previous_interaction_id = None
        st.rerun()

    st.markdown("---")
    st.markdown(
        "<div style='text-align:center;color:#666;font-size:0.8rem'>"
        "Propulsé par<br><b>Google Gemini 3.8 Flash</b><br>"
        "<a href='https://github.com/Pa08800sto/mon-agent-ia' style='color:#4285F4'>📂 Code source</a>"
        "</div>",
        unsafe_allow_html=True,
    )

# ──────────────────────────────────────────────
# En-tête principal
# ──────────────────────────────────────────────
st.markdown(
    "<h1 style='text-align:center'>🤖 Mon Agent IA</h1>"
    "<p style='text-align:center;color:#888'>Pose-moi une question — je choisis l'outil adapté automatiquement</p>",
    unsafe_allow_html=True,
)

# ──────────────────────────────────────────────
# Initialisation de l'état
# ──────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "previous_interaction_id" not in st.session_state:
    st.session_state.previous_interaction_id = None

# ──────────────────────────────────────────────
# Affichage de l'historique
# ──────────────────────────────────────────────
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f"<div class='user-bubble'>👤 {msg['content']}</div>",
            unsafe_allow_html=True,
        )
    else:
        tools_html = ""
        if msg.get("tools_used"):
            badges = "".join(
                f"<span class='tool-badge'>🔧 {t}</span>"
                for t in msg["tools_used"]
            )
            tools_html = f"<div style='margin-bottom:6px'>{badges}</div>"

        st.markdown(
            f"<div class='agent-bubble'>{tools_html}{msg['content']}</div>",
            unsafe_allow_html=True,
        )

# ──────────────────────────────────────────────
# Input utilisateur
# ──────────────────────────────────────────────
exemples = [
    "Météo à Paris 🌤",
    "Calcule sqrt(2) * pi 🧮",
    "Cherche des infos sur Gemini 🌐",
    "Exécute : print(sum(range(100))) 🐍",
]

if not st.session_state.messages:
    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(2)
    for i, exemple in enumerate(exemples):
        if cols[i % 2].button(exemple, use_container_width=True):
            st.session_state["quick_input"] = exemple.split(" ")[0] + " " + " ".join(exemple.split(" ")[1:-1])

prompt = st.chat_input("Écris ton message ici…")

# Gestion du quick input (boutons d'exemples)
if "quick_input" in st.session_state:
    prompt = st.session_state.pop("quick_input")

# ──────────────────────────────────────────────
# Traitement du message
# ──────────────────────────────────────────────
if prompt:
    if not api_key:
        st.error("❌ Entre ta clé API Gemini dans la barre latérale pour commencer !")
        st.stop()

    # Ajoute le message utilisateur
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.markdown(
        f"<div class='user-bubble'>👤 {prompt}</div>",
        unsafe_allow_html=True,
    )

    # Appel à l'agent
    with st.spinner("🤖 L'agent réfléchit…"):
        try:
            client = genai.Client(api_key=api_key)

            kwargs = {
                "model": MODEL,
                "input": prompt,
                "tools": TOUS_LES_OUTILS,
                "system_instruction": SYSTEM_INSTRUCTION,
            }
            if st.session_state.previous_interaction_id:
                kwargs["previous_interaction_id"] = st.session_state.previous_interaction_id

            interaction = client.interactions.create(**kwargs)
            st.session_state.previous_interaction_id = interaction.id

            # Récupère les outils utilisés
            tools_used = []
            for step in (interaction.steps or []):
                if getattr(step, "type", None) == "function_call":
                    tools_used.append(step.name)

            reponse = interaction.output_text or "_(Pas de réponse textuelle)_"

            # Sauvegarde et affichage
            st.session_state.messages.append({
                "role": "assistant",
                "content": reponse,
                "tools_used": tools_used,
            })

            tools_html = ""
            if tools_used:
                badges = "".join(
                    f"<span class='tool-badge'>🔧 {t}</span>"
                    for t in tools_used
                )
                tools_html = f"<div style='margin-bottom:6px'>{badges}</div>"

            st.markdown(
                f"<div class='agent-bubble'>{tools_html}{reponse}</div>",
                unsafe_allow_html=True,
            )

        except Exception as e:
            st.error(f"❌ Erreur : {e}")
