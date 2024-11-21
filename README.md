# Proteção Diferencial de Tensão em Banco Fuseless com Ligação em Estrela Dividida e Aterrado

Este aplicativo Streamlit implementa uma ferramenta interativa para análise de proteção diferencial de tensão em bancos fuseless com ligação em estrela dividida e aterrada. Ele permite a entrada de parâmetros, execução da análise e exibição dos resultados em forma de tabelas e gráficos, bem como a exportação de dados para um arquivo Excel.

## Funcionalidades
1. **Exibição Interativa:**
   - Explicação teórica sobre proteção diferencial.
   - Exibição de imagem da configuração do sistema (Figura 26 do IEEE 37.99).
   
2. **Configuração de Parâmetros de Entrada:**
   - Frequência (Hz).
   - Tensão de linha (kV).
   - Número de impedâncias em série e em paralelo.
   - Capacitâncias (padrão e de baixa tensão) em µF.

3. **Resultados:**
   - Matrizes de tensões (em kV) e potências reativas (em kVAr) para as duas redes.
   - Grandezas relacionadas ao capacitor de baixa tensão:
     - Tensão (kV), Corrente (A) e Potência Reativa (kVAr).
   - Diferença de tensão de baixa tensão (em kV).

4. **Exportação:**
   - Os resultados podem ser exportados em formato Excel.

## Instalação

Certifique-se de ter o Python instalado na máquina e siga os passos abaixo:

1. Clone este repositório ou baixe os arquivos do projeto.
2. Instale as dependências necessárias:
   ```bash
   pip install streamlit numpy pandas
   ```
3. Certifique-se de que o arquivo de imagem `Figura_26_ieee37p99.png` e os scripts auxiliares (`impedance_analysis.py`, `input_data.py`) estão no mesmo diretório do script principal.

## Como Executar
1. Execute o aplicativo Streamlit:
   ```bash
   streamlit run app.py
   ```
2. O aplicativo abrirá automaticamente no navegador. Caso isso não aconteça, acesse o link indicado no terminal (geralmente `http://localhost:8501`).

## Estrutura do Projeto

```plaintext
|-- app.py                  # Arquivo principal do aplicativo Streamlit
|-- impedance_analysis.py   # Script com os cálculos da análise de impedâncias
|-- input_data.py           # Script com dados auxiliares e explicações
|-- Figura_26_ieee37p99.png # Imagem do sistema de exemplo
|-- README.md               # Documentação do projeto
```

## Uso
1. Configure os parâmetros no menu lateral (frequência, tensão, número de impedâncias, etc.).
2. Clique no botão "Executar Análise" para realizar os cálculos.
3. Visualize os resultados diretamente no navegador:
   - Matrizes de tensões e potências reativas.
   - Grandezas do capacitor de baixa tensão.
   - Diferença de baixa tensão.
4. Exporte os resultados para um arquivo Excel usando o botão disponível.

## Dependências
- `streamlit`
- `numpy`
- `pandas`

## Licença
Este projeto é apenas para fins educacionais e acadêmicos. Consulte a documentação do IEEE para referências adicionais.

---

Desenvolvido com ❤️ para facilitar a análise de proteção diferencial em sistemas elétricos.
