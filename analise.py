import streamlit as st
import pandas as pd
from geobr import read_municipality
import pydeck as pdk


def formatar_colunas_br(df, casas_decimais=2):
    """
    Formata colunas numéricas no padrão brasileiro:
    - float: separador de milhar (.) e decimal (,)
    - int: separador de milhar (.), sem decimais

    Parâmetros:
        df (pd.DataFrame): DataFrame de entrada
        casas_decimais (int): número de casas para float (default=2)

    Retorna:
        df_formatado (pd.DataFrame): cópia do DataFrame com strings formatadas
    """
    df_formatado = df.copy()

    for col in df.columns:
        if pd.api.types.is_float_dtype(df[col]):
            df_formatado[col] = df[col].map(
                lambda x: f"{x:,.{casas_decimais}f}"
                .replace(",", "X")
                .replace(".", ",")
                .replace("X", ".")
                if pd.notnull(x) else ""
            )
        elif pd.api.types.is_integer_dtype(df[col]):
            df_formatado[col] = df[col].map(
                lambda x: f"{x:,}".replace(",", ".") if pd.notnull(x) else ""
            )

    return df_formatado



pdk.settings.mapbox_api_key = "pk.eyJ1IjoibWFwbGl2cmUiLCJhIjoiY2t2bDNqYnhmMGRjaTJvbWhnZTQ4dGZrcSJ9.93xQMoQWVpJeHd2J-wtwMg"


DATA_DIR = "data"

allowed_users = st.secrets["access"]["allowed_users"]
def on_click_callback(x): 
    print(x)
    """Função de callback para o botão 'Acompanhar distribuição'."""
    st.session_state.page = x

@st.cache_data
def load_data():
    df = pd.read_csv(f"{DATA_DIR}/assentamentosgeral.csv",encoding='utf-8',delimiter=',')
    df["Área"]= df["Área"]\
    .str.replace(".", "", regex=False) \
    .str.replace(",", ".", regex=False) \
    .astype(float)

    gdf = read_municipality(code_muni="MT", year=2020)
    return df[df["Código"].str.startswith("MT")].reset_index(drop=True), gdf.to_crs(epsg=4326)
