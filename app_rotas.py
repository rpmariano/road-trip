import streamlit as st
import folium
from folium import plugins
import gpxpy
import requests
import datetime
from streamlit_folium import st_folium

st.set_page_config(page_title="Rotas Xisto", page_icon="🏍️", layout="wide")

# CSS Avançado: Mobile-First + Forçar Empilhamento
st.markdown("""
<style>
    .block-container { padding-top: 1.5rem !important; padding-bottom: 1rem !important; max-width: 1200px; }
    .stButton>button { border-radius: 8px; padding: 0.5rem 1rem; font-weight: 500; transition: all 0.2s ease; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    .stMarkdown p { font-size: 0.95em; }
    
    /* Regras específicas para ecrãs de telemóvel */
    @media (max-width: 768px) {
        .block-container { padding-top: 1rem !important; padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
        /* Forçar colunas a ocuparem 100% da largura no telemóvel */
        div[data-testid="column"] { width: 100% !important; flex: 1 1 100% !important; min-width: 100% !important; margin-bottom: 0.5rem; }
        .stMarkdown p { font-size: 0.9em; }
    }
</style>
""", unsafe_allow_html=True)

# Gestão de Estado Inteligente
if 'foco_prefixo' not in st.session_state:
    st.session_state.foco_prefixo = "Visão Geral"
if 'versao_ativa' not in st.session_state:
    st.session_state.versao_ativa = "V1"

# ==========================================
# GPX DA V1 (ORIGINAL)
# ==========================================
gpx_data_v1 = """<?xml version="1.0" ?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" creator="Gemini" version="1.1">
  <metadata><name>Passeio de Mota - V1 (Original)</name></metadata>
  <rte><name>Dia 1 - Atlântico e Pinhal</name>
    <rtept lat="38.6970" lon="-9.4215"><name>Cascais</name></rtept>
    <rtept lat="38.9637" lon="-9.4173"><name>Ericeira</name></rtept>
    <rtept lat="39.4290" lon="-9.2248"><name>Foz do Arelho</name></rtept>
    <rtept lat="39.7640" lon="-9.0310"><name>São Pedro de Moel</name></rtept>
    <rtept lat="39.7436" lon="-8.8071"><name>Leiria</name></rtept>
  </rte>
  <rte><name>Dia 2 - Transição para a Serra</name>
    <rtept lat="39.7436" lon="-8.8071"><name>Leiria</name></rtept>
    <rtept lat="40.0310" lon="-8.3900"><name>Penela</name></rtept>
    <rtept lat="40.0925" lon="-8.2263"><name>Talasnal</name></rtept>
    <rtept lat="40.1121" lon="-8.2476"><name>Lousã</name></rtept>
  </rte>
  <rte><name>Dia 3 - O Coração do Xisto</name>
    <rtept lat="40.1121" lon="-8.2476"><name>Lousã</name></rtept>
    <rtept lat="40.1541" lon="-8.1105"><name>Góis</name></rtept>
    <rtept lat="40.2240" lon="-7.8294"><name>Piódão</name></rtept>
  </rte>
  <rte><name>Dia 4 - Cascatas e Património</name>
    <rtept lat="40.2240" lon="-7.8294"><name>Piódão</name></rtept>
    <rtept lat="40.2202" lon="-7.9360"><name>Fraga da Pena</name></rtept>
    <rtept lat="39.6589" lon="-8.8252"><name>Batalha</name></rtept>
  </rte>
  <rte><name>Dia 5 - Vilas Medievais e Regresso a Casa</name>
    <rtept lat="39.6589" lon="-8.8252"><name>Batalha</name></rtept>
    <rtept lat="39.3592" lon="-9.1573"><name>Óbidos</name></rtept>
    <rtept lat="38.6970" lon="-9.4215"><name>Cascais</name></rtept>
  </rte>
</gpx>"""

