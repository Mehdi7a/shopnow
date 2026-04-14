import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import uuid
import hashlib

st.set_page_config(page_title="ShopZone", layout="wide")

# ─── FIREBASE ─────────────────────────────────────────────
@st.cache_resource
def init_firebase():
    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate("firebase_credentials.json")
            firebase_admin.initialize_app(cred)
        return firestore.client(), True
    except:
        return None, False

db, firebase_ok = init_firebase()

# ─── HASH ─────────────────────────────────────────────
def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ─── SEED DATA (IMPORTANT) ─────────────────────────────
def seed_products():
    if firebase_ok:
        if len(list(db.collection("products").stream())) == 0:
            sample = [
                {"id":"p1","name":"Produit Test","brand":"Test","category":"Electronics","price":100,"stock":10}
            ]
            for p in sample:
                db.collection("products").document(p["id"]).set(p)

def seed_admin():
    if firebase_ok:
        ref = db.collection("users").document("admin")
        if not ref.get().exists:
            ref.set({
                "name":"Admin",
                "password":hash_pw("admin123"),
                "role":"admin"
            })

seed_products()
seed_admin()

# ─── GET DATA ─────────────────────────────────────────────
def get_products():
    if firebase_ok:
        docs = db.collection("products").stream()
        return [{"id":d.id, **d.to_dict()} for d in docs]
    return []

def get_users():
    if firebase_ok:
        docs = db.collection("users").stream()
        return {d.id: d.to_dict() for d in docs}
    return {}

# ─── AUTH ─────────────────────────────────────────────
def login_user(username, password):
    if firebase_ok:
        doc = db.collection("users").document(username).get()
        if doc.exists:
            data = doc.to_dict()
            if data["password"] == hash_pw(password):
                return True, data["role"], data["name"]
    return False, None, None

def register_user(username, password, name):
    if firebase_ok:
        if db.collection("users").document(username).get().exists:
            return False
        db.collection("users").document(username).set({
            "name":name,
            "password":hash_pw(password),
            "role":"user"
        })
        return True
    return False

# ─── PRODUITS ─────────────────────────────────────────────
def add_product(product):
    product_id = str(uuid.uuid4())[:8]
    product["id"] = product_id
    db.collection("products").document(product_id).set(product)

def delete_product(pid):
    db.collection("products").document(pid).delete()

# ─── SESSION ─────────────────────────────────────────────
if "logged" not in st.session_state:
    st.session_state.logged = False

# ─── LOGIN PAGE ─────────────────────────────────────────────
if not st.session_state.logged:

    tab1, tab2 = st.tabs(["Login", "Register"])

    with tab1:
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Login"):
            ok, role, name = login_user(u, p)
            if ok:
                st.session_state.logged = True
                st.session_state.user = u
                st.session_state.role = role
                st.session_state.name = name
                st.rerun()
            else:
                st.error("Wrong credentials")

    with tab2:
        n = st.text_input("Name")
        u = st.text_input("Username")
        p = st.text_input("Password", type="password")
        if st.button("Register"):
            if register_user(u, p, n):
                st.success("Account created")
            else:
                st.error("User exists")

    st.stop()

# ─── APP ─────────────────────────────────────────────
st.sidebar.write(f"👤 {st.session_state.name}")
st.sidebar.write(f"Role: {st.session_state.role}")

menu = ["Shop"]
if st.session_state.role == "admin":
    menu += ["Add Product", "Admin Panel"]

page = st.sidebar.selectbox("Menu", menu)

# ─── SHOP ─────────────────────────────────────────────
if page == "Shop":
    products = get_products()

    for p in products:
        st.write(f"### {p['name']}")
        st.write(f"Price: {p['price']} DT")
        st.write(f"Stock: {p['stock']}")
        st.divider()

# ─── ADD PRODUCT ─────────────────────────────────────────────
elif page == "Add Product":
    name = st.text_input("Name")
    price = st.number_input("Price")
    stock = st.number_input("Stock")

    if st.button("Add"):
        add_product({
            "name":name,
            "price":price,
            "stock":stock,
            "created_at":datetime.now().isoformat()
        })
        st.success("Added!")
        st.rerun()

# ─── ADMIN PANEL ─────────────────────────────────────────────
elif page == "Admin Panel":

    st.subheader("Products")
    for p in get_products():
        col1, col2 = st.columns([4,1])
        with col1:
            st.write(p["name"])
        with col2:
            if st.button("Delete", key=p["id"]):
                delete_product(p["id"])
                st.rerun()

    st.subheader("Users")
    users = get_users()
    for u, data in users.items():
        st.write(f"{u} - {data['role']}")
