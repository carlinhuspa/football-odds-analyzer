import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats
import re
from datetime import datetime
import base64
from io import BytesIO

# Adicionar diretório atual ao path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Importar módulos do projeto
from data_processor import (
    process_odds_text,
    process_historical_matches_text,
    process_statistics_text
)
from analyzer import (
    calculate_poisson_probabilities,
    adjust_probabilities_with_history,
    calculate_market_probabilities,
    find_most_probable_scores,
    calculate_expected_value,
    dixon_coles_adjustment,
    calculate_dixon_coles_matrix,
    calculate_kelly_criterion
)
from visualizer import (
    create_probability_matrix_heatmap,
    create_market_probabilities_chart,
    create_most_probable_scores_chart,
    create_historical_comparison_chart,
    create_expected_value_chart,
    create_team_comparison_chart
)
from report_generator import (
    generate_technical_report,
    generate_humanized_interpretation
)

def main():
    # Configuração da página
    st.set_page_config(
        page_title="Analisador de Odds e Estatísticas de Futebol",
        page_icon="⚽",
        layout="wide",
        initial_sidebar_state="expanded"
    )

    # Título e descrição
    st.title("⚽ Analisador de Odds e Estatísticas de Futebol")
    st.markdown("""
    Este aplicativo analisa odds, histórico de jogos e estatísticas de times de futebol para gerar:
    - Probabilidades de diferentes resultados e placares
    - Visualizações detalhadas das análises
    - Recomendações de apostas com melhor valor
    - Interpretação humanizada dos resultados
    """)

    # Sidebar para entrada de dados
    st.sidebar.header("Entrada de Dados")

    # Opções de entrada
    input_method = st.sidebar.radio(
        "Método de entrada de dados:",
        ["Texto", "Arquivo"]
    )

    # Opções avançadas
    st.sidebar.header("Opções Avançadas")
    use_dixon_coles = st.sidebar.checkbox("Usar modelo Dixon-Coles", value=True, 
                                        help="Modelo que ajusta a correlação entre gols dos times")
    history_weight = st.sidebar.slider("Peso do histórico", 0.0, 1.0, 0.3, 0.1,
                                    help="Quanto maior o valor, mais influência o histórico terá na previsão")
    max_goals = st.sidebar.slider("Máximo de gols", 3, 10, 5, 1,
                                help="Número máximo de gols a considerar no modelo")
    kelly_fraction = st.sidebar.slider("Fração de Kelly", 0.1, 1.0, 0.5, 0.1,
                                    help="Fração do critério de Kelly para recomendações de apostas")

    # Interface principal
    if input_method == "Texto":
        # Entrada de texto
        odds_text = st.sidebar.text_area(
            "Odds (formato: mercado, odd):",
            height=150,
            placeholder="1, 1.56\nX, 4.00\n2, 5.80\nOver 2.5, 1.70\nAmbas Marcam Sim, 2.00"
        )
        
        historical_matches_text = st.sidebar.text_area(
            "Histórico de Jogos:",
            height=150,
            placeholder="21/12/2024, Time A 5-1 Time B\n18/12/2024, Time A 3-2 Time B\n..."
        )
        
        statistics_text = st.sidebar.text_area(
            "Estatísticas dos Times:",
            height=150,
            placeholder="Time da Casa: Time A\nTime Visitante: Time B\nGols marcados casa: 1.94\nGols sofridos casa: 0.81\n..."
        )
    else:
        # Upload de arquivos
        odds_file = st.sidebar.file_uploader("Arquivo de Odds", type=["txt", "csv"])
        historical_file = st.sidebar.file_uploader("Arquivo de Histórico de Jogos", type=["txt", "csv"])
        statistics_file = st.sidebar.file_uploader("Arquivo de Estatísticas", type=["txt", "csv"])
        
        odds_text = ""
        historical_matches_text = ""
        statistics_text = ""
        
        if odds_file is not None:
            odds_text = odds_file.getvalue().decode("utf-8")
        if historical_file is not None:
            historical_matches_text = historical_file.getvalue().decode("utf-8")
        if statistics_file is not None:
            statistics_text = statistics_file.getvalue().decode("utf-8")

    # Botão para processar
    process_button = st.sidebar.button("Analisar Dados")

    # Processar dados quando o botão for clicado
    if process_button:
        if not odds_text or not historical_matches_text or not statistics_text:
            st.error("Por favor, forneça todos os dados necessários para a análise.")
        else:
            # Processar os dados
            results = process_data(
                odds_text, 
                historical_matches_text, 
                statistics_text,
                use_dixon_coles,
                history_weight,
                max_goals,
                kelly_fraction
            )
            
            # Exibir resultados em abas
            tab1, tab2, tab3, tab4 = st.tabs(["Resumo", "Visualizações", "Relatório Técnico", "Interpretação Humanizada"])
            
            with tab1:
                display_summary_tab(results, use_dixon_coles, history_weight)
            
            with tab2:
                display_visualizations_tab(results)
            
            with tab3:
                display_technical_report_tab(results)
            
            with tab4:
                display_humanized_interpretation_tab(results)
    else:
        display_example_usage()

    # Rodapé
    st.sidebar.markdown("---")
    st.sidebar.info(
        "Este aplicativo foi desenvolvido para análise de odds e estatísticas de futebol. "
        "Os resultados são baseados em modelos estatísticos e não garantem sucesso em apostas."
    )