# ==========================================
# GPX DA V2 (PORTAS DE RÓDÃO + AUTOESTRADA)
# ==========================================
gpx_data_v2 = """<?xml version="1.0" ?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" creator="Gemini" version="1.1">
  <metadata><name>Passeio de Mota - V2 (Alternativa)</name></metadata>
  <rte><name>Dia 1 - Atlântico e Pinhal</name>
    <rtept lat="38.6970" lon="-9.4215"><name>Cascais</name></rtept>
    <rtept lat="38.9637" lon="-9.4173"><name>Ericeira</name></rtept>
    <rtept lat="39.4290" lon="-9.2248"><name>Foz do Arelho</name></rtept>
    <rtept lat="39.6047" lon="-9.0830"><name>Nazaré</name></rtept>
    <rtept lat="39.7640" lon="-9.0310"><name>São Pedro de Moel</name></rtept>
    <rtept lat="39.7436" lon="-8.8071"><name>Leiria</name></rtept>
  </rte>
  <rte><name>Dia 2 - Transição para a Serra</name>
    <rtept lat="39.7436" lon="-8.8071"><name>Leiria</name></rtept>
    <rtept lat="40.0310" lon="-8.3900"><name>Penela</name></rtept>
    <rtept lat="40.0925" lon="-8.2263"><name>Talasnal</name></rtept>
    <rtept lat="40.0934" lon="-8.1923"><name>Cerdeira</name></rtept>
    <rtept lat="40.1121" lon="-8.2476"><name>Lousã</name></rtept>
  </rte>
  <rte><name>Dia 3 - O Coração do Xisto</name>
    <rtept lat="40.1121" lon="-8.2476"><name>Lousã</name></rtept>
    <rtept lat="40.1541" lon="-8.1105"><name>Góis</name></rtept>
    <rtept lat="40.2240" lon="-7.8294"><name>Piódão</name></rtept>
  </rte>
  <rte><name>Dia 4 - As Portas de Ródão</name>
    <rtept lat="40.2240" lon="-7.8294"><name>Piódão</name></rtept>
    <rtept lat="39.7561" lon="-7.7719"><name>Foz do Cobrão</name></rtept>
    <rtept lat="39.6570" lon="-7.6740"><name>Vila Velha de Ródão</name></rtept>
  </rte>
  <rte><name>Dia 5 - Regresso Rápido (Autoestrada)</name>
    <rtept lat="39.6570" lon="-7.6740"><name>Vila Velha de Ródão</name></rtept>
    <rtept lat="39.4678" lon="-8.1994"><name>Abrantes (A23)</name></rtept>
    <rtept lat="38.6970" lon="-9.4215"><name>Cascais</name></rtept>
  </rte>
</gpx>"""

# Informações V1
info_dias_v1 = {
    "Dia 1 - Atlântico e Pinhal": {"km": "165 km", "tempo": "3h 45m", "pontos": "Cascais » Ericeira » Foz do Arelho » S. Pedro de Moel » Leiria", "vistas": "Encontro da Lagoa de Óbidos com o mar; Farol do Penedo da Saudade.", "comer": "Tasca do Zé Mário ou Ao Largo.", "dormir": "Hostel Leiria ou Hotel Ibis.", "equipamento": "Fato de meia-estação. O vento costeiro pode arrefecer; usem luvas windstopper."},
    "Dia 2 - Transição para a Serra": {"km": "92 km", "tempo": "2h 15m", "pontos": "Leiria » Penela » Talasnal » Lousã", "vistas": "Castelo de Penela e quelhas a pé no Talasnal.", "comer": "O Burgo (Vitela assada).", "dormir": "Palácio da Lousã ou HI Hostel.", "equipamento": "Temperatura desce na serra. Forro térmico acessível na top-case."},
    "Dia 3 - O Coração do Xisto": {"km": "80 km", "tempo": "2h 30m", "pontos": "Lousã » Góis » Piódão", "vistas": "Margens do rio Ceira (Góis); Anfiteatro do Piódão.", "comer": "O Fontinha (Cabrito assado).", "dormir": "Inatel Piódão ou Casa da Padaria.", "equipamento": "Vales cerrados. Pinlock obrigatório e buff de pescoço contra frio."},
    "Dia 4 - Cascatas e Património": {"km": "140 km", "tempo": "2h 45m", "pontos": "Piódão » Fraga da Pena » Batalha", "vistas": "Cascata da Fraga da Pena; Mosteiro da Batalha.", "comer": "Tasca do Xico ou Burro Velho.", "dormir": "Hotel Casa do Outeiro.", "equipamento": "Manhã fria na serra, tarde quente no litoral. Sistema de camadas ideal."},
    "Dia 5 - Vilas Medievais e Regresso": {"km": "150 km", "tempo": "1h 45m", "pontos": "Batalha » Óbidos » Cascais (A8/A16)", "vistas": "Muralhas e ruelas calcetadas de Óbidos (Ginjinha).", "comer": "Jamon Jamon (Pregos/Carnes Ibéricas).", "dormir": "Chegada a Casa.", "equipamento": "Fato bem ventilado para tarde amena. Luvas mais leves para trânsito."}
}

