import streamlit as st
import firebase_admin
from firebase_admin import credentials, db as rtdb
from datetime import datetime
import uuid
import hashlib
import os

st.set_page_config(page_title="ShopZone", page_icon="🛍️", layout="wide")

# ─── CUSTOM CSS ─────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800&family=Poppins:wght@400;500;600;700&display=swap');
html, body, [class*="css"] { font-family: 'Poppins', sans-serif; }
.stApp { background: #f5f6fa; color: #1a1a2e; }
section[data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #e8eaf0; box-shadow: 2px 0 12px rgba(0,0,0,0.04); }
.hero { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); border-radius: 24px; padding: 52px 56px; margin-bottom: 36px; color: white; position: relative; overflow: hidden; }
.product-card { background: #ffffff; border-radius: 20px; overflow: hidden; box-shadow: 0 4px 20px rgba(0,0,0,0.07); transition: transform 0.25s ease; margin-bottom: 24px; }
.product-card:hover { transform: translateY(-6px); }
.product-img-wrap { width: 100%; height: 210px; overflow: hidden; position: relative; background: #f0f2f8; }
.product-img-wrap img { width: 100%; height: 100%; object-fit: cover; }
.product-weight { font-size: 0.75rem; color: #764ba2; font-weight: 600; background: #f3e5f5; padding: 3px 8px; border-radius: 8px; display: inline-block; margin-bottom: 14px; }
.product-price { font-size: 1.35rem; font-weight: 800; color: #667eea; }
.stock-ok { background:#e8f5e9; color:#2e7d32; font-size:0.73rem; padding:4px 10px; border-radius:20px; }
</style>
""", unsafe_allow_html=True)

# ─── FIREBASE INITIALIZATION ────────────────
@st.cache_resource
def init_firebase():
    try:
        if not firebase_admin._apps:
            # Priorité aux Secrets Streamlit (Cloud), sinon fichier local
            if "firebase" in st.secrets:
                creds_dict = dict(st.secrets["firebase"])
                creds_dict["private_key"] = creds_dict["private_key"].replace("\\n", "\n")
                cred = credentials.Certificate(creds_dict)
            else:
                cred = credentials.Certificate("firebase_credentials.json")
            
            firebase_admin.initialize_app(cred, {
                "databaseURL": "https://shopnow-ba63f-default-rtdb.europe-west1.firebasedatabase.app"
            })
        return rtdb, True, None
    except Exception as e:
        return None, False, str(e)

database, firebase_ok, firebase_error = init_firebase()

# ─── DATABASE HELPER FUNCTIONS ──────────────
def rtdb_get(path):
    try:
        return rtdb.reference(path).get()
    except: return None

def rtdb_set(path, data):
    try:
        rtdb.reference(path).set(data); return True
    except: return False

def rtdb_delete(path):
    try:
        rtdb.reference(path).delete(); return True
    except: return False

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ─── DATA MODELS ────────────────────────────
def get_products():
    data = rtdb_get("products")
    return list(data.values()) if data else []

def get_users():
    data = rtdb_get("users")
    return data if data else {}

def login_user(username, password):
    data = rtdb_get(f"users/{username}")
    if data and data.get("password") == hash_pw(password):
        return True, data["role"], data["name"]
    return False, None, None

def register_user(username, password, name):
    if rtdb_get(f"users/{username}"): return False
    return rtdb_set(f"users/{username}", {"name": name, "password": hash_pw(password), "role": "user"})

def add_product(product):
    pid = str(uuid.uuid4())[:8]
    product["id"] = pid
    return rtdb_set(f"products/{pid}", product)

# ─── AUTHENTICATION CHECK ───────────────────
if not firebase_ok:
    st.error(f"Erreur Firebase: {firebase_error}")
    st.stop()

if "logged" not in st.session_state:
    st.session_state.logged = False

# ─── LOGIN PAGE ─────────────────────────────
if not st.session_state.logged:
    _, mid, _ = st.columns([1, 1.6, 1])
    with mid:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("<h1 style='color:#667eea'>🛍️ ShopZone</h1>", unsafe_allow_html=True)
        tab1, tab2 = st.tabs(["Connexion", "Créer un compte"])
        
        with tab1:
            u = st.text_input("Nom d'utilisateur", key="l_u")
            p = st.text_input("Mot de passe", type="password", key="l_p")
            if st.button("Se connecter", use_container_width=True):
                ok, role, name = login_user(u, p)
                if ok:
                    st.session_state.update({"logged": True, "user": u, "role": role, "name": name})
                    st.rerun()
                else: st.error("Identifiants incorrects")
        
        with tab2:
            n = st.text_input("Nom complet")
            u2 = st.text_input("Username")
            p2 = st.text_input("Password", type="password")
            if st.button("S'inscrire", use_container_width=True):
                if register_user(u2, p2, n): st.success("Compte créé !")
                else: st.error("Utilisateur déjà existant")
    st.stop()

# ─── MAIN APP ───────────────────────────────
with st.sidebar:
    st.title(f"Salut, {st.session_state.name}")
    st.write(f"Rôle: {st.session_state.role}")
    menu = ["🛒 Boutique"]
    if st.session_state.role == "admin":
        menu += ["➕ Ajouter Produit", "🛠 Admin"]
    page = st.radio("Navigation", menu)
    if st.button("Déconnexion"):
        st.session_state.logged = False
        st.rerun()

# --- PAGE: BOUTIQUE ---
if page == "🛒 Boutique":
    st.markdown('<div class="hero"><h1>Bienvenue sur ShopZone</h1><p>Le meilleur du tech et lifestyle.</p></div>', unsafe_allow_html=True)
    products = get_products()
    if products:
        cols = st.columns(3)
        for i, p in enumerate(products):
            with cols[i % 3]:
                st.markdown(f"""
                <div class="product-card">
                    <div class="product-img-wrap"><img src="{p.get('image','')}"></div>
                    <div style="padding:15px">
                        <h4>{p['name']}</h4>
                        <div class="product-weight">⚖️ {p.get('weight','N/D')}</div>
                        <p style="font-size:1.2rem; color:#667eea; font-weight:bold">{p['price']} DT</p>
                        <span class="stock-ok">Stock: {p.get('stock',0)}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

# --- PAGE: AJOUTER PRODUIT ---
elif page == "➕ Ajouter Produit":
    st.header("Nouveau Produit")
    col1, col2 = st.columns(2)
    with col1:
        n = st.text_input("Nom")
        p = st.number_input("Prix (DT)", min_value=0.0)
        w = st.text_input("Poids (ex: 200g)")
    with col2:
        s = st.number_input("Stock", min_value=0)
        img = st.text_input("URL Image")
    
    if st.button("Enregistrer"):
        if n and w:
            add_product({"name":n, "price":p, "weight":w, "stock":s, "image":img, "created_at": datetime.now().isoformat()})
            st.success("Produit ajouté !")
        else: st.error("Nom et Poids requis")

# --- PAGE: ADMIN ---
elif page == "🛠 Admin":
    st.header("Gestion Stock")
    prods = get_products()
    for pr in prods:
        c1, c2, c3 = st.columns([3, 1, 1])
        c1.write(f"**{pr['name']}** ({pr.get('weight')})")
        c2.write(f"{pr['price']} DT")
        if c3.button("Supprimer", key=pr['id']):
            rtdb_delete(f"products/{pr['id']}")
            st.rerun()
