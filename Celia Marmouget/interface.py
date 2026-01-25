import streamlit as st


# -----------------------
# Configuration page
# -----------------------
st.set_page_config(
    page_title="Agent CNRS",
    page_icon="logo_cnrs.png", 
    layout="wide"
)

# -----------------------
# CSS Personnalisé (Style CNRS & Relief Gemini)
# -----------------------
st.markdown("""
<style>
/* Fond de la page */
.stApp {
    background-color: #f8f9fa;
}

/* Sidebar blanche et propre */
[data-testid="stSidebar"] {
    background-color: #ffffff;
    border-right: 1px solid #e0e0e0;
}

/* Conteneur principal du chat */
.main-chat-wrapper {
    max-width: 850px;
    margin: auto;
    padding: 20px;
}

/* En-tête avec titre agrandi */
.header-container {
    text-align: center;
    border-bottom: 2px solid #002957;
    margin-bottom: 35px;
    padding-bottom: 15px;
}

.title {
    color: #002957;
    font-size: 36px; /* Taille augmentée */
    font-weight: 900; /* Plus gros/gras */
    letter-spacing: -0.5px;
    line-height: 1.2;
}

/* Bulles de chat */
.message-row {
    display: flex;
    margin-bottom: 20px;
    width: 100%;
}
.row-assistant { justify-content: flex-start; }
.row-user { justify-content: flex-end; }

.bubble {
    padding: 14px 20px;
    border-radius: 20px;
    max-width: 75%;
    font-size: 15px;
    line-height: 1.5;
}

.assistant-bubble {
    background-color: #002957;
    color: white;
    border-bottom-left-radius: 4px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
}

.user-bubble {
    background-color: #ffffff;
    color: #333;
    border: 1px solid #e0e0e0;
    border-bottom-right-radius: 4px;
    box-shadow: 0 2px 5px rgba(0,0,0,0.05);
}

/* ZONE DE SAISIE EN RELIEF (Style Gemini) */
div[data-testid="stTextInput"] > div {
    background-color: #ffffff !important; 
    border-radius: 28px !important;
    padding: 8px 20px !important;
    border: 1px solid #d1d5db !important;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important; 
    transition: all 0.3s ease-in-out;
}

div[data-testid="stTextInput"] > div:focus-within {
    border: 1px solid #002957 !important;
    box-shadow: 0 6px 16px rgba(0, 41, 87, 0.15) !important;
    transform: translateY(-1px);
}

input[data-testid="stTextInputInternal"] {
    background-color: transparent !important;
}
</style>
""", unsafe_allow_html=True)

# -----------------------
# Initialisation de l'historique
# -----------------------
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Bonjour 👋, je suis l’agent spécialisé du CNRS.\n\nComment puis-je vous aider dans votre candidature aux concours ?"
    }]

# -----------------------
# Fonctions de gestion
# -----------------------
def send_message(text):
    if text:
        st.session_state.messages.append({"role": "user", "content": text})
        query = text.lower()
        if any(word in query for word in ["concours", "insc", "date", "grade", "bap"]):
            reply = "📄 Les informations sur les concours CNRS sont disponibles sur le portail emploi. Les campagnes de recrutement ITRF (Ingénieurs et Personnels Techniques de Recherche et de Formation) se déroulent généralement une fois par an."
        else:
            reply = "❌ Je suis un agent spécialisé uniquement sur les questions de concours au CNRS. Pourriez-vous préciser votre demande ?"
        st.session_state.messages.append({"role": "assistant", "content": reply})

def handle_input():
    user_text = st.session_state.main_input
    send_message(user_text)
    st.session_state.main_input = "" 

# -----------------------
# Barre latérale (Sidebar)
# -----------------------
with st.sidebar:
    st.image("logo_cnrs.png", width=120) 
    st.markdown("### Navigation")
    if st.button("🏠 Revenir à l'accueil", use_container_width=True):
        st.session_state.messages = [st.session_state.messages[0]]
        st.rerun()

    st.markdown("---")
    st.markdown("### Idées de questions")
    
    questions_types = [
        "Quels sont les types de concours ?",
        "Comment s'inscrire ?",
        "Quelles sont les dates limites ?",
        "Quels sont les grades disponibles ?"
    ]
    
    for q in questions_types:
        if st.button(q, use_container_width=True):
            send_message(q)
            st.rerun()

# -----------------------
# Affichage Principal
# -----------------------
st.markdown('<div class="main-chat-wrapper">', unsafe_allow_html=True)

# Header avec nouveau titre
st.markdown('<div class="header-container"><div class="title">Posez une question à votre agent CNRS !</div></div>', unsafe_allow_html=True)

# Historique des bulles
for msg in st.session_state.messages:
    side = "row-assistant" if msg["role"] == "assistant" else "row-user"
    bubble_type = "assistant-bubble" if msg["role"] == "assistant" else "user-bubble"
    st.markdown(
        f'<div class="message-row {side}"><div class="bubble {bubble_type}">{msg["content"]}</div></div>',
        unsafe_allow_html=True
    )

# Saisie utilisateur
st.text_input(
    "Votre message :", 
    key="main_input", 
    placeholder="Écrivez votre question ici...", 
    on_change=handle_input
)

st.markdown('</div>', unsafe_allow_html=True)