# Informações V2
info_dias_v2 = {
    "Dia 1 - Atlântico e Pinhal": {"km": "165 km", "tempo": "3h 50m", "pontos": "Cascais » Ericeira » Foz do Arelho » Nazaré » S. Pedro Moel » Leiria", "vistas": "Encontro da Lagoa de Óbidos c/ o mar; Sítio da Nazaré; Farol do Penedo da Saudade.", "comer": "Tasca do Zé Mário ou Ao Largo.", "dormir": "Hostel Leiria ou Hotel Ibis.", "equipamento": "Fato de meia-estação. O vento costeiro pode arrefecer; usem luvas windstopper."},
    "Dia 2 - Transição para a Serra": {"km": "105 km", "tempo": "2h 45m", "pontos": "Leiria » Penela » Talasnal » Cerdeira » Alto do Trebim » Lousã", "vistas": "Castelo de Penela, quelhas no Talasnal, refúgio da Cerdeira e panorâmica no Alto do Trebim.", "comer": "O Burgo (Vitela assada).", "dormir": "Palácio da Lousã ou HI Hostel.", "equipamento": "Temperatura desce na serra. Forro térmico acessível na top-case."},
    "Dia 3 - O Coração do Xisto": {"km": "75 km", "tempo": "2h 00m", "pontos": "Lousã » Góis » Piódão", "vistas": "Margens do rio Ceira; Tarde de descanso na praia fluvial do Piódão.", "comer": "O Fontinha (Cabrito assado).", "dormir": "Inatel Piódão ou Casa da Padaria.", "equipamento": "Vales cerrados. Pinlock obrigatório."},
    "Dia 4 - As Portas de Ródão": {"km": "115 km", "tempo": "2h 20m", "pontos": "Piódão » Foz do Cobrão » V. V. Ródão", "vistas": "Aldeia de Foz do Cobrão (Ribeira do Ocreza); Monumento Natural das Portas de Ródão.", "comer": "Restaurante Vila Portuguesa (Sopa de Peixe do Tejo).", "dormir": "Hotel Portas de Ródão.", "equipamento": "Clima ameno/quente na aproximação ao Tejo e fronteira com o Alentejo."},
    "Dia 5 - Regresso Rápido (AE)": {"km": "210 km", "tempo": "2h 00m", "pontos": "V. V. Ródão » A23 » A1 » Cascais", "vistas": "Tirada de autoestrada contínua para minimizar o desgaste da serra.", "comer": "Chegada a Cascais para almoço.", "dormir": "Chegada a Casa.", "equipamento": "Tampões para os ouvidos (earplugs) para viagem prolongada em via rápida."}
}

st.markdown("<h2 style='text-align: center; margin-bottom: 0;'>🏍️ Rota das Aldeias do Xisto</h2>", unsafe_allow_html=True)
st.markdown("<br>", unsafe_allow_html=True)

