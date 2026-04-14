import streamlit as st
import firebase_admin
from firebase_admin import credentials, db as rtdb
from datetime import datetime
import uuid
import hashlib
import os

# Configuration de la page
st.set_page_config(page_title="ShopZone", page_icon="🛍️", layout="wide")

# ─── FIREBASE INITIALISATION ────────────────
@st.cache_resource
def init_firebase():
    try:
        if not firebase_admin._apps:
            if "firebase" in st.secrets:
                creds_dict = dict(st.secrets["firebase"])
                # Correction cruciale pour l'erreur PEM (InvalidByte)
                if "private_key" in creds_dict:
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

# ─── FONCTIONS DE BASE DE DONNÉES ───────────
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

# ─── LOGIQUE AUTH ET PRODUITS ───────────────
def login_user(username, password):
    data = rtdb_get(f"users/{username}")
    if data and data.get("password") == hash_pw(password):
        return True, data["role"], data["name"]
    return False, None, None

def get_products():
    data = rtdb_get("products")
    return list(data.values()) if data else []

def add_product(product):
    pid = str(uuid.uuid4())[:8]
    product["id"] = pid
    return rtdb_set(f"products/{pid}", product)

# ─── INTERFACE UTILISATEUR (UI) ─────────────
if not firebase_ok:
    st.error(f"❌ Erreur Firebase : {firebase_error}")
    st.stop()

if "logged" not in st.session_state:
    st.session_state.logged = False

# PAGE DE CONNEXION
if not st.session_state.logged:
    _, mid, _ = st.columns([1, 1.5, 1])
    with mid:
        st.title("🛍️ ShopZone Login")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Connexion", use_container_width=True):
            ok, role, name = login_user(u, p)
            if ok:
                st.session_state.update({"logged": True, "user": u, "role": role, "name": name})
                st.rerun()
            else:
                st.error("Identifiants invalides")
    st.stop()

# BARRE LATÉRALE
with st.sidebar:
    st.title(f"Salut {st.session_state.name}")
    menu = ["Boutique"]
    if st.session_state.role == "admin":
        menu += ["Ajouter Produit", "Admin Panel"]
    page = st.radio("Menu", menu)
    if st.button("Déconnexion"):
        st.session_state.logged = False
        st.rerun()

# PAGE BOUTIQUE
if page == "Boutique":
    st.header("Nos Produits")
    prods = get_products()
    if prods:
        cols = st.columns(3)
        for i, p in enumerate(prods):
            with cols[i % 3]:
                st.subheader(p['name'])
                if p.get('image'): st.image(p['image'])
                st.write(f"Prix : {p['price']} DT")
                st.write(f"Poids : {p.get('weight', 'N/D')}")
    else:
        st.info("Aucun produit en stock.")

# PAGE AJOUT PRODUIT
elif page == "Ajouter Produit":
    st.header("Ajouter un nouvel article")
    n = st.text_input("Nom du produit")
    pr = st.number_input("Prix (DT)", min_value=0.0)
    w = st.text_input("Poids (ex: 500g)")
    img = st.text_input("Lien image")
    if st.button("Valider l'ajout"):
        if n and w:
            add_product({"name": n, "price": pr, "weight": w, "image": img, "created_at": str(datetime.now())})
            st.success("Produit ajouté !")
        else:
            st.warning("Remplis le nom et le poids !")

# PAGE ADMIN
elif page == "Admin Panel":
    st.header("Gestion du catalogue")
    prods = get_products()
    for p in prods:
        c1, c2 = st.columns([4, 1])
        c1.write(f"{p['name']} - {p['price']} DT")
        if c2.button("Supprimer", key=p['id']):
            rtdb_delete(f"products/{p['id']}")
            st.rerun()