def process_data(odds_text, historical_matches_text, statistics_text, 
                use_dixon_coles=True, history_weight=0.3, max_goals=5, kelly_fraction=0.5):
    """
    Processa os dados de entrada e gera os resultados da análise
    """
    with st.spinner("Processando dados..."):
        # Processar textos de entrada
        odds_data = process_odds_text(odds_text)
        historical_data = process_historical_matches_text(historical_matches_text)
        stats_data = process_statistics_text(statistics_text)
        
        # Extrair informações relevantes
        home_team = stats_data.get('home_team', 'Time da Casa')
        away_team = stats_data.get('away_team', 'Time Visitante')
        
        # Calcular gols esperados
        home_expected_goals = stats_data.get('home_expected_goals', 1.5)
        away_expected_goals = stats_data.get('away_expected_goals', 1.0)
        
        # Ajustar com base na força relativa
        strength_adjustment = 0.15
        if 'home_position' in stats_data and 'away_position' in stats_data:
            position_diff = stats_data['away_position'] - stats_data['home_position']
            strength_adjustment = min(0.3, max(0.0, 0.1 + position_diff * 0.02))
        
        adjusted_home_expected_goals = home_expected_goals * (1 + strength_adjustment)
        adjusted_away_expected_goals = away_expected_goals * (1 - strength_adjustment)
        
        # Calcular probabilidades base usando Poisson ou Dixon-Coles
        if use_dixon_coles:
            # Usar modelo Dixon-Coles com correlação negativa entre gols
            prob_matrix = calculate_dixon_coles_matrix(
                adjusted_home_expected_goals, 
                adjusted_away_expected_goals,
                max_goals=max_goals,
                rho=-0.1  # Correlação negativa padrão
            )
        else:
            # Usar modelo Poisson padrão
            prob_matrix = calculate_poisson_probabilities(
                adjusted_home_expected_goals, 
                adjusted_away_expected_goals,
                max_goals=max_goals
            )
        
        # Ajustar com histórico
        if historical_data and 'match_results' in historical_data:
            prob_matrix = adjust_probabilities_with_history(
                prob_matrix, 
                historical_data['match_results'],
                weight=history_weight,
                max_goals=max_goals
            )
        
        # Calcular probabilidades de mercados
        market_probs = calculate_market_probabilities(prob_matrix)
        
        # Encontrar placares mais prováveis
        top_scores = find_most_probable_scores(prob_matrix, n=10)
        
        # Calcular valor esperado e Kelly
        market_ev = {}
        kelly_stakes = {}
        if 'market_odds' in odds_data:
            for market, odd in odds_data['market_odds'].items():
                if market in market_probs:
                    prob = market_probs[market]
                    market_ev[market] = calculate_expected_value(prob, odd)
                    kelly_stakes[market] = calculate_kelly_criterion(prob, odd, kelly_fraction)
        
        # Gerar relatórios
        technical_report = generate_technical_report(
            home_team, away_team,
            adjusted_home_expected_goals, adjusted_away_expected_goals,
            prob_matrix, market_probs, top_scores[:5],
            odds_data.get('market_odds', {}), market_ev
        )
        
        humanized_interpretation = generate_humanized_interpretation(
            home_team, away_team,
            stats_data, historical_data,
            market_probs, top_scores[:5], market_ev
        )
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'prob_matrix': prob_matrix,
            'market_probs': market_probs,
            'top_scores': top_scores,
            'market_ev': market_ev,
            'kelly_stakes': kelly_stakes,
            'technical_report': technical_report,
            'humanized_interpretation': humanized_interpretation,
            'stats_data': stats_data,
            'historical_data': historical_data,
            'odds_data': odds_data,
            'adjusted_home_expected_goals': adjusted_home_expected_goals,
            'adjusted_away_expected_goals': adjusted_away_expected_goals
        }

