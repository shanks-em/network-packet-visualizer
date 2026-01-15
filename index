import streamlit as st
import time
import plotly.graph_objects as go
from datetime import datetime
import pandas as pd

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
    .step-card {
        padding: 20px;
        border-radius: 10px;
        border-left: 5px solid #667eea;
        background-color: #f8f9ff;
        margin: 10px 0;
    }
    .security-badge {
        background-color: #4caf50;
        color: white;
        padding: 5px 15px;
        border-radius: 15px;
        font-size: 0.9em;
        font-weight: bold;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
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

# Définition des nœuds du réseau
nodes = [
    {"id": "pc", "icon": "💻", "label": "Votre PC", "x": 0, "y": 2},
    {"id": "firewall1", "icon": "🛡️", "label": "Pare-feu Local", "x": 1, "y": 2},
    {"id": "router", "icon": "📡", "label": "Routeur/FAI", "x": 2, "y": 2},
    {"id": "internet", "icon": "☁️", "label": "Internet", "x": 3, "y": 2},
    {"id": "firewall2", "icon": "🛡️", "label": "Pare-feu Serveur", "x": 4, "y": 2},
    {"id": "server", "icon": "🖥️", "label": "Serveur", "x": 5, "y": 2}
]

# Définition des étapes
steps = [
    {"node": 0, "title": "🔵 Initialisation", "desc": "Le navigateur crée une requête HTTP/HTTPS", "security": False},
    {"node": 0, "title": "🔍 Résolution DNS", "desc": "Conversion du nom de domaine en adresse IP", "security": False},
    {"node": 0, "title": "🔒 Chiffrement TLS", "desc": "Le paquet est chiffré avec SSL/TLS", "security": True},
    {"node": 1, "title": "🛡️ Pare-feu sortant", "desc": "Vérification que la connexion est autorisée", "security": True},
    {"node": 2, "title": "📡 Routage", "desc": "Le routeur envoie le paquet vers Internet", "security": False},
    {"node": 3, "title": "☁️ Transit Internet", "desc": "Passage par plusieurs routeurs intermédiaires", "security": False},
    {"node": 4, "title": "🛡️ Pare-feu entrant", "desc": "Le serveur vérifie la légitimité du paquet", "security": True},
    {"node": 5, "title": "📥 Réception", "desc": "Le serveur déchiffre et traite la requête", "security": False},
    {"node": 5, "title": "✅ Réponse", "desc": "Le serveur envoie les données demandées", "security": False}
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
        start_btn = st.button("🚀 Démarrer", use_container_width=True, type="primary")
    with col2:
        reset_btn = st.button("🔄 Reset", use_container_width=True)
    
    st.divider()
    
    # Informations techniques
    st.header("📊 Informations")
    st.info("""
    **Ce que vous allez voir :**
    - 🔐 Chiffrement TLS/SSL
    - 🛡️ Pare-feu (entrée/sortie)
    - 📡 Routage réseau
    - ☁️ Transit Internet
    - ✅ Vérifications sécurité
    """)
    
    if protocol == "HTTP (Non sécurisé)":
        st.warning("⚠️ HTTP n'est pas sécurisé ! Vos données peuvent être interceptées.")
    else:
        st.success("✅ HTTPS est sécurisé avec chiffrement TLS.")

# Fonction pour créer le graphique du réseau
def create_network_graph(current_step, packet_position):
    fig = go.Figure()
    
    # Ajouter les connexions (lignes)
    for i in range(len(nodes) - 1):
        fig.add_trace(go.Scatter(
            x=[nodes[i]["x"], nodes[i+1]["x"]],
            y=[nodes[i]["y"], nodes[i+1]["y"]],
            mode='lines',
            line=dict(color='rgba(102, 126, 234, 0.3)', width=3),
            hoverinfo='none',
            showlegend=False
        ))
    
    # Ajouter les nœuds
    node_x = [node["x"] for node in nodes]
    node_y = [node["y"] for node in nodes]
    node_text = [f"{node['icon']}<br>{node['label']}" for node in nodes]
    
    fig.add_trace(go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers+text',
        marker=dict(
            size=60,
            color='white',
            line=dict(color='#667eea', width=3)
        ),
        text=[node["icon"] for node in nodes],
        textfont=dict(size=30),
        textposition="middle center",
        hovertext=node_text,
        hoverinfo='text',
        showlegend=False
    ))
    
    # Ajouter les labels des nœuds
    fig.add_trace(go.Scatter(
        x=node_x,
        y=[y - 0.3 for y in node_y],
        mode='text',
        text=[node["label"] for node in nodes],
        textfont=dict(size=12, color='#333'),
        hoverinfo='none',
        showlegend=False
    ))
    
    # Ajouter le paquet en mouvement
    if packet_position is not None:
        packet_icon = "🔒" if current_step >= 2 else "📦"
        fig.add_trace(go.Scatter(
            x=[packet_position[0]],
            y=[packet_position[1]],
            mode='markers+text',
            marker=dict(size=40, color='#f5576c'),
            text=packet_icon,
            textfont=dict(size=25),
            textposition="middle center",
            hovertext="Paquet réseau",
            hoverinfo='text',
            showlegend=False
        ))
    
    # Configuration du layout
    fig.update_layout(
        height=400,
        showlegend=False,
        hovermode='closest',
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 5.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[0.5, 3.5]),
        plot_bgcolor='rgba(248, 249, 255, 0.5)',
        paper_bgcolor='white',
        margin=dict(t=20, b=20, l=20, r=20)
    )
    
    return fig

