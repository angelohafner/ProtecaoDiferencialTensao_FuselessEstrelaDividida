import streamlit as st
import pandas as pd
import numpy as np
from impedance_analysis import ImpedanceAnalysis


def configure_inputs():
    st.sidebar.header("Parâmetros de Entrada")

    frequencia = st.sidebar.number_input("Frequência (Hz)", value=60, step=1, format="%d")
    tensao_kv = st.sidebar.number_input("Tensão de Linha (kV)", value=138.0, step=1.0, format="%.2f")
    nr_serie = st.sidebar.number_input("Número de Capacitores em Série", value=12, step=1, format="%d")
    nr_paralelo = st.sidebar.number_input("Número de Capacitores em Paralelo", value=1, step=1, format="%d")
    capacitancia_padrao_uf = st.sidebar.number_input("Capacitância Padrão (µF)", value=8.37, step=0.1, format="%.2f")
    capacitancia_baixa_tensao_uf = st.sidebar.number_input("Capacitância Baixa Tensão (µF)", value=200.0, step=1.0,
                                                           format="%.2f")
    nr_serie_internos = st.sidebar.number_input("Número de SubCapacitores em Série", value=4, step=1, format="%d")
    nr_paralelo_internos = st.sidebar.number_input("Número de SubCapacitores em Paralelo", value=9, step=1, format="%d")

    # Retornar entradas como dicionário
    return {
        "frequencia": frequencia,
        "tensao_kv": tensao_kv,
        "nr_serie": nr_serie,
        "nr_paralelo": nr_paralelo,
        "capacitancia_padrao_uf": capacitancia_padrao_uf,
        "capacitancia_baixa_tensao_uf": capacitancia_baixa_tensao_uf,
        "nr_serie_internos": nr_serie_internos,
        "nr_paralelo_internos": nr_paralelo_internos,
        "tensao_lata": 7967.4
    }


