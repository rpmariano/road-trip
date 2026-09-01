import streamlit as st
import folium
from folium import plugins
import gpxpy
import requests
import datetime
from streamlit_folium import st_folium

st.set_page_config(page_title="Rotas Xisto", page_icon="🏍️", layout="wide")

# CSS para forçar um design de App Nativa (Mobile-First)
st.markdown("""
<style>
    .block-container { padding-top: 1rem !important; padding-bottom: 1rem !important; max-width: 1400px; }
    #MainMenu {visibility: hidden;} footer {visibility: hidden;} header {visibility: hidden;}
    
    /* Cartões de Informação estilo App */
    .roteiro-card {
        background-color: #ffffff;
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.05);
        border: 1px solid #e0e0e0;
        color: #333333;
    }
    .roteiro-card h4 { margin-top: 0; padding-bottom: 8px; border-bottom: 1px solid #eee; }
    .roteiro-card p { margin-bottom: 8px; font-size: 0.95em; line-height: 1.4; }
    .roteiro-card b { color: #111; }
    
    /* Adaptações para telemóvel */
    @media (max-width: 768px) {
        .block-container { padding-left: 0.5rem !important; padding-right: 0.5rem !important; }
        .roteiro-card { padding: 12px; }
    }
</style>
""", unsafe_allow_html=True)

# ==========================================
# DADOS GPX
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
  <rte><name>Dia 5 - Vilas Medievais e Regresso</name>
    <rtept lat="39.6589" lon="-8.8252"><name>Batalha</name></rtept>
    <rtept lat="39.3592" lon="-9.1573"><name>Óbidos</name></rtept>
    <rtept lat="38.6970" lon="-9.4215"><name>Cascais</name></rtept>
  </rte>
