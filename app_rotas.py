import streamlit as st
import folium
from folium import plugins
import gpxpy
import requests
import datetime
from streamlit_folium import st_folium

st.set_page_config(page_title="Rotas Xisto", page_icon="🏍️", layout="wide")

# CSS customizado para otimização Mobile e Desktop
st.markdown("""
<style>
    .block-container {
        padding-top: 1.5rem !important;
        padding-bottom: 1rem !important;
        max-width: 1400px;
    }
    .stButton>button {
        border-radius: 12px;
        padding: 0.6rem 1rem;
        font-size: 16px;
        font-weight: 500;
        border: 1px solid #ddd;
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        border-color: #ff4b4b;
        color: #ff4b4b;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

if 'dia_foco' not in st.session_state:
    st.session_state.dia_foco = "Visão Geral"

gpx_data = """<?xml version="1.0" ?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" creator="Gemini" version="1.1">
  <metadata><name>Passeio de Mota - Aldeias de Xisto</name></metadata>
  <rte><name>Dia 1 - Atlântico e Pinhal</name>
    <rtept lat="38.6979" lon="-9.4215"><name>Cascais</name></rtept>
    <rtept lat="38.9616" lon="-9.4139"><name>Ericeira</name></rtept>
    <rtept lat="39.4290" lon="-9.2201"><name>Foz do Arelho</name></rtept>
    <rtept lat="39.7583" lon="-9.0306"><name>São Pedro de Moel</name></rtept>
    <rtept lat="39.7436" lon="-8.8071"><name>Leiria</name></rtept>
  </rte>
  <rte><name>Dia 2 - Transição para a Serra</name>
    <rtept lat="39.7436" lon="-8.8071"><name>Leiria</name></rtept>
    <rtept lat="40.0302" lon="-8.3897"><name>Penela</name></rtept>
    <rtept lat="40.0945" lon="-8.2307"><name>Talasnal</name></rtept>
    <rtept lat="40.1121" lon="-8.2476"><name>Lousã</name></rtept>
  </rte>
  <rte><name>Dia 3 - O Coração do Xisto</name>
    <rtept lat="40.1121" lon="-8.2476"><name>Lousã</name></rtept>
    <rtept lat="40.1539" lon="-8.1105"><name>Góis</name></rtept>
    <rtept lat="40.2294" lon="-7.8250"><name>Piódão</name></rtept>
  </rte>
  <rte><name>Dia 4 - Cascatas e Património</name>
    <rtept lat="40.2294" lon="-7.8250"><name>Piódão</name></rtept>
    <rtept lat="40.2185" lon="-7.9355"><name>Fraga da Pena</name></rtept>
    <rtept lat="39.6589" lon="-8.8247"><name>Batalha</name></rtept>
  </rte>
  <rte><name>Dia 5 - Vilas Medievais e Regresso</name>
    <rtept lat="39.6589" lon="-8.8247"><name>Batalha</name></rtept>
    <rtept lat="39.3621" lon="-9.1571"><name>Óbidos</name></rtept>
    <rtept lat="38.6979" lon="-9.4215"><name>Cascais</name></rtept>
  </rte>
</gpx>"""

info_dias = {
    "Dia 1 - Atlântico e Pinhal": {
        "km": "165 km", "tempo": "3h 45m", 
        "pontos": "Cascais » Ericeira » Foz do Arelho » S. Pedro de Moel » Leiria", 
        "vistas": "Encontro da Lagoa de Óbidos com o mar; Farol do Penedo da Saudade.", 
        "comer": "Tasca do Zé Mário ou Ao Largo.", 
        "dormir": "Hostel Leiria ou Hotel Ibis Leiria.",
        "equipamento": "Fato de meia-estação. O vento costeiro e a nortada podem arrefecer o corpo. Usem luvas que cortem o vento (windstopper) e fechem as entradas de ar frontais do casaco durante a manhã."
    },
    "Dia 2 - Transição para a Serra": {
        "km": "92 km", "tempo": "2h 15m", 
        "pontos": "Leiria » Penela » Talasnal » Lousã", 
        "vistas": "Castelo de Penela e quelhas a pé no Talasnal.", 
        "comer": "O Burgo (Vitela assada no forno a lenha).", 
        "dormir": "Palácio da Lousã Boutique Hotel ou HI Hostel Lousã.",
        "equipamento": "Ao subirem de elevação em direção à serra, a temperatura desce. Garantam que o forro térmico ou um impermeável leve vai à mão na top-case para vestirem quando o frio apertar perto do Talasnal."
    },
    "Dia 3 - O Coração do Xisto": {
        "km": "80 km", "tempo": "2h 30m", 
        "pontos": "Lousã » Góis » Piódão", 
        "vistas": "Margens do rio Ceira (Góis); Anfiteatro do Piódão.", 
        "comer": "O Fontinha (Cabrito assado).", 
        "dormir": "Inatel Piódão ou Casa da Padaria.",
        "equipamento": "Dia exigente e húmido nos vales cerrados. Pinlock obrigatório no capacete para a viseira não embaciar, luvas mais quentes (ou punhos aquecidos ligados) e um bom *buff* de pescoço para evitar as correntes de ar frio."
    },
    "Dia 4 - Cascatas e Património": {
        "km": "140 km", "tempo": "2h 45m", 
        "pontos": "Piódão » Fraga da Pena » Batalha", 
        "vistas": "Cascata da Fraga da Pena; Mosteiro da Batalha.", 
        "comer": "Tasca do Xico ou Burro Velho.", 
        "dormir": "Hotel Casa do Outeiro ou Villa Batalha.",
        "equipamento": "Sistema de 'camadas'. A manhã no Piódão será fria, mas à tarde, na descida para a Batalha, o clima aquece. Tirem o forro ao almoço e troquem para luvas de verão/malha à tarde."
    },
    "Dia 5 - Vilas Medievais e Regresso": {
        "km": "150 km", "tempo": "1h 45m", 
        "pontos": "Batalha » Óbidos » Cascais", 
        "vistas": "Muralhas e ruelas de Óbidos.", 
        "comer": "Jamon Jamon.", 
        "dormir": "Chegada a Casa.",
        "equipamento": "Clima de final de verão. Fato bem ventilado (podem abrir os fechos todos), óculos de sol (ou viseira escura no capacete) e luvas leves para maior destreza no trânsito à aproximação a Cascais."
    }
}

st.markdown("<h1 style='text-align: center; margin-bottom: 0;'>🏍️ Rota das Aldeias do Xisto</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: #666; font-size: 1.1em;'>📍 627 km &nbsp; | &nbsp; ⏱️ 13h 00m de condução</p>", unsafe_allow_html=True)
st.divider()

weather_api_key = st.secrets.get("OPENWEATHER_KEY", "")
ors_api_key = st.secrets.get("ORS_KEY", "")

if not ors_api_key:
    st.warning("⚠️ Chave de Rotas (ORS_KEY) não configurada. A exibir ligação direta entre os pontos.")

@st.cache_data(ttl=1800)
def obter_previsao(lat, lon, key):
    if not key: return ""
    url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={key}&units=metric&lang=pt"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            dados = res.json()
            previsoes_diarias = {}
            for item in dados['list']:
                data_texto, hora = item['dt_txt'].split(' ')
                if data_texto not in previsoes_diarias or hora == '15:00:00':
                    previsoes_diarias[data_texto] = item
            
            html = "<div style='display: flex; overflow-x: auto; gap: 8px; margin-top: 10px; padding-bottom: 5px;'>"
            for data, prev in list(previsoes_diarias.items())[:5]:
                temp = prev['main']['temp']
                icone = prev['weather'][0]['icon']
                dia_semana = datetime.datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m')
                html += f"""
                <div style='background-color:#f0f2f6; border-radius:8px; padding:6px; min-width:70px; text-align:center;'>
                    <div style='font-size:0.8em; color:#555; font-weight:bold;'>{dia_semana}</div>
                    <img src='https://openweathermap.org/img/wn/{icone}@2x.png' width='40' style='margin:-5px 0;'>
                    <div style='font-size:0.9em; font-weight:bold;'>{temp:.0f}°C</div>
                </div>
                """
            html += "</div>"
            return html
        return ""
    except: return ""

@st.cache_data(ttl=86400)
def obter_tracado_cénico(pontos, api_key):
    coords = [[lon, lat] for lat, lon in pontos]
    headers = {
        'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8',
        'Authorization': api_key,
        'Content-Type': 'application/json; charset=utf-8'
    }
    body = {
        "coordinates": coords,
        "options": {"avoid_features": ["highways", "tollways"]},
        "elevation": False, "instructions": False
    }
    url = 'https://api.openrouteservice.org/v2/directions/driving-car/geojson'
    try:
        res = requests.post(url, json=body, headers=headers)
        if res.status_code == 200:
            coords_geojson = res.json()['features'][0]['geometry']['coordinates']
            return [[lat, lon] for lon, lat in coords_geojson]
    except Exception as e: print(f"Erro no routing cénico: {e}")
    return pontos

col_mapa, col_info = st.columns([6, 4], gap="large")

temas_dias = [
    {"hex": "#3498db", "folium": "blue", "emoji": "🔵"},
    {"hex": "#e67e22", "folium": "orange", "emoji": "🟠"},
    {"hex": "#2ecc71", "folium": "green", "emoji": "🟢"},
    {"hex": "#9b59b6", "folium": "purple", "emoji": "🟣"},
    {"hex": "#e74c3c", "folium": "red", "emoji": "🔴"}
]

with col_mapa:
    gpx = gpxpy.parse(gpx_data)
    mapa = folium.Map(location=[39.6, -8.5], zoom_start=8)
    
    folium.TileLayer('OpenStreetMap').add_to(mapa)
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)',
        name='Topográfico'
    ).add_to(mapa)
    plugins.Fullscreen(position='topright').add_to(mapa)
    
    todas_coords = []
    coords_dia_focado = [] 
    
    for index, rota in enumerate(gpx.routes):
        tema = temas_dias[index % len(temas_dias)]
        coords_waypoints = []
        
        dia_esta_focado = (st.session_state.dia_foco == "Visão Geral") or (st.session_state.dia_foco == rota.name)
        
        opacidade_linha = 0.8 if dia_esta_focado else 0.25
        peso_linha = 5 if dia_esta_focado else 3
        
        for i, ponto in enumerate(rota.points):
            coords = (ponto.latitude, ponto.longitude)
            coords_waypoints.append(coords)
            todas_coords.append(coords)
            if st.session_state.dia_foco == rota.name:
                coords_dia_focado.append(coords)
            
            previsao_html = obter_previsao(ponto.latitude, ponto.longitude, weather_api_key)
            popup_html = f"<div style='font-family:sans-serif; min-width:250px;'><h4 style='margin:0; color:{tema['hex']};'>{ponto.name}</h4><p style='margin:2px 0 10px 0; font-size:12px; color:gray;'>{rota.name}</p>{previsao_html}</div>"
            
            if dia_esta_focado:
                icone_tipo = 'motorcycle' if i == 0 or i == len(rota.points)-1 else 'flag'
                folium.Marker(
                    location=coords,
                    popup=folium.Popup(popup_html, max_width=350),
                    tooltip=ponto.name,
                    icon=folium.Icon(color=tema['folium'], icon=icone_tipo, prefix='fa')
                ).add_to(mapa)
            
        if coords_waypoints:
            tracado_real = obter_tracado_cénico(coords_waypoints, ors_api_key) if ors_api_key else coords_waypoints
            
            linha_rota = folium.PolyLine(
                locations=tracado_real,
                color=tema['hex'], 
                weight=peso_linha, 
                opacity=opacidade_linha,
                tooltip=rota.name
            ).add_to(mapa)
            
            if dia_esta_focado:
                plugins.PolyLineTextPath(
                    linha_rota, '  ►  ', repeat=True, offset=5.5,
                    attributes={'fill': '#000000', 'font-weight': 'bold', 'font-size': '15', 'fill-opacity': '0.7'}
                ).add_to(mapa)

    folium.LayerControl().add_to(mapa)
    
    if st.session_state.dia_foco != "Visão Geral" and coords_dia_focado:
        mapa.fit_bounds(coords_dia_focado)
    elif todas_coords:
        mapa.fit_bounds(todas_coords)

    st_folium(mapa, use_container_width=True, height=500)


with col_info:
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    
    if st.button("🗺️ Mostrar Toda a Viagem", use_container_width=True):
        st.session_state.dia_foco = "Visão Geral"
        st.rerun()

    for i, (dia, info) in enumerate(info_dias.items()):
        tema = temas_dias[i % len(temas_dias)]
        
        if st.button(f"{tema['emoji']} {dia}", use_container_width=True):
            if st.session_state.dia_foco == dia:
                st.session_state.dia_foco = "Visão Geral"
            else:
                st.session_state.dia_foco = dia
            st.rerun()
            
        if st.session_state.dia_foco == dia:
            with st.container(border=True):
                st.markdown(f"**🛣️ Rota:** {info['pontos']}")
                st.markdown(f"**📏 Distância:** {info['km']} | **⏱️ Tempo:** {info['tempo']}")
                st.markdown(f"📸 **Paragens:** {info['vistas']}")
                st.markdown(f"🍽️ **Comer:** {info['comer']}")
                st.markdown(f"🛏️ **Dormir:** {info['dormir']}")
                st.markdown(f"🧳 **Equipamento:** {info['equipamento']}")