def execute_analysis(inputs):
    st.info("Executando análise...")

    # Processar entradas
    frequencia = inputs["frequencia"]
    tensao = inputs["tensao_kv"] * 1e3  # Convertendo kV para V
    capacitancia_padrao = inputs["capacitancia_padrao_uf"] * 1e-6  # Convertendo µF para F
    capacitancia_baixa_tensao = inputs["capacitancia_baixa_tensao_uf"] * 1e-6  # Convertendo µF para F
    nr_serie = inputs["nr_serie"]
    nr_paralelo = inputs["nr_paralelo"]
    nr_serie_internos = inputs["nr_serie_internos"]
    nr_paralelo_internos = inputs["nr_paralelo_internos"]
    tensao_lata = inputs["tensao_lata"]
    capacitancia_internos = capacitancia_padrao / nr_paralelo_internos * nr_serie_internos

    # Calcular impedâncias
    impedancia_padrao = 1 / (1j * 2 * np.pi * frequencia * capacitancia_padrao)
    impedancia_bt = 1 / (1j * 2 * np.pi * frequencia * capacitancia_baixa_tensao)
    impedancia_internos = 1 / (1j * 2 * np.pi * frequencia * capacitancia_internos)
    v_phase = complex(tensao / np.sqrt(3), 0)

    # Matrizes de impedância
    impedance_matrix = impedancia_padrao * np.ones((nr_serie, nr_paralelo), dtype=complex)
    impedance_matrix_internos = impedancia_internos * np.ones((nr_serie_internos, nr_paralelo_internos), dtype=complex)
    impedance_matrix_internos2 = impedancia_internos * np.ones((nr_serie_internos, nr_paralelo_internos), dtype=complex)
    impedance_matrix_internos3 = impedancia_internos * np.ones((nr_serie_internos, nr_paralelo_internos), dtype=complex)

    df1_voltage_list = []
    df2_voltagedf_list = []
    df1_reactive_power_list = []
    df2_reactive_power_list = []
    v_low_voltage_1_list = []
    v_low_voltage_2_list = []
    i_low_voltage_1_list = []
    i_low_voltage_2_list = []
    low_voltage_reactive_power_1_list = []
    low_voltage_reactive_power_2_list = []
    potential_transformer_ddp_list = []
    impedance_matrix_1 = impedance_matrix.copy()
    impedance_matrix_2 = impedance_matrix.copy()
    for ii in range(0, 3*nr_serie_internos+1, 1):
        if ii <= nr_serie_internos:
            impedance_matrix_internos[0:ii, :] = 1e-99
            impedance_paralelos_internos = 1 / np.sum(1 / impedance_matrix_internos, axis=1)
            impedance_00 = np.sum(impedance_paralelos_internos)
            impedance_matrix_1[0, 0] = impedance_00
        elif ii <= 2*nr_serie_internos:
            jj = ii - nr_serie_internos
            impedance_matrix_internos2[0:jj, :] = 1e-99
            impedance_paralelos_internos2 = 1 / np.sum(1 / impedance_matrix_internos2, axis=1)
            impedance_10 = np.sum(impedance_paralelos_internos2)
            impedance_matrix_1[1, 0] = impedance_10
        elif ii <= 3*nr_serie_internos:
            kk = ii - 2*nr_serie_internos
            impedance_matrix_internos3[0:kk, :] = 1e-99
            impedance_paralelos_internos3 = 1 / np.sum(1 / impedance_matrix_internos3, axis=1)
            impedance_20 = np.sum(impedance_paralelos_internos3)
            impedance_matrix_1[2, 0] = impedance_20

        analysis = ImpedanceAnalysis(
            impedance_matrix_1,
            impedancia_bt,
            impedance_matrix_2,
            impedancia_bt,
            v_phase
        )
        analysis.perform_analysis()

        voltage_matrix_1, v_low_voltage_1 = analysis.network_1.calculate_voltage_matrix()
        voltage_matrix_2, v_low_voltage_2 = analysis.network_2.calculate_voltage_matrix()
        reactive_power_matrix_1 = analysis.network_1.calculate_reactive_power_matrix()
        reactive_power_matrix_2 = analysis.network_2.calculate_reactive_power_matrix()

        df1_voltage = pd.DataFrame({
            f"V (pu) {ii}": np.abs(voltage_matrix_1).flatten() / tensao_lata,
            # f"Potências Reativas (kVAr) {ii}": reactive_power_matrix_1.flatten() / tensao_lata
        })
        df1_reactive_power = pd.DataFrame({
            f"Potências Reativas (kVAr) {ii}": reactive_power_matrix_1.flatten()
        })
        df1_voltage_list.append(df1_voltage)
        df1_reactive_power_list.append(df1_reactive_power)

        df2_voltagedf = pd.DataFrame({
            f"Tensões (kV) {ii}": np.abs(voltage_matrix_2).flatten() / tensao_lata,
        })
        df2_reactive_power = pd.DataFrame({
            f"Potências Reativas (kVAr) {ii}": reactive_power_matrix_2.flatten()
        })
        df2_voltagedf_list.append(df2_voltagedf)
        df2_reactive_power_list.append(df1_reactive_power)

        v_low_voltage_1_list.append(np.abs(v_low_voltage_1))
        v_low_voltage_2_list.append(np.abs(v_low_voltage_2))
        i_low_voltage_1_list.append(np.abs(analysis.i_low_voltage_1))
        i_low_voltage_2_list.append(np.abs(analysis.i_low_voltage_2))
        low_voltage_reactive_power_1_list.append(analysis.low_voltage_reactive_power_1)
        low_voltage_reactive_power_2_list.append(analysis.low_voltage_reactive_power_2)
        potential_transformer_ddp_list.append(np.abs(v_low_voltage_1 - v_low_voltage_2))

    df_combined = pd.DataFrame()
    df_last_rows = pd.DataFrame()


    for ii, df in enumerate(df1_voltage_list):
        df_combined = pd.concat([df_combined, df], axis=1)
        first_row = df.iloc[0:]
        second_row = df.iloc[1:]
        last_row = df.iloc[-1:]
        df_last_rows = pd.concat([df_last_rows, last_row], axis=1)

    # Criar o DataFrame final diretamente
    df_final = pd.DataFrame(
        {
            f"{ii}": [potential_transformer_ddp_list[ii], df_last_rows.iloc[0, ii]]
            for ii in range(len(potential_transformer_ddp_list))
        },
        index=["Potential Transformer DDP", "Voltage Healty Capacitors"]
    )

    # Exibir o DataFrame final
    st.markdown("## DDP and voltage at healthy capacitors as a function of blown fuses" )
    st.write("DataFrame Final:", df_final.T)

    soma_reativos_list = []

    # Iterar sobre todas as posições das listas de reativos
    for idx in range(len(low_voltage_reactive_power_1_list)):
        soma_reativos = (
                low_voltage_reactive_power_1_list[idx] +
                low_voltage_reactive_power_2_list[idx] +
                df1_reactive_power_list[idx].values.sum() +
                df2_reactive_power_list[idx].values.sum() +
                2 * low_voltage_reactive_power_1_list[0] +
                2 * low_voltage_reactive_power_2_list[0] +
                2 * df1_reactive_power_list[0].values.sum() +
                2 * df2_reactive_power_list[0].values.sum()
        )
        soma_reativos_list.append(soma_reativos)

    st.markdown("## Low voltage capacitors work quantities:")
    st.write(f"Voltage  = {round(v_low_voltage_1_list[0], 2)} V")
    st.write(f"Current  = {round(i_low_voltage_1_list[0], 2)} A")
    st.write(f"Power    = {round(low_voltage_reactive_power_1_list[0] / 1e3, 2)} kVAr")

    st.markdown("## Power as function of blown fuses")
    st.write(soma_reativos_list)

