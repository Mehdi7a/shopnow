import streamlit as st
import firebase_admin
from firebase_admin import credentials, db as rtdb
from datetime import datetime
import uuid
import hashlib

# Configuration
st.set_page_config(page_title="ShopZone", page_icon="🛍️", layout="wide")

# ─── FIREBASE INITIALISATION (CORRIGÉE) ──────
@st.cache_resource
def init_firebase():
    try:
        if not firebase_admin._apps:
            if "firebase" in st.secrets:
                # On récupère les secrets
                creds = dict(st.secrets["firebase"])
                
                # RÉPARATION DE LA CLÉ PRIVÉE (Crucial pour l'erreur PEM)
                if "private_key" in creds:
                    # On remplace les \n textuels par de vrais sauts de ligne
                    creds["private_key"] = creds["private_key"].replace("\\n", "\n")
                
                cred = credentials.Certificate(creds)
            else:
                # Local
                cred = credentials.Certificate("firebase_credentials.json")
            
            firebase_admin.initialize_app(cred, {
                "databaseURL": "https://shopnow-ba63f-default-rtdb.europe-west1.firebasedatabase.app"
            })
        return rtdb, True, None
    except Exception as e:
        return None, False, str(e)

database, firebase_ok, firebase_error = init_firebase()

# ─── FONCTIONS CRUD ──────────────────────────
def rtdb_get(path):
    try: return rtdb.reference(path).get()
    except: return None

def rtdb_set(path, data):
    try: rtdb.reference(path).set(data); return True
    except: return False

def rtdb_delete(path):
    try: rtdb.reference(path).delete(); return True
    except: return False

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ─── LOGIQUE APP ─────────────────────────────
if not firebase_ok:
    st.error(f"Erreur connexion : {firebase_error}")
    st.stop()

if "logged" not in st.session_state:
    st.session_state.logged = False

# --- LOGIN ---
if not st.session_state.logged:
    _, col, _ = st.columns([1, 1.5, 1])
    with col:
        st.title("🛍️ Connexion")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Entrer", use_container_width=True):
            data = rtdb_get(f"users/{u}")
            if data and data.get("password") == hash_pw(p):
                st.session_state.update({"logged": True, "user": u, "role": data["role"], "name": data["name"]})
                st.rerun()
            else: st.error("Échec connexion")
    st.stop()

# --- SIDEBAR ---
with st.sidebar:
    st.write(f"Utilisateur : {st.session_state.name}")
    menu = ["Boutique"]
    if st.session_state.role == "admin": menu += ["Ajouter Produit", "Admin"]
    choice = st.radio("Menu", menu)
    if st.button("Logout"):
        st.session_state.logged = False
        st.rerun()

# --- PAGES ---
if choice == "Boutique":
    st.header("Catalogue")
    data = rtdb_get("products")
    if data:
        items = list(data.values())
        cols = st.columns(3)
        for i, itm in enumerate(items):
            with cols[i % 3]:
                if itm.get('image'): st.image(itm['image'])
                st.subheader(itm['name'])
                st.write(f"Poids: {itm.get('weight', 'N/D')} | Prix: {itm['price']} DT")
    else: st.info("Vide")

elif choice == "Ajouter Produit":
    st.header("Nouvel Article")
    n = st.text_input("Nom")
    w = st.text_input("Poids (ex: 100g)")
    p = st.number_input("Prix", min_value=0.0)
    img = st.text_input("URL Image")
    if st.button("Ajouter"):
        if n and w:
            pid = str(uuid.uuid4())[:8]
            rtdb_set(f"products/{pid}", {"id": pid, "name": n, "weight": w, "price": p, "image": img})
            st.success("Ajouté !")
        else: st.warning("Nom et Poids obligatoires")

elif choice == "Admin":
    st.header("Gestion")
    data = rtdb_get("products")
    if data:
        for k, v in data.items():
            c1, c2 = st.columns([4, 1])
            c1.write(f"{v['name']} - {v.get('weight')}")
            if c2.button("Supprimer", key=k):
                rtdb_delete(f"products/{k}")
                st.rerun()
