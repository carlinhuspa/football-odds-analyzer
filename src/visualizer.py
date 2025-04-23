import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import pandas as pd

def create_probability_matrix_heatmap(prob_matrix, title):
    """
    Cria um heatmap para visualizar a matriz de probabilidades de placares
    
    Args:
        prob_matrix: DataFrame com probabilidades de placares
        title: Título do gráfico
        
    Returns:
        Figura matplotlib
    """
    plt.figure(figsize=(10, 8))
    ax = sns.heatmap(prob_matrix, annot=True, cmap='YlGnBu', fmt='.3f')
    plt.title(title)
    plt.tight_layout()
    
    return plt.gcf()

def create_market_probabilities_chart(probabilities):
    """
    Cria um gráfico de barras para visualizar probabilidades de diferentes mercados
    
    Args:
        probabilidades: Dicionário com probabilidades para diferentes mercados
        
    Returns:
        Figura matplotlib
    """
    # Selecionar mercados principais
    main_markets = [
        '1', 'X', '2', 
        'Over 0.5', 'Under 0.5',
        'Over 1.5', 'Under 1.5',
        'Over 2.5', 'Under 2.5',
        'Over 3.5', 'Under 3.5',
        'Over 4.5', 'Under 4.5',
        'Ambas Marcam Sim', 'Ambas Marcam Não'
    ]
    
    # Filtrar mercados disponíveis
    markets = []
    probs = []
    
    for market in main_markets:
        if market in probabilities:
            markets.append(market)
            probs.append(probabilities[market])
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(markets, probs)
    
    # Adicionar valores nas barras
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                 f'{height:.2%}', ha='center', va='bottom')
    
    plt.title('Probabilidades por Mercado')
    plt.ylabel('Probabilidade')
    plt.ylim(0, 1)
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return plt.gcf()

def create_most_probable_scores_chart(scores, title):
    """
    Cria um gráfico de barras para visualizar os placares mais prováveis
    
    Args:
        scores: Lista de tuplas (placar, probabilidade)
        title: Título do gráfico
        
    Returns:
        Figura matplotlib
    """
    labels = [p[0] for p in scores]
    probs = [p[1] for p in scores]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(labels, probs)
    
    # Adicionar valores nas barras
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                 f'{height:.2%}', ha='center', va='bottom')
    
    plt.title(title)
    plt.ylabel('Probabilidade')
    plt.ylim(0, max(probs) * 1.2)
    plt.tight_layout()
    
    return plt.gcf()

def create_historical_comparison_chart(historical_data, title):
    """
    Cria um gráfico de barras para visualizar os placares históricos mais comuns
    
    Args:
        historical_data: Dicionário com dados históricos
        title: Título do gráfico
        
    Returns:
        Figura matplotlib
    """
    if 'common_scores' not in historical_data or not historical_data['common_scores']:
        # Criar gráfico vazio se não houver dados
        plt.figure(figsize=(10, 6))
        plt.title(f"{title} (Sem dados históricos suficientes)")
        plt.ylabel('Frequência')
        plt.tight_layout()
        return plt.gcf()
    
    scores = [s[0] for s in historical_data['common_scores']]
    counts = [s[1] for s in historical_data['common_scores']]
    
    plt.figure(figsize=(10, 6))
    bars = plt.bar(scores, counts)
    
    # Adicionar valores nas barras
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                 str(int(height)), ha='center', va='bottom')
    
    plt.title(title)
    plt.ylabel('Frequência')
    plt.tight_layout()
    
    return plt.gcf()