</gpx>"""

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

# ==========================================
# DADOS DE TEXTO
# ==========================================
info_dias_v1 = {
    "Dia 1 - Atlântico e Pinhal": {"km": "165 km", "tempo": "3h 45m", "pontos": "Cascais » Ericeira » Foz do Arelho » S. Pedro de Moel » Leiria", "vistas": "Encontro da Lagoa de Óbidos c/ o mar; Farol do Penedo da Saudade.", "comer": "Tasca do Zé Mário ou Ao Largo.", "dormir": "Hostel Leiria ou Hotel Ibis.", "equipamento": "Fato de meia-estação. O vento costeiro pode arrefecer."},
    "Dia 2 - Transição para a Serra": {"km": "92 km", "tempo": "2h 15m", "pontos": "Leiria » Penela » Talasnal » Lousã", "vistas": "Castelo de Penela e quelhas a pé no Talasnal.", "comer": "O Burgo (Vitela assada).", "dormir": "Palácio da Lousã ou HI Hostel.", "equipamento": "Temperatura desce na serra. Forro térmico acessível na top-case."},
    "Dia 3 - O Coração do Xisto": {"km": "80 km", "tempo": "2h 30m", "pontos": "Lousã » Góis » Piódão", "vistas": "Margens do rio Ceira (Góis); Anfiteatro do Piódão.", "comer": "O Fontinha (Cabrito assado).", "dormir": "Inatel Piódão ou Casa da Padaria.", "equipamento": "Vales cerrados. Pinlock obrigatório e buff de pescoço contra frio."},
    "Dia 4 - Cascatas e Património": {"km": "140 km", "tempo": "2h 45m", "pontos": "Piódão » Fraga da Pena » Batalha", "vistas": "Cascata da Fraga da Pena; Mosteiro da Batalha.", "comer": "Tasca do Xico ou Burro Velho.", "dormir": "Hotel Casa do Outeiro.", "equipamento": "Manhã fria na serra, tarde quente no litoral. Sistema de camadas ideal."},
    "Dia 5 - Vilas Medievais e Regresso": {"km": "150 km", "tempo": "1h 45m", "pontos": "Batalha » Óbidos » Cascais (A8/A16)", "vistas": "Muralhas e ruelas calcetadas de Óbidos (Ginjinha).", "comer": "Jamon Jamon (Pregos/Carnes Ibéricas).", "dormir": "Chegada a Casa.", "equipamento": "Fato bem ventilado para tarde amena. Luvas mais leves para trânsito."}
}

info_dias_v2 = {
    "Dia 1 - Atlântico e Pinhal": {"km": "165 km", "tempo": "3h 50m", "pontos": "Cascais » Ericeira » Foz do Arelho » Nazaré » S. Pedro Moel » Leiria", "vistas": "Sítio da Nazaré; Farol do Penedo da Saudade.", "comer": "Tasca do Zé Mário ou Ao Largo.", "dormir": "Hostel Leiria ou Hotel Ibis.", "equipamento": "Fato de meia-estação. O vento costeiro pode arrefecer."},
    "Dia 2 - Transição para a Serra": {"km": "105 km", "tempo": "2h 45m", "pontos": "Leiria » Penela » Talasnal » Cerdeira » Alto do Trebim » Lousã", "vistas": "Castelo de Penela, quelhas no Talasnal, Cerdeira e Alto do Trebim.", "comer": "O Burgo (Vitela assada).", "dormir": "Palácio da Lousã ou HI Hostel.", "equipamento": "Temperatura desce na serra. Forro térmico acessível na top-case."},
    "Dia 3 - O Coração do Xisto": {"km": "75 km", "tempo": "2h 00m", "pontos": "Lousã » Góis » Piódão", "vistas": "Margens do rio Ceira; Tarde de descanso na praia fluvial do Piódão.", "comer": "O Fontinha (Cabrito assado).", "dormir": "Inatel Piódão ou Casa da Padaria.", "equipamento": "Vales cerrados. Pinlock obrigatório."},
    "Dia 4 - As Portas de Ródão": {"km": "115 km", "tempo": "2h 20m", "pontos": "Piódão » Foz do Cobrão » V. V. Ródão", "vistas": "Aldeia de Foz do Cobrão; Monumento Natural das Portas de Ródão.", "comer": "Restaurante Vila Portuguesa (Sopa de Peixe).", "dormir": "Hotel Portas de Ródão.", "equipamento": "Clima ameno/quente na aproximação ao Tejo."},
    "Dia 5 - Regresso Rápido (AE)": {"km": "210 km", "tempo": "2h 00m", "pontos": "V. V. Ródão » A23 » A1 » Cascais", "vistas": "Tirada de autoestrada contínua para minimizar o desgaste da serra.", "comer": "Chegada a Cascais para almoço.", "dormir": "Chegada a Casa.", "equipamento": "Tampões para ouvidos (earplugs) para viagem longa em via rápida."}
}

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

totais_v1 = calcular_totais(info_dias_v1)
totais_v2 = calcular_totais(info_dias_v2)

# ==========================================
# UI: TOPO E NAVEGAÇÃO FIXA
# ==========================================
st.markdown("<h2 style='text-align: center; margin-bottom: 0px;'>🏍️ Rota das Aldeias do Xisto</h2>", unsafe_allow_html=True)

# Comandos fixos no topo previnem "saltos" ao carregar botões
st.markdown("---")
col_ctrl1, col_ctrl2 = st.columns(2)
with col_ctrl1:
    versao_ativa = st.radio("🟢 Destacar no Mapa:", ["Versão 1 (Original)", "Versão 2 (Alternativa)"], horizontal=True)
with col_ctrl2:
    dia_foco = st.selectbox("🔍 Focar no Dia:", ["Visão Geral", "Dia 1", "Dia 2", "Dia 3", "Dia 4", "Dia 5"])
st.markdown("---")

# ==========================================
# MAPA (Totalmente isolado de reruns)
# ==========================================
gpx_ativo_data = gpx_data_v1 if "Versão 1" in versao_ativa else gpx_data_v2
gpx_sombra_data = gpx_data_v2 if "Versão 1" in versao_ativa else gpx_data_v1
prefixo_foco = dia_foco.split("-")[0].strip()

weather_api_key = st.secrets.get("OPENWEATHER_KEY", "")
ors_api_key = st.secrets.get("ORS_KEY", "")

@st.cache_data(ttl=1800)
def obter_previsao(lat, lon, key):
    if not key: return ""
    try:
        res = requests.get(f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={key}&units=metric&lang=pt")
        if res.status_code == 200:
            dados = res.json()
            previsoes_diarias = {}
            for item in dados['list']:
                data_texto, hora = item['dt_txt'].split(' ')
                if data_texto not in previsoes_diarias or hora == '15:00:00':
                    previsoes_diarias[data_texto] = item
            html = "<div style='display: flex; overflow-x: auto; gap: 8px; margin-top: 5px; padding-bottom: 5px;'>"
            for data, prev in list(previsoes_diarias.items())[:5]:
                temp = prev['main']['temp']
                icone = prev['weather'][0]['icon']
                dia_sem = datetime.datetime.strptime(data, '%Y-%m-%d').strftime('%d/%m')
                html += f"<div style='background:#f0f2f6; border-radius:6px; padding:4px; min-width:60px; text-align:center;'><div style='font-size:0.7em; color:#555;'><b>{dia_sem}</b></div><img src='https://openweathermap.org/img/wn/{icone}@2x.png' width='35' style='margin:-5px 0;'><div style='font-size:0.85em; font-weight:bold;'>{temp:.0f}°C</div></div>"
            return html + "</div>"
    except: return ""

@st.cache_data(ttl=86400)
def obter_tracado_cénico(pontos, api_key, evitar_autoestradas=True):
    coords = [[lon, lat] for lat, lon in pontos]
    headers = {'Accept': 'application/json, application/geo+json', 'Authorization': api_key, 'Content-Type': 'application/json'}
    body = {"coordinates": coords, "elevation": False, "instructions": False}
    if evitar_autoestradas: body["options"] = {"avoid_features": ["highways", "tollways"]}
    try:
        res = requests.post('https://api.openrouteservice.org/v2/directions/driving-car/geojson', json=body, headers=headers)
        if res.status_code == 200:
            return [[lat, lon] for lon, lat in res.json()['features'][0]['geometry']['coordinates']]
    except: pass
    return pontos

temas_dias = [{"hex": "#3498db", "folium": "blue", "emoji": "🔵"}, {"hex": "#e67e22", "folium": "orange", "emoji": "🟠"}, {"hex": "#2ecc71", "folium": "green", "emoji": "🟢"}, {"hex": "#9b59b6", "folium": "purple", "emoji": "🟣"}, {"hex": "#e74c3c", "folium": "red", "emoji": "🔴"}]

mapa = folium.Map(location=[39.6, -8.5], zoom_start=8)
folium.TileLayer('OpenStreetMap').add_to(mapa)
plugins.Fullscreen(position='topright').add_to(mapa)

fg_sombra = folium.FeatureGroup(name="🛣️ Rota Alternativa (Fundo)", show=True)
gpx_sombra = gpxpy.parse(gpx_sombra_data)
for rota in gpx_sombra.routes:
    if prefixo_foco == "Visão Geral" or prefixo_foco == rota.name.split("-")[0].strip():
        coords = [(pt.latitude, pt.longitude) for pt in rota.points]
        if coords:
            tracado = obter_tracado_cénico(coords, ors_api_key, not ("Autoestrada" in rota.name)) if ors_api_key else coords
            folium.PolyLine(locations=tracado, color='#2c3e50', weight=10, opacity=0.45, dash_array='15, 15', tooltip=f"Sombra: {rota.name}").add_to(fg_sombra)
fg_sombra.add_to(mapa)

gpx_ativo = gpxpy.parse(gpx_ativo_data)
todas_coords, coords_dia_focado = [], []

for index, rota in enumerate(gpx_ativo.routes):
    tema = temas_dias[index % len(temas_dias)]
    coords_wp = []
    prefixo_rota = rota.name.split("-")[0].strip()
    dia_ativo = (prefixo_foco == "Visão Geral") or (prefixo_foco == prefixo_rota)
    
    for i, pt in enumerate(rota.points):
        coords_wp.append((pt.latitude, pt.longitude))
        todas_coords.append((pt.latitude, pt.longitude))
        if prefixo_foco == prefixo_rota: coords_dia_focado.append((pt.latitude, pt.longitude))
        
        if dia_ativo:
            html = f"<div style='min-width:220px;'><h4 style='margin:0; color:{tema['hex']};'>{pt.name}</h4><p style='margin:0; font-size:11px; color:gray;'>{rota.name}</p>{obter_previsao(pt.latitude, pt.longitude, weather_api_key)}</div>"
            folium.Marker((pt.latitude, pt.longitude), popup=folium.Popup(html, max_width=300), tooltip=pt.name, icon=folium.Icon(color=tema['folium'], icon='motorcycle' if i==0 or i==len(rota.points)-1 else 'flag', prefix='fa')).add_to(mapa)
            
    if coords_wp:
        tracado_real = obter_tracado_cénico(coords_wp, ors_api_key, not ("Autoestrada" in rota.name)) if ors_api_key else coords_wp
        linha = folium.PolyLine(locations=tracado_real, color=tema['hex'], weight=5 if dia_ativo else 3, opacity=0.9 if dia_ativo else 0.2, tooltip=rota.name).add_to(mapa)
        if dia_ativo: plugins.PolyLineTextPath(linha, '  ►  ', repeat=True, offset=5.5, attributes={'fill':'#000', 'font-weight':'bold', 'font-size':'15', 'fill-opacity':'0.7'}).add_to(mapa)

folium.LayerControl().add_to(mapa)
if prefixo_foco != "Visão Geral" and coords_dia_focado: mapa.fit_bounds(coords_dia_focado)
elif todas_coords: mapa.fit_bounds(todas_coords)

# returned_objects=[] É O SEGREDO que impede o mapa de recarregar a app ao mexer!
st_folium(mapa, use_container_width=True, height=400, returned_objects=[])

# ==========================================
# COMPARAÇÃO LADO-A-LADO (HTML CARDS)
# ==========================================
def renderizar_cartao(titulo, emoji, hex_color, info):
    return f"""
    <div class="roteiro-card" style="border-left: 6px solid {hex_color};">
        <h4 style="color:{hex_color};">{emoji} {titulo}</h4>
        <p><b>🛣️ Rota:</b> {info['pontos']}</p>
        <p><b>📏 Dist:</b> {info['km']} &nbsp;|&nbsp; <b>⏱️ Tempo:</b> {info['tempo']}</p>
        <p><b>📸 Paragens:</b> {info['vistas']}</p>
        <p><b>🍽️ Comer:</b> {info['comer']}</p>
        <p><b>🛏️ Dormir:</b> {info['dormir']}</p>
        <p style="margin-top:10px; padding-top:10px; border-top:1px dashed #ddd; color:#555;">
        <b>🧳 Equipamento:</b> {info['equipamento']}</p>
    </div>
    """

col_v1, col_v2 = st.columns(2, gap="large")

with col_v1:
    st.markdown(f"<h3 style='text-align:center;'>📘 Versão 1</h3><p style='text-align:center; color:gray; margin-top:-10px;'>📍 ~{totais_v1[0]} km | ⏱️ ~{totais_v1[1]}</p>", unsafe_allow_html=True)
    for i, (key, info) in enumerate(info_dias_v1.items()):
        tema = temas_dias[i % len(temas_dias)]
        if prefixo_foco == "Visão Geral" or prefixo_foco == key.split("-")[0].strip():
            st.markdown(renderizar_cartao(key, tema['emoji'], tema['hex'], info), unsafe_allow_html=True)

with col_v2:
    st.markdown(f"<h3 style='text-align:center;'>📙 Versão 2</h3><p style='text-align:center; color:gray; margin-top:-10px;'>📍 ~{totais_v2[0]} km | ⏱️ ~{totais_v2[1]}</p>", unsafe_allow_html=True)
    for i, (key, info) in enumerate(info_dias_v2.items()):
        tema = temas_dias[i % len(temas_dias)]
        if prefixo_foco == "Visão Geral" or prefixo_foco == key.split("-")[0].strip():
            st.markdown(renderizar_cartao(key, tema['emoji'], tema['hex'], info), unsafe_allow_html=True)