def display_summary_tab(results, use_dixon_coles, history_weight):
    """
    Exibe a aba de resumo com os principais resultados
    """
    st.header(f"Análise: {results['home_team']} vs {results['away_team']}")
    
    # Mostrar placares mais prováveis
    st.subheader("Placares Mais Prováveis")
    scores_df = pd.DataFrame(results['top_scores'][:5], columns=["Placar", "Probabilidade"])
    scores_df["Probabilidade"] = scores_df["Probabilidade"].apply(lambda x: f"{x:.2%}")
    st.table(scores_df)
    
    # Mostrar probabilidades de mercados principais
    st.subheader("Probabilidades por Mercado")
    main_markets = ['1', 'X', '2', 'Over 2.5', 'Under 2.5', 'Ambas Marcam Sim', 'Ambas Marcam Não']
    market_data = []
    
    for market in main_markets:
        if market in results['market_probs']:
            prob = results['market_probs'][market]
            odd = results['odds_data'].get('market_odds', {}).get(market, "-")
            ev = results['market_ev'].get(market, "-")
            kelly = results['kelly_stakes'].get(market, "-")
            
            if isinstance(ev, (int, float)):
                ev = f"{ev:.2f}"
            if isinstance(kelly, (int, float)):
                kelly = f"{kelly:.2%}"
                
            market_data.append([market, f"{prob:.2%}", odd, ev, kelly])
    
    market_df = pd.DataFrame(market_data, columns=["Mercado", "Probabilidade", "Odd", "Valor Esperado", "Kelly"])
    st.table(market_df)
    
    # Mostrar apostas com valor
    st.subheader("Apostas com Melhor Valor")
    value_bets = {k: v for k, v in results['market_ev'].items() if isinstance(v, (int, float)) and v > 1.0}
    
    if value_bets:
        value_data = []
        for market, ev in sorted(value_bets.items(), key=lambda x: x[1], reverse=True):
            prob = results['market_probs'][market]
            odd = results['odds_data'].get('market_odds', {}).get(market, "-")
            kelly = results['kelly_stakes'].get(market, "-")
            
            if isinstance(kelly, (int, float)):
                kelly = f"{kelly:.2%}"
                
            value_data.append([market, f"{prob:.2%}", odd, f"{ev:.2f}", kelly])
        
        value_df = pd.DataFrame(value_data, columns=["Mercado", "Probabilidade", "Odd", "Valor Esperado", "Kelly"])
        st.table(value_df)
    else:
        st.info("Nenhuma aposta com valor positivo identificada.")
    
    # Parâmetros do modelo
    st.subheader("Parâmetros do Modelo")
    st.write(f"- Gols esperados do {results['home_team']} (casa): {results['adjusted_home_expected_goals']:.2f}")
    st.write(f"- Gols esperados do {results['away_team']} (fora): {results['adjusted_away_expected_goals']:.2f}")
    st.write(f"- Modelo utilizado: {'Dixon-Coles' if use_dixon_coles else 'Poisson'}")
    st.write(f"- Peso do histórico: {history_weight:.1f}")
    
    # Botões de download
    st.subheader("Downloads")
    
    # Criar figuras para download
    matrix_fig = create_probability_matrix_heatmap(
        results['prob_matrix'],
        f"Probabilidades: {results['home_team']} vs {results['away_team']}"
    )
    
    scores_fig = create_most_probable_scores_chart(
        results['top_scores'][:10],
        f"Placares Mais Prováveis: {results['home_team']} vs {results['away_team']}"
    )
    
    market_fig = create_market_probabilities_chart(results['market_probs'])
    
    # Links de download
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown(get_image_download_link(matrix_fig, 'matriz_probabilidades.png', 'Download Matriz de Probabilidades'), unsafe_allow_html=True)
    
    with col2:
        st.markdown(get_image_download_link(scores_fig, 'placares_provaveis.png', 'Download Placares Prováveis'), unsafe_allow_html=True)
    
    with col3:
        st.markdown(get_image_download_link(market_fig, 'probabilidades_mercados.png', 'Download Probabilidades por Mercado'), unsafe_allow_html=True)
    
    # Download dos relatórios
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(get_markdown_download_link(results['technical_report'], 'relatorio_tecnico.md', 'Download Relatório Técnico'), unsafe_allow_html=True)
    
    with col2:
        st.markdown(get_markdown_download_link(results['humanized_interpretation'], 'interpretacao_humanizada.md', 'Download Interpretação Humanizada'), unsafe_allow_html=True)

