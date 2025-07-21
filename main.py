import streamlit as st
import analise
import home
import pandas as pd
import folium
st.set_page_config(page_title="Painel da Reforma Agrária", page_icon="./assets/images/ialogo2.png")

# st.logo("./assets/images/ialogo.png", icon_image="./assets/images/ialogo2.png")

DATA_DIR = "data"


if 'page' not in st.session_state:
    st.session_state['page'] = "home"


def load_css(file_name: str):
    """Função para carregar CSS externo e aplicá-lo no Streamlit."""
    with open(file_name, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)

load_css("./assets/css/styles.css")
if not st.user.is_logged_in:
    home.run()
else:
    try:
        st.session_state['user_email'] = st.user.email
    except:
        pass
    if st.sidebar.button("Encerrar sessão", use_container_width=True):
        st.logout()
        st.session_state['page'] = "home"
        st.experimental_rerun()
    analise.run()

