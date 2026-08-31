import streamlit as st
import folium
import gpxpy
import requests
from streamlit_folium import st_folium

# Layout panorâmico para melhor visualização
st.set_page_config(page_title="Rotas Xisto", layout="wide")

gpx_data = """<?xml version="1.0" ?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" creator="Gemini" version="1.1">
  <metadata><name>Passeio de Mota - Aldeias de Xisto</name></metadata>
  <rte>
    <name>Dia 1 - Atlântico e Pinhal</name>
    <rtept lat="38.6979" lon="-9.4215"><name>Cascais</name></rtept>
    <rtept lat="38.9616" lon="-9.4139"><name>Ericeira</name></rtept>
    <rtept lat="39.4290" lon="-9.2201"><name>Foz do Arelho</name></rtept>
    <rtept lat="39.7583" lon="-9.0306"><name>São Pedro de Moel</name></rtept>
    <rtept lat="39.7436" lon="-8.8071"><name>Leiria</name></rtept>
  </rte>
  <rte>
    <name>Dia 2 - Transição para a Serra</name>
    <rtept lat="39.7436" lon="-8.8071"><name>Leiria</name></rtept>
    <rtept lat="40.0302" lon="-8.3897"><name>Penela</name></rtept>
    <rtept lat="40.0945" lon="-8.2307"><name>Talasnal</name></rtept>
    <rtept lat="40.1121" lon="-8.2476"><name>Lousã</name></rtept>
  </rte>
  <rte>
    <name>Dia 3 - O Coração do Xisto</name>
    <rtept lat="40.1121" lon="-8.2476"><name>Lousã</name></rtept>
    <rtept lat="40.1539" lon="-8.1105"><name>Góis</name></rtept>
    <rtept lat="40.2294" lon="-7.8250"><name>Piódão</name></rtept>
  </rte>
  <rte>
    <name>Dia 4 - Cascatas e Património</name>
    <rtept lat="40.2294" lon="-7.8250"><name>Piódão</name></rtept>
    <rtept lat="40.2185" lon="-7.9355"><name>Fraga da Pena</name></rtept>
    <rtept lat="39.6589" lon="-8.8247"><name>Batalha</name></rtept>
  </rte>
  <rte>
    <name>Dia 5 - Vilas Medievais e Regresso</name>
    <rtept lat="39.6589" lon="-8.8247"><name>Batalha</name></rtept>
    <rtept lat="39.3621" lon="-9.1571"><name>Óbidos</name></rtept>
    <rtept lat="38.6979" lon="-9.4215"><name>Cascais</name></rtept>
  </rte>
</gpx>"""

# Dados detalhados de cada etapa para a UI
info_dias = {
    "Dia 1 - Atlântico e Pinhal": {
        "km": "165 km", "tempo": "3h 45m",
        "pontos": "Cascais » Ericeira » Foz do Arelho » S. Pedro de Moel » Leiria",
        "vistas": "Encontro da Lagoa de Óbidos com o mar (Foz do Arelho); Farol do Penedo da Saudade (S. Pedro de Moel).",
        "comer": "Tasca do Zé Mário ou Ao Largo (Naco de vitela/bife c/ cogumelos).",
        "dormir": "Hostel Leiria ou Hotel Ibis Leiria."
    },
    "Dia 2 - Transição para a Serra": {
        "km": "92 km", "tempo": "2h 15m",
        "pontos": "Leiria » Penela » Talasnal » Lousã",
        "vistas": "Castelo de Penela e quelhas a pé no Talasnal.",
        "comer": "O Burgo (Vitela assada no forno a lenha).",
        "dormir": "Palácio da Lousã Boutique Hotel ou HI Hostel Lousã."
    },
    "Dia 3 - O Coração do Xisto": {
        "km": "80 km", "tempo": "2h 30m",
        "pontos": "Lousã » Góis » Piódão",
        "vistas": "Margens do rio Ceira (Góis); Anfiteatro e casas azuis do Piódão.",
        "comer": "O Fontinha (Cabrito assado).",
        "dormir": "Inatel Piódão ou Casa da Padaria."
    },
    "Dia 4 - Cascatas e Património": {
        "km": "140 km", "tempo": "2h 45m",
        "pontos": "Piódão » Fraga da Pena » Batalha",
        "vistas": "Cascata da Fraga da Pena (Mata da Margaraça); Mosteiro da Batalha.",
        "comer": "Tasca do Xico ou Burro Velho (Tábua de carnes ou bife na pedra).",
        "dormir": "Hotel Casa do Outeiro ou Villa Batalha."
    },
    "Dia 5 - Vilas Medievais e Regresso": {
        "km": "150 km", "tempo": "1h 45m",
        "pontos": "Batalha » Óbidos » Cascais",
        "vistas": "Muralhas e ruelas calcetadas de Óbidos (provar a Ginjinha).",
        "comer": "Jamon Jamon (Pregos e carnes ibéricas).",
        "dormir": "Chegada a Casa."
    }
}

st.title("🏍️ Rota das Aldeias do Xisto")

# Barra lateral apenas para configurações compactas
api_key = st.sidebar.text_input("🔑 Chave OpenWeatherMap", type="password", help="Insere a chave para veres a meteorologia no mapa.")
st.sidebar.markdown("---")
st.sidebar.info("Total Estimado: 627 km | 13h 00m de condução")

@st.cache_data(ttl=600)
def obter_meteorologia(lat, lon, key):
    if not key:
        return "<br><small><i>S/ Info Tempo</i></small>"
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric&lang=pt"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            d = res.json()
            return f"<br><img src='http://openweathermap.org/img/wn/{d['weather'][0]['icon']}.png' width='30'><br><b>{d['main']['temp']:.1f}°C</b>"
        return ""
    except:
        return ""

col_mapa, col_info = st.columns([6, 4]) # 60% Mapa, 40% Informação

with col_mapa:
    gpx = gpxpy.parse(gpx_data)
    mapa = folium.Map(location=[39.6, -8.5], zoom_start=8)
    cores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#d62728']
    
    for index, rota in enumerate(gpx.routes):
        cor = cores[index % len(cores)]
        coords_rota = []
        
        for ponto in rota.points:
            coords = (ponto.latitude, ponto.longitude)
            coords_rota.append(coords)
            
            tempo = obter_meteorologia(ponto.latitude, ponto.longitude, api_key)
            html_popup = f"<div style='text-align:center; min-width:100px;'><b>{ponto.name}</b>{tempo}</div>"
            
            folium.Marker(
                location=coords,
                popup=folium.Popup(html_popup, max_width=200),
                tooltip=f"{ponto.name} ({rota.name})",
                icon=folium.Icon(color=cor if cor in ['blue', 'green', 'purple', 'red', 'orange'] else 'blue')
            ).add_to(mapa)
            
        if coords_rota:
            folium.PolyLine(coords_rota, color=cor, weight=5, opacity=0.8).add_to(mapa)

    st_folium(mapa, width="100%", height=650)

with col_info:
    st.subheader("📋 Itinerário Detalhado")
    for dia, info in info_dias.items():
        with st.expander(f"📍 {dia}"):
            st.markdown(f"**Rota:** {info['pontos']}")
            st.markdown(f"**Distância:** {info['km']} | **Tempo:** {info['tempo']}")
            st.markdown(f"📸 **Paragens & Vistas:** {info['vistas']}")
            st.markdown(f"🍽️ **Onde Comer:** {info['comer']}")
            st.markdown(f"🛏️ **Onde Dormir:** {info['dormir']}")
