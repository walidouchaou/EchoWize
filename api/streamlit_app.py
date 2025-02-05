import streamlit as st
import duckdb
import plotly.express as px
import requests

# Configuration de la page avec un thème sombre
st.set_page_config(
    page_title="EchoWize Analytics",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Styles personnalisés avec un thème sombre professionnel
st.markdown("""
    <style>
    /* Thème sombre global */
    .main {
        background-color: #1a1a1a;
        color: #ffffff !important;
    }
    
    /* En-tête principal */
    .main-header {
        font-size: 2.8rem;
        font-weight: 700;
        background: linear-gradient(120deg, #4CAF50, #2196F3);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin: 2rem 0;
        padding: 1rem;
    }
    
    /* Style des métriques */
    .metric-container {
        background: linear-gradient(145deg, #2d2d2d, #353535);
        padding: 1.5rem;
        border-radius: 10px;
        text-align: center;
        border: 1px solid #404040;
        margin-bottom: 1rem;
    }
    
    .metric-value {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4CAF50;
        margin-bottom: 0.5rem;
    }
    
    .metric-label {
        color: #ffffff;
        font-size: 1rem;
        font-weight: 500;
    }

    /* Override Streamlit's default text color */
    .css-1dp5vir, .css-81oif8, .css-10trblm {
        color: #ffffff !important;
    }
    
    /* Override pour les graphiques */
    .js-plotly-plot .plotly .gtitle {
        fill: #ffffff !important;
    }
    
    /* Conteneurs de cartes */
    .card-container {
        background: #2d2d2d;
        border-radius: 12px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
        border: 1px solid #3d3d3d;
    }
    
    /* Style des graphiques */
    .chart-container {
        background: #2d2d2d;
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid #3d3d3d;
    }
    
    /* Style des onglets */
    .stTabs [data-baseweb="tab-list"] {
        background-color: #2d2d2d;
        padding: 0.5rem;
        border-radius: 8px;
        border: 1px solid #3d3d3d;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #ffffff;
        background-color: #353535;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        margin-right: 0.5rem;
    }
    
    /* Style des avis */
    .review-card {
        background: #2d2d2d;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 4px solid #4CAF50;
    }
    
    .review-header {
        color: #ffffff;
        font-size: 1.1rem;
        font-weight: 600;
        margin-bottom: 1rem;
    }
    
    .review-content {
        color: #b0b0b0;
        line-height: 1.6;
    }
    
    .review-stats {
        display: flex;
        justify-content: space-between;
        margin-top: 1rem;
        padding-top: 1rem;
        border-top: 1px solid #3d3d3d;
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
    st.markdown('<h1 class="main-header">EchoWize Analytics</h1>', unsafe_allow_html=True)
    
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
                ORDER BY rating ASC
            """).fetchdf()
            
            fig = px.pie(ratings_data, values='count', names='rating',
                         title=' ',
                         color_discrete_sequence=[
                             '#FF0000',  # Note 1 - Rouge vif
                             '#FF8C00',  # Note 2 - Orange
                             '#FFD700',  # Note 3 - Jaune doré
                             '#90EE90',  # Note 4 - Vert clair
                             '#008000'   # Note 5 - Vert foncé
                         ])
            
            fig.update_layout(
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
        st.subheader("Évolution dans le temps")
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
                        📝 Avis #{review['review_id']} | {review['iso_date'].strftime('%d/%m/%Y')} | {'⭐' * int(review['rating'])}
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
    afficher_dashboard()
    with st.form("restaurant_form"):
        st.markdown('<h1 class="main-header">EchoWize Analytics</h1>', unsafe_allow_html=True)
        restaurant_name = st.text_input("Nom du restaurant")
        submitted = st.form_submit_button("Analyser")
        
        if submitted and restaurant_name:
            with st.spinner('Récupération et analyse des données en cours...'):
                resultats = call_api(restaurant_name)
                if resultats:
                    afficher_dashboard()

if __name__ == "__main__":
    main()