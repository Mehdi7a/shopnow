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

html, body, [class*="css"] {
    font-family: 'Poppins', sans-serif;
}

.stApp {
    background: #f5f6fa;
    color: #1a1a2e;
}

section[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #e8eaf0;
    box-shadow: 2px 0 12px rgba(0,0,0,0.04);
}
section[data-testid="stSidebar"] * {
    color: #1a1a2e !important;
}

h1 {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 800 !important;
    color: #1a1a2e !important;
}
h2, h3 {
    font-family: 'Nunito', sans-serif !important;
    font-weight: 700 !important;
    color: #1a1a2e !important;
}

.hero {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    border-radius: 24px;
    padding: 52px 56px;
    margin-bottom: 36px;
    color: white;
    position: relative;
    overflow: hidden;
}
.hero::after {
    content: '🛍️';
    position: absolute;
    right: 60px; top: 50%;
    transform: translateY(-50%);
    font-size: 120px;
    opacity: 0.15;
}
.hero h1 {
    color: white !important;
    font-size: 2.8rem !important;
    margin: 0 0 10px !important;
}
.hero p {
    color: rgba(255,255,255,0.82);
    font-size: 1.05rem;
    margin: 0;
}
.hero-badge {
    display: inline-block;
    background: rgba(255,255,255,0.2);
    color: white;
    font-size: 0.72rem;
    font-weight: 700;
    letter-spacing: 2px;
    text-transform: uppercase;
    padding: 5px 14px;
    border-radius: 20px;
    margin-bottom: 16px;
}