def calcular_totais(info_dict):
    km_totais, minutos_totais = 0, 0
    for info in info_dict.values():
        km_str = info['km'].replace('km', '').replace('~', '').strip()
        km_totais += int(km_str)
        tempo_str = info['tempo'].replace('~', '').strip()
        h = int(tempo_str.split('h')[0].strip()) if 'h' in tempo_str else 0
        m = int(tempo_str.split('h')[1].replace('m', '').strip()) if 'm' in tempo_str else 0
        minutos_totais += (h * 60) + m
    return km_totais, f"{minutos_totais // 60}h {minutos_totais % 60:02d}m"

if st.session_state.versao_ativa == "V1":
    gpx_ativo_data, gpx_sombra_data = gpx_data_v1, gpx_data_v2
else:
    gpx_ativo_data, gpx_sombra_data = gpx_data_v2, gpx_data_v1

weather_api_key = st.secrets.get("OPENWEATHER_KEY", "")
ors_api_key = st.secrets.get("ORS_KEY", "")

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
                html += f"<div style='background-color:#f0f2f6; border-radius:8px; padding:6px; min-width:70px; text-align:center;'><div style='font-size:0.8em; color:#555; font-weight:bold;'>{dia_semana}</div><img src='https://openweathermap.org/img/wn/{icone}@2x.png' width='40' style='margin:-5px 0;'><div style='font-size:0.9em; font-weight:bold;'>{temp:.0f}°C</div></div>"
            html += "</div>"
            return html
        return ""
    except: return ""

@st.cache_data(ttl=86400)
def obter_tracado_cénico(pontos, api_key, evitar_autoestradas=True):
    coords = [[lon, lat] for lat, lon in pontos]
    headers = {'Accept': 'application/json, application/geo+json, application/gpx+xml, img/png; charset=utf-8', 'Authorization': api_key, 'Content-Type': 'application/json; charset=utf-8'}
    body = {"coordinates": coords, "elevation": False, "instructions": False}
    if evitar_autoestradas:
        body["options"] = {"avoid_features": ["highways", "tollways"]}
        
    try:
        res = requests.post('https://api.openrouteservice.org/v2/directions/driving-car/geojson', json=body, headers=headers)
        if res.status_code == 200:
            coords_geojson = res.json()['features'][0]['geometry']['coordinates']
            return [[lat, lon] for lon, lat in coords_geojson]
    except Exception as e: print(f"Erro: {e}")
    return pontos

temas_dias = [
    {"hex": "#3498db", "folium": "blue", "emoji": "🔵"},
    {"hex": "#e67e22", "folium": "orange", "emoji": "🟠"},
    {"hex": "#2ecc71", "folium": "green", "emoji": "🟢"},
    {"hex": "#9b59b6", "folium": "purple", "emoji": "🟣"},
    {"hex": "#e74c3c", "folium": "red", "emoji": "🔴"}
]

# ==========================================
# 1. RENDERIZAÇÃO DO MAPA (Topo - Largura Total)
# ==========================================
mapa = folium.Map(location=[39.6, -8.5], zoom_start=8)
folium.TileLayer('OpenStreetMap').add_to(mapa)
folium.TileLayer(tiles='https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png', attr='© OpenStreetMap | © OpenTopoMap', name='Topográfico').add_to(mapa)
plugins.Fullscreen(position='topright').add_to(mapa)

fg_sombra = folium.FeatureGroup(name="🛣️ Rota Alternativa (Fundo)", show=True)

# Desenhar Sombra
gpx_sombra = gpxpy.parse(gpx_sombra_data)
for index, rota in enumerate(gpx_sombra.routes):
    prefixo_rota = rota.name.split("-")[0].strip()
    if st.session_state.foco_prefixo == "Visão Geral" or st.session_state.foco_prefixo == prefixo_rota:
        coords_sombra = [(pt.latitude, pt.longitude) for pt in rota.points]
        if coords_sombra:
            evitar_ae = not ("Autoestrada" in rota.name)
            tracado_sombra = obter_tracado_cénico(coords_sombra, ors_api_key, evitar_ae) if ors_api_key else coords_sombra
            folium.PolyLine(locations=tracado_sombra, color='#2c3e50', weight=10, opacity=0.45, dash_array='15, 15', tooltip=f"Sombra: {rota.name}").add_to(fg_sombra)