def display_visualizations_tab(results):
    """
    Exibe a aba de visualizações com gráficos detalhados
    """
    st.header("Visualizações")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Matriz de probabilidades
        st.subheader("Matriz de Probabilidades de Placares")
        matrix_fig = create_probability_matrix_heatmap(
            results['prob_matrix'],
            f"Probabilidades: {results['home_team']} vs {results['away_team']}"
        )
        st.pyplot(matrix_fig)
    
    with col2:
        # Placares mais prováveis
        st.subheader("Placares Mais Prováveis")
        scores_fig = create_most_probable_scores_chart(
            results['top_scores'][:10],
            f"Placares Mais Prováveis: {results['home_team']} vs {results['away_team']}"
        )
        st.pyplot(scores_fig)
    
    # Probabilidades por mercado
    st.subheader("Probabilidades por Mercado")
    market_fig = create_market_probabilities_chart(results['market_probs'])
    st.pyplot(market_fig)
    
    # Valor esperado por mercado
    st.subheader("Valor Esperado por Mercado")
    ev_fig = create_expected_value_chart(results['market_ev'])
    st.pyplot(ev_fig)
    
    # Se houver dados históricos suficientes
    if results['historical_data'] and 'common_scores' in results['historical_data']:
        st.subheader("Placares Históricos Mais Comuns")
        hist_fig = create_historical_comparison_chart(
            results['historical_data'],
            f"Placares Históricos: {results['home_team']} vs {results['away_team']}"
        )
        st.pyplot(hist_fig)
    
    # Se houver dados estatísticos suficientes para comparação
    if (results['stats_data'] and 
        any(k in results['stats_data'] for k in ['gols_marcados_casa', 'gols_marcados_fora'])):
        st.subheader("Comparação entre Times")
        team_fig = create_team_comparison_chart(
            results['stats_data'],
            results['home_team'],
            results['away_team']
        )
        st.pyplot(team_fig)

def display_technical_report_tab(results):
    """
    Exibe a aba de relatório técnico
    """
    st.header("Relatório Técnico")
    st.markdown(results['technical_report'])

def display_humanized_interpretation_tab(results):
    """
    Exibe a aba de interpretação humanizada
    """
    st.header("Interpretação Humanizada")
    st.markdown(results['humanized_interpretation'])

def display_example_usage():
    """
    Exibe instruções de exemplo quando nenhum dado foi processado
    """
    st.header("Exemplo de Uso")
    st.markdown("""
    ### Como usar este aplicativo:

    1. **Insira as odds** no formato "mercado, odd" (uma por linha):
       ```
       1, 1.56
       X, 4.00
       2, 5.80
       Over 2.5, 1.70
       Ambas Marcam Sim, 2.00
       ```

    2. **Insira o histórico de jogos** no formato "data, time_casa placar time_fora" (um por linha):
       ```
       21/12/2024, Arsenal 5-1 Crystal Palace
       18/12/2024, Arsenal 3-2 Crystal Palace
       15/11/2024, Crystal Palace 0-1 Arsenal
       ```

    3. **Insira as estatísticas dos times** no formato "chave: valor" (uma por linha):
       ```
       Time da Casa: Arsenal
       Time Visitante: Crystal Palace
       Gols marcados casa: 1.94
       Gols sofridos casa: 0.81
       Gols marcados fora: 1.38
       Gols sofridos fora: 1.38
       Posicao casa: 2
       Posicao fora: 12
       ```

    4. Clique em **Analisar Dados** para processar as informações e gerar a análise completa.
    """)

    st.subheader("Opções Avançadas")
    st.markdown("""
    - **Modelo Dixon-Coles**: Ajusta a correlação entre gols dos times, geralmente mais preciso que o modelo Poisson padrão
    - **Peso do histórico**: Controla quanto o histórico de confrontos influencia as probabilidades (0 = sem influência, 1 = máxima influência)
    - **Máximo de gols**: Define o número máximo de gols a considerar no modelo (afeta a precisão e o tempo de processamento)
    - **Fração de Kelly**: Ajusta as recomendações de apostas (valores menores são mais conservadores)
    """)

    st.subheader("Exemplo de Análise")
    st.image("https://i.imgur.com/XYZ123.png", caption="Exemplo de visualização de probabilidades de placares")

# Função para converter figura matplotlib para imagem base64
def get_image_download_link(fig, filename, text):
    """
    Gera um link para download de uma figura matplotlib
    """
    buf = BytesIO()
    fig.savefig(buf, format='png', dpi=300, bbox_inches='tight')
    buf.seek(0)
    b64 = base64.b64encode(buf.read()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">{text}</a>'
    return href

# Função para gerar arquivo markdown para download
def get_markdown_download_link(markdown_text, filename, link_text):
    """
    Gera um link para download de texto markdown
    """
    b64 = base64.b64encode(markdown_text.encode()).decode()
    href = f'<a href="data:file/markdown;base64,{b64}" download="{filename}">{link_text}</a>'
    return href

if __name__ == "__main__":
    main()
