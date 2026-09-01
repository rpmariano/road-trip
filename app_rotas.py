import streamlit as st
import folium
from folium import plugins
import gpxpy
import requests
import datetime
from streamlit_folium import st_folium

st.set_page_config(page_title="Rotas Xisto", layout="wide")

# Inicialização da variável de sessão para o comportamento "Acordeão"
if 'dia_foco' not in st.session_state:
    st.session_state.dia_foco = "Visão Geral"

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

info_dias = {
    "Dia 1 - Atlântico e Pinhal": {"km": "165 km", "tempo": "3h 45m", "pontos": "Cascais » Ericeira » Foz do Arelho » S. Pedro de Moel » Leiria", "vistas": "Encontro da Lagoa de Óbidos com o mar; Farol do Penedo da Saudade.", "comer": "Tasca do Zé Mário ou Ao Largo.", "dormir": "Hostel Leiria ou Hotel Ibis Leiria."},
    "Dia 2 - Transição para a Serra": {"km": "92 km", "tempo": "2h 15m", "pontos": "Leiria » Penela » Talasnal » Lousã", "vistas": "Castelo de Penela e quelhas a pé no Talasnal.", "comer": "O Burgo (Vitela assada no forno a lenha).", "dormir": "Palácio da Lousã Boutique Hotel ou HI Hostel Lousã."},
    "Dia 3 - O Coração do Xisto": {"km": "80 km", "tempo": "2h 30m", "pontos": "Lousã » Góis » Piódão", "vistas": "Margens do rio Ceira (Góis); Anfiteatro do Piódão.", "comer": "O Fontinha (Cabrito assado).", "dormir": "Inatel Piódão ou Casa da Padaria."},
    "Dia 4 - Cascatas e Património": {"km": "140 km", "tempo": "2h 45m", "pontos": "Piódão » Fraga da Pena » Batalha", "vistas": "Cascata da Fraga da Pena; Mosteiro da Batalha.", "comer": "Tasca do Xico ou Burro Velho.", "dormir": "Hotel Casa do Outeiro ou Villa Batalha."},
    "Dia 5 - Vilas Medievais e Regresso": {"km": "150 km", "tempo": "1h 45m", "pontos": "Batalha » Óbidos » Cascais", "vistas": "Muralhas e ruelas de Óbidos.", "comer": "Jamon Jamon.", "dormir": "Chegada a Casa."}
}

st.title("🏍️ Rota das Aldeias do Xisto")

weather_api_key = st.secrets.get("OPENWEATHER_KEY", "")
ors_api_key = st.secrets.get("ORS_KEY", "")

st.sidebar.markdown("---")
st.sidebar.info("Total Estimado: 627 km | 13h 00m de condução")
if not ors_api_key:
    st.sidebar.error("Falta configurar a ORS_KEY nos Secrets para evitar autoestradas.")

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

col_mapa, col_info = st.columns([6, 4])

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
    coords_dia_focado = [] # Guarda os limites apenas do dia selecionado
    
    for index, rota in enumerate(gpx.routes):
        tema = temas_dias[index % len(temas_dias)]
        coords_waypoints = []
        
        # Verifica se este é o dia atualmente selecionado (ou se está na Visão Geral)
        dia_esta_focado = (st.session_state.dia_foco == "Visão Geral") or (st.session_state.dia_foco == rota.name)
        
        # Ajusta a visibilidade: dias não focados ficam semi-transparentes
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
            
            # Esconde os marcadores dos dias inativos para limpar o mapa
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
            
            # Só desenha as setas direcionais no dia que está em foco
            if dia_esta_focado:
                plugins.PolyLineTextPath(
                    linha_rota, '  ►  ', repeat=True, offset=5.5,
                    attributes={'fill': '#000000', 'font-weight': 'bold', 'font-size': '15', 'fill-opacity': '0.7'}
                ).add_to(mapa)

    folium.LayerControl().add_to(mapa)
    
    # Aplica o Zoom (Fit Bounds) dinâmico
    if st.session_state.dia_foco != "Visão Geral" and coords_dia_focado:
        mapa.fit_bounds(coords_dia_focado)
    elif todas_coords:
        mapa.fit_bounds(todas_coords)

    st_folium(mapa, width="100%", height=650)


with col_info:
    st.subheader("📋 Itinerário Detalhado")
    
    # Botão de Reset para ver o mapa todo
    if st.button("🗺️ Mostrar Toda a Viagem", use_container_width=True):
        st.session_state.dia_foco = "Visão Geral"
        st.rerun()

    for i, (dia, info) in enumerate(info_dias.items()):
        tema = temas_dias[i % len(temas_dias)]
        
        # O botão serve de gatilho para o "Uncollapse"
        if st.button(f"{tema['emoji']} {dia}", use_container_width=True):
            if st.session_state.dia_foco == dia:
                st.session_state.dia_foco = "Visão Geral" # Clicar no mesmo fecha-o
            else:
                st.session_state.dia_foco = dia
            st.rerun() # Força a atualização imediata do mapa e da interface
            
        # O conteúdo expandido: só aparece se este for o dia ativo
        if st.session_state.dia_foco == dia:
            with st.container(border=True):
                st.markdown(f"**🛣️ Rota:** {info['pontos']}")
                st.markdown(f"**📏 Distância:** {info['km']} | **⏱️ Tempo:** {info['tempo']}")
                st.markdown(f"📸 **Paragens & Vistas:** {info['vistas']}")
                st.markdown(f"🍽️ **Onde Comer:** {info['comer']}")
                st.markdown(f"🛏️ **Onde Dormir:** {info['dormir']}")