fg_sombra.add_to(mapa)

# Desenhar Rota Ativa
gpx_ativo = gpxpy.parse(gpx_ativo_data)
todas_coords = []
coords_dia_focado = [] 

for index, rota in enumerate(gpx_ativo.routes):
    tema = temas_dias[index % len(temas_dias)]
    coords_waypoints = []
    prefixo_rota = rota.name.split("-")[0].strip()
    
    dia_esta_focado = (st.session_state.foco_prefixo == "Visão Geral") or (st.session_state.foco_prefixo == prefixo_rota)
    opacidade_linha = 0.9 if dia_esta_focado else 0.2
    peso_linha = 5 if dia_esta_focado else 3
    
    for i, ponto in enumerate(rota.points):
        coords = (ponto.latitude, ponto.longitude)
        coords_waypoints.append(coords)
        todas_coords.append(coords)
        if st.session_state.foco_prefixo == prefixo_rota:
            coords_dia_focado.append(coords)
        
        if dia_esta_focado:
            previsao_html = obter_previsao(ponto.latitude, ponto.longitude, weather_api_key)
            popup_html = f"<div style='font-family:sans-serif; min-width:250px;'><h4 style='margin:0; color:{tema['hex']};'>{ponto.name}</h4><p style='margin:2px 0 10px 0; font-size:12px; color:gray;'>{rota.name}</p>{previsao_html}</div>"
            icone_tipo = 'motorcycle' if i == 0 or i == len(rota.points)-1 else 'flag'
            folium.Marker(location=coords, popup=folium.Popup(popup_html, max_width=350), tooltip=ponto.name, icon=folium.Icon(color=tema['folium'], icon=icone_tipo, prefix='fa')).add_to(mapa)
        
    if coords_waypoints:
        evitar_ae = not ("Autoestrada" in rota.name)
        tracado_real = obter_tracado_cénico(coords_waypoints, ors_api_key, evitar_ae) if ors_api_key else coords_waypoints
        linha_rota = folium.PolyLine(locations=tracado_real, color=tema['hex'], weight=peso_linha, opacity=opacidade_linha, tooltip=rota.name).add_to(mapa)
        
        if dia_esta_focado:
            plugins.PolyLineTextPath(linha_rota, '  ►  ', repeat=True, offset=5.5, attributes={'fill': '#000000', 'font-weight': 'bold', 'font-size': '15', 'fill-opacity': '0.7'}).add_to(mapa)

folium.LayerControl().add_to(mapa)

if st.session_state.foco_prefixo != "Visão Geral" and coords_dia_focado:
    mapa.fit_bounds(coords_dia_focado)
elif todas_coords:
    mapa.fit_bounds(todas_coords)

# Mapa ocupa 100% da largura. Altura adaptada para não prender o scroll no telemóvel.
st_folium(mapa, use_container_width=True, height=450)
st.markdown("<br>", unsafe_allow_html=True)


# ==========================================
# 2. CABEÇALHOS DAS VERSÕES
# ==========================================
col_hdr1, col_hdr2 = st.columns(2, gap="medium")

with col_hdr1:
    st.markdown("<h3 style='text-align: center; margin-bottom:0;'>📘 Versão 1</h3>", unsafe_allow_html=True)
    km_v1, tempo_v1 = calcular_totais(info_dias_v1)
    st.markdown(f"<p style='text-align: center; color: gray; font-size: 0.9em; margin-top:0;'>📍 ~{km_v1} km | ⏱️ ~{tempo_v1}</p>", unsafe_allow_html=True)
    is_v1_geral = (st.session_state.foco_prefixo == "Visão Geral" and st.session_state.versao_ativa == "V1")
    if st.button("🗺️ Mostrar Toda a V1", key="all_v1", use_container_width=True, type="primary" if is_v1_geral else "secondary"):
        st.session_state.foco_prefixo = "Visão Geral"
        st.session_state.versao_ativa = "V1"
        st.rerun()

