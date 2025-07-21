import streamlit as st
import pandas as pd
DATA_DIR = "data"

def on_click_callback(x): 
    print(x)
    """Função de callback para o botão 'Acompanhar distribuição'."""
    st.session_state.page = x

def load_css(file_name: str):
    """Função para carregar CSS externo e aplicá-lo no Streamlit."""
    with open(file_name, "r") as f:
        css = f.read()
    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def run():
   
    # Centraliza com colunas e flex
    if st.session_state['page']=="home":
        load_css("./assets/css/styles.css")
        st.markdown("""<div class="title-text">Painel da Reforma Agrária</div>""", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([0.3, 0.4, 0.3])
        with col2:
            st.markdown('<div class="button-space"></div>', unsafe_allow_html=True)
            
            if st.button("Acessar o sistema", use_container_width=True):
                st.login()
            

    

    if st.session_state['page']=="acompanhamento":
        load_css("./assets/css/styles.css")
        st.write(f"Bem-vindo, teste!")
        
     
if __name__ == "__main__":
    run()
