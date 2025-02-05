import streamlit as st
import duckdb
import plotly.express as px
import requests
import plotly.graph_objects as go
import time

# Configuration de la page avec un thème sombre
st.set_page_config(
    page_title="EchoWize Analytics",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Styles personnalisés avec un thème sombre professionnel
st.markdown("""
    <style>
    /* Styles globaux pour le texte */
    .main *, 
    .element-container, 
    .stMarkdown,
    .stText,
    p, h1, h2, h3, h4, h5, h6,
    .stTextInput > label,
    .stSelectbox > label,
    .stMultiSelect > label {
        color: white !important;
    }

    /* Override pour les éléments Streamlit spécifiques */
    .css-1dp5vir,
    .css-81oif8,
    .css-10trblm,
    .css-1aehpvj,
    .css-1q8dd3e,
    .css-1p0hnsx,
    .css-145kmo2,
    .css-1b0udgb {
        color: white !important;
    }

    /* Style pour les inputs */
    .stTextInput input,
    .stSelectbox select,
    .stMultiSelect select {
        color: white !important;
        background-color: rgba(255, 255, 255, 0.1) !important;
        border: 1px solid rgba(255, 255, 255, 0.2) !important;
    }

    /* Style pour les widgets */
    .stSlider,
    .stCheckbox,
    .stRadio {
        color: white !important;
    }

    /* Style pour les graphiques */
    .js-plotly-plot .plotly .gtitle,
    .js-plotly-plot .plotly .xtitle,
    .js-plotly-plot .plotly .ytitle {
        fill: white !important;
    }

    .js-plotly-plot .plotly .xtick text,
    .js-plotly-plot .plotly .ytick text {
        fill: white !important;
    }

    /* Style pour les tableaux */
    .dataframe {
        color: white !important;
    }

    .dataframe th {
        background-color: rgba(255, 255, 255, 0.1) !important;
        color: white !important;
    }

    .dataframe td {
        color: white !important;
    }

    /* Thème sombre global avec animation de fond */
    .main {
        background: linear-gradient(-45deg, #1a1a1a, #2d2d2d, #1f1f1f, #2a2a2a);
        background-size: 400% 400%;
        animation: gradient 15s ease infinite;
        color: #ffffff !important;
    }
    
    @keyframes gradient {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* En-tête principal avec animation */
    .main-header {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(120deg, #4CAF50, #2196F3, #9C27B0);
        background-size: 200% auto;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        animation: shine 3s linear infinite;
        text-align: center;
        margin: 2rem 0;
        padding: 1.5rem;
        text-transform: uppercase;
        letter-spacing: 2px;
    }
    
    @keyframes shine {
        to { background-position: 200% center; }
    }
    
    /* Style des métriques avec hover effect */
    .metric-container {
        background: linear-gradient(145deg, #2d2d2d, #353535);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        border: 1px solid #404040;
        margin-bottom: 1.5rem;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .metric-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    }
    
    .metric-value {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(45deg, #4CAF50, #2196F3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.8rem;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    
    .metric-label {
        color: #ffffff;
        font-size: 1.2rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    /* Style des cartes avec animation au hover */
    .card-container {
        background: rgba(45, 45, 45, 0.9);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        transition: all 0.3s ease;
    }
    
    .card-container:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.2);
    }
    
    /* Style des onglets modernisé */
    .stTabs [data-baseweb="tab-list"] {
        background: rgba(45, 45, 45, 0.9);
        backdrop-filter: blur(10px);
        padding: 1rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.1);
        display: flex;
        justify-content: center;
        gap: 1rem;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #ffffff;
        background: linear-gradient(145deg, #353535, #2d2d2d);
        border-radius: 8px;
        padding: 0.8rem 1.5rem;
        font-weight: 600;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    
    .stTabs [data-baseweb="tab"]:hover {
        transform: translateY(-2px);
        background: linear-gradient(145deg, #4CAF50, #2196F3);
    }
    
    /* Style des avis avec animation */
    .review-card {
        background: rgba(45, 45, 45, 0.9);
        backdrop-filter: blur(10px);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 1.5rem;
        border-left: 4px solid #4CAF50;
        transition: all 0.3s ease;
        animation: slideIn 0.5s ease-out;
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
    
    .review-card:hover {
        transform: scale(1.02);
        box-shadow: 0 8px 25px rgba(0,0,0,0.2);
    }
    
    .review-header {
        color: #ffffff;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 1.2rem;
        letter-spacing: 1px;
    }
    
    .review-content {
        color: #e0e0e0;
        line-height: 1.8;
        font-size: 1.1rem;
    }
    
    .review-stats {
        display: flex;
        justify-content: space-between;
        margin-top: 1.5rem;
        padding-top: 1.5rem;
        border-top: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    /* Personnalisation des boutons */
    .stButton button {
        background: linear-gradient(45deg, #4CAF50, #2196F3);
        color: white;
        border: none;
        padding: 0.8rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        letter-spacing: 1px;
        transition: all 0.3s ease;
    }
    
    .stButton button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
    }
    
    /* Animation de chargement personnalisée */
    .stSpinner {
        animation: rotate 2s linear infinite;
    }
    
    @keyframes rotate {
        100% { transform: rotate(360deg); }
    }

    /* Style du conteneur principal */
    .main-container {
        background: rgba(31, 41, 55, 0.8);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 2rem;
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
        border: 1px solid rgba(255, 255, 255, 0.1);
        margin: 2rem auto;
        max-width: 1200px;
    }
    
    /* Style du logo animé */
    .logo-container {
        text-align: center;
        margin-bottom: 2rem;
        animation: fadeInDown 1s ease-out;
    }
    
    @keyframes fadeInDown {
        from {
            opacity: 0;
            transform: translateY(-20px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    /* Style du formulaire */
    .search-container {
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        padding: 2rem;
        margin-top: 2rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
        animation: fadeIn 0.8s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    
    /* Style du bouton */
    .custom-button {
        background: linear-gradient(135deg, #4CAF50, #2196F3);
        color: white;
        padding: 0.8rem 2rem;
        border-radius: 10px;
        border: none;
        font-weight: 600;
        letter-spacing: 1px;
        text-transform: uppercase;
        transition: all 0.3s ease;
        width: 100%;
        margin-top: 1rem;
    }
    
    .custom-button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
    }
    
    /* Style de la barre de progression */
    .progress-container {
        margin: 2rem 0;
        position: relative;
    }
    
    .progress-bar {
        height: 6px;
        background: linear-gradient(90deg, #4CAF50, #2196F3);
        border-radius: 3px;
        transition: width 0.3s ease;
    }
    
    .progress-label {
        position: absolute;
        top: -25px;
        right: 0;
        color: white;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Animation de chargement */
    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.5; }
        100% { opacity: 1; }
    }
    
    .loading-text {
        color: white;
        text-align: center;
        margin-top: 1rem;
        animation: pulse 1.5s infinite;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

def call_api(restaurant_name: str):
    try:
        response = requests.get(f'http://localhost:5000/restaurant/{restaurant_name}/reviews')
        if response.status_code == 200:
            return response.json()
        else:
            st.error(f"Erreur lors de l'appel API: {response.status_code}")
            return None
    except Exception as e:
        st.error(f"Erreur de connexion à l'API: {str(e)}")
        return None

def afficher_dashboard():
    # Connexion à la base
    con = duckdb.connect('echowize.db')
    
    # Titre principal
    ##st.markdown('<h1 class="main-header">EchoWize Analytics</h1>', unsafe_allow_html=True)
    
    # Métriques principales
    with st.container():
        col1, col2, col3 = st.columns(3)
        
        # Calcul des métriques à partir de la base de données
        total_reviews = con.execute("SELECT COUNT(*) FROM conso_reviews").fetchone()[0]
        avg_rating = con.execute("SELECT ROUND(AVG(rating), 2) FROM conso_reviews").fetchone()[0]
        
        # Calcul du taux de satisfaction (notes >= 3)
        satisfaction_rate = con.execute("""
            SELECT 
                ROUND(
                    (CAST(COUNT(CASE WHEN rating >= 3 THEN 1 END) AS FLOAT) / 
                     CAST(COUNT(*) AS FLOAT) * 100),
                    1
                ) as satisfaction_rate
            FROM conso_reviews
        """).fetchone()[0]
        
        with col1:
            avg_rating_color = "#4CAF50" if avg_rating >= 3 else "#FF5252"
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value" style="color: {avg_rating_color}">{avg_rating}/5</div>
                    <div class="metric-label">Note moyenne globale</div>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value">{total_reviews:,}</div>
                    <div class="metric-label">Total des avis</div>
                </div>
            """, unsafe_allow_html=True)
        
        
        with col3:
            satisfaction_color = "#4CAF50" if satisfaction_rate >= 50 else "#FF5252"
            st.markdown(f"""
                <div class="metric-container">
                    <div class="metric-value" style="color: {satisfaction_color}">
                        {int(satisfaction_rate)}%
                    </div>
                    <div class="metric-label">Taux de satisfaction</div>
                </div>
            """, unsafe_allow_html=True)

    # Onglets d'analyse
    tab1, tab2, tab3 = st.tabs(["📊 Vue Générale", "📈 Analyse Temporelle", "💬 Avis Clients"])
    
    with tab1:
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📊 Distribution des Notes")
            ratings_data = con.execute("""
                SELECT rating, COUNT(*) as count
                FROM conso_reviews
                GROUP BY rating
                ORDER BY rating DESC
            """).fetchdf()
            
            colors = {
                5: '#00FF00',  # Vert
                4: '#7FFF00',  # Vert clair
                3: '#FFFF00',  # Jaune
                2: '#FF7F00',  # Orange
                1: '#FF0000'   # Rouge
            }
            
            fig = go.Figure(data=[go.Pie(
                labels=ratings_data['rating'],
                values=ratings_data['count'],
                marker_colors=[colors[int(rating)] for rating in ratings_data['rating']]
            )])
            
            fig.update_layout(
                title=' ',
                plot_bgcolor='rgba(0,0,0,0)',
                paper_bgcolor='rgba(0,0,0,0)',
                font_color='#ffffff',
                title_font_size=20,
                showlegend=True,
                legend=dict(
                    bgcolor='rgba(0,0,0,0)',
                    bordercolor='rgba(0,0,0,0)',
                    font=dict(color='#ffffff'),
                    traceorder='normal'
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

        with col2:
            st.subheader("📈 Statistiques Clés")
            
            # Calcul des métriques avec plus de contexte
            total_reviews = con.execute("SELECT COUNT(*) as count FROM conso_reviews").fetchone()[0]
            avg_rating = con.execute("SELECT AVG(rating) as avg FROM conso_reviews").fetchone()[0]
            negative_count = con.execute("SELECT COUNT(*) as count FROM negative_reviews").fetchone()[0]
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Total Avis", f"{total_reviews:,}", delta=None)
                st.metric("Note Moyenne", f"{avg_rating:.2f}/5", delta=None)
            with col2:
                st.metric("Avis Négatifs", negative_count, 
                         delta=f"-{round((negative_count/total_reviews)*100, 1)}%",
                         delta_color="inverse")
            st.markdown('</div>', unsafe_allow_html=True)

    with tab2:
        st.subheader("📈 Évolution dans le temps")
        time_data = con.execute("""
            SELECT DATE_TRUNC('month', iso_date) as month, 
                   AVG(rating) as avg_rating,
                   COUNT(*) as review_count
            FROM conso_reviews
            GROUP BY month
        """).fetchdf()
        
        col1, col2 = st.columns(2)
        with col1:
            fig_ratings = px.line(time_data, x='month', y='avg_rating',
                                title="Évolution de la note moyenne")
            st.plotly_chart(fig_ratings, use_container_width=True)
        
        with col2:
            fig_volume = px.bar(time_data, x='month', y='review_count',
                              title="Volume d'avis par mois")
            st.plotly_chart(fig_volume, use_container_width=True)

    with tab3:
        st.subheader("🔍 Analyse des Avis Critiques")
        
        # Filtrage des avis
        reviews_data = con.execute("""
            SELECT review_id, snippet, rating, iso_date, recommendation
            FROM negative_reviews
            ORDER BY iso_date DESC
        """).fetchdf()
        
        # Statistiques des avis critiques
        col1, col2, col3 = st.columns(3)
        with col1:
            total_critical = len(reviews_data)
            st.metric("Nombre d'avis critiques", total_critical)
        with col2:
            avg_critical = reviews_data['rating'].mean()
            st.metric("Note moyenne des avis critiques", f"{avg_critical:.1f}/5")
        with col3:
            recent_critical = reviews_data['iso_date'].max()
            st.metric("Dernier avis critique", recent_critical.strftime('%d/%m/%Y'))

        # Affichage des avis avec un style amélioré
        for _, review in reviews_data.iterrows():
            st.markdown(f"""
                <div class="review-card">
                    <div class="review-header">
                        📝 Avis # {review['iso_date'].strftime('%d/%m/%Y')} | {'⭐' * int(review['rating'])}
                    </div>
                    <div class="review-content">
                        {review['snippet']}
                    </div>
                    <div class="review-stats">
                        <div class="review-recommendation">
                            💡 {review['recommendation']}
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)
    
    con.close()

def main():
    # Style personnalisé pour le conteneur principal
    st.markdown("""
        <style>
        /* Style du conteneur principal */
        .main-container {
            background: rgba(31, 41, 55, 0.8);
            backdrop-filter: blur(10px);
            border-radius: 20px;
            padding: 2rem;
            box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
            border: 1px solid rgba(255, 255, 255, 0.1);
            margin: 2rem auto;
            max-width: 1200px;
        }
        
        /* Style du logo animé */
        .logo-container {
            text-align: center;
            margin-bottom: 2rem;
            animation: fadeInDown 1s ease-out;
        }
        
        @keyframes fadeInDown {
            from {
                opacity: 0;
                transform: translateY(-20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }
        
        /* Style du formulaire */
        .search-container {
            background: rgba(255, 255, 255, 0.05);
            border-radius: 15px;
            padding: 2rem;
            margin-top: 2rem;
            border: 1px solid rgba(255, 255, 255, 0.1);
            animation: fadeIn 0.8s ease-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; }
            to { opacity: 1; }
        }
        
        /* Style du bouton */
        .custom-button {
            background: linear-gradient(135deg, #4CAF50, #2196F3);
            color: white;
            padding: 0.8rem 2rem;
            border-radius: 10px;
            border: none;
            font-weight: 600;
            letter-spacing: 1px;
            text-transform: uppercase;
            transition: all 0.3s ease;
            width: 100%;
            margin-top: 1rem;
        }
        
        .custom-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(33, 150, 243, 0.3);
        }
        
        /* Style de la barre de progression */
        .progress-container {
            margin: 2rem 0;
            position: relative;
        }
        
        .progress-bar {
            height: 6px;
            background: linear-gradient(90deg, #4CAF50, #2196F3);
            border-radius: 3px;
            transition: width 0.3s ease;
        }
        
        .progress-label {
            position: absolute;
            top: -25px;
            right: 0;
            color: white;
            font-size: 0.9rem;
            font-weight: 500;
        }
        
        /* Animation de chargement */
        @keyframes pulse {
            0% { opacity: 1; }
            50% { opacity: 0.5; }
            100% { opacity: 1; }
        }
        
        .loading-text {
            color: white;
            text-align: center;
            margin-top: 1rem;
            animation: pulse 1.5s infinite;
            font-weight: 500;
        }
        </style>
    """, unsafe_allow_html=True)

    
    # Logo et titre
    st.markdown("""
        <div class="logo-container">
            <h1 class="main-header">EchoWize Analytics</h1>
            <p style="color: #B0B0B0; font-size: 1.2rem; margin-top: 0.5rem;">
                Analysez et optimisez votre réputation en ligne
            </p>
        </div>
    """, unsafe_allow_html=True)
    # Formulaire de recherche
    with st.form("restaurant_form"):
        restaurant_name = st.text_input("Nom du restaurant", 
                                      placeholder="Ex: Le Petit Bistrot",
                                      help="Entrez le nom exact du restaurant à analyser")
        
        # Bouton personnalisé
        submitted = st.form_submit_button("Analyser", 
                                        help="Cliquez pour lancer l'analyse")
        st.markdown('</div>', unsafe_allow_html=True)

        if submitted and restaurant_name:
            # Animation de chargement personnalisée
            progress_text = "Analyse en cours..."
            progress_bar = st.progress(0)
            status_text = st.empty()

            # Étapes avec leur durée relative (total = 60 secondes)
            etapes = [
                ("Récupération des données...", 15),  # 15 secondes
                ("Analyse des avis...", 25),          # 25 secondes
                ("Génération des insights...", 15),   # 15 secondes
                ("Finalisation...", 5)                # 5 secondes
            ]
            
            temps_total = 120  # 60 secondes au total
            for etape, duree in etapes:
                status_text.markdown(f'<div class="loading-text">{etape}</div>', unsafe_allow_html=True)
                iterations = 20  # Nombre d'étapes pour une progression fluide
                for i in range(iterations):
                    # Calcul du progrès global
                    progress_precedent = sum([d for _, d in etapes[:etapes.index((etape, duree))]])
                    progress = (progress_precedent + (i + 1) * duree / iterations) / temps_total
                    progress_bar.progress(progress)
                    time.sleep(duree / iterations)  # Divise la durée de l'étape en iterations égales

            # Appel API et affichage des résultats
            resultats = call_api(restaurant_name)
            if resultats:
                progress_bar.empty()
                status_text.empty()
                afficher_dashboard()
            else:
                st.error("Aucun résultat trouvé pour ce restaurant.")

    st.markdown('</div>', unsafe_allow_html=True)

if __name__ == "__main__":
    main()