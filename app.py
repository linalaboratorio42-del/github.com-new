import streamlit as st
import pandas as pd
import requests
from sklearn.ensemble import RandomForestClassifier
import warnings
warnings.filterwarnings("ignore")

st.set_page_config(page_title="LA FIJA 🔮", page_icon="⚽", layout="centered")

st.markdown("""
<style>
    h1 { text-align: center; color: #00FF88; }
    .stButton>button { background-color: #00FF88; color: black; font-weight: bold; width: 100%; height: 50px; font-size: 20px; border-radius: 15px; }
</style>
""", unsafe_allow_html=True)

st.title("🔮 LA FIJA")
st.markdown("### ¡Qué hubo, crack! ¿Quién se lleva el partido hoy?")
st.markdown("Champions • Premier • La Liga • Serie A • Bundesliga • Liga 1 Perú")
st.markdown("---")

try:
    API_KEY = st.secrets["API_KEY"]
except:
    API_KEY = "TU_LLAVE_AQUI"

@st.cache_data(ttl=3600)
def cargar_y_entrenar():
    ligas = {"PD": "La Liga", "PL": "Premier", "SA": "Serie A", "BL1": "Bundesliga", "CL": "Champions"}
    todo = []
    headers = {"X-Auth-Token": API_KEY}
    for codigo in ligas:
        url = f"https://api.football-data.org/v4/competitions/{codigo}/matches?season=2024&status=FINISHED"
        r = requests.get(url, headers=headers).json()
        for m in r.get("matches", []):
            if m["score"]["fullTime"]["home"] is not None:
                todo.append({"local": m["homeTeam"]["shortName"], "visita": m["awayTeam"]["shortName"], "goles_local": m["score"]["fullTime"]["home"], "goles_visita": m["score"]["fullTime"]["away"]})
    df = pd.DataFrame(todo)
    X = []
    y = []
    for _, fila in df.iterrows():
        X.append([fila["goles_local"], fila["goles_visita"], fila["goles_local"]-fila["goles_visita"]])
        y.append(1 if fila["goles_local"] > fila["goles_visita"] else (2 if fila["goles_visita"] > fila["goles_local"] else 0))
    modelo = RandomForestClassifier(n_estimators=100, random_state=42)
    modelo.fit(X, y)
    return df, modelo

with st.spinner("Cargando La Fija..."):
    df_todo, modelo_global = cargar_y_entrenar()

equipos = sorted(list(set(df_todo['local'].unique()) | set(df_todo['visita'].unique())))
local = st.selectbox("🏠 Equipo de casa", equipos, index=equipos.index("Real Madrid") if "Real Madrid" in equipos else 0)
visita = st.selectbox("✈️ Equipo visitante", equipos, index=equipos.index("Barcelona") if "Barcelona" in equipos else 1)

if st.button("🔮 ¡DIME LA FIJA!"):
    def prom(equipo):
        hist = df_todo[(df_todo['local'] == equipo) | (df_todo['visita'] == equipo)].tail(5)
        g = []
        for _, h in hist.iterrows():
            g.append(h['goles_local'] if h['local'] == equipo else h['goles_visita'])
        return sum(g)/len(g) if g else 1.2
    gl = prom(local)
    gv = prom(visita)
    pred = modelo_global.predict([[gl, gv, gl-gv]])[0]
    prob = modelo_global.predict_proba([[gl, gv, gl-gv]])[0]
    if pred == 1:
        st.success(f"🏆 ¡LA FIJA ES EL LOCAL! 🏠🔥 {local} se lo lleva, crack.")
    elif pred == 2:
        st.success(f"🏆 ¡LA FIJA ES LA VISITA! ✈️🔥 {visita} se lleva los 3 puntos.")
    else:
        st.warning(f"🤝 ¡EMPATE! Nadie se lo lleva.")
    st.markdown(f"**📊 ¿Cómo va la cosa?**\n- 🏠 Gana {local}: **{prob[1]*100:.0f}%**\n- 🤝 Empate: **{prob[0]*100:.0f}%**\n- ✈️ Gana {visita}: **{prob[2]*100:.0f}%**\n\n**⚽ Goles promedio:** {local}: {gl:.1f} | {visita}: {gv:.1f}\n\n¡Suerte, crack! 🍀")
st.markdown("---")
st.caption("Hecho con ❤️ en Perú | LA FIJA - Tu IA de Fútbol")
