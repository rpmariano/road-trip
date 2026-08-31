import streamlit as st
import folium
from folium import plugins
import gpxpy
import requests
import datetime
from streamlit_folium import st_folium

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

info_dias = {
    "Dia 1 - Atlântico e Pinhal": {"km": "165 km", "tempo": "3h 45m", "pontos": "Cascais » Ericeira » Foz do Arelho » S. Pedro de Moel » Leiria", "vistas": "Encontro da Lagoa de Óbidos com o mar; Farol do Penedo da Saudade.", "comer": "Tasca do Zé Mário ou Ao Largo.", "dormir": "Hostel Leiria ou Hotel Ibis Leiria."},
    "Dia 2 - Transição para a Serra": {"km": "92 km", "tempo": "2h 15m", "pontos": "Leiria » Penela » Talasnal » Lousã", "vistas": "Castelo de Penela e quelhas a pé no Talasnal.", "comer": "O Burgo (Vitela assada no forno a lenha).", "dormir": "Palácio da Lousã Boutique Hotel ou HI Hostel Lousã."},
    "Dia 3 - O Coração do Xisto": {"km": "80 km", "tempo": "2h 30m", "pontos": "Lousã » Góis » Piódão", "vistas": "Margens do rio Ceira (Góis); Anfiteatro do Piódão.", "comer": "O Fontinha (Cabrito assado).", "dormir": "Inatel Piódão ou Casa da Padaria."},
    "Dia 4 - Cascatas e Património": {"km": "140 km", "tempo": "2h 45m", "pontos": "Piódão » Fraga da Pena » Batalha", "vistas": "Cascata da Fraga da Pena; Mosteiro da Batalha.", "comer": "Tasca do Xico ou Burro Velho.", "dormir": "Hotel Casa do Outeiro ou Villa Batalha."},
    "Dia 5 - Vilas Medievais e Regresso": {"km": "150 km", "tempo": "1h 45m", "pontos": "Batalha » Óbidos » Cascais", "vistas": "Muralhas e ruelas de Óbidos.", "comer": "Jamon Jamon.", "dormir": "Chegada a Casa."}
}

st.title("🏍️ Rota das Aldeias do Xisto")

api_key = st.sidebar.text_input("🔑 Chave OpenWeatherMap", type="password")
st.sidebar.markdown("---")
st.sidebar.info("Total Estimado: 627 km | 13h 00m de condução")

@st.cache_data(ttl=1800)
def obter_previsao(lat, lon, key):
    if not key:
        return "<br><small><i>Insere a API Key para Previsão</i></small>"
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
        return "<br><small>Erro na API</small>"
    except:
        return "<br><small>Erro de ligação</small>"

@st.cache_data(ttl=86400)
def obter_tracado_estrada(pontos):
    # API OSRM para desenhar as estradas reais (requer lon,lat)
    str_coords = ";".join([f"{lon},{lat}" for lat, lon in pontos])
    url = f"https://router.project-osrm.org/route/v1/driving/{str_coords}?overview=full&geometries=geojson"
    try:
        res = requests.get(url)
        if res.status_code == 200:
            dados = res.json()
            # GeoJSON devolve [lon, lat], Folium precisa de [lat, lon]
            coords_geojson = dados['routes'][0]['geometry']['coordinates']
            return [[lat, lon] for lon, lat in coords_geojson]
    except Exception as e:
        print(f"Erro no routing: {e}")
    return pontos # Se a API falhar, cai para as linhas retas como redundância

col_mapa, col_info = st.columns([6, 4])

with col_mapa:
    gpx = gpxpy.parse(gpx_data)
    mapa = folium.Map(location=[39.6, -8.5], zoom_start=8)
    
    folium.TileLayer('OpenStreetMap').add_to(mapa)
    folium.TileLayer(
        tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png',
        attr='Map data: © OpenStreetMap contributors, SRTM | Map style: © OpenTopoMap (CC-BY-SA)',
        name='Topográfico'
    ).add_to(mapa)
    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Esri', name='Satélite', overlay=False, control=True
    ).add_to(mapa)
    
    plugins.Fullscreen(position='topright').add_to(mapa)
    
    cores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#d62728']
    todas_coords = []
    
    for index, rota in enumerate(gpx.routes):
        cor = cores[index % len(cores)]
        coords_waypoints = []
        
        # 1. Recolher paragens e criar Marcadores
        for i, ponto in enumerate(rota.points):
            coords = (ponto.latitude, ponto.longitude)
            coords_waypoints.append(coords)
            todas_coords.append(coords)
            
            previsao_html = obter_previsao(ponto.latitude, ponto.longitude, api_key)
            
            popup_html = f"""
            <div style='font-family:sans-serif; min-width:250px;'>
                <h4 style='margin:0; color:{cor};'>{ponto.name}</h4>
                <p style='margin:2px 0 10px 0; font-size:12px; color:gray;'>{rota.name}</p>
                {previsao_html}
            </div>
            """
            
            icone_tipo = 'motorcycle' if i == 0 or i == len(rota.points)-1 else 'flag'
            
            folium.Marker(
                location=coords,
                popup=folium.Popup(popup_html, max_width=350),
                tooltip=ponto.name,
                icon=folium.Icon(color=cor if cor in ['blue', 'green', 'purple', 'red', 'orange'] else 'blue', icon=icone_tipo, prefix='fa')
            ).add_to(mapa)
            
        # 2. Obter o traçado das estradas e desenhar a linha
        if coords_waypoints:
            tracado_real = obter_tracado_estrada(coords_waypoints)
            plugins.AntPath(
                locations=tracado_real,
                color=cor, weight=5, opacity=0.8,
                dash_array=[10, 20], delay=1000,
                tooltip=f"{rota.name}"
            ).add_to(mapa)

    folium.LayerControl().add_to(mapa)
    if todas_coords:
        mapa.fit_bounds(todas_coords)

    st_folium(mapa, width="100%", height=650)

with col_info:
    st.subheader("📋 Itinerário Detalhado")
    for dia, info in info_dias.items():
        with st.expander(f"📍 {dia}"):
            st.markdown(f"**🛣️ Rota:** {info['pontos']}")
            st.markdown(f"**📏 Distância:** {info['km']} | **⏱️ Tempo:** {info['tempo']}")
            st.markdown(f"📸 **Paragens & Vistas:** {info['vistas']}")
            st.markdown(f"🍽️ **Onde Comer:** {info['comer']}")
            st.markdown(f"🛏️ **Onde Dormir:** {info['dormir']}")
