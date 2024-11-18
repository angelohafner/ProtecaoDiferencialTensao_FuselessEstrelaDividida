import numpy as np
import pandas as pd


class ImpedanceNetwork:
    def __init__(self, impedance_matrix, low_voltage_impedance, v_phase):
        self.impedance_matrix = impedance_matrix
        self.low_voltage_impedance = low_voltage_impedance
        self.v_phase = v_phase
        self.total_impedance = None

    def calculate_series_equivalent_impedance(self):
        return np.sum(self.impedance_matrix, axis=0)

    def calculate_parallel_equivalent_impedance(self, series_impedances):
        return 1 / np.sum(1 / series_impedances)

    def calculate_total_impedance(self):
        series_eq_impedances = self.calculate_series_equivalent_impedance()
        parallel_eq_impedance = self.calculate_parallel_equivalent_impedance(series_eq_impedances)
        self.total_impedance = parallel_eq_impedance + self.low_voltage_impedance
        return self.total_impedance

    def calculate_total_current(self):
        if self.total_impedance is None:
            self.calculate_total_impedance()
        return self.v_phase / self.total_impedance

    def calculate_voltage_matrix(self):
        total_current = self.calculate_total_current()
        series_eq_impedances = self.calculate_series_equivalent_impedance()

        voltage_matrix = np.zeros(self.impedance_matrix.shape, dtype=complex)
        for col in range(self.impedance_matrix.shape[1]):
            branch_current = total_current * (series_eq_impedances[col] / np.sum(series_eq_impedances))
            voltage_matrix[:, col] = branch_current * self.impedance_matrix[:, col]

        v_low_voltage_impedance = total_current * self.low_voltage_impedance
        return voltage_matrix, v_low_voltage_impedance

    def calculate_reactive_power_matrix(self):
        total_current = self.calculate_total_current()
        series_eq_impedances = self.calculate_series_equivalent_impedance()

        reactive_power_matrix = np.zeros(self.impedance_matrix.shape)
        for col in range(self.impedance_matrix.shape[1]):
            branch_current = total_current * (series_eq_impedances[col] / np.sum(series_eq_impedances))
            for row in range(self.impedance_matrix.shape[0]):
                impedance = self.impedance_matrix[row, col]
                reactive_power_matrix[row, col] = (np.abs(branch_current) ** 2) * impedance.imag

        return reactive_power_matrix

    def calculate_low_voltage_reactive_power(self):
        total_current = self.calculate_total_current()
        return (np.abs(total_current) ** 2) * self.low_voltage_impedance.imag

    def calculate_current_matrix(self):
        total_current = self.calculate_total_current()
        series_eq_impedances = self.calculate_series_equivalent_impedance()

        current_matrix = np.zeros(self.impedance_matrix.shape, dtype=complex)
        for col in range(self.impedance_matrix.shape[1]):
            branch_current = total_current * (series_eq_impedances[col] / np.sum(series_eq_impedances))
            current_matrix[:, col] = branch_current

        i_low_voltage_impedance = total_current
        return current_matrix, i_low_voltage_impedance

    def calculate_capacitance_matrix(self, frequency):
        # Calcula a pulsação angular
        omega = 2 * np.pi * frequency
        # Divide a parte imaginária da impedância por omega para obter a capacitância
        capacitance_matrix = -1 / (np.imag(self.impedance_matrix) * omega)
        return capacitance_matrix


