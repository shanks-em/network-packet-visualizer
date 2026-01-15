import streamlit as st
import time

# Configuration de la page
st.set_page_config(
    page_title="Network Packet Visualizer",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-title {
        text-align: center;
        color: #667eea;
        font-size: 3em;
        font-weight: bold;
        margin-bottom: 0;
    }
    .subtitle {
        text-align: center;
        color: #666;
        font-size: 1.2em;
        margin-bottom: 2em;
    }
    .network-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 40px 20px;
        background: linear-gradient(to bottom, #f8f9ff 0%, #e8eeff 100%);
        border-radius: 15px;
        margin: 20px 0;
        min-height: 300px;
        position: relative;
    }
    .node {
        display: flex;
        flex-direction: column;
        align-items: center;
        z-index: 2;
        transition: all 0.3s;
    }
    .node-icon {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 40px;
        background: white;
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        margin-bottom: 10px;
    }
    .node-icon.active {
        animation: pulse 1s infinite;
        box-shadow: 0 5px 25px rgba(102, 126, 234, 0.5);
    }
    @keyframes pulse {
        0%, 100% { transform: scale(1); }
        50% { transform: scale(1.1); }
    }
    .node-label {
        font-weight: bold;
        color: #333;
        text-align: center;
        font-size: 14px;
    }
    .packet {
        position: absolute;
        font-size: 40px;
        animation: move 2s ease-in-out;
        z-index: 10;
    }
    .step-card {
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        background-color: #f8f9ff;
        margin: 10px 0;
        animation: slideIn 0.5s;
    }
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateX(-20px);
        }
        to {
            opacity: 1;
            transform: translateX(0);
        }
    }
    .security-badge {
        background-color: #4caf50;
        color: white;
        padding: 5px 15px;
        border-radius: 15px;
        font-size: 0.9em;
        font-weight: bold;
        display: inline-block;
        margin-left: 10px;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 30px;
        border-radius: 15px;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2.5em;
        font-weight: bold;
        margin-bottom: 10px;
    }
    .metric-label {
        font-size: 1em;
        opacity: 0.9;
    }
    .connection-line {
        position: absolute;
        height: 3px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        top: 50%;
        left: 0;
        right: 0;
        opacity: 0.3;
        z-index: 1;
    }
    .info-box {
        background: #fff3cd;
        border-left: 4px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
    .success-box {
        background: #d4edda;
        border-left: 4px solid #28a745;
        padding: 15px;
        border-radius: 5px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# Titre principal
st.markdown('<h1 class="main-title">🌐 Network Packet Visualizer</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Visualisez le voyage sécurisé de vos données sur Internet</p>', unsafe_allow_html=True)

# Initialisation des variables de session
if 'animation_running' not in st.session_state:
    st.session_state.animation_running = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'total_time' not in st.session_state:
    st.session_state.total_time = 0
if 'security_checks' not in st.session_state:
    st.session_state.security_checks = 0
if 'packet_position' not in st.session_state:
    st.session_state.packet_position = 0

# Définition des nœuds du réseau
nodes = [
    {"id": "pc", "icon": "💻", "label": "Votre PC"},
    {"id": "firewall1", "icon": "🛡️", "label": "Pare-feu Local"},
    {"id": "router", "icon": "📡", "label": "Routeur/FAI"},
    {"id": "internet", "icon": "☁️", "label": "Internet"},
    {"id": "firewall2", "icon": "🛡️", "label": "Pare-feu Serveur"},
    {"id": "server", "icon": "🖥️", "label": "Serveur"}
]

# Définition des étapes
steps = [
    {"node": 0, "title": "🔵 Initialisation", "desc": "Le navigateur crée une requête HTTP/HTTPS", "security": False},
    {"node": 0, "title": "🔍 Résolution DNS", "desc": "Conversion du nom de domaine en adresse IP (ex: google.com → 142.250.185.46)", "security": False},
    {"node": 0, "title": "🔒 Chiffrement TLS", "desc": "Le paquet est chiffré avec SSL/TLS pour protéger vos données", "security": True},
    {"node": 1, "title": "🛡️ Pare-feu sortant", "desc": "Vérification que la connexion est autorisée à quitter votre réseau", "security": True},
    {"node": 2, "title": "📡 Routage", "desc": "Le routeur envoie le paquet vers Internet via votre FAI", "security": False},
    {"node": 3, "title": "☁️ Transit Internet", "desc": "Passage par plusieurs routeurs intermédiaires (10-15 sauts en moyenne)", "security": False},
    {"node": 4, "title": "🛡️ Pare-feu entrant", "desc": "Le serveur vérifie la légitimité du paquet et bloque les menaces", "security": True},
    {"node": 5, "title": "📥 Réception", "desc": "Le serveur déchiffre et traite la requête", "security": False},
    {"node": 5, "title": "✅ Réponse", "desc": "Le serveur envoie les données demandées (page web, API, etc.)", "security": False}
]

# Sidebar - Contrôles
with st.sidebar:
    st.header("⚙️ Contrôles")
    
    url_input = st.text_input("🌐 URL de destination", value="google.com", placeholder="Ex: google.com")
    
    protocol = st.selectbox("🔐 Protocole", ["HTTPS (Sécurisé)", "HTTP (Non sécurisé)"])
    
    animation_speed = st.slider("⚡ Vitesse d'animation", min_value=0.5, max_value=3.0, value=1.5, step=0.5)
    
    st.divider()
    
    col1, col2 = st.columns(2)
    with col1:
        start_btn = st.button("🚀 Démarrer", use_container_width=True, type="primary", disabled=st.session_state.animation_running)
    with col2:
        reset_btn = st.button("🔄 Reset", use_container_width=True)
    
    st.divider()
    
    # Informations techniques
    st.header("📊 Informations")
    
    with st.expander("🔐 Qu'est-ce que TLS/SSL ?", expanded=False):
        st.write("""
        **TLS (Transport Layer Security)** chiffre vos données pour que personne ne puisse les lire pendant le transit.
        
        - 🔒 Chiffrement de bout en bout
        - 🔑 Échange de clés sécurisé
        - ✅ Authentification du serveur
        """)
    
    with st.expander("🛡️ Rôle des pare-feu", expanded=False):
        st.write("""
        Les **pare-feu** filtrent le trafic réseau :
        
        - ⛔ Bloquent les connexions suspectes
        - ✅ Autorisent le trafic légitime
        - 📊 Analysent les paquets en temps réel
        """)
    
    with st.expander("📡 Qu'est-ce qu'un routeur ?", expanded=False):
        st.write("""
        Le **routeur** dirige vos paquets :
        
        - 🗺️ Trouve le meilleur chemin
        - 🔄 Transmet entre réseaux
        - 📍 Utilise des tables de routage
        """)
    
    st.divider()
    
    if protocol == "HTTP (Non sécurisé)":
        st.warning("⚠️ **HTTP n'est pas sécurisé !**\n\nVos données peuvent être interceptées en clair.")
    else:
        st.success("✅ **HTTPS est sécurisé**\n\nChiffrement TLS actif")

# Réinitialisation
if reset_btn:
    st.session_state.animation_running = False
    st.session_state.current_step = 0
    st.session_state.total_time = 0
    st.session_state.security_checks = 0
    st.session_state.packet_position = 0
    st.rerun()

# Affichage des métriques
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{st.session_state.total_time:.1f}s</div>
        <div class="metric-label">⏱️ Temps écoulé</div>
    </div>
    """, unsafe_allow_html=True)

with col2:
    hop_count = len(set([step["node"] for step in steps[:st.session_state.current_step + 1]])) - 1 if st.session_state.current_step > 0 else 0
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{hop_count}</div>
        <div class="metric-label">🔄 Nombre de sauts</div>
    </div>
    """, unsafe_allow_html=True)

with col3:
    st.markdown(f"""
    <div class="metric-card">
        <div class="metric-value">{st.session_state.security_checks}</div>
        <div class="metric-label">🛡️ Vérifications sécurité</div>
    </div>
    """, unsafe_allow_html=True)

st.markdown("<br>", unsafe_allow_html=True)

# Zone principale - Visualisation du réseau
st.subheader("🗺️ Trajet du paquet réseau")

network_placeholder = st.empty()
status_placeholder = st.empty()

# Fonction pour afficher le réseau
def display_network(current_node_idx, packet_icon="📦"):
    nodes_html = ""
    for i, node in enumerate(nodes):
        active_class = "active" if i == current_node_idx else ""
        nodes_html += f"""
        <div class="node">
            <div class="node-icon {active_class}">{node['icon']}</div>
            <div class="node-label">{node['label']}</div>
        </div>
        """
    
    packet_html = ""
    if current_node_idx >= 0:
        packet_position = (100 / (len(nodes) - 1)) * current_node_idx
        packet_html = f'<div class="packet" style="left: {packet_position}%;">{packet_icon}</div>'
    
    return f"""
    <div class="network-container">
        <div class="connection-line"></div>
        {nodes_html}
        {packet_html}
    </div>
    """

# Animation
if start_btn and not st.session_state.animation_running:
    st.session_state.animation_running = True
    st.session_state.current_step = 0
    st.session_state.total_time = 0
    st.session_state.security_checks = 0
    st.session_state.packet_position = 0
    
    start_time = time.time()
    
    for step_idx in range(len(steps)):
        st.session_state.current_step = step_idx
        current_step_data = steps[step_idx]
        current_node_idx = current_step_data["node"]
        
        # Déterminer l'icône du paquet
        packet_icon = "🔒" if step_idx >= 2 else "📦"
        
        # Afficher le réseau
        network_placeholder.markdown(display_network(current_node_idx, packet_icon), unsafe_allow_html=True)
        
        # Afficher le statut actuel
        security_badge = '<span class="security-badge">🔒 Sécurisé</span>' if current_step_data["security"] else ''
        status_placeholder.markdown(f"""
        <div class="step-card">
            <h3>{current_step_data["title"]} {security_badge}</h3>
            <p>{current_step_data["desc"]}</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Compter les vérifications de sécurité
        if current_step_data["security"]:
            st.session_state.security_checks += 1
        
        # Mettre à jour le temps
        st.session_state.total_time = time.time() - start_time
        
        time.sleep(animation_speed)
        st.rerun()
    
    # Animation terminée
    status_placeholder.markdown("""
    <div class="success-box">
        <h3>✅ Transmission réussie !</h3>
        <p>Le paquet a été transmis avec succès. Toutes les vérifications de sécurité sont passées.</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.balloons()
    st.session_state.animation_running = False

else:
    # Affichage statique initial
    current_node = steps[st.session_state.current_step]["node"] if st.session_state.current_step < len(steps) else 0
    packet_icon = "🔒" if st.session_state.current_step >= 2 else "📦"
    network_placeholder.markdown(display_network(current_node, packet_icon), unsafe_allow_html=True)
    
    if st.session_state.current_step == 0 and not st.session_state.animation_running:
        status_placeholder.markdown("""
        <div class="info-box">
            <h3>👆 Prêt à démarrer</h3>
            <p>Cliquez sur <strong>'🚀 Démarrer'</strong> dans la barre latérale pour lancer la simulation</p>
        </div>
        """, unsafe_allow_html=True)

# Section d'information
st.divider()
st.subheader("📋 Toutes les étapes de transmission")

cols = st.columns(3)
for idx, step in enumerate(steps):
    col_idx = idx % 3
    with cols[col_idx]:
        security_indicator = "🔒" if step["security"] else "🔓"
        with st.expander(f"{security_indicator} {step['title']}", expanded=False):
            st.write(step["desc"])
            if step["security"]:
                st.success("✅ Cette étape inclut des mesures de sécurité")
            else:
                st.info("ℹ️ Étape de transmission standard")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>💡 <strong>Projet éducatif pour comprendre la communication réseau sécurisée</strong></p>
    <p><strong>Technologies :</strong> Python • Streamlit • Cybersécurité • Réseaux</p>
    <p><strong>Objectif :</strong> Vulgariser les concepts de sécurité réseau de manière interactive</p>
</div>
""", unsafe_allow_html=True)