def create_expected_value_chart(market_ev):
    """
    Cria um gráfico de barras para visualizar o valor esperado de diferentes mercados
    
    Args:
        market_ev: Dicionário com valor esperado para diferentes mercados
        
    Returns:
        Figura matplotlib
    """
    # Filtrar apenas mercados com valor esperado numérico
    markets = []
    values = []
    
    for market, ev in market_ev.items():
        if isinstance(ev, (int, float)):
            markets.append(market)
            values.append(ev)
    
    if not markets:
        # Criar gráfico vazio se não houver dados
        plt.figure(figsize=(10, 6))
        plt.title("Valor Esperado por Mercado (Sem dados suficientes)")
        plt.ylabel('Valor Esperado')
        plt.tight_layout()
        return plt.gcf()
    
    # Ordenar por valor esperado
    sorted_indices = np.argsort(values)[::-1]
    markets = [markets[i] for i in sorted_indices]
    values = [values[i] for i in sorted_indices]
    
    plt.figure(figsize=(12, 6))
    bars = plt.bar(markets, values)
    
    # Colorir barras com base no valor (verde para >1, vermelho para <1)
    for i, bar in enumerate(bars):
        bar.set_color('green' if values[i] > 1 else 'red')
        
        # Adicionar valores nas barras
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 0.01,
                 f'{height:.2f}', ha='center', va='bottom')
    
    # Adicionar linha horizontal em y=1
    plt.axhline(y=1, color='black', linestyle='--', alpha=0.7)
    
    plt.title('Valor Esperado por Mercado')
    plt.ylabel('Valor Esperado')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    
    return plt.gcf()

def create_team_comparison_chart(stats_data, home_team, away_team):
    """
    Cria um gráfico de radar para comparar estatísticas dos times
    
    Args:
        stats_data: Dicionário com estatísticas dos times
        home_team: Nome do time da casa
        away_team: Nome do time visitante
        
    Returns:
        Figura matplotlib
    """
    # Métricas para comparação
    metrics = [
        ('Gols Marcados', 'gols_marcados_casa', 'gols_marcados_fora'),
        ('Gols Sofridos', 'gols_sofridos_casa', 'gols_sofridos_fora'),
        ('Posse de Bola', 'posse_casa', 'posse_fora'),
        ('Finalizações', 'finalizacoes_casa', 'finalizacoes_fora'),
        ('Precisão Passes', 'precisao_passes_casa', 'precisao_passes_fora'),
        ('Vitórias %', 'vitorias_pct_casa', 'vitorias_pct_fora')
    ]
    
    # Verificar quais métricas estão disponíveis
    available_metrics = []
    home_values = []
    away_values = []
    
    for label, home_key, away_key in metrics:
        if home_key in stats_data and away_key in stats_data:
            available_metrics.append(label)
            home_values.append(stats_data[home_key])
            away_values.append(stats_data[away_key])
    
    if not available_metrics:
        # Criar gráfico vazio se não houver dados suficientes
        plt.figure(figsize=(10, 8))
        plt.title(f"Comparação: {home_team} vs {away_team} (Sem dados suficientes)")
        plt.tight_layout()
        return plt.gcf()
    
    # Número de variáveis
    N = len(available_metrics)
    
    # Ângulos para o gráfico radar
    angles = [n / float(N) * 2 * np.pi for n in range(N)]
    angles += angles[:1]  # Fechar o círculo
    
    # Valores para o gráfico radar
    home_values += home_values[:1]
    away_values += away_values[:1]
    
    # Criar figura
    plt.figure(figsize=(10, 8))
    ax = plt.subplot(111, polar=True)
    
    # Adicionar linhas para cada time
    plt.plot(angles, home_values, 'o-', linewidth=2, label=home_team)
    plt.plot(angles, away_values, 'o-', linewidth=2, label=away_team)
    plt.fill(angles, home_values, alpha=0.25)
    plt.fill(angles, away_values, alpha=0.25)
    
    # Adicionar rótulos
    plt.xticks(angles[:-1], available_metrics)
    
    # Adicionar legenda
    plt.legend(loc='upper right', bbox_to_anchor=(0.1, 0.1))
    
    plt.title(f"Comparação: {home_team} vs {away_team}")
    plt.tight_layout()
    
    return plt.gcf()