with col_hdr2:
    st.markdown("<h3 style='text-align: center; margin-bottom:0;'>📙 Versão 2</h3>", unsafe_allow_html=True)
    km_v2, tempo_v2 = calcular_totais(info_dias_v2)
    st.markdown(f"<p style='text-align: center; color: gray; font-size: 0.9em; margin-top:0;'>📍 ~{km_v2} km | ⏱️ ~{tempo_v2}</p>", unsafe_allow_html=True)
    is_v2_geral = (st.session_state.foco_prefixo == "Visão Geral" and st.session_state.versao_ativa == "V2")
    if st.button("🗺️ Mostrar Toda a V2", key="all_v2", use_container_width=True, type="primary" if is_v2_geral else "secondary"):
        st.session_state.foco_prefixo = "Visão Geral"
        st.session_state.versao_ativa = "V2"
        st.rerun()

st.divider()

# ==========================================
# 3. LISTAGEM DOS DIAS (Intercalada linha a linha)
# ==========================================
dias_v1_keys = list(info_dias_v1.keys())
dias_v2_keys = list(info_dias_v2.keys())

# Percorremos os dias um a um. Em mobile, o Streamlit empilha as colunas: 
# Ex: V1 (Dia 1) -> V2 (Dia 1) -> V1 (Dia 2) -> V2 (Dia 2)
for i in range(len(dias_v1_keys)):
    dia_key_v1 = dias_v1_keys[i]
    dia_key_v2 = dias_v2_keys[i]
    info_v1 = info_dias_v1[dia_key_v1]
    info_v2 = info_dias_v2[dia_key_v2]
    tema = temas_dias[i % len(temas_dias)]
    prefixo = dia_key_v1.split("-")[0].strip() # Isola "Dia 1", "Dia 2", etc.
    
    col_day1, col_day2 = st.columns(2, gap="medium")
    
    with col_day1:
        is_active_btn1 = (st.session_state.foco_prefixo == prefixo and st.session_state.versao_ativa == "V1")
        if st.button(f"{tema['emoji']} {dia_key_v1}", key=f"btn_v1_{i}", use_container_width=True, type="primary" if is_active_btn1 else "secondary"):
            st.session_state.foco_prefixo = "Visão Geral" if is_active_btn1 else prefixo
            st.session_state.versao_ativa = "V1"
            st.rerun()
            
        if st.session_state.foco_prefixo == prefixo:
            with st.container(border=True):
                st.markdown(f"**🛣️ Rota:** {info_v1['pontos']}")
                st.markdown(f"**📏 Dist:** {info_v1['km']} | **⏱️ Temp:** {info_v1['tempo']}")
                st.markdown(f"📸 **Paragens:** {info_v1['vistas']}")
                st.markdown(f"🍽️ **Comer:** {info_v1['comer']}")
                st.markdown(f"🛏️ **Dormir:** {info_v1['dormir']}")

    with col_day2:
        is_active_btn2 = (st.session_state.foco_prefixo == prefixo and st.session_state.versao_ativa == "V2")
        if st.button(f"{tema['emoji']} {dia_key_v2}", key=f"btn_v2_{i}", use_container_width=True, type="primary" if is_active_btn2 else "secondary"):
            st.session_state.foco_prefixo = "Visão Geral" if is_active_btn2 else prefixo
            st.session_state.versao_ativa = "V2"
            st.rerun()
            
        if st.session_state.foco_prefixo == prefixo:
            with st.container(border=True):
                st.markdown(f"**🛣️ Rota:** {info_v2['pontos']}")
                st.markdown(f"**📏 Dist:** {info_v2['km']} | **⏱️ Temp:** {info_v2['tempo']}")
                st.markdown(f"📸 **Paragens:** {info_v2['vistas']}")
                st.markdown(f"🍽️ **Comer:** {info_v2['comer']}")
                st.markdown(f"🛏️ **Dormir:** {info_v2['dormir']}")