.product-card {
    background: #ffffff;
    border-radius: 20px;
    overflow: hidden;
    box-shadow: 0 4px 20px rgba(0,0,0,0.07);
    transition: transform 0.25s ease, box-shadow 0.25s ease;
    margin-bottom: 24px;
}
.product-card:hover {
    transform: translateY(-6px);
    box-shadow: 0 16px 48px rgba(0,0,0,0.13);
}
.product-img-wrap {
    width: 100%;
    height: 210px;
    overflow: hidden;
    position: relative;
    background: #f0f2f8;
}
.product-img-wrap img {
    width: 100%;
    height: 100%;
    object-fit: cover;
    display: block;
    transition: transform 0.4s ease;
}
.product-card:hover .product-img-wrap img {
    transform: scale(1.05);
}
.cat-tag {
    position: absolute;
    top: 12px; left: 12px;
    background: #667eea;
    color: white;
    font-size: 0.68rem;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 4px 12px;
    border-radius: 20px;
}
.product-body {
    padding: 16px 18px 20px;
}
.product-name {
    font-family: 'Nunito', sans-serif;
    font-size: 1.05rem;
    font-weight: 700;
    color: #1a1a2e;
    margin: 0 0 5px;
}
.product-desc {
    font-size: 0.8rem;
    color: #888;
    margin: 0 0 10px;
    line-height: 1.5;
}
.product-weight {
    font-size: 0.75rem;
    color: #764ba2;
    font-weight: 600;
    background: #f3e5f5;
    padding: 3px 8px;
    border-radius: 8px;
    display: inline-block;
    margin-bottom: 14px;
}
.product-footer {
    display: flex;
    justify-content: space-between;
    align-items: center;
}
.product-price {
    font-size: 1.35rem;
    font-weight: 800;
    color: #667eea;
    font-family: 'Nunito', sans-serif;
}
.product-price small {
    font-size: 0.75rem;
    color: #aaa;
    font-weight: 400;
    margin-left: 3px;
}
.stock-ok  { background:#e8f5e9; color:#2e7d32; font-size:0.73rem; font-weight:600; padding:4px 10px; border-radius:20px; }
.stock-low { background:#fff3e0; color:#e65100; font-size:0.73rem; font-weight:600; padding:4px 10px; border-radius:20px; }
.stock-out { background:#fce4ec; color:#c62828; font-size:0.73rem; font-weight:600; padding:4px 10px; border-radius:20px; }

.stat-card {
    background: white;
    border-radius: 16px;
    padding: 24px 28px;
    box-shadow: 0 4px 20px rgba(0,0,0,0.06);
    text-align: center;
}
.stat-num {
    font-family: 'Nunito', sans-serif;
    font-size: 2.2rem;
    font-weight: 800;
    color: #667eea;
}
.stat-label {
    font-size: 0.8rem;
    color: #999;
    font-weight: 500;
    margin-top: 4px;
}

.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: #ffffff !important;
    border: 1.5px solid #e0e3ef !important;
    border-radius: 12px !important;
    color: #1a1a2e !important;
}
.stButton > button {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
    color: white !important;
    font-weight: 600 !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 10px 26px !important;
    transition: opacity 0.2s !important;
}
.stButton > button:hover {
    opacity: 0.88 !important;
}
.stTabs [data-baseweb="tab"] {
    font-weight: 500 !important;
    color: #888 !important;
}
.stTabs [aria-selected="true"] {
    color: #667eea !important;
    border-bottom-color: #667eea !important;
}
</style>
""", unsafe_allow_html=True)

# ─── FIREBASE ─────────────────────────────
@st.cache_resource
def init_firebase():
    try:
        if not firebase_admin._apps:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            paths = [os.path.join(script_dir, "firebase_credentials.json"), "firebase_credentials.json"]
            cred_path = next((p for p in paths if os.path.exists(p)), None)
            if not cred_path:
                return None, False, "Credentials file not found."
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {
                "databaseURL": "https://shopnow-ba63f-default-rtdb.europe-west1.firebasedatabase.app"
            })
        return rtdb, True, None
    except Exception as e:
        return None, False, str(e)

database, firebase_ok, firebase_error = init_firebase()

def rtdb_get(path):
    try:
        return database.reference(path).get()
    except Exception as e:
        st.error(f"Read error: {e}"); return None

def rtdb_set(path, data):
    try:
        database.reference(path).set(data); return True
    except Exception as e:
        st.error(f"Write error: {e}"); return False

def rtdb_delete(path):
    try:
        database.reference(path).delete(); return True
    except Exception as e:
        st.error(f"Delete error: {e}"); return False

def hash_pw(pw):
    return hashlib.sha256(pw.encode()).hexdigest()

# ─── SEED DATA ─────────────────────────────
SAMPLE_PRODUCTS = [
    {"name": "Sony WH-1000XM5",       "price": 399, "stock": 12, "category": "Audio", "weight": "250g",
     "image": "https://images.unsplash.com/photo-1618366712010-f4ae9c647dcb?w=600&q=80",
     "description": "Casque premium ANC, 30h autonomie, Hi-Res Audio certifié"},
    {"name": "AirPods Pro 2",          "price": 279, "stock": 20, "category": "Audio", "weight": "50g",
     "image": "https://images.unsplash.com/photo-1600294037681-c80b4cb5b434?w=600&q=80",
     "description": "Audio spatial adaptatif, ANC, boîtier MagSafe"},
    {"name": "Marshall Emberton III",  "price": 149, "stock": 8,  "category": "Audio", "weight": "700g",
     "image": "https://images.unsplash.com/photo-1608043152269-423dbba4e7e1?w=600&q=80",
     "description": "Enceinte portable, son signature Marshall, IP67"},
    {"name": "Nike Air Force 1",       "price": 115, "stock": 15, "category": "Footwear", "weight": "850g",
     "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=600&q=80",
     "description": "Icône sneaker, cuir blanc premium, semelle Air"},
    {"name": "Adidas Stan Smith",      "price": 95,  "stock": 22, "category": "Footwear", "weight": "750g",
     "image": "https://images.unsplash.com/photo-1539185441755-769473a23570?w=600&q=80",
     "description": "Classique tennis, cuir pleine fleur, look intemporel"},
    {"name": "New Balance 574",        "price": 119, "stock": 5,  "category": "Footwear", "weight": "780g",
     "image": "https://images.unsplash.com/photo-1556906781-9a412961a28c?w=600&q=80",
     "description": "Confort légendaire, semelle ENCAP, style rétro"},
    {"name": "Apple Watch Ultra 2",    "price": 899, "stock": 6,  "category": "Accessories", "weight": "61g",
     "image": "https://images.unsplash.com/photo-1551816230-ef5deaed4a26?w=600&q=80",
     "description": "Titane 49mm, GPS dual-frequency, 36h autonomie"},
    {"name": "Casio G-Shock GA-2100",  "price": 89,  "stock": 18, "category": "Accessories", "weight": "51g",
     "image": "https://images.unsplash.com/photo-1523170335258-f5ed11844a49?w=600&q=80",
     "description": "Carbon Core Guard, résistance chocs, étanche 200m"},
    {"name": "Ray-Ban Wayfarer",       "price": 159, "stock": 13, "category": "Accessories", "weight": "45g",
     "image": "https://images.unsplash.com/photo-1572635196237-14b3f281503f?w=600&q=80",
     "description": "Monture iconique, verres polarisés UV400"},
    {"name": "Logitech MX Master 3S",  "price": 109, "stock": 14, "category": "Tech", "weight": "141g",
     "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=600&q=80",
     "description": "Souris 8000 DPI, scroll MagSpeed, USB-C, multi-device"},
    {"name": "Keychron Q1 Pro",        "price": 185, "stock": 7,  "category": "Tech", "weight": "1.7kg",
     "image": "https://images.unsplash.com/photo-1595225476474-87563907ef34?w=600&q=80",
     "description": "Clavier mécanique sans fil, aluminium CNC, switches Gateron"},
    {"name": "Samsung T7 SSD 1TB",     "price": 99,  "stock": 30, "category": "Tech", "weight": "58g",
     "image": "https://images.unsplash.com/photo-1597740985671-2a8a3b80502e?w=600&q=80",
     "description": "SSD externe 1To, 1050 Mo/s, USB 3.2 Gen 2"},
    {"name": "iPad Air M2",            "price": 699, "stock": 9,  "category": "Tech", "weight": "462g",
     "image": "https://images.unsplash.com/photo-1544244015-0df4b3ffc6b0?w=600&q=80",
     "description": "Puce M2, écran Liquid Retina 11\", Apple Pencil Pro"},
    {"name": "Polaroid Now+",          "price": 149, "stock": 9,  "category": "Lifestyle", "weight": "457g",
     "image": "https://images.unsplash.com/photo-1526170375885-4d8ecf77b99f?w=600&q=80",
     "description": "Appareil instantané Bluetooth, 5 modes créatifs"},
    {"name": "Yeti Rambler 1L",        "price": 55,  "stock": 25, "category": "Lifestyle", "weight": "460g",
     "image": "https://images.unsplash.com/photo-1588776814546-1ffedda98f5e?w=600&q=80",
     "description": "Gourde inox double paroi, froid 24h, chaud 6h"},
    {"name": "Moleskine Classic A5",   "price": 22,  "stock": 40, "category": "Lifestyle", "weight": "340g",
     "image": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=600&q=80",
     "description": "Carnet hardcover 240 pages, papier 70g ivoire"},
]

def seed():
    if not firebase_ok or database is None: return
    if not rtdb_get("users/admin"):
        rtdb_set("users/admin", {"name": "Admin", "password": hash_pw("admin123"), "role": "admin"})
    if not rtdb_get("users/user1"):
        rtdb_set("users/user1", {"name": "User Test", "password": hash_pw("user123"), "role": "user"})
    if not rtdb_get("products"):
        for p in SAMPLE_PRODUCTS:
            pid = str(uuid.uuid4())[:8]
            data = dict(p); data["id"] = pid; data["created_at"] = datetime.now().isoformat()
            rtdb_set(f"products/{pid}", data)

seed()

def get_products():
    data = rtdb_get("products")
    return list(data.values()) if data else []

def get_users():
    data = rtdb_get("users")
    return data if data else {}

def login_user(username, password):
    if not firebase_ok: return False, None, None
    data = rtdb_get(f"users/{username}")
    if data and data.get("password") == hash_pw(password):
        return True, data["role"], data["name"]
    return False, None, None

def register_user(username, password, name):
    if not firebase_ok: return False
    if rtdb_get(f"users/{username}"): return False
    rtdb_set(f"users/{username}", {"name": name, "password": hash_pw(password), "role": "user"})
    return True

def add_product(product):
    pid = str(uuid.uuid4())[:8]; product["id"] = pid
    rtdb_set(f"products/{pid}", product)

def delete_product(pid):
    rtdb_delete(f"products/{pid}")

# ─── SESSION ─────────────────────────────
if "logged" not in st.session_state:
    st.session_state.logged = False

if not firebase_ok:
    st.error(f"❌ Firebase not connected: {firebase_error}"); st.stop()

# ─── LOGIN PAGE ─────────────────────────────
if not st.session_state.logged:
    _, mid, _ = st.columns([1, 1.6, 1])
    with mid:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background:white;border-radius:24px;padding:40px 44px;box-shadow:0 8px 40px rgba(102,126,234,0.12)">
            <div style="font-family:'Nunito',sans-serif;font-size:2rem;font-weight:800;color:#667eea">🛍️ ShopZone</div>
            <div style="color:#aaa;font-size:0.88rem;margin-bottom:28px">Your premium shopping destination</div>
        </div>
        """, unsafe_allow_html=True)

        tab1, tab2 = st.tabs(["Sign In", "Create Account"])
        with tab1:
            u = st.text_input("Username", key="login_user", placeholder="your_username")
            p = st.text_input("Password", type="password", key="login_pw", placeholder="••••••••")
            if st.button("Sign In →", use_container_width=True, key="btn_login"):
                ok, role, name = login_user(u, p)
                if ok:
                    st.session_state.update({"logged": True, "user": u, "role": role, "name": name})
                    st.rerun()
                else:
                    st.error("❌ Invalid credentials")
        with tab2:
            n  = st.text_input("Full Name", key="reg_name")
            u2 = st.text_input("Username", key="reg_user")
            p2 = st.text_input("Password", type="password", key="reg_pw")
            if st.button("Create Account →", use_container_width=True, key="btn_reg"):
                if register_user(u2, p2, n):
                    st.success("✅ Account created!")
                else:
                    st.error("❌ Username already taken")

        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        with c1: st.info("👑 **Admin**\n`admin` / `admin123`")
        with c2: st.info("👤 **User**\n`user1` / `user123`")
    st.stop()

# ─── SIDEBAR ─────────────────────────────
with st.sidebar:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown(f"## 👋 {st.session_state.name}")
    color = "#667eea" if st.session_state.role == "admin" else "#888"
    label = "👑 Admin" if st.session_state.role == "admin" else "🛍️ Customer"
    st.markdown(f"<span style='background:#eef0ff;color:{color};padding:3px 12px;border-radius:20px;font-size:0.8rem;font-weight:600'>{label}</span>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    st.divider()
    menu = ["🛒 Shop"]
    if st.session_state.role == "admin":
        menu += ["➕ Add Product", "🛠 Admin Panel"]
    page = st.selectbox("Navigation", menu)
    st.divider()
    if st.button("← Logout", use_container_width=True):
        st.session_state.logged = False; st.rerun()

# ─── SHOP ─────────────────────────────
if page == "🛒 Shop":
    st.markdown("""
    <div class="hero">
        <span class="hero-badge">✨ New Arrivals 2025</span>
        <h1>Find Your Next<br>Favourite Thing.</h1>
        <p>Premium tech, sneakers & lifestyle — all in one place.</p>
    </div>
    """, unsafe_allow_html=True)

    products = get_products()
    if not products:
        st.warning("No products available."); st.stop()

    categories = ["All"] + sorted(set(p.get("category", "Other") for p in products))
    col_f, col_c = st.columns([2, 4])
    with col_f:
        selected_cat = st.selectbox("Category", categories, label_visibility="collapsed")
    filtered = products if selected_cat == "All" else [p for p in products if p.get("category") == selected_cat]
    with col_c:
        st.markdown(f"<p style='color:#aaa;font-size:0.85rem;padding-top:10px'>{len(filtered)} products</p>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    cols = st.columns(3, gap="large")
    for i, p in enumerate(filtered):
        img   = p.get("image", "https://images.unsplash.com/photo-1491553895911-0055eca6402d?w=600&q=80")
        stock = p.get("stock", 0)
        poids = p.get("weight", "N/D") # Récupération du poids, "N/D" si absent
        
        if stock == 0:
            stock_html = '<span class="stock-out">Out of stock</span>'
        elif stock <= 5:
            stock_html = f'<span class="stock-low">⚠ Only {stock} left</span>'
        else:
            stock_html = f'<span class="stock-ok">✓ In stock</span>'
            
        with cols[i % 3]:
            st.markdown(f"""
            <div class="product-card">
                <div class="product-img-wrap">
                    <img src="{img}" alt="{p['name']}"/>
                    <span class="cat-tag">{p.get('category','')}</span>
                </div>
                <div class="product-body">
                    <p class="product-name">{p['name']}</p>
                    <p class="product-desc">{p.get('description','')}</p>
                    <div class="product-weight">⚖️ Poids : {poids}</div>
                    <div class="product-footer">
                        <span class="product-price">{p['price']} DT<small>TTC</small></span>
                        {stock_html}
                    </div>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ─── ADD PRODUCT ─────────────────────────────
elif page == "➕ Add Product":
    st.title("Add a Product")
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2 = st.columns(2, gap="large")
    with col1:
        name     = st.text_input("Product name *")
        price    = st.number_input("Price (DT)", min_value=0.0)
        stock    = st.number_input("Stock", min_value=0, step=1)
        category = st.selectbox("Category", ["Audio","Footwear","Tech","Accessories","Lifestyle","Other"])
        weight   = st.text_input("Poids (ex: 250g, 1.5kg) *", placeholder="Ex: 500g") # Ajout de l'input du poids
    with col2:
        image_url   = st.text_input("Image URL", placeholder="https://images.unsplash.com/...")
        description = st.text_area("Description", height=120)
        if image_url:
            st.image(image_url, use_container_width=True)
            
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("➕ Add Product"):
        if name and weight: # Vérification que le nom et le poids sont renseignés
            add_product({
                "name": name, 
                "price": price, 
                "stock": int(stock), 
                "category": category,
                "weight": weight, # Insertion du poids dans le dictionnaire
                "image": image_url, 
                "description": description, 
                "created_at": datetime.now().isoformat()
            })
            st.success("✅ Product added!"); st.rerun()
        else:
            st.error("Le nom et le poids sont obligatoires !")

# ─── ADMIN PANEL ─────────────────────────────
elif page == "🛠 Admin Panel":
    st.title("Admin Panel")
    products = get_products()
    users    = get_users()
    total_stock = sum(p.get("stock", 0) for p in products)

    st.markdown(f"""
    <div style="display:flex;gap:20px;margin:16px 0 32px">
        <div class="stat-card" style="flex:1"><div class="stat-num">{len(products)}</div><div class="stat-label">Products</div></div>
        <div class="stat-card" style="flex:1"><div class="stat-num">{total_stock}</div><div class="stat-label">Items in Stock</div></div>
        <div class="stat-card" style="flex:1"><div class="stat-num">{len(users)}</div><div class="stat-label">Users</div></div>
    </div>
    """, unsafe_allow_html=True)

    tab_p, tab_u = st.tabs(["📦 Products", "👥 Users"])
    with tab_p:
        st.markdown("<br>", unsafe_allow_html=True)
        for p in products:
            c1,c2,c3,c4,c5 = st.columns([0.6,2.5,1.2,0.8,0.6])
            with c1:
                if p.get("image"): st.image(p["image"], width=52)
            with c2:
                st.markdown(f"**{p['name']}**"); st.caption(f"{p.get('category','')} | ⚖️ {p.get('weight', 'N/D')}")
            with c3:
                st.markdown(f"💰 **{p['price']} DT**")
            with c4:
                st.markdown(f"📦 {p.get('stock',0)}")
            with c5:
                if st.button("🗑", key=f"del_{p['id']}"):
                    delete_product(p["id"]); st.rerun()
            st.divider()
    with tab_u:
        st.markdown("<br>", unsafe_allow_html=True)
        for uid, data in users.items():
            c1,c2,c3 = st.columns([1.5,2,1])
            with c1: st.markdown(f"{'👑' if data['role']=='admin' else '👤'} **{uid}**")
            with c2: st.caption(data.get("name",""))
            with c3:
                col = "#667eea" if data["role"]=="admin" else "#aaa"
                st.markdown(f"<span style='background:#eef0ff;color:{col};padding:2px 10px;border-radius:20px;font-size:0.75rem;font-weight:600'>{data['role']}</span>", unsafe_allow_html=True)
            st.divider()