def run():
    if not st.session_state['page']=="home":
        st.sidebar.button("Retornar ao Início", use_container_width=True, on_click=on_click_callback, args=['home'])

    df, mt = load_data()
    municipios_destaque = list(df["Município IBGE"].unique())
    if st.user.email in allowed_users:
        if st.session_state['page']=='home': 
            st.image("./assets/images/imagem.jpg",use_container_width=True)    
            st.button("Iniciar análises", use_container_width=True, on_click=on_click_callback, args=['mapas'])

        if st.session_state['page']=='mapas':
            mun = st.sidebar.selectbox('Selecione um município:',municipios_destaque, index=None,placeholder="Clique para selecionar")
            if mun:
                lista = df[df['Município IBGE']==mun]['Nome'].unique()
                ass = st.sidebar.selectbox('Selecione um PA:',lista, index=None,placeholder="Clique para selecionar")
                
                gdf_muni = mt[mt["name_muni"] ==mun]
                mt["name_muni"].to_csv(f"{DATA_DIR}/municipios.csv")

                layer_base = pdk.Layer(
                    "GeoJsonLayer",
                    data=gdf_muni.__geo_interface__,
                    get_fill_color="[220, 220, 220, 100]",
                    get_line_color=[180, 180, 180],
                    line_width_min_pixels=0.5,
                    pickable=False,
                )

                # Camada de destaque

                # 🔷 Camada do contorno do estado de MT
                layer_contorno = pdk.Layer(
                    "GeoJsonLayer",
                    data=gdf_muni.__geo_interface__,
                    get_fill_color="[0, 0, 0, 0]",  # Sem preenchimento
                    get_line_color=[128, 0, 0],       # Contorno preto
                    line_width_min_pixels=2,
                    pickable=False
                )
                st.markdown(f'''
                <h4 align="center">
                Mapa dos Projetos de Assentamentos em {mun}
                </h4>
                ''',unsafe_allow_html=True)
                # View inicial
                view_state = pdk.ViewState(
                    latitude=gdf_muni.geometry.centroid.y.mean(),
                    longitude=gdf_muni.geometry.centroid.x.mean(),
                    zoom=8,
                    pitch=0,
                )

                # Mostrar o mapa
                st.pydeck_chart(pdk.Deck(
                    layers=[layer_base, layer_contorno],
                    initial_view_state=view_state,
                    map_style='mapbox://styles/mapbox/light-v9',  # exige token
                    tooltip={"text": "{name_muni}"},
                ))
                if ass:
                    st.write('---')
                    st.markdown(f'''
                    <h4 align="center">
                    Informações Projeto de Assentamento {ass} 
                    </h4>
                    ''',unsafe_allow_html=True)
                    df_exibicao = formatar_colunas_br(df[df['Nome']==ass]).T

                    df_exibicao.columns = ["Valor"]             # Nome da coluna de valores
                    df_exibicao.index.name = None

                    st.dataframe(df_exibicao)
                else:
                    st.write('---')
                    st.markdown(f'''
                    <h4 align="center">
                    Informações dos Projetos de Assentamentos em {mun}
                    </h4>
                    ''',unsafe_allow_html=True)

                    df_br = df.groupby("Município").agg(
                    municipio = ("Município", "first"),
                    municipio_ibge = ("Município IBGE", "first"),
                    total = ("Município","count"),
                    area = ("Área", "sum"),
                    familias = ("Total de Famílias", "sum")
                    ).rename(columns={"municipio":'Município',"total":"No de Assentamentos","area": "Área Total","familias": "Total de Famílias", "municipio_ibge": "Município IBGE"}).sort_values(by='Total de Famílias',ascending=False).rename(columns={"municipio":'Município',"total":"No de Assentamentos","area": "Área Total","familias": "Total de Famílias"}).sort_values(by='Total de Famílias',ascending=False)
                    df_br = formatar_colunas_br(df_br[df_br['Município IBGE']==mun].drop('Município IBGE',axis=1)).T
                    df_br.columns = ["Valor"]             # Nome da coluna de valores
                    df_br.index.name = None
                    st.dataframe(df_br)


                    st.dataframe(formatar_colunas_br(df[df['Município IBGE']==mun]),hide_index=True)
                    
                    st.write('---')
            
            else:
                mt_destaque = mt[mt["name_muni"].isin(municipios_destaque)]
                layer_destaque = pdk.Layer(
                    "GeoJsonLayer",
                    data=mt_destaque.__geo_interface__,
                    get_fill_color="[128, 0, 0, 100]",   # vermelho transparente
                    get_line_color=[0, 0, 0],           # contorno preto
                    line_width_min_pixels=1,
                    pickable=True,
                    auto_highlight=True,
                )

                # View inicial centrada no estado
                view_state = pdk.ViewState(
                    latitude=mt.geometry.centroid.y.mean(),
                    longitude=mt.geometry.centroid.x.mean(),
                    zoom=5,
                    pitch=0,
                )

                st.markdown('''
                <h4 align="center">
                Mapa dos Municípios com Projetos de Assentamentos
                </h4>
                ''',unsafe_allow_html=True)

                # Mostrar o mapa
                st.pydeck_chart(pdk.Deck(
                    layers=[layer_destaque],
                    initial_view_state=view_state,
                    map_style='mapbox://styles/mapbox/light-v9',
                    tooltip={"text": "{name_muni}"},
                ))

                st.write('---')

                st.markdown('''
                <h4 align="center">
                Informações dos Projetos de Assentamentos
                </h4>
                ''',unsafe_allow_html=True)
                df_br = df.groupby("Município").agg(
                    municipio = ("Município", "first"),
                    total = ("Município","count"),
                    area = ("Área", "sum"),
                    familias = ("Total de Famílias", "sum")
                    ).rename(columns={"municipio":'Município',"total":"No de Assentamentos","area": "Área Total","familias": "Total de Famílias"}).sort_values(by='Total de Famílias',ascending=False)
                st.dataframe(formatar_colunas_br(df_br), use_container_width=True, hide_index=True)
    
            
    else:
        st.write("Acesso negado. Você não tem permissão para acessar esta página.")
        