class ImpedanceAnalysis:
    def __init__(self, impedance_matrix_1, low_voltage_impedance_1, impedance_matrix_2, low_voltage_impedance_2,
                 v_phase):
        self.network_1 = ImpedanceNetwork(impedance_matrix_1, low_voltage_impedance_1, v_phase)
        self.network_2 = ImpedanceNetwork(impedance_matrix_2, low_voltage_impedance_2, v_phase)
        self.v_phase = v_phase
        self.low_voltage_impedance_1 = low_voltage_impedance_1
        self.low_voltage_impedance_2 = low_voltage_impedance_2
        self.initialize_analysis_variables()

    def initialize_analysis_variables(self):
        self.voltage_matrix_1 = None
        self.voltage_matrix_2 = None
        self.reactive_power_matrix_1 = None
        self.reactive_power_matrix_2 = None
        self.current_matrix_1 = None
        self.current_matrix_2 = None
        self.v_low_voltage_1 = None
        self.v_low_voltage_2 = None
        self.i_low_voltage_1 = None
        self.i_low_voltage_2 = None
        self.low_voltage_difference = None
        self.low_voltage_reactive_power_1 = None
        self.low_voltage_reactive_power_2 = None

    def perform_analysis(self):
        self.voltage_matrix_1, self.v_low_voltage_1 = self.network_1.calculate_voltage_matrix()
        self.voltage_matrix_2, self.v_low_voltage_2 = self.network_2.calculate_voltage_matrix()
        self.low_voltage_difference = np.abs(self.v_low_voltage_2 - self.v_low_voltage_1)

        self.reactive_power_matrix_1 = self.network_1.calculate_reactive_power_matrix()
        self.reactive_power_matrix_2 = self.network_2.calculate_reactive_power_matrix()

        self.low_voltage_reactive_power_1 = self.network_1.calculate_low_voltage_reactive_power()
        self.low_voltage_reactive_power_2 = self.network_2.calculate_low_voltage_reactive_power()

        self.current_matrix_1, self.i_low_voltage_1 = self.network_1.calculate_current_matrix()
        self.current_matrix_2, self.i_low_voltage_2 = self.network_2.calculate_current_matrix()

    def create_matrix_with_extra_row(self, matrix, extra_value):
        extra_row = [extra_value] + [0] * (matrix.shape[1] - 1)
        return np.vstack([matrix, extra_row])

    def create_dataframe(self, matrix, name="Branch"):
        columns = [f"{name} {i + 1}" for i in range(matrix.shape[1])]
        return pd.DataFrame(matrix, columns=columns)

    def export_to_excel(self, filename, frequency):
        voltage_magnitude_matrix_1 = self.create_matrix_with_extra_row(np.abs(self.voltage_matrix_1),
                                                                       np.abs(self.v_low_voltage_1))
        voltage_magnitude_matrix_2 = self.create_matrix_with_extra_row(np.abs(self.voltage_matrix_2),
                                                                       np.abs(self.v_low_voltage_2))

        reactive_power_matrix_1 = self.create_matrix_with_extra_row(self.reactive_power_matrix_1,
                                                                    self.low_voltage_reactive_power_1)
        reactive_power_matrix_2 = self.create_matrix_with_extra_row(self.reactive_power_matrix_2,
                                                                    self.low_voltage_reactive_power_2)

        current_magnitude_matrix_1 = self.create_matrix_with_extra_row(np.abs(self.current_matrix_1),
                                                                       np.abs(self.i_low_voltage_1))
        current_magnitude_matrix_2 = self.create_matrix_with_extra_row(np.abs(self.current_matrix_2),
                                                                       np.abs(self.i_low_voltage_2))

        df_difference = pd.DataFrame([[self.low_voltage_difference]], columns=['Low Voltage Difference'])

        # Calcula as matrizes de capacitância e adiciona a capacitância de baixa tensão
        capacitance_matrix_1 = self.network_1.calculate_capacitance_matrix(frequency)
        capacitance_matrix_2 = self.network_2.calculate_capacitance_matrix(frequency)
        capacitance_low_voltage_1 = -1 / (np.imag(self.low_voltage_impedance_1) * (2 * np.pi * frequency))
        capacitance_low_voltage_2 = -1 / (np.imag(self.low_voltage_impedance_2) * (2 * np.pi * frequency))

        # Adiciona a linha extra de capacitância de baixa tensão
        capacitance_matrix_1 = self.create_matrix_with_extra_row(capacitance_matrix_1, capacitance_low_voltage_1)
        capacitance_matrix_2 = self.create_matrix_with_extra_row(capacitance_matrix_2, capacitance_low_voltage_2)

        with pd.ExcelWriter(filename) as writer:
            self.create_dataframe(voltage_magnitude_matrix_1).to_excel(writer, sheet_name='Network 1 Voltage Magnitude',
                                                                       index=False)
            self.create_dataframe(voltage_magnitude_matrix_2).to_excel(writer, sheet_name='Network 2 Voltage Magnitude',
                                                                       index=False)
            self.create_dataframe(reactive_power_matrix_1).to_excel(writer, sheet_name='Network 1 Reactive Power',
                                                                    index=False)
            self.create_dataframe(reactive_power_matrix_2).to_excel(writer, sheet_name='Network 2 Reactive Power',
                                                                    index=False)
            self.create_dataframe(current_magnitude_matrix_1).to_excel(writer, sheet_name='Network 1 Current Magnitude',
                                                                       index=False)
            self.create_dataframe(current_magnitude_matrix_2).to_excel(writer, sheet_name='Network 2 Current Magnitude',
                                                                       index=False)
            df_difference.to_excel(writer, sheet_name='Low Voltage Difference', index=False)
            # Exporta as matrizes de capacitância com a linha extra
            pd.DataFrame(capacitance_matrix_1,
                         columns=[f'Branch {i + 1}' for i in range(capacitance_matrix_1.shape[1])]).to_excel(
                writer, sheet_name='Network 1 Capacitance', index=False)
            pd.DataFrame(capacitance_matrix_2,
                         columns=[f'Branch {i + 1}' for i in range(capacitance_matrix_2.shape[1])]).to_excel(
                writer, sheet_name='Network 2 Capacitance', index=False)

        print(f"Arquivo Excel '{filename}' criado com sucesso.")
