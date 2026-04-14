import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import uuid
import hashlib

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ShopZone",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CSS ────────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=DM+Sans:wght@400;500&display=swap');
    html, body, [class*="css"] { font-family: 'DM Sans', sans-serif; }
    .main { background-color: #f7f8fc; }

    .shop-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.2rem 2rem; border-radius: 16px; margin-bottom: 1.5rem;
        display: flex; align-items: center; justify-content: space-between;
    }
    .shop-logo { font-family:'Sora',sans-serif; font-size:2rem; font-weight:800; color:#e94560; letter-spacing:-1px; }
    .shop-tagline { color:#aab4be; font-size:0.85rem; margin-top:2px; }

    .hero-banner {
        background: linear-gradient(135deg, #e94560 0%, #c0392b 100%);
        border-radius: 20px; padding: 2rem 2.5rem; margin-bottom: 1.5rem;
        color: white; position: relative; overflow: hidden;
    }
    .hero-title { font-family:'Sora',sans-serif; font-size:2rem; font-weight:800; margin:0 0 0.5rem 0; }
    .hero-sub { font-size:0.95rem; opacity:0.85; margin-bottom:1rem; }
    .badge {
        display:inline-block; background:rgba(255,255,255,0.2);
        border:1px solid rgba(255,255,255,0.3); padding:4px 14px;
        border-radius:50px; font-size:0.78rem; margin-right:8px;
    }

    .product-card {
        background:white; border-radius:16px; overflow:hidden;
        box-shadow:0 2px 12px rgba(0,0,0,0.07);
        transition:transform 0.2s ease, box-shadow 0.2s ease;
        border:1px solid #eef0f5;
    }
    .product-card:hover { transform:translateY(-4px); box-shadow:0 8px 30px rgba(0,0,0,0.12); }
    .product-img { width:100%; height:190px; object-fit:cover; background:#f0f2f5; }
    .product-body { padding:0.9rem 1.1rem 1.1rem; }
    .product-category { font-size:0.7rem; font-weight:600; color:#e94560; text-transform:uppercase; letter-spacing:0.5px; margin-bottom:5px; }
    .product-name { font-family:'Sora',sans-serif; font-size:0.95rem; font-weight:700; color:#1a1a2e; margin-bottom:3px; line-height:1.3; }
    .product-brand { font-size:0.78rem; color:#888; margin-bottom:7px; }
    .stars { color:#f4a017; font-size:0.82rem; margin-bottom:7px; }
    .product-price { font-family:'Sora',sans-serif; font-size:1.3rem; font-weight:800; color:#1a1a2e; }
    .price-currency { font-size:0.85rem; font-weight:600; color:#666; }

    .stock-badge { display:inline-block; font-size:0.7rem; padding:2px 10px; border-radius:20px; font-weight:600; margin-left:6px; }
    .in-stock { background:#e8f8f0; color:#27ae60; }
    .low-stock { background:#fff3e0; color:#f39c12; }
    .out-stock { background:#fdecea; color:#e74c3c; }

    .stat-card { background:white; border-radius:12px; padding:1rem 1.2rem; text-align:center; box-shadow:0 2px 8px rgba(0,0,0,0.06); border:1px solid #eef0f5; }
    .stat-number { font-family:'Sora',sans-serif; font-size:1.7rem; font-weight:800; color:#e94560; }
    .stat-label { font-size:0.75rem; color:#888; margin-top:2px; }

    .order-row { background:white; border-radius:10px; padding:0.9rem 1.2rem; margin-bottom:8px; border:1px solid #eef0f5; }

    .stButton > button {
        background:#e94560 !important; color:white !important; border:none !important;
        border-radius:10px !important; font-weight:600 !important;
        font-family:'Sora',sans-serif !important; transition:all 0.2s !important;
    }
    .stButton > button:hover { background:#c0392b !important; transform:translateY(-1px) !important; }

    [data-testid="stSidebar"] { background:#1a1a2e !important; }
    [data-testid="stSidebar"] * { color:#c8cdd8 !important; }
    [data-testid="stSidebar"] h1,[data-testid="stSidebar"] h2,[data-testid="stSidebar"] h3 { color:white !important; }

    .section-title { font-family:'Sora',sans-serif; font-size:1.3rem; font-weight:700; color:#1a1a2e; margin-bottom:1rem; }

    .admin-table { width:100%; border-collapse:collapse; }
    .admin-table th { background:#1a1a2e; color:white; padding:10px 14px; font-size:0.82rem; text-align:left; }
    .admin-table td { padding:10px 14px; border-bottom:1px solid #eef0f5; font-size:0.85rem; }
    .admin-table tr:hover td { background:#f7f8fc; }

    .role-admin { background:#fff3e0; color:#f39c12; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
    .role-user { background:#e8f0fe; color:#1a73e8; padding:3px 10px; border-radius:20px; font-size:0.72rem; font-weight:700; }
</style>
""", unsafe_allow_html=True)

# ─── FIREBASE ────────────────────────────────────────────────────────────────────
@st.cache_resource
def init_firebase():
    try:
        if not firebase_admin._apps:
            if "firebase" in st.secrets:
                cred = credentials.Certificate(dict(st.secrets["firebase"]))
            else:
                cred = credentials.Certificate("firebase_credentials.json")
            firebase_admin.initialize_app(cred)
        return firestore.client(), True
    except:
        return None, False

db, firebase_ok = init_firebase()

# ─── DEMO DATA ───────────────────────────────────────────────────────────────────
DEMO_PRODUCTS = [
    {"id":"p1","name":"Sony WH-1000XM5","brand":"Sony","category":"Electronics","price":349.99,
     "description":"Casque sans fil réduction de bruit active.","specs":{"Poids":"250g","Autonomie":"30h","Bluetooth":"5.2"},"stock":12,"rating":4.8,"reviews":2341,
     "image":"https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80"},
    {"id":"p2","name":"Nike Air Max 270","brand":"Nike","category":"Sports","price":150.00,
     "description":"Chaussure running amorti Air Max.","specs":{"Taille":"40-46","Poids":"320g","Semelle":"Air Max"},"stock":5,"rating":4.5,"reviews":3421,
     "image":"https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80"},
    {"id":"p3","name":"Logitech MX Master 3S","brand":"Logitech","category":"Electronics","price":99.99,
     "description":"Souris ergonomique 8000 DPI.","specs":{"DPI":"200-8000","Poids":"141g","Autonomie":"70 jours"},"stock":20,"rating":4.7,"reviews":4231,
     "image":"https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&q=80"},
    {"id":"p4","name":"Philips Air Fryer XL","brand":"Philips","category":"Home & Kitchen","price":159.99,
     "description":"Friteuse à air 6.2L Rapid Air.","specs":{"Capacité":"6.2L","Puissance":"2000W","Poids":"4.5kg"},"stock":8,"rating":4.6,"reviews":3187,
     "image":"https://images.unsplash.com/photo-1585515320310-259814833e62?w=400&q=80"},
    {"id":"p5","name":"IKEA KALLAX Shelf","brand":"IKEA","category":"Home & Kitchen","price":79.99,
     "description":"Étagère modulable 4 cases.","specs":{"Dimensions":"77x77cm","Poids":"22kg","Matière":"Panneau"},"stock":3,"rating":4.2,"reviews":4521,
     "image":"https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&q=80"},
    {"id":"p6","name":"Apple AirPods Pro 2","brand":"Apple","category":"Electronics","price":249.99,
     "description":"Écouteurs sans fil réduction bruit adaptative.","specs":{"Autonomie":"6h+24h","Poids":"5.3g","IP":"IPX4"},"stock":0,"rating":4.9,"reviews":8921,
     "image":"https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=400&q=80"},
    {"id":"p7","name":"De'Longhi Magnifica","brand":"De'Longhi","category":"Home & Kitchen","price":599.99,
     "description":"Machine à café automatique broyeur intégré.","specs":{"Puissance":"1450W","Pression":"15 bars","Réservoir":"1.8L"},"stock":6,"rating":4.7,"reviews":1876,
     "image":"https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&q=80"},
    {"id":"p8","name":"Levi's 501 Original","brand":"Levi's","category":"Clothing","price":89.99,
     "description":"Jean droit iconique 100% coton.","specs":{"Taille":"28-38","Longueur":"30-34","Matière":"100% Coton"},"stock":15,"rating":4.4,"reviews":6234,
     "image":"https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&q=80"},
]

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

DEMO_USERS = {
    "admin": {"password": hash_pw("admin123"), "role": "admin", "name": "Administrateur"},
    "ahmed": {"password": hash_pw("ahmed123"), "role": "user",  "name": "Ahmed Ben Ali"},
    "sara":  {"password": hash_pw("sara123"),  "role": "user",  "name": "Sara Mansour"},
}

# ─── SESSION STATE ────────────────────────────────────────────────────────────────
for key, val in [
    ("logged_in", False), ("current_user", None), ("user_role", None),
    ("user_name", None), ("demo_products", None), ("orders", []),
    ("demo_users", None)
]:
    if key not in st.session_state:
        st.session_state[key] = val

if st.session_state.demo_products is None:
    st.session_state.demo_products = [p.copy() for p in DEMO_PRODUCTS]
if st.session_state.demo_users is None:
    st.session_state.demo_users = {k: v.copy() for k, v in DEMO_USERS.items()}

# ─── HELPERS ─────────────────────────────────────────────────────────────────────
def get_products():
    if firebase_ok:
        try:
            docs = db.collection("products").stream()
            prods = [{"id": d.id, **d.to_dict()} for d in docs]
            return prods or st.session_state.demo_products
        except:
            pass
    return st.session_state.demo_products

def star_display(r):
    f = int(r); h = 1 if (r - f) >= 0.5 else 0
    return "★" * f + ("½" if h else "") + "☆" * (5 - f - h)

def stock_badge(s):
    if s == 0: return '<span class="stock-badge out-stock">Rupture</span>'
    elif s <= 5: return f'<span class="stock-badge low-stock">⚠ {s} restants</span>'
    else: return f'<span class="stock-badge in-stock">✓ En stock</span>'

def login_user(username, password):
    pw_hash = hash_pw(password)
    if firebase_ok:
        try:
            doc = db.collection("users").document(username).get()
            if doc.exists:
                data = doc.to_dict()
                if data.get("password") == pw_hash:
                    return True, data.get("role", "user"), data.get("name", username)
        except:
            pass
    users = st.session_state.demo_users
    if username in users and users[username]["password"] == pw_hash:
        u = users[username]
        return True, u["role"], u["name"]
    return False, None, None

def register_user(username, password, name):
    if username in st.session_state.demo_users:
        return False, "Ce nom d'utilisateur existe déjà."
    new_user_data = {"password": hash_pw(password), "role": "user", "name": name}
    if firebase_ok:
        try:
            db.collection("users").document(username).set({
                "name": name, "password": hash_pw(password), "role": "user",
                "created_at": datetime.now().isoformat()
            })
        except:
            pass
    st.session_state.demo_users[username] = new_user_data
    return True, "Compte créé avec succès !"

def buy_product(product_id, quantity):
    buyer = st.session_state.current_user
    buyer_name = st.session_state.demo_users.get(buyer, {}).get("name", buyer)
    if firebase_ok:
        try:
            ref = db.collection("products").document(product_id)
            p = ref.get().to_dict()
            if p and p.get("stock", 0) >= quantity:
                ref.update({"stock": firestore.Increment(-quantity)})
                db.collection("orders").add({
                    "product_id": product_id, "product_name": p["name"],
                    "buyer_username": buyer, "buyer_name": buyer_name,
                    "quantity": quantity, "total": p["price"] * quantity,
                    "date": datetime.now().isoformat()
                })
                return True, "✅ Commande passée avec succès !"
            return False, "Stock insuffisant."
        except Exception as e:
            return False, f"Erreur: {e}"
    else:
        for p in st.session_state.demo_products:
            if p["id"] == product_id:
                if p["stock"] >= quantity:
                    p["stock"] -= quantity
                    st.session_state.orders.append({
                        "product_id": product_id, "product_name": p["name"],
                        "buyer_username": buyer, "buyer_name": buyer_name,
                        "quantity": quantity, "total": p["price"] * quantity,
                        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                    return True, "✅ Commande passée (mode démo) !"
                return False, "Stock insuffisant."
        return False, "Produit introuvable."

def get_all_orders():
    if firebase_ok:
        try:
            docs = db.collection("orders").stream()
            return [d.to_dict() for d in docs]
        except:
            pass
    return st.session_state.orders

def get_my_orders():
    user = st.session_state.current_user
    return [o for o in get_all_orders() if o.get("buyer_username") == user]

def add_product_to_db(product):
    if firebase_ok:
        db.collection("products").add(product)
    else:
        product["id"] = str(uuid.uuid4())[:8]
        st.session_state.demo_products.append(product)

def delete_product(product_id):
    if firebase_ok:
        try:
            db.collection("products").document(product_id).delete()
        except:
            pass
    else:
        st.session_state.demo_products = [
            p for p in st.session_state.demo_products if p["id"] != product_id
        ]

# ════════════════════════════════════════════════════════════════════
# PAGE LOGIN (si pas connecté)
# ════════════════════════════════════════════════════════════════════
if not st.session_state.logged_in:
    st.markdown("""
    <div style="text-align:center;padding:2.5rem 0 1rem;">
        <div style="font-family:'Sora',sans-serif;font-size:2.8rem;font-weight:800;color:#e94560;">🛒 ShopZone</div>
        <div style="color:#888;margin-top:6px;font-size:1rem;">La meilleure expérience d'achat en ligne</div>
    </div>
    """, unsafe_allow_html=True)

    tab_login, tab_register = st.tabs(["🔐 Se connecter", "📝 Créer un compte"])

    with tab_login:
        st.markdown("")
        _, col_form, _ = st.columns([1, 2, 1])
        with col_form:
            st.markdown("### Bienvenue 👋")
            username = st.text_input("Nom d'utilisateur", placeholder="Ex: ahmed", key="li_user")
            password = st.text_input("Mot de passe", type="password", placeholder="••••••••", key="li_pw")
            if st.button("Se connecter →", use_container_width=True, key="btn_login"):
                if username and password:
                    ok, role, name = login_user(username.strip(), password)
                    if ok:
                        st.session_state.logged_in = True
                        st.session_state.current_user = username.strip()
                        st.session_state.user_role = role
                        st.session_state.user_name = name
                        st.rerun()
                    else:
                        st.error("❌ Identifiants incorrects.")
                else:
                    st.warning("Veuillez remplir tous les champs.")
            st.markdown("---")
            st.markdown("**Comptes de test :**")
            st.code("admin / admin123  →  Administrateur\nahmed / ahmed123  →  Utilisateur\nsara  / sara123   →  Utilisateur")

    with tab_register:
        st.markdown("")
        _, col_form2, _ = st.columns([1, 2, 1])
        with col_form2:
            st.markdown("### Créer un compte 🆕")
            new_name = st.text_input("Nom complet", placeholder="Ex: Mohamed Trabelsi", key="rg_name")
            new_user = st.text_input("Nom d'utilisateur", placeholder="Ex: mohamed123", key="rg_user")
            new_pw   = st.text_input("Mot de passe", type="password", placeholder="Min. 6 caractères", key="rg_pw")
            new_pw2  = st.text_input("Confirmer mot de passe", type="password", placeholder="••••••••", key="rg_pw2")
            if st.button("Créer mon compte →", use_container_width=True, key="btn_register"):
                if not all([new_name, new_user, new_pw, new_pw2]):
                    st.warning("Veuillez remplir tous les champs.")
                elif new_pw != new_pw2:
                    st.error("Les mots de passe ne correspondent pas.")
                elif len(new_pw) < 6:
                    st.error("Mot de passe trop court (min 6 caractères).")
                else:
                    ok, msg = register_user(new_user.strip(), new_pw, new_name.strip())
                    if ok:
                        st.success(f"✅ {msg} Connectez-vous maintenant.")
                    else:
                        st.error(f"❌ {msg}")
    st.stop()

# ════════════════════════════════════════════════════════════════════
# APP PRINCIPALE (connecté)
# ════════════════════════════════════════════════════════════════════
role      = st.session_state.user_role
user_name = st.session_state.user_name or st.session_state.current_user

# SIDEBAR
with st.sidebar:
    st.markdown("## 🛒 ShopZone")
    st.markdown(f"👤 **{user_name}**")
    st.markdown("🔴 Admin" if role == "admin" else "🔵 Client")
    st.markdown("---")

    if role == "admin":
        nav_options = ["🏪 Boutique", "📦 Toutes les commandes", "➕ Ajouter Produit", "🔧 Administration"]
    else:
        nav_options = ["🏪 Boutique", "📋 Mes commandes"]

    page = st.selectbox("Navigation", nav_options)
    st.markdown("---")
    st.markdown("### 🔍 Filtres")
    selected_cat = st.selectbox("Catégorie", ["Tous", "Electronics", "Sports", "Home & Kitchen", "Clothing"])
    price_max    = st.slider("Prix max (DT)", 0, 1000, 1000, step=10)
    search_q     = st.text_input("🔎 Rechercher", placeholder="Ex: Sony, Nike...")
    st.markdown("---")
    st.markdown("🟢 Firebase connecté" if firebase_ok else "🟡 Mode démo")
    if st.button("🚪 Se déconnecter"):
        for k in ["logged_in","current_user","user_role","user_name"]:
            st.session_state[k] = False if k == "logged_in" else None
        st.rerun()

# HEADER
st.markdown(f"""
<div class="shop-header">
    <div>
        <div class="shop-logo">🛒 ShopZone</div>
        <div class="shop-tagline">Des milliers de produits au meilleur prix</div>
    </div>
    <div style="color:#aab4be;font-size:0.9rem;text-align:right">
        👤 {user_name} &nbsp;·&nbsp; {'🔴 Admin' if role=='admin' else '🔵 Client'}<br>
        <span style="font-size:0.75rem">{'🟢 Firebase' if firebase_ok else '🟡 Mode démo'}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# BOUTIQUE
# ════════════════════════════════════════════════════════════════════
if page == "🏪 Boutique":
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">Bienvenue sur ShopZone 🎉</div>
        <div class="hero-sub">Des milliers de produits au meilleur prix. Livraison gratuite.</div>
        <span class="badge">🚚 Livraison gratuite</span>
        <span class="badge">🔄 Retours faciles</span>
        <span class="badge">🔒 Paiement sécurisé</span>
    </div>
    """, unsafe_allow_html=True)

    products_list = get_products()
    c1, c2, c3, c4 = st.columns(4)
    for col, label, val in zip(
        [c1, c2, c3, c4],
        ["Produits", "En stock", "Commandes", "Catégories"],
        [len(products_list), sum(1 for p in products_list if p.get("stock",0)>0), len(get_all_orders()), 5]
    ):
        with col:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{val}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">🛍️ Nos Produits</div>', unsafe_allow_html=True)

    filtered = products_list
    if selected_cat != "Tous":
        filtered = [p for p in filtered if p.get("category") == selected_cat]
    filtered = [p for p in filtered if p.get("price", 0) <= price_max]
    if search_q:
        q = search_q.lower()
        filtered = [p for p in filtered if q in p.get("name","").lower() or q in p.get("brand","").lower()]

    st.caption(f"{len(filtered)} produit(s) trouvé(s)")

    if not filtered:
        st.info("Aucun produit trouvé. Ajustez les filtres.")
    else:
        cols = st.columns(4)
        for i, product in enumerate(filtered):
            with cols[i % 4]:
                stock = product.get("stock", 0)
                st.markdown(f"""
                <div class="product-card">
                    <img class="product-img" src="{product.get('image','')}" onerror="this.src='https://via.placeholder.com/400x190?text=Produit'"/>
                    <div class="product-body">
                        <div class="product-category">{product.get('category','')}</div>
                        <div class="product-name">{product.get('name','')}</div>
                        <div class="product-brand">{product.get('brand','')}</div>
                        <div class="stars">{star_display(product.get('rating',4.0))} <span style="color:#999;font-size:0.75rem">({product.get('reviews',0):,})</span></div>
                        <div>
                            <span class="product-price">{product.get('price',0):.2f}</span>
                            <span class="price-currency"> DT</span>
                            {stock_badge(stock)}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                with st.expander("📋 Caractéristiques"):
                    for k, v in product.get("specs", {}).items():
                        st.markdown(f"**{k}:** {v}")
                    if product.get("description"):
                        st.markdown(f"_{product['description']}_")

                if stock > 0:
                    qty = st.number_input("Quantité", 1, min(stock, 10), 1, key=f"qty_{product['id']}")
                    if st.button("🛒 Acheter", key=f"buy_{product['id']}"):
                        ok, msg = buy_product(product["id"], qty)
                        if ok:
                            st.success(msg)
                            st.rerun()
                        else:
                            st.error(msg)
                else:
                    st.markdown("🚫 **Indisponible**")
                st.markdown("---")

# ════════════════════════════════════════════════════════════════════
# MES COMMANDES (utilisateur)
# ════════════════════════════════════════════════════════════════════
elif page == "📋 Mes commandes":
    st.markdown('<div class="section-title">📋 Mes Commandes</div>', unsafe_allow_html=True)
    orders = get_my_orders()
    if not orders:
        st.info("Vous n'avez pas encore commandé. Visitez la boutique !")
    else:
        total = sum(o.get("total", 0) for o in orders)
        c1, c2 = st.columns(2)
        with c1: st.markdown(f'<div class="stat-card"><div class="stat-number">{len(orders)}</div><div class="stat-label">Commandes</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-card"><div class="stat-number">{total:.2f} DT</div><div class="stat-label">Total dépensé</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        for o in orders:
            st.markdown(f"""
            <div class="order-row">
                <div>
                    <strong>{o.get('product_name','')}</strong><br>
                    <span style="color:#888;font-size:0.8rem">📅 {str(o.get('date',''))[:10]}</span>
                </div>
                <div style="text-align:right">
                    <span style="color:#666">x{o.get('quantity','')}</span><br>
                    <strong style="color:#e94560;font-family:'Sora',sans-serif">{o.get('total',0):.2f} DT</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# TOUTES LES COMMANDES (admin)
# ════════════════════════════════════════════════════════════════════
elif page == "📦 Toutes les commandes" and role == "admin":
    st.markdown('<div class="section-title">📦 Toutes les Commandes</div>', unsafe_allow_html=True)
    orders = get_all_orders()
    if not orders:
        st.info("Aucune commande pour l'instant.")
    else:
        rev = sum(o.get("total", 0) for o in orders)
        clients = len(set(o.get("buyer_username","") for o in orders))
        c1, c2, c3 = st.columns(3)
        with c1: st.markdown(f'<div class="stat-card"><div class="stat-number">{len(orders)}</div><div class="stat-label">Commandes</div></div>', unsafe_allow_html=True)
        with c2: st.markdown(f'<div class="stat-card"><div class="stat-number">{rev:.2f} DT</div><div class="stat-label">Revenu total</div></div>', unsafe_allow_html=True)
        with c3: st.markdown(f'<div class="stat-card"><div class="stat-number">{clients}</div><div class="stat-label">Clients uniques</div></div>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        rows = ""
        for o in orders:
            rows += f"""<tr>
                <td><strong>{o.get('product_name','')}</strong></td>
                <td>{o.get('buyer_name', o.get('buyer_username',''))}</td>
                <td style="text-align:center">{o.get('quantity','')}</td>
                <td style="color:#e94560;font-weight:700">{o.get('total',0):.2f} DT</td>
                <td style="color:#888">{str(o.get('date',''))[:10]}</td>
            </tr>"""
        st.markdown(f"""
        <table class="admin-table">
            <tr><th>Produit</th><th>Client</th><th style="text-align:center">Qté</th><th>Total</th><th>Date</th></tr>
            {rows}
        </table>
        """, unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════
# AJOUTER PRODUIT (admin)
# ════════════════════════════════════════════════════════════════════
elif page == "➕ Ajouter Produit" and role == "admin":
    st.markdown('<div class="section-title">➕ Ajouter un Produit</div>', unsafe_allow_html=True)
    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name     = st.text_input("Nom *", placeholder="Ex: Samsung Galaxy S24")
            brand    = st.text_input("Marque *", placeholder="Ex: Samsung")
            category = st.selectbox("Catégorie *", ["Electronics","Sports","Home & Kitchen","Clothing"])
            price    = st.number_input("Prix (DT) *", min_value=0.0, step=0.5, format="%.2f")
            stock    = st.number_input("Stock *", min_value=0, step=1, value=10)
        with col2:
            image_url   = st.text_input("URL image", placeholder="https://...")
            description = st.text_area("Description", height=100)
            rating      = st.slider("Note", 1.0, 5.0, 4.0, step=0.1)
            reviews     = st.number_input("Nb avis", min_value=0, value=0)

        st.markdown("**Caractéristiques**")
        sc1, sc2 = st.columns(2)
        specs = {}
        with sc1:
            s1k=st.text_input("Spec 1 nom", placeholder="Poids")
            s1v=st.text_input("Spec 1 valeur", placeholder="250g")
            s2k=st.text_input("Spec 2 nom", placeholder="Taille")
            s2v=st.text_input("Spec 2 valeur", placeholder="L")
        with sc2:
            s3k=st.text_input("Spec 3 nom", placeholder="Couleur")
            s3v=st.text_input("Spec 3 valeur", placeholder="Noir")
            s4k=st.text_input("Spec 4 nom", placeholder="Matière")
            s4v=st.text_input("Spec 4 valeur", placeholder="Coton")
        for k, v in [(s1k,s1v),(s2k,s2v),(s3k,s3v),(s4k,s4v)]:
            if k and v: specs[k] = v

        if st.form_submit_button("✅ Ajouter le produit", use_container_width=True):
            if not name or not brand or price <= 0:
                st.error("Remplissez les champs obligatoires (*).")
            else:
                add_product_to_db({
                    "name":name, "brand":brand, "category":category,
                    "price":price, "stock":int(stock), "description":description,
                    "image":image_url or "https://via.placeholder.com/400x190?text=Produit",
                    "rating":rating, "reviews":int(reviews), "specs":specs,
                    "created_at":datetime.now().isoformat()
                })
                st.success(f"✅ '{name}' ajouté avec succès !")
                st.rerun()

# ════════════════════════════════════════════════════════════════════
# ADMINISTRATION (admin)
# ════════════════════════════════════════════════════════════════════
elif page == "🔧 Administration" and role == "admin":
    st.markdown('<div class="section-title">🔧 Panneau d\'Administration</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["📦 Produits", "👥 Utilisateurs", "📊 Statistiques"])

    with tab1:
        st.markdown("#### Gérer les produits")
        for p in get_products():
            col_info, col_stock, col_del = st.columns([4, 2, 1])
            with col_info:
                st.markdown(f"**{p.get('name','')}** — {p.get('brand','')} | {p.get('category','')} | **{p.get('price',0):.2f} DT**")
            with col_stock:
                s = p.get("stock", 0)
                color = "#27ae60" if s > 5 else ("#f39c12" if s > 0 else "#e74c3c")
                st.markdown(f"<span style='color:{color};font-weight:700'>Stock: {s}</span>", unsafe_allow_html=True)
            with col_del:
                if st.button("🗑️", key=f"del_{p['id']}", help="Supprimer"):
                    delete_product(p["id"])
                    st.success("Supprimé !")
                    st.rerun()
            st.divider()

    with tab2:
        st.markdown("#### Liste des utilisateurs")
        users = st.session_state.demo_users
        rows = ""
        for uname, udata in users.items():
            badge = f'<span class="role-admin">Admin</span>' if udata["role"]=="admin" else f'<span class="role-user">Client</span>'
            rows += f"<tr><td><strong>{uname}</strong></td><td>{udata.get('name','')}</td><td>{badge}</td></tr>"
        st.markdown(f"""
        <table class="admin-table">
            <tr><th>Username</th><th>Nom complet</th><th>Rôle</th></tr>
            {rows}
        </table>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        normal_users = [u for u, d in users.items() if d["role"] == "user"]
        if normal_users:
            st.markdown("#### ⬆️ Promouvoir en Admin")
            to_promote = st.selectbox("Choisir", normal_users)
            if st.button("Promouvoir en Admin"):
                st.session_state.demo_users[to_promote]["role"] = "admin"
                if firebase_ok:
                    try: db.collection("users").document(to_promote).update({"role":"admin"})
                    except: pass
                st.success(f"✅ {to_promote} est maintenant Admin !")
                st.rerun()

    with tab3:
        st.markdown("#### Statistiques")
        products_list = get_products()
        orders = get_all_orders()
        rev = sum(o.get("total",0) for o in orders)
        out = sum(1 for p in products_list if p.get("stock",0)==0)
        c1,c2,c3,c4 = st.columns(4)
        for col, label, val in zip([c1,c2,c3,c4],
            ["Produits","Commandes","Revenu total","Ruptures"],
            [len(products_list), len(orders), f"{rev:.0f} DT", out]):
            with col: st.markdown(f'<div class="stat-card"><div class="stat-number">{val}</div><div class="stat-label">{label}</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        if orders and rev > 0:
            st.markdown("**Ventes par catégorie :**")
            cat_sales = {}
            for o in orders:
                pid = o.get("product_id","")
                prod = next((p for p in products_list if p.get("id")==pid), None)
                cat = prod.get("category","Autre") if prod else "Autre"
                cat_sales[cat] = cat_sales.get(cat, 0) + o.get("total", 0)
            for cat, total_cat in sorted(cat_sales.items(), key=lambda x: -x[1]):
                pct = int(total_cat / rev * 100)
                st.markdown(f"""
                <div style="margin-bottom:10px">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                        <span style="font-weight:600">{cat}</span>
                        <span style="color:#e94560;font-weight:700">{total_cat:.2f} DT</span>
                    </div>
                    <div style="background:#eef0f5;border-radius:10px;height:8px">
                        <div style="background:#e94560;width:{pct}%;height:8px;border-radius:10px"></div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

elif role != "admin" and page in ["📦 Toutes les commandes","➕ Ajouter Produit","🔧 Administration"]:
    st.error("⛔ Accès refusé. Page réservée aux administrateurs.")
