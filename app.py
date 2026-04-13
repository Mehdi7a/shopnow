import streamlit as st
import firebase_admin
from firebase_admin import credentials, firestore
from datetime import datetime
import json

# ─── PAGE CONFIG ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="ShopZone",
    page_icon="🛒",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─── CUSTOM CSS ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;600;700;800&family=DM+Sans:wght@400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'DM Sans', sans-serif;
    }

    .main { background-color: #f7f8fc; }

    /* Header */
    .shop-header {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .shop-logo {
        font-family: 'Sora', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #e94560;
        letter-spacing: -1px;
    }
    .shop-tagline {
        color: #aab4be;
        font-size: 0.85rem;
        margin-top: 2px;
    }

    /* Hero Banner */
    .hero-banner {
        background: linear-gradient(135deg, #e94560 0%, #c0392b 100%);
        border-radius: 20px;
        padding: 2.5rem 3rem;
        margin-bottom: 2rem;
        color: white;
        position: relative;
        overflow: hidden;
    }
    .hero-banner::before {
        content: '';
        position: absolute;
        top: -50px; right: -50px;
        width: 200px; height: 200px;
        background: rgba(255,255,255,0.08);
        border-radius: 50%;
    }
    .hero-title {
        font-family: 'Sora', sans-serif;
        font-size: 2.2rem;
        font-weight: 800;
        margin: 0 0 0.5rem 0;
        line-height: 1.2;
    }
    .hero-sub { font-size: 1rem; opacity: 0.85; margin-bottom: 1rem; }
    .badge {
        display: inline-block;
        background: rgba(255,255,255,0.2);
        border: 1px solid rgba(255,255,255,0.3);
        padding: 4px 14px;
        border-radius: 50px;
        font-size: 0.8rem;
        margin-right: 8px;
        backdrop-filter: blur(4px);
    }

    /* Product Card */
    .product-card {
        background: white;
        border-radius: 16px;
        overflow: hidden;
        box-shadow: 0 2px 12px rgba(0,0,0,0.07);
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
        border: 1px solid #eef0f5;
    }
    .product-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 8px 30px rgba(0,0,0,0.12);
    }
    .product-img {
        width: 100%;
        height: 200px;
        object-fit: cover;
        background: #f0f2f5;
    }
    .product-body { padding: 1rem 1.2rem 1.2rem; }
    .product-category {
        font-size: 0.72rem;
        font-weight: 600;
        color: #e94560;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 6px;
    }
    .product-name {
        font-family: 'Sora', sans-serif;
        font-size: 1rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 4px;
        line-height: 1.3;
    }
    .product-brand {
        font-size: 0.8rem;
        color: #888;
        margin-bottom: 8px;
    }
    .stars { color: #f4a017; font-size: 0.85rem; margin-bottom: 8px; }
    .product-price {
        font-family: 'Sora', sans-serif;
        font-size: 1.4rem;
        font-weight: 800;
        color: #1a1a2e;
    }
    .price-currency { font-size: 0.9rem; font-weight: 600; color: #666; }
    .stock-badge {
        display: inline-block;
        font-size: 0.72rem;
        padding: 2px 10px;
        border-radius: 20px;
        font-weight: 600;
        margin-left: 8px;
    }
    .in-stock { background: #e8f8f0; color: #27ae60; }
    .low-stock { background: #fff3e0; color: #f39c12; }
    .out-stock { background: #fdecea; color: #e74c3c; }

    /* Category pills */
    .cat-pill {
        display: inline-block;
        padding: 6px 18px;
        border-radius: 50px;
        font-size: 0.82rem;
        font-weight: 600;
        cursor: pointer;
        margin: 3px;
        border: 2px solid transparent;
        transition: all 0.2s;
    }
    .cat-active {
        background: #1a1a2e;
        color: white;
    }
    .cat-inactive {
        background: white;
        color: #444;
        border-color: #dde2ec;
    }

    /* Stats */
    .stat-card {
        background: white;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        border: 1px solid #eef0f5;
    }
    .stat-number {
        font-family: 'Sora', sans-serif;
        font-size: 1.8rem;
        font-weight: 800;
        color: #e94560;
    }
    .stat-label { font-size: 0.78rem; color: #888; margin-top: 2px; }

    /* Order history */
    .order-row {
        background: white;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        margin-bottom: 8px;
        border: 1px solid #eef0f5;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    /* Form styling */
    .stButton > button {
        background: #e94560 !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        font-weight: 600 !important;
        font-family: 'Sora', sans-serif !important;
        padding: 0.5rem 1.5rem !important;
        transition: all 0.2s !important;
    }
    .stButton > button:hover {
        background: #c0392b !important;
        transform: translateY(-1px) !important;
    }
    .stTextInput > div > div > input, .stSelectbox > div > div {
        border-radius: 10px !important;
        border-color: #dde2ec !important;
    }
    .stNumberInput > div > div > input { border-radius: 10px !important; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #1a1a2e !important;
    }
    [data-testid="stSidebar"] * { color: #c8cdd8 !important; }
    [data-testid="stSidebar"] .stSelectbox label,
    [data-testid="stSidebar"] .stSlider label { color: #aab4be !important; }
    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h2,
    [data-testid="stSidebar"] h3 { color: white !important; }

    .divider { border: none; border-top: 1px solid #eef0f5; margin: 1.5rem 0; }
    
    .section-title {
        font-family: 'Sora', sans-serif;
        font-size: 1.3rem;
        font-weight: 700;
        color: #1a1a2e;
        margin-bottom: 1rem;
    }

    /* Success/error messages */
    .msg-success {
        background: #e8f8f0;
        color: #27ae60;
        padding: 12px 18px;
        border-radius: 10px;
        border-left: 4px solid #27ae60;
        font-weight: 600;
        margin: 10px 0;
    }
    .msg-error {
        background: #fdecea;
        color: #e74c3c;
        padding: 12px 18px;
        border-radius: 10px;
        border-left: 4px solid #e74c3c;
        font-weight: 600;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)

# ─── FIREBASE INIT ───────────────────────────────────────────────────────────────
@st.cache_resource
def init_firebase():
    """Initialize Firebase. Returns (db, True) or (None, False) on error."""
    try:
        if not firebase_admin._apps:
            # Load from secrets or local file
            if "firebase" in st.secrets:
                cred_dict = dict(st.secrets["firebase"])
                cred = credentials.Certificate(cred_dict)
            else:
                cred = credentials.Certificate("firebase_credentials.json")
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        return db, True
    except Exception as e:
        return None, False

db, firebase_ok = init_firebase()

# ─── DEMO DATA (used if Firebase not connected) ──────────────────────────────────
DEMO_PRODUCTS = [
    {
        "id": "p1", "name": "Sony WH-1000XM5", "brand": "Sony",
        "category": "Electronics", "price": 349.99,
        "description": "Casque sans fil avec réduction de bruit active de classe mondiale.",
        "specs": {"Poids": "250g", "Autonomie": "30h", "Bluetooth": "5.2", "Couleur": "Noir"},
        "stock": 12, "rating": 4.8, "reviews": 2341,
        "image": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=400&q=80"
    },
    {
        "id": "p2", "name": "Nike Air Max 270", "brand": "Nike",
        "category": "Sports", "price": 150.00,
        "description": "Chaussure de running avec amorti Air Max pour un confort optimal.",
        "specs": {"Taille": "40-46", "Poids": "320g", "Matière": "Mesh", "Semelle": "Air Max"},
        "stock": 5, "rating": 4.5, "reviews": 3421,
        "image": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=400&q=80"
    },
    {
        "id": "p3", "name": "Logitech MX Master 3S", "brand": "Logitech",
        "category": "Electronics", "price": 99.99,
        "description": "Souris ergonomique avec capteur 8000 DPI et connexion multi-appareils.",
        "specs": {"DPI": "200-8000", "Poids": "141g", "Autonomie": "70 jours", "Connexion": "USB-C"},
        "stock": 20, "rating": 4.7, "reviews": 4231,
        "image": "https://images.unsplash.com/photo-1527864550417-7fd91fc51a46?w=400&q=80"
    },
    {
        "id": "p4", "name": "Philips Air Fryer XL", "brand": "Philips",
        "category": "Home & Kitchen", "price": 159.99,
        "description": "Friteuse à air chaud 6.2L avec technologie Rapid Air.",
        "specs": {"Capacité": "6.2L", "Puissance": "2000W", "Poids": "4.5kg", "Couleur": "Noir"},
        "stock": 8, "rating": 4.6, "reviews": 3187,
        "image": "https://images.unsplash.com/photo-1585515320310-259814833e62?w=400&q=80"
    },
    {
        "id": "p5", "name": "IKEA KALLAX Shelf", "brand": "IKEA",
        "category": "Home & Kitchen", "price": 79.99,
        "description": "Étagère modulable 4 cases, idéale pour ranger livres et objets.",
        "specs": {"Dimensions": "77x77cm", "Poids": "22kg", "Matière": "Panneau de particules", "Couleur": "Blanc"},
        "stock": 3, "rating": 4.2, "reviews": 4521,
        "image": "https://images.unsplash.com/photo-1555041469-a586c61ea9bc?w=400&q=80"
    },
    {
        "id": "p6", "name": "Apple AirPods Pro 2", "brand": "Apple",
        "category": "Electronics", "price": 249.99,
        "description": "Écouteurs sans fil avec réduction de bruit adaptative et audio spatial.",
        "specs": {"Autonomie": "6h (+24h boîtier)", "Poids": "5.3g", "Bluetooth": "5.3", "IP": "IPX4"},
        "stock": 0, "rating": 4.9, "reviews": 8921,
        "image": "https://images.unsplash.com/photo-1606220945770-b5b6c2c55bf1?w=400&q=80"
    },
    {
        "id": "p7", "name": "De'Longhi Magnifica", "brand": "De'Longhi",
        "category": "Home & Kitchen", "price": 599.99,
        "description": "Machine à café automatique avec broyeur intégré.",
        "specs": {"Puissance": "1450W", "Pression": "15 bars", "Réservoir": "1.8L", "Poids": "9.5kg"},
        "stock": 6, "rating": 4.7, "reviews": 1876,
        "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=400&q=80"
    },
    {
        "id": "p8", "name": "Levi's 501 Original", "brand": "Levi's",
        "category": "Clothing", "price": 89.99,
        "description": "Jean droit iconique coupe classique, 100% coton.",
        "specs": {"Taille": "28-38", "Longueur": "30-34", "Matière": "100% Coton", "Coupe": "Droite"},
        "stock": 15, "rating": 4.4, "reviews": 6234,
        "image": "https://images.unsplash.com/photo-1542272604-787c3835535d?w=400&q=80"
    },
]

# ─── HELPERS ─────────────────────────────────────────────────────────────────────
def get_products():
    if firebase_ok:
        try:
            docs = db.collection("products").stream()
            products = []
            for doc in docs:
                p = doc.to_dict()
                p["id"] = doc.id
                products.append(p)
            return products if products else DEMO_PRODUCTS
        except:
            return DEMO_PRODUCTS
    return DEMO_PRODUCTS

def add_product_to_db(product):
    if firebase_ok:
        db.collection("products").add(product)

def buy_product(product_id, buyer_name, quantity):
    if firebase_ok:
        try:
            ref = db.collection("products").document(product_id)
            product = ref.get().to_dict()
            if product and product.get("stock", 0) >= quantity:
                ref.update({"stock": firestore.Increment(-quantity)})
                db.collection("orders").add({
                    "product_id": product_id,
                    "product_name": product["name"],
                    "buyer": buyer_name,
                    "quantity": quantity,
                    "total": product["price"] * quantity,
                    "date": datetime.now().isoformat()
                })
                return True, "Commande passée avec succès !"
            else:
                return False, "Stock insuffisant."
        except Exception as e:
            return False, f"Erreur Firebase: {e}"
    else:
        # Demo mode
        for p in st.session_state.get("demo_products", []):
            if p["id"] == product_id:
                if p["stock"] >= quantity:
                    p["stock"] -= quantity
                    if "orders" not in st.session_state:
                        st.session_state.orders = []
                    st.session_state.orders.append({
                        "product_name": p["name"],
                        "buyer": buyer_name,
                        "quantity": quantity,
                        "total": p["price"] * quantity,
                        "date": datetime.now().strftime("%d/%m/%Y %H:%M")
                    })
                    return True, "✅ Commande passée (mode démo) !"
                else:
                    return False, "Stock insuffisant."
        return False, "Produit introuvable."

def get_orders():
    if firebase_ok:
        try:
            docs = db.collection("orders").order_by("date", direction=firestore.Query.DESCENDING).limit(50).stream()
            return [doc.to_dict() for doc in docs]
        except:
            return st.session_state.get("orders", [])
    return st.session_state.get("orders", [])

def star_display(rating):
    full = int(rating)
    half = 1 if (rating - full) >= 0.5 else 0
    empty = 5 - full - half
    return "★" * full + "½" * half + "☆" * empty

def stock_badge(stock):
    if stock == 0:
        return '<span class="stock-badge out-stock">Rupture</span>'
    elif stock <= 5:
        return f'<span class="stock-badge low-stock">⚠ {stock} restants</span>'
    else:
        return f'<span class="stock-badge in-stock">✓ En stock</span>'

# ─── SESSION STATE ────────────────────────────────────────────────────────────────
if "demo_products" not in st.session_state:
    st.session_state.demo_products = [p.copy() for p in DEMO_PRODUCTS]
if "orders" not in st.session_state:
    st.session_state.orders = []
if "cart" not in st.session_state:
    st.session_state.cart = []
if "selected_product" not in st.session_state:
    st.session_state.selected_product = None
if "page" not in st.session_state:
    st.session_state.page = "shop"

# ─── SIDEBAR ─────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🛒 ShopZone")
    st.markdown("---")

    page = st.selectbox(
        "Navigation",
        ["🏪 Boutique", "📦 Commandes", "➕ Ajouter Produit", "ℹ️ À propos"],
        key="nav"
    )

    st.markdown("---")
    st.markdown("### 🔍 Filtres")

    categories = ["Tous", "Electronics", "Sports", "Home & Kitchen", "Clothing"]
    selected_cat = st.selectbox("Catégorie", categories)

    price_range = st.slider("Prix max (DT)", 0, 1000, 1000, step=10)
    search_query = st.text_input("🔎 Rechercher", placeholder="Ex: Sony, Nike...")

    st.markdown("---")

    # Firebase status
    if firebase_ok:
        st.markdown("🟢 **Firebase** connecté")
    else:
        st.markdown("🟡 **Mode démo** (Firebase non connecté)")
        st.caption("Voir le guide de connexion ci-dessous")

    st.markdown("---")
    st.markdown("**ShopZone** v1.0  \nProjet Faculté 2025")

# ─── HEADER ──────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="shop-header">
    <div>
        <div class="shop-logo">🛒 ShopZone</div>
        <div class="shop-tagline">Des milliers de produits au meilleur prix</div>
    </div>
    <div style="color:#aab4be; font-size:0.9rem;">
        Livraison gratuite · Retours faciles · Paiement sécurisé
    </div>
</div>
""", unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# PAGE: BOUTIQUE
# ═══════════════════════════════════════════════════════════════════
if page == "🏪 Boutique":

    # Hero
    st.markdown("""
    <div class="hero-banner">
        <div class="hero-title">Bienvenue sur ShopZone 🎉</div>
        <div class="hero-sub">Des milliers de produits au meilleur prix. Livraison gratuite sur toutes vos commandes.</div>
        <span class="badge">🚚 Livraison gratuite</span>
        <span class="badge">🔄 Retours faciles</span>
        <span class="badge">🔒 Paiement sécurisé</span>
    </div>
    """, unsafe_allow_html=True)

    # Stats row
    products_list = get_products() if firebase_ok else st.session_state.demo_products
    total_products = len(products_list)
    total_orders = len(get_orders())
    in_stock = sum(1 for p in products_list if p.get("stock", 0) > 0)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{total_products}</div><div class="stat-label">Produits</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{in_stock}</div><div class="stat-label">En stock</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="stat-card"><div class="stat-number">{total_orders}</div><div class="stat-label">Commandes</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="stat-card"><div class="stat-number">5</div><div class="stat-label">Catégories</div></div>', unsafe_allow_html=True)

    st.markdown("<hr class='divider'>", unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">🛍️ Nos Produits</div>', unsafe_allow_html=True)

    # Filter
    filtered = products_list
    if selected_cat != "Tous":
        filtered = [p for p in filtered if p.get("category") == selected_cat]
    if price_range < 1000:
        filtered = [p for p in filtered if p.get("price", 0) <= price_range]
    if search_query:
        q = search_query.lower()
        filtered = [p for p in filtered if q in p.get("name", "").lower() or q in p.get("brand", "").lower()]

    st.caption(f"{len(filtered)} produit(s) trouvé(s)")

    if not filtered:
        st.info("Aucun produit trouvé. Essayez d'ajuster vos filtres.")
    else:
        cols = st.columns(4)
        for i, product in enumerate(filtered):
            with cols[i % 4]:
                stock = product.get("stock", 0)
                rating = product.get("rating", 4.0)
                reviews = product.get("reviews", 0)

                st.markdown(f"""
                <div class="product-card">
                    <img class="product-img" src="{product.get('image', '')}" onerror="this.src='https://via.placeholder.com/400x200?text=Produit'"/>
                    <div class="product-body">
                        <div class="product-category">{product.get('category','')}</div>
                        <div class="product-name">{product.get('name','')}</div>
                        <div class="product-brand">{product.get('brand','')}</div>
                        <div class="stars">{star_display(rating)} <span style="color:#999;font-size:0.78rem">({reviews:,})</span></div>
                        <div>
                            <span class="product-price">{product.get('price', 0):.2f}</span>
                            <span class="price-currency"> DT</span>
                            {stock_badge(stock)}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

                st.markdown("<br>", unsafe_allow_html=True)

                # Specs expander
                with st.expander("📋 Caractéristiques"):
                    specs = product.get("specs", {})
                    if specs:
                        for key, val in specs.items():
                            st.markdown(f"**{key}:** {val}")
                    desc = product.get("description", "")
                    if desc:
                        st.markdown(f"_{desc}_")

                # Buy section
                if stock > 0:
                    qty = st.number_input(
                        "Quantité", min_value=1, max_value=min(stock, 10),
                        value=1, key=f"qty_{product['id']}"
                    )
                    buyer = st.text_input(
                        "Votre nom", placeholder="Ex: Ahmed Ben Ali",
                        key=f"buyer_{product['id']}"
                    )
                    if st.button(f"🛒 Acheter", key=f"buy_{product['id']}"):
                        if buyer.strip():
                            ok, msg = buy_product(product["id"], buyer.strip(), qty)
                            if ok:
                                st.markdown(f'<div class="msg-success">{msg}</div>', unsafe_allow_html=True)
                                st.rerun()
                            else:
                                st.markdown(f'<div class="msg-error">{msg}</div>', unsafe_allow_html=True)
                        else:
                            st.warning("Veuillez entrer votre nom.")
                else:
                    st.markdown("**Produit indisponible**")

                st.markdown("---")

# ═══════════════════════════════════════════════════════════════════
# PAGE: COMMANDES
# ═══════════════════════════════════════════════════════════════════
elif page == "📦 Commandes":
    st.markdown('<div class="section-title">📦 Historique des Commandes</div>', unsafe_allow_html=True)

    orders = get_orders()
    if not orders:
        st.info("Aucune commande pour l'instant. Passez votre première commande !")
    else:
        total_revenue = sum(o.get("total", 0) for o in orders)
        c1, c2 = st.columns(2)
        with c1:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{len(orders)}</div><div class="stat-label">Commandes totales</div></div>', unsafe_allow_html=True)
        with c2:
            st.markdown(f'<div class="stat-card"><div class="stat-number">{total_revenue:.2f} DT</div><div class="stat-label">Revenu total</div></div>', unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        for order in orders:
            st.markdown(f"""
            <div class="order-row">
                <div>
                    <strong>{order.get('product_name','')}</strong><br>
                    <span style="color:#888;font-size:0.82rem">👤 {order.get('buyer','')} · 📅 {order.get('date','')[:10]}</span>
                </div>
                <div style="text-align:right">
                    <span style="color:#666">x{order.get('quantity','')}</span><br>
                    <strong style="color:#e94560;font-family:'Sora',sans-serif">{order.get('total',0):.2f} DT</strong>
                </div>
            </div>
            """, unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════════════════
# PAGE: AJOUTER PRODUIT
# ═══════════════════════════════════════════════════════════════════
elif page == "➕ Ajouter Produit":
    st.markdown('<div class="section-title">➕ Ajouter un Nouveau Produit</div>', unsafe_allow_html=True)

    with st.form("add_product_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            name = st.text_input("Nom du produit *", placeholder="Ex: Samsung Galaxy S24")
            brand = st.text_input("Marque *", placeholder="Ex: Samsung")
            category = st.selectbox("Catégorie *", ["Electronics", "Sports", "Home & Kitchen", "Clothing"])
            price = st.number_input("Prix (DT) *", min_value=0.0, step=0.5, format="%.2f")
            stock = st.number_input("Stock *", min_value=0, step=1, value=10)
        with col2:
            image_url = st.text_input("URL de l'image", placeholder="https://...")
            description = st.text_area("Description", placeholder="Décrivez le produit...", height=100)
            rating = st.slider("Note (étoiles)", 1.0, 5.0, 4.0, step=0.1)
            reviews = st.number_input("Nombre d'avis", min_value=0, value=0)

        st.markdown("**Caractéristiques (optionnel)**")
        sc1, sc2 = st.columns(2)
        specs = {}
        with sc1:
            s1k = st.text_input("Spec 1 - Nom", placeholder="Poids")
            s1v = st.text_input("Spec 1 - Valeur", placeholder="250g")
            s2k = st.text_input("Spec 2 - Nom", placeholder="Taille")
            s2v = st.text_input("Spec 2 - Valeur", placeholder="L")
        with sc2:
            s3k = st.text_input("Spec 3 - Nom", placeholder="Couleur")
            s3v = st.text_input("Spec 3 - Valeur", placeholder="Noir")
            s4k = st.text_input("Spec 4 - Nom", placeholder="Matière")
            s4v = st.text_input("Spec 4 - Valeur", placeholder="Coton")

        if s1k and s1v: specs[s1k] = s1v
        if s2k and s2v: specs[s2k] = s2v
        if s3k and s3v: specs[s3k] = s3v
        if s4k and s4v: specs[s4k] = s4v

        submitted = st.form_submit_button("✅ Ajouter le produit", use_container_width=True)
        if submitted:
            if not name or not brand or price <= 0:
                st.error("Veuillez remplir tous les champs obligatoires (*).")
            else:
                new_product = {
                    "name": name, "brand": brand, "category": category,
                    "price": price, "stock": int(stock), "description": description,
                    "image": image_url or "https://via.placeholder.com/400x200?text=Produit",
                    "rating": rating, "reviews": int(reviews),
                    "specs": specs,
                    "created_at": datetime.now().isoformat()
                }
                if firebase_ok:
                    add_product_to_db(new_product)
                    st.success(f"✅ '{name}' ajouté à Firebase avec succès !")
                else:
                    import uuid
                    new_product["id"] = str(uuid.uuid4())[:8]
                    st.session_state.demo_products.append(new_product)
                    st.success(f"✅ '{name}' ajouté en mode démo !")
                    st.rerun()

# ═══════════════════════════════════════════════════════════════════
# PAGE: À PROPOS
# ═══════════════════════════════════════════════════════════════════
elif page == "ℹ️ À propos":
    st.markdown('<div class="section-title">ℹ️ Guide de connexion Firebase</div>', unsafe_allow_html=True)

    st.markdown("""
    ### 🔥 Comment connecter Firebase ?

    #### Étape 1 — Créer un projet Firebase
    1. Va sur [console.firebase.google.com](https://console.firebase.google.com)
    2. Clique **"Ajouter un projet"** → donne un nom → Continue
    3. Désactive Google Analytics (optionnel) → **Créer le projet**

    #### Étape 2 — Activer Firestore
    1. Dans le menu gauche → **Firestore Database**
    2. Clique **"Créer une base de données"**
    3. Choisis **Mode test** (pour débuter) → Sélectionne une région → **Activer**

    #### Étape 3 — Générer les credentials
    1. ⚙️ Paramètres du projet → **Comptes de service**
    2. Clique **"Générer une nouvelle clé privée"**
    3. Un fichier JSON est téléchargé → renomme-le `firebase_credentials.json`
    4. Place ce fichier dans le **même dossier que `app.py`**

    #### Étape 4 — Lancer l'application
    ```bash
    pip install streamlit firebase-admin
    streamlit run app.py
    ```

    #### Étape 5 — Ajouter des produits dans Firestore
    Dans la console Firebase → Firestore → **Ajouter une collection** nommée `products`
    Chaque document doit avoir les champs : `name`, `brand`, `category`, `price`, `stock`, `image`, `description`, `specs`, `rating`, `reviews`

    ---
    **🛒 ShopZone** — Projet Faculté 2025
    """)

    with st.expander("📄 Structure du fichier firebase_credentials.json"):
        st.code("""{
  "type": "service_account",
  "project_id": "VOTRE_PROJECT_ID",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\\n...\\n-----END PRIVATE KEY-----\\n",
  "client_email": "firebase-adminsdk-xxx@projet.iam.gserviceaccount.com",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token"
}""", language="json")
