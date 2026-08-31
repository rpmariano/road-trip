import streamlit as st
import folium
import gpxpy
import requests
from streamlit_folium import st_folium

# Os dados GPX estão embutidos para execução standalone
gpx_data = """<?xml version="1.0" ?>
<gpx xmlns="http://www.topografix.com/GPX/1/1" creator="Gemini" version="1.1">
  <metadata>
    <name>Passeio de Mota - Aldeias de Xisto</name>
  </metadata>
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

# Configuração da página Streamlit
st.set_page_config(page_title="Rotas Xisto", layout="wide")
st.title("Visualizador de Rotas de Mota")
st.markdown("O mapa com as tuas etapas diárias. Insere a chave de API na barra lateral para veres a meteorologia nas paragens.")

# Barra lateral para credenciais
st.sidebar.header("Configurações")
api_key = st.sidebar.text_input("Chave API OpenWeatherMap", type="password", help="Gera uma chave gratuita em openweathermap.org")

# Função de obtenção e cache de dados meteorológicos
@st.cache_data(ttl=600)
def obter_meteorologia(lat, lon, key):
    if not key:
        return "<br><small><i>API Key necessária</i></small>"
    
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={key}&units=metric&lang=pt"
    try:
        resposta = requests.get(url)
        if resposta.status_code == 200:
            dados = resposta.json()
            temp = dados['main']['temp']
            desc = dados['weather'][0]['description'].capitalize()
            icone = dados['weather'][0]['icon']
            return f"<br><img src='http://openweathermap.org/img/wn/{icone}.png' width='30'><br><b>{temp:.1f}°C</b><br>{desc}"
        return "<br>Dados indisponíveis"
    except:
        return "<br>Erro de ligação"

# Parse do GPX embutido
gpx = gpxpy.parse(gpx_data)

# Inicializar o mapa (centrado na zona centro do país)
mapa = folium.Map(location=[39.6, -8.5], zoom_start=8)
cores = ['#1f77b4', '#ff7f0e', '#2ca02c', '#9467bd', '#d62728'] # Cores mais contrastantes

# Construção das rotas e marcadores
for index, rota in enumerate(gpx.routes):
    cor = cores[index % len(cores)]
    coordenadas_rota = []
    
    for ponto in rota.points:
        coords = (ponto.latitude, ponto.longitude)
        coordenadas_rota.append(coords)
        
        info_tempo = obter_meteorologia(ponto.latitude, ponto.longitude, api_key)
        conteudo_popup = f"<div style='text-align:center; min-width:130px; font-family:sans-serif;'><b>{ponto.name}</b><br><span style='color:gray; font-size:0.9em;'>{rota.name}</span>{info_tempo}</div>"
        
        folium.Marker(
            location=coords,
            popup=folium.Popup(conteudo_popup, max_width=250),
            tooltip=ponto.name,
            icon=folium.Icon(color=cor if cor in ['blue', 'green', 'purple', 'red', 'orange'] else 'blue', icon='flag')
        ).add_to(mapa)
        
    if coordenadas_rota:
        folium.PolyLine(
            coordenadas_rota,
            color=cor,
            weight=5,
            opacity=0.8,
            tooltip=rota.name
        ).add_to(mapa)

# Renderizar mapa
st_folium(mapa, width=1200, height=700)