# Réinitialisation
if reset_btn:
    st.session_state.animation_running = False
    st.session_state.current_step = 0
    st.session_state.total_time = 0
    st.session_state.security_checks = 0
    st.rerun()

# Affichage des métriques
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("⏱️ Temps écoulé", f"{st.session_state.total_time:.1f}s")

with col2:
    hop_count = len(set([step["node"] for step in steps[:st.session_state.current_step + 1]])) - 1
    st.metric("🔄 Nombre de sauts", hop_count)

with col3:
    st.metric("🛡️ Vérifications sécurité", st.session_state.security_checks)

# Zone principale - Graphique du réseau
st.subheader("🗺️ Trajet du paquet réseau")

graph_placeholder = st.empty()
status_placeholder = st.empty()

# Animation
if start_btn and not st.session_state.animation_running:
    st.session_state.animation_running = True
    st.session_state.current_step = 0
    st.session_state.total_time = 0
    st.session_state.security_checks = 0
    
    start_time = time.time()
    
    for step_idx in range(len(steps)):
        st.session_state.current_step = step_idx
        current_step_data = steps[step_idx]
        current_node_idx = current_step_data["node"]
        
        # Calculer la position du paquet
        if step_idx == 0:
            packet_pos = (nodes[0]["x"], nodes[0]["y"])
        else:
            prev_node_idx = steps[step_idx - 1]["node"]
            if current_node_idx != prev_node_idx:
                # Animation du mouvement
                for progress in range(0, 101, 10):
                    t = progress / 100
                    x = nodes[prev_node_idx]["x"] + (nodes[current_node_idx]["x"] - nodes[prev_node_idx]["x"]) * t
                    y = nodes[prev_node_idx]["y"] + (nodes[current_node_idx]["y"] - nodes[prev_node_idx]["y"]) * t
                    packet_pos = (x, y)
                    
                    fig = create_network_graph(step_idx, packet_pos)
                    graph_placeholder.plotly_chart(fig, use_container_width=True, key=f"graph_{step_idx}_{progress}")
                    time.sleep(animation_speed / 20)
            else:
                packet_pos = (nodes[current_node_idx]["x"], nodes[current_node_idx]["y"])
        
        # Afficher le graphique
        fig = create_network_graph(step_idx, packet_pos)
        graph_placeholder.plotly_chart(fig, use_container_width=True, key=f"graph_final_{step_idx}")
        
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
    
    # Animation terminée
    status_placeholder.success("✅ Paquet transmis avec succès ! Toutes les vérifications de sécurité sont passées.")
    st.balloons()
    st.session_state.animation_running = False

else:
    # Affichage statique initial
    fig = create_network_graph(st.session_state.current_step, None)
    graph_placeholder.plotly_chart(fig, use_container_width=True)
    
    if st.session_state.current_step == 0:
        status_placeholder.info("👆 Cliquez sur '🚀 Démarrer' dans la barre latérale pour lancer la simulation")

# Section d'information
st.divider()
st.subheader("📋 Détails des étapes de transmission")

cols = st.columns(3)
for idx, step in enumerate(steps):
    col_idx = idx % 3
    with cols[col_idx]:
        security_indicator = "🔒" if step["security"] else "🔓"
        with st.expander(f"{security_indicator} {step['title']}", expanded=False):
            st.write(step["desc"])
            if step["security"]:
                st.success("Cette étape inclut des mesures de sécurité")

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 20px;'>
    <p>💡 <strong>Projet réalisé pour vulgariser la communication réseau sécurisée</strong></p>
    <p>Technologies : Python • Streamlit • Plotly • Cybersécurité</p>
</div>
""", unsafe_allow_html=True)
