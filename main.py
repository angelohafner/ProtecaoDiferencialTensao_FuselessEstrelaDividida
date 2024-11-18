import streamlit as st
import numpy as np
import pandas as pd
from impedance_analysis import ImpedanceAnalysis
from input_data import texto_1, texto_2

def main():
    st.title("Proteção diferencial de tensão em banco fuseless com ligação em estrela dividida e aterrado")
    st.write(texto_1)
    st.image("Figura_26_ieee37p99.png", caption="Figura 26 IEEE39.99", use_container_width=True)
    st.write(texto_2)
    st.sidebar.header("Parâmetros de Entrada")

    # Configuração de parâmetros de entrada
    frequencia = st.sidebar.number_input("Frequência (Hz)", value=60, step=1, format="%d")
    tensao_kv = st.sidebar.number_input("Tensão de Linha (kV)", value=138.0, step=1.0, format="%.2f")
    nr_serie = st.sidebar.number_input("Número de Impedâncias em Série", value=12, step=1, format="%d")
    nr_paralelo = st.sidebar.number_input("Número de Impedâncias em Paralelo", value=1, step=1, format="%d")
    capacitancia_padrao_uf = st.sidebar.number_input("Capacitância Padrão (µF)", value=8.16, step=0.1, format="%.2f")
    capacitancia_baixa_tensao_uf = st.sidebar.number_input("Capacitância Baixa Tensão (µF)", value=200.0, step=1.0, format="%.2f")

    # Conversão de entradas para unidades do SI
    tensao = tensao_kv * 1e3  # Convertendo kV para V
    capacitancia_padrao = capacitancia_padrao_uf * 1e-6  # Convertendo µF para F
    capacitancia_baixa_tensao = capacitancia_baixa_tensao_uf * 1e-6  # Convertendo µF para F

    # Calculando valores iniciais de impedâncias
    impedancia_padrao = 1 / (1j * 2 * np.pi * frequencia * capacitancia_padrao)
    impedancia_bt = 1 / (1j * 2 * np.pi * frequencia * capacitancia_baixa_tensao)
    v_phase = complex(tensao / np.sqrt(3), 0)

    # Matrizes de impedância
    impedance_matrix_1 = impedancia_padrao * np.ones((nr_serie, nr_paralelo))
    impedance_matrix_2 = impedancia_padrao * np.ones((nr_serie, nr_paralelo))
    low_voltage_impedance_1 = impedancia_bt
    low_voltage_impedance_2 = impedancia_bt

    # Botão para executar a análise
    if st.sidebar.button("Executar Análise"):
        st.info("Executando análise...")

        # Instancia a análise
        analysis = ImpedanceAnalysis(
            impedance_matrix_1,
            low_voltage_impedance_1,
            impedance_matrix_2,
            low_voltage_impedance_2,
            v_phase
        )
        analysis.perform_analysis()

        # Mostra os resultados
        st.header("Resultados da Análise")

        # Matrizes de tensões e potências reativas
        st.subheader("Tensões (em kV) e Potências Reativas (em kVAr)")
        voltage_matrix_1, v_low_voltage_1 = analysis.network_1.calculate_voltage_matrix()
        voltage_matrix_2, v_low_voltage_2 = analysis.network_2.calculate_voltage_matrix()
        reactive_power_matrix_1 = analysis.network_1.calculate_reactive_power_matrix()
        reactive_power_matrix_2 = analysis.network_2.calculate_reactive_power_matrix()

        col1, col2 = st.columns(2)
        with col1:
            st.write("Rede 1 - Tensões e Potências Reativas:")
            df1 = pd.DataFrame({
                "Tensões (kV)": np.abs(voltage_matrix_1).flatten() / 1e3,
                "Potências Reativas (kVAr)": reactive_power_matrix_1.flatten() / 1e3
            })
            st.dataframe(df1)
        with col2:
            st.write("Rede 2 - Tensões e Potências Reativas:")
            df2 = pd.DataFrame({
                "Tensões (kV)": np.abs(voltage_matrix_2).flatten() / 1e3,
                "Potências Reativas (kVAr)": reactive_power_matrix_2.flatten() / 1e3
            })
            st.dataframe(df2)

        # Dados do capacitor de baixa tensão
        st.subheader("Grandezas do Capacitor de Baixa Tensão")
        col1, col2 = st.columns(2)
        with col1:
            st.write("Rede 1 - Capacitor:")
            st.write(f"Tensão: {np.abs(v_low_voltage_1) / 1e3:.2f} kV")
            st.write(f"Corrente: {np.abs(analysis.i_low_voltage_1):.2f} A")
            st.write(f"Potência Reativa: {analysis.low_voltage_reactive_power_1 / 1e3:.2f} kVAr")
        with col2:
            st.write("Rede 2 - Capacitor:")
            st.write(f"Tensão: {np.abs(v_low_voltage_2) / 1e3:.2f} kV")
            st.write(f"Corrente: {np.abs(analysis.i_low_voltage_2):.2f} A")
            st.write(f"Potência Reativa: {analysis.low_voltage_reactive_power_2 / 1e3:.2f} kVAr")

        # Diferença de baixa tensão
        st.subheader("Diferença de Baixa Tensão (em kV)")
        st.write(f"Diferença: {np.abs(v_low_voltage_1 - v_low_voltage_2) / 1e3:.2f} kV")

        # Gerando arquivo Excel em memória
        from io import BytesIO
        output = BytesIO()
        analysis.export_to_excel(output, frequencia)
        output.seek(0)

        # Botão para baixar o arquivo Excel
        st.download_button(
            label="Baixar Resultados em Excel",
            data=output,
            file_name="resultados_impedancia.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )

if __name__ == "__main__":
    main()
