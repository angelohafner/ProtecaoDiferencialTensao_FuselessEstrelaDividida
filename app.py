
import streamlit as st
from utils import configure_inputs, execute_analysis
from input_data import texto_1, texto_2

def main():
    st.title("Proteção diferencial de tensão em banco fuseless com ligação em estrela dividida e aterrado")
    st.write(texto_1)
    st.image("Figura_26_ieee37p99.png", caption="Figura 26 IEEE37.99", use_container_width=True)
    st.write(texto_2)

    # Configurar entradas
    inputs = configure_inputs()

    # Botão para executar a análise
    if st.sidebar.button("Executar Análise"):
        execute_analysis(inputs)

if __name__ == "__main__":
    main()
