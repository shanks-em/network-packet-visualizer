import streamlit as st
import time

st.set_page_config(
    page_title="Network Packet Visualizer",
    page_icon="🌐",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── CSS GLOBAL DARK TERMINAL ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;700&display=swap');

/* ── ROOT ── */
:root {
    --bg:       #050c12;
    --bg2:      #0a1520;
    --bg3:      #0d1e2e;
    --panel:    #0a1929;
    --border:   #0e2d40;
    --border2:  #164060;
    --accent:   #00d4aa;
    --accent2:  #00a8ff;
    --warn:     #f5a623;
    --danger:   #ff4d4d;
    --muted:    #3a7a8a;
    --sub:      #1a4a5a;
    --font:     'JetBrains Mono', monospace;
}

/* ── GLOBAL OVERRIDES ── */
html, body, [data-testid="stApp"] {
    background: var(--bg) !important;
    font-family: var(--font) !important;
    color: #c8e8f0 !important;
}
[data-testid="stSidebar"] {
    background: var(--bg2) !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: #8ab8c8 !important; font-family: var(--font) !important; }
[data-testid="stSidebarContent"] { padding: 1rem !important; }

/* Sidebar title */
[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3 {
    color: var(--accent) !important;
    font-size: 11px !important;
    letter-spacing: .12em !important;
    text-transform: uppercase !important;
    border-bottom: 1px solid var(--border) !important;
    padding-bottom: 6px !important;
    margin-bottom: 10px !important;
}

/* Inputs */
[data-testid="stTextInput"] input,
[data-testid="stSelectbox"] select,
div[data-baseweb="select"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border2) !important;
    color: var(--accent) !important;
    font-family: var(--font) !important;
    font-size: 12px !important;
    border-radius: 3px !important;
}
div[data-baseweb="select"] * { color: #8ab8c8 !important; font-size: 12px !important; }

/* Slider */
[data-testid="stSlider"] { filter: hue-rotate(160deg) !important; }

/* Buttons */
[data-testid="stButton"] button {
    background: transparent !important;
    border: 1px solid var(--accent) !important;
    color: var(--accent) !important;
    font-family: var(--font) !important;
    font-size: 11px !important;
    letter-spacing: .08em !important;
    border-radius: 2px !important;
    padding: 6px 14px !important;
    transition: all .2s !important;
}
[data-testid="stButton"] button:hover {
    background: var(--accent) !important;
    color: var(--bg) !important;
}
[data-testid="stButton"][data-key*="start"] button,
button[kind="primary"] {
    background: var(--accent) !important;
    color: var(--bg) !important;
    font-weight: 700 !important;
}

/* Expander */
[data-testid="stExpander"] {
    background: var(--bg3) !important;
    border: 1px solid var(--border) !important;
    border-radius: 3px !important;
}
[data-testid="stExpander"] summary { color: #5a9aaa !important; font-size: 11px !important; }

/* Divider */
hr { border-color: var(--border) !important; margin: 10px 0 !important; }

/* Warning / success in sidebar */
[data-testid="stAlert"] {
    background: var(--bg3) !important;
    border-left: 3px solid var(--warn) !important;
    border-radius: 2px !important;
    font-size: 11px !important;
}

/* Scrollbar */
::-webkit-scrollbar { width: 4px; height: 4px; }
::-webkit-scrollbar-track { background: var(--bg2); }
::-webkit-scrollbar-thumb { background: var(--sub); border-radius: 2px; }

/* Hide streamlit chrome */
#MainMenu, footer, header { visibility: hidden; }
[data-testid="stDecoration"] { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
</style>
""", unsafe_allow_html=True)

# ── SESSION STATE ─────────────────────────────────────────────────────────────
if 'animation_running' not in st.session_state:
    st.session_state.animation_running = False
if 'current_step' not in st.session_state:
    st.session_state.current_step = 0
if 'total_time' not in st.session_state:
    st.session_state.total_time = 0.0
if 'security_checks' not in st.session_state:
    st.session_state.security_checks = 0
if 'packet_position' not in st.session_state:
    st.session_state.packet_position = 0

# ── DATA ─────────────────────────────────────────────────────────────────────
nodes = [
    {"id": "pc",       "icon": "🖥",  "label": "YOUR MACHINE", "sub": "192.168.1.10"},
    {"id": "fw1",      "icon": "🛡",  "label": "ISP Gateway",  "sub": "12ms"},
    {"id": "router",   "icon": "📡",  "label": "Router",       "sub": "10ms"},
    {"id": "ixp",      "icon": "🖧",  "label": "IXP Paris",    "sub": "45ms"},
    {"id": "frankfurt","icon": "🌐",  "label": "Frankfurt DC", "sub": "142ms"},
    {"id": "dest",     "icon": "🎯",  "label": "DESTINATION",  "sub": "google.com"},
]

steps = [
    {"node": 0, "title": "Initialisation",       "desc": "Création de la requête HTTP/HTTPS par le navigateur", "security": False},
    {"node": 0, "title": "Résolution DNS",        "desc": "Conversion nom de domaine → adresse IP (ex: 8.8.8.8)", "security": False},
    {"node": 0, "title": "Chiffrement TLS",       "desc": "Chiffrement SSL/TLS du paquet pour protéger les données", "security": True},
    {"node": 1, "title": "Pare-feu sortant",      "desc": "Vérification que la connexion est autorisée à quitter le réseau", "security": True},
    {"node": 2, "title": "Routage FAI",           "desc": "Le routeur envoie le paquet vers Internet via votre FAI", "security": False},
    {"node": 3, "title": "IXP Paris",             "desc": "Point d'échange Internet — transit entre opérateurs", "security": False},
    {"node": 4, "title": "Frankfurt DC",          "desc": "Data center Frankfurt — nœud Google backbone", "security": False},
    {"node": 4, "title": "Pare-feu entrant",      "desc": "Le serveur vérifie la légitimité du paquet", "security": True},
    {"node": 5, "title": "Réception & Réponse",  "desc": "Déchiffrement, traitement et envoi de la réponse", "security": False},
]

HOP_TABLE = [
    (1,  "192.168.1.1",   "gateway",             "Local",          "🟢", 2,   "ok"),
    (2,  "10.10.0.1",     "isp-gateway.bj",      "Cotonou, Bénin", "🇧🇯", 12,  "ok"),
    (3,  "41.203.64.1",   "backbone-west-africa","West Africa IXP","🌍", 28,  "ok"),
    (5,  "195.66.224.1",  "linx.net",            "Paris, France",  "🇫🇷", 45,  "warn"),
    (8,  "142.250.78.1",  "google-dc-fra",       "Frankfurt, DE",  "🇩🇪", 142, "warn"),
    (12, "8.8.8.8",       "dns.google",          "Google Cloud",   "🌐", 245, "hi"),
]

# ── SIDEBAR ──────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙ Contrôles")
    url_input = st.text_input("", value="google.com", placeholder="Destination")
    protocol  = st.selectbox("Protocole", ["HTTPS (Sécurisé)", "HTTP (Non sécurisé)"], label_visibility="collapsed")
    anim_speed = st.slider("Vitesse", 0.5, 3.0, 1.2, 0.5)

    st.markdown("---")
    c1, c2 = st.columns(2)
    with c1:
        start_btn = st.button("▶ START", use_container_width=True,
                              disabled=st.session_state.animation_running)
    with c2:
        reset_btn = st.button("↺ RESET", use_container_width=True)

    st.markdown("---")
    st.markdown("### 📊 Infos")

    with st.expander("🔐 TLS/SSL"):
        st.write("Chiffrement bout en bout · Échange de clés · Auth serveur")
    with st.expander("🛡 Pare-feux"):
        st.write("Filtrage entrant/sortant · Analyse paquets temps réel")
    with st.expander("📡 Routage"):
        st.write("Meilleur chemin · Tables de routage · Transit FAI")

    st.markdown("---")
    if protocol == "HTTP (Non sécurisé)":
        st.warning("⚠ HTTP non sécurisé — données en clair")
    else:
        st.success("✅ HTTPS — chiffrement TLS actif")

# ── RESET ─────────────────────────────────────────────────────────────────────
if reset_btn:
    for k in ['animation_running','current_step','total_time','security_checks','packet_position']:
        st.session_state[k] = False if k == 'animation_running' else 0
    st.rerun()

# ── HEADER BAR ────────────────────────────────────────────────────────────────
step_done = st.session_state.current_step
hops_done = min(step_done, 12)
rtt_done  = int(245 * (step_done / max(len(steps)-1, 1)))

st.markdown(f"""
<div style="
    display:flex; align-items:center; gap:20px;
    padding:10px 20px;
    background:#0a1520;
    border-bottom:1px solid #0e2d40;
    font-family:'JetBrains Mono',monospace;
    font-size:12px;
">
  <span style="color:#00d4aa;font-size:15px;font-weight:700;letter-spacing:.05em">
    🌐 Network Packet Visualizer
  </span>
  <div style="
    flex:1; max-width:500px;
    background:#0d1e2e; border:1px solid #164060;
    border-radius:3px; padding:6px 12px;
    color:#00d4aa;
  ">
    <span style="color:#3a7a8a">$ </span>
    traceroute {url_input} --visualize --geo
    <span style="
      display:inline-block;width:8px;height:12px;
      background:#00d4aa;margin-left:4px;
      animation:blink 1s step-end infinite;vertical-align:middle
    "></span>
  </div>
  <span style="color:#3a7a8a">●</span>
  <span style="color:#8ab8c8">{hops_done} hops</span>
  <span style="color:#f5a623">●</span>
  <span style="color:#8ab8c8">{rtt_done}ms RTT</span>
  <span style="color:#00d4aa">●</span>
  <span style="color:#8ab8c8">Trace {'complet' if step_done >= len(steps)-1 else 'en cours...'}</span>
</div>
<style>
@keyframes blink{{0%,100%{{opacity:1}}50%{{opacity:0}}}}
</style>
""", unsafe_allow_html=True)

# ── MAIN LAYOUT : canvas + panel ─────────────────────────────────────────────
col_canvas, col_panel = st.columns([3, 1], gap="small")

# ── CANVAS ────────────────────────────────────────────────────────────────────
with col_canvas:
    network_ph = st.empty()

    def build_network_html(active_node: int, step_idx: int) -> str:
        # node positions (percentage) along a gentle S-curve
        positions = [
            (8,  72),
            (20, 55),
            (33, 65),
            (48, 52),
            (63, 38),
            (85, 30),
        ]

        # SVG paths between nodes
        paths_html = ""
        for i in range(len(nodes) - 1):
            x1, y1 = positions[i]
            x2, y2 = positions[i+1]
            done = (i < active_node)
            color = "#00d4aa" if done else "#0e2d40"
            dash  = "none" if done else "6 5"
            paths_html += f"""
            <line x1="{x1}%" y1="{y1}%"
                  x2="{x2}%" y2="{y2}%"
                  stroke="{color}" stroke-width="1.5"
                  stroke-dasharray="{dash}" opacity="0.7"/>
            """

        # animated packet dot on active segment
        packet_html = ""
        if 0 <= active_node < len(nodes) - 1:
            x1, y1 = positions[active_node]
            x2, y2 = positions[active_node+1]
            mx = (x1 + x2) / 2
            my = (y1 + y2) / 2
            packet_html = f"""
            <circle cx="{mx}%" cy="{my}%"
                    r="4" fill="#ffffff"
                    style="filter:drop-shadow(0 0 6px #00d4aa)">
              <animate attributeName="cx"
                from="{x1}%" to="{x2}%"
                dur="0.8s" repeatCount="indefinite"/>
              <animate attributeName="cy"
                from="{y1}%" to="{y2}%"
                dur="0.8s" repeatCount="indefinite"/>
            </circle>
            """

        # node circles
        nodes_html = ""
        for i, (node, (px, py)) in enumerate(zip(nodes, positions)):
            is_active = (i == active_node)
            is_done   = (i < active_node)
            is_src    = (i == 0)
            is_dst    = (i == len(nodes)-1)

            r_outer = 38 if (is_src or is_dst) else 28
            r_inner = 26 if (is_src or is_dst) else 18

            if is_active:
                ring_color = "#00d4aa"
                ring_opacity = "0.5"
                fill_color  = "#0a1929"
                icon_color  = "#00d4aa"
            elif is_done:
                ring_color = "#00d4aa"
                ring_opacity = "0.25"
                fill_color  = "#0a1929"
                icon_color  = "#00d4aa"
            elif is_src:
                ring_color = "#00a8ff"
                ring_opacity = "0.4"
                fill_color  = "#050c12"
                icon_color  = "#00a8ff"
            elif is_dst:
                ring_color = "#f5a623"
                ring_opacity = "0.4"
                fill_color  = "#050c12"
                icon_color  = "#f5a623"
            else:
                ring_color = "#0e2d40"
                ring_opacity = "1"
                fill_color  = "#0a1929"
                icon_color  = "#1a4a5a"

            pulse = ""
            if is_active:
                pulse = f"""
                <circle cx="{px}%" cy="{py}%"
                        r="{r_outer+6}" fill="none"
                        stroke="{ring_color}" stroke-width="1" opacity="0.3">
                  <animate attributeName="r"
                    values="{r_outer};{r_outer+14};{r_outer}"
                    dur="1.5s" repeatCount="indefinite"/>
                  <animate attributeName="opacity"
                    values="0.4;0;0.4" dur="1.5s" repeatCount="indefinite"/>
                </circle>
                """

            label_y_off = r_outer + 14
            sub_y_off   = r_outer + 26

            nodes_html += f"""
            {pulse}
            <circle cx="{px}%" cy="{py}%"
                    r="{r_outer}" fill="none"
                    stroke="{ring_color}" stroke-width="1"
                    opacity="{ring_opacity}"/>
            <circle cx="{px}%" cy="{py}%"
                    r="{r_inner}" fill="{fill_color}"
                    stroke="{ring_color}" stroke-width="{'2' if is_active else '1'}"
                    opacity="{'1' if is_active or is_src or is_dst else '0.7'}"/>
            <text x="{px}%" y="{py}%"
                  text-anchor="middle" dominant-baseline="central"
                  font-size="{'16' if is_src or is_dst else '13'}"
                  fill="{icon_color}">{node['icon']}</text>
            <text x="{px}%" y="calc({py}% + {label_y_off}px)"
                  text-anchor="middle"
                  font-family="JetBrains Mono,monospace"
                  font-size="11" font-weight="{'600' if is_active else '400'}"
                  fill="{'#00d4aa' if is_active or is_src else '#f5a623' if is_dst else '#5a8a9a'}"
                  >{node['label']}</text>
            <text x="{px}%" y="calc({py}% + {sub_y_off}px)"
                  text-anchor="middle"
                  font-family="JetBrains Mono,monospace"
                  font-size="9"
                  fill="#2a5a6a">{node['sub']}</text>
            """

        # grid lines
        grid = ""
        for i in range(0, 101, 5):
            grid += f'<line x1="{i}%" y1="0" x2="{i}%" y2="100%" stroke="#0a1f2e" stroke-width="0.5"/>'
            grid += f'<line x1="0" y1="{i}%" x2="100%" y2="{i}%" stroke="#0a1f2e" stroke-width="0.5"/>'

        # trace label
        trace_label = f"""
        <rect x="12" y="10" width="220" height="24" rx="3"
              fill="#0a1520" stroke="#0e2d40" stroke-width="1"/>
        <text x="20" y="26" font-family="JetBrains Mono,monospace"
              font-size="10" fill="#3a7a8a">
          TRACE · <tspan fill="#00a8ff">{url_input}</tspan>
          · <tspan fill="#3a7a8a">8.8.8.8</tspan>
        </text>
        """

        # legend
        legend = """
        <rect x="12" y="calc(100% - 40px)" width="230" height="26" rx="3"
              fill="#0a1520" stroke="#0e2d40" stroke-width="1"/>
        <circle cx="26" cy="calc(100% - 27px)" r="4" fill="#00d4aa"/>
        <text x="36" y="calc(100% - 23px)" font-family="JetBrains Mono,monospace"
              font-size="9" fill="#3a7a8a">Hop actif</text>
        <circle cx="90" cy="calc(100% - 27px)" r="4" fill="#f5a623"/>
        <text x="100" y="calc(100% - 23px)" font-family="JetBrains Mono,monospace"
              font-size="9" fill="#3a7a8a">Délai élevé</text>
        <circle cx="160" cy="calc(100% - 27px)" r="4" fill="#1a4a5a"/>
        <text x="170" y="calc(100% - 23px)" font-family="JetBrains Mono,monospace"
              font-size="9" fill="#3a7a8a">Normal</text>
        """

        return f"""
        <div style="
            width:100%; height:420px;
            background:#050c12;
            border:1px solid #0e2d40;
            border-radius:4px;
            position:relative; overflow:hidden;
        ">
          <svg width="100%" height="100%"
               xmlns="http://www.w3.org/2000/svg"
               style="position:absolute;top:0;left:0">
            {grid}
            {paths_html}
            {packet_html}
            {nodes_html}
            {trace_label}
            {legend}
          </svg>
        </div>
        """

    # ── step info bar below canvas ──
    step_ph  = st.empty()

    def render_step(step_idx):
        if step_idx < len(steps):
            s = steps[step_idx]
            color = "#00d4aa" if s["security"] else "#00a8ff"
            badge = f'<span style="background:#002a1a;color:#00d4aa;border:1px solid #00d4aa;padding:2px 8px;border-radius:2px;font-size:10px;margin-left:10px">🔒 SÉCURISÉ</span>' if s["security"] else ""
            step_ph.markdown(f"""
            <div style="
                margin-top:8px; padding:12px 16px;
                background:#0a1929;
                border:1px solid #0e2d40;
                border-left:3px solid {color};
                border-radius:3px;
                font-family:'JetBrains Mono',monospace;
            ">
              <div style="font-size:12px;font-weight:700;color:{color};margin-bottom:4px">
                ▶ {s['title']} {badge}
              </div>
              <div style="font-size:11px;color:#5a9aaa">{s['desc']}</div>
            </div>
            """, unsafe_allow_html=True)
        else:
            step_ph.markdown("""
            <div style="
                margin-top:8px; padding:12px 16px;
                background:#001a0e;
                border:1px solid #00d4aa;
                border-left:3px solid #00d4aa;
                border-radius:3px;
                font-family:'JetBrains Mono',monospace;
            ">
              <div style="font-size:12px;font-weight:700;color:#00d4aa">
                ✔ Transmission réussie — 0% paquets perdus
              </div>
            </div>
            """, unsafe_allow_html=True)

    # ── metrics row ──
    st.markdown("""
    <style>
    .m-row {
        display:flex; gap:8px; margin-top:8px;
    }
    .m-card {
        flex:1; padding:10px 14px;
        background:#0a1929;
        border:1px solid #0e2d40; border-radius:3px;
        font-family:'JetBrains Mono',monospace;
    }
    .m-label { font-size:9px; color:#2a5a6a; letter-spacing:.1em; text-transform:uppercase; }
    .m-val   { font-size:18px; font-weight:700; color:#00d4aa; }
    .m-sub   { font-size:10px; color:#3a7a8a; }
    </style>
    """, unsafe_allow_html=True)

    hop_count  = min(st.session_state.current_step, 12)
    rtt_val    = int(245 * (st.session_state.current_step / max(len(steps)-1, 1)))
    sec_checks = st.session_state.security_checks

    metrics_ph = st.empty()

    def render_metrics():
        h  = min(st.session_state.current_step, 12)
        r  = int(245 * (st.session_state.current_step / max(len(steps)-1, 1)))
        sc = st.session_state.security_checks
        t  = st.session_state.total_time
        metrics_ph.markdown(f"""
        <div class="m-row">
          <div class="m-card">
            <div class="m-label">Hops totaux</div>
            <div class="m-val">{h}</div>
            <div class="m-sub">sur 12</div>
          </div>
          <div class="m-card">
            <div class="m-label">RTT total</div>
            <div class="m-val" style="color:#f5a623">{r}ms</div>
            <div class="m-sub">latence cumulée</div>
          </div>
          <div class="m-card">
            <div class="m-label">Paquets perdus</div>
            <div class="m-val">0%</div>
            <div class="m-sub">aucune perte</div>
          </div>
          <div class="m-card">
            <div class="m-label">Sécurité</div>
            <div class="m-val" style="color:#00a8ff">{sc}</div>
            <div class="m-sub">vérifications</div>
          </div>
          <div class="m-card">
            <div class="m-label">Distance est.</div>
            <div class="m-val" style="color:#8ab8c8">9 200</div>
            <div class="m-sub">km</div>
          </div>
          <div class="m-card">
            <div class="m-label">Temps sim.</div>
            <div class="m-val" style="color:#8ab8c8">{t:.1f}s</div>
            <div class="m-sub">écoulés</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

# ── RIGHT PANEL : hop list ────────────────────────────────────────────────────
with col_panel:
    st.markdown("""
    <div style="
        background:#0a1929; border:1px solid #0e2d40;
        border-radius:4px; overflow:hidden;
        font-family:'JetBrains Mono',monospace;
    ">
      <div style="
          display:flex; justify-content:space-between; align-items:center;
          padding:10px 14px; border-bottom:1px solid #0e2d40;
      ">
        <span style="font-size:10px;color:#2a5a6a;letter-spacing:.12em;text-transform:uppercase">
          Hops réseau
        </span>
        <span style="font-size:11px;color:#00d4aa">12 total</span>
      </div>
    """ + "".join([
        f"""
      <div style="
          display:flex; align-items:center; gap:8px;
          padding:8px 14px;
          border-left:2px solid {'#00d4aa' if row[0] == 8 else 'transparent'};
          background:{'#0d1e2e' if row[0] == 8 else 'transparent'};
          {'border-bottom:1px solid #050c12;' if i < len(HOP_TABLE)-1 else ''}
      ">
        <span style="font-size:9px;color:#2a5a6a;width:12px;text-align:right">{row[0]}</span>
        <div style="flex:1;min-width:0">
          <div style="font-size:11px;color:#8ab8c8;
               white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{row[1]}</div>
          <div style="font-size:9px;color:#3a7a8a;
               white-space:nowrap;overflow:hidden;text-overflow:ellipsis">{row[2]}</div>
        </div>
        <span style="font-size:12px">{row[4]}</span>
        <div style="width:3px;height:22px;background:#0a1520;border-radius:1px;flex-shrink:0">
          <div style="width:3px;height:{int(4+18*(row[5]/245))}px;
               background:{'#ff4d4d' if row[6]=='hi' else '#f5a623' if row[6]=='warn' else '#00d4aa'};
               border-radius:1px"></div>
        </div>
        <span style="font-size:11px;font-weight:700;min-width:36px;text-align:right;
              color:{'#ff4d4d' if row[6]=='hi' else '#f5a623' if row[6]=='warn' else '#00d4aa'}">{row[5]}ms</span>
      </div>
        """
        for i, row in enumerate(HOP_TABLE)
    ]) + """
      <div style="
          display:grid; grid-template-columns:1fr 1fr;
          gap:1px; background:#0e2d40;
          border-top:1px solid #0e2d40;
      ">
        <div style="padding:10px 14px;background:#0a1929">
          <div style="font-size:9px;color:#2a5a6a;text-transform:uppercase;letter-spacing:.08em">Hops totaux</div>
          <div style="font-size:14px;font-weight:700;color:#c8e8f0">12</div>
        </div>
        <div style="padding:10px 14px;background:#0a1929">
          <div style="font-size:9px;color:#2a5a6a;text-transform:uppercase;letter-spacing:.08em">RTT total</div>
          <div style="font-size:14px;font-weight:700;color:#00d4aa">245ms</div>
        </div>
        <div style="padding:10px 14px;background:#0a1929">
          <div style="font-size:9px;color:#2a5a6a;text-transform:uppercase;letter-spacing:.08em">Paquets perdus</div>
          <div style="font-size:14px;font-weight:700;color:#00d4aa">0%</div>
        </div>
        <div style="padding:10px 14px;background:#0a1929">
          <div style="font-size:9px;color:#2a5a6a;text-transform:uppercase;letter-spacing:.08em">Distance est.</div>
          <div style="font-size:14px;font-weight:700;color:#8ab8c8">9 200 km</div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

# ── ANIMATION ────────────────────────────────────────────────────────────────
# initial render
active_node = steps[st.session_state.current_step]["node"] if st.session_state.current_step < len(steps) else len(nodes)-1
network_ph.markdown(build_network_html(active_node, st.session_state.current_step), unsafe_allow_html=True)
render_step(st.session_state.current_step)
render_metrics()

if start_btn and not st.session_state.animation_running:
    st.session_state.animation_running = True
    st.session_state.current_step = 0
    st.session_state.total_time = 0.0
    st.session_state.security_checks = 0
    start_t = time.time()

    for idx, step in enumerate(steps):
        st.session_state.current_step = idx
        st.session_state.total_time   = time.time() - start_t
        if step["security"]:
            st.session_state.security_checks += 1

        an = step["node"]
        network_ph.markdown(build_network_html(an, idx), unsafe_allow_html=True)
        render_step(idx)
        render_metrics()
        time.sleep(anim_speed)

    # final state
    st.session_state.current_step = len(steps)
    network_ph.markdown(build_network_html(len(nodes)-1, len(steps)), unsafe_allow_html=True)
    render_step(len(steps))
    render_metrics()
    st.session_state.animation_running = False

# ── STEPS TABLE ──────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    margin-top:16px;
    border:1px solid #0e2d40; border-radius:4px; overflow:hidden;
    font-family:'JetBrains Mono',monospace;
">
  <div style="
      padding:8px 14px; background:#0a1929;
      border-bottom:1px solid #0e2d40;
      font-size:10px; color:#2a5a6a;
      letter-spacing:.12em; text-transform:uppercase
  ">Toutes les étapes de transmission</div>
""", unsafe_allow_html=True)

for i, s in enumerate(steps):
    color = "#00d4aa" if s["security"] else "#00a8ff"
    icon  = "🔒" if s["security"] else "⬡"
    st.markdown(f"""
  <div style="
      display:flex; align-items:center; gap:12px;
      padding:8px 14px;
      border-bottom:{'1px solid #050c12' if i < len(steps)-1 else 'none'};
      font-size:11px;
  ">
    <span style="color:{color};font-size:12px">{icon}</span>
    <span style="color:#5a8a9a;width:14px">{i+1}</span>
    <span style="color:#8ab8c8;font-weight:600">{s['title']}</span>
    <span style="color:#3a7a8a;flex:1">{s['desc']}</span>
    {'<span style="font-size:9px;color:#00d4aa;border:1px solid #00d4aa;padding:1px 6px;border-radius:2px">SECURE</span>' if s["security"] else '<span style="font-size:9px;color:#1a4a5a;border:1px solid #1a4a5a;padding:1px 6px;border-radius:2px">TRANSIT</span>'}
  </div>
    """, unsafe_allow_html=True)

st.markdown("</div>", unsafe_allow_html=True)

# ── FOOTER ────────────────────────────────────────────────────────────────────
st.markdown("""
<div style="
    margin-top:12px; padding:10px 16px;
    display:flex; justify-content:space-between; align-items:center;
    font-family:'JetBrains Mono',monospace; font-size:10px; color:#2a5a6a;
    border-top:1px solid #0e2d40;
">
  <span>Python · Streamlit · Réseau · Cybersécurité</span>
  <span>Network Packet Visualizer — Projet éducatif</span>
</div>
""", unsafe_allow_html=True)
