import numpy as np
import pandas as pd
from scipy import stats
import math

def calculate_poisson_probabilities(home_expected_goals, away_expected_goals, max_goals=5):
    """
    Calcula a matriz de probabilidades de placares usando distribuição de Poisson
    
    Args:
        home_expected_goals: Média de gols esperados para o time da casa
        away_expected_goals: Média de gols esperados para o time de fora
        max_goals: Número máximo de gols a considerar (default: 5)
        
    Returns:
        DataFrame com as probabilidades de cada placar
    """
    # Criando matriz de probabilidades
    probabilidades = np.zeros((max_goals+1, max_goals+1))
    
    # Calculando probabilidades para cada combinação de gols
    for i in range(max_goals+1):
        for j in range(max_goals+1):
            # Probabilidade de Poisson
            home_prob = stats.poisson.pmf(i, home_expected_goals)
            away_prob = stats.poisson.pmf(j, away_expected_goals)
            
            # Probabilidade conjunta
            probabilidades[i, j] = home_prob * away_prob
    
    # Convertendo para DataFrame para melhor visualização
    df_prob = pd.DataFrame(probabilidades)
    df_prob.columns = [f'Fora {i}' for i in range(max_goals+1)]
    df_prob.index = [f'Casa {i}' for i in range(max_goals+1)]
    
    return df_prob

def adjust_probabilities_with_history(prob_base, historical_results, weight=0.3, max_goals=5):
    """
    Ajusta as probabilidades base considerando o histórico de confrontos diretos
    
    Args:
        prob_base: DataFrame com probabilidades base (Poisson)
        historical_results: Lista de tuplas (gols_casa, gols_fora) dos confrontos históricos
        weight: Peso a ser dado ao histórico (entre 0 e 1)
        max_goals: Número máximo de gols a considerar
        
    Returns:
        DataFrame com probabilidades ajustadas
    """
    # Criando matriz de frequências históricas
    freq_historica = np.zeros((max_goals+1, max_goals+1))
    
    # Contando ocorrências de cada placar no histórico
    for gols_casa, gols_fora in historical_results:
        if gols_casa <= max_goals and gols_fora <= max_goals:
            freq_historica[gols_casa, gols_fora] += 1
        elif gols_casa > max_goals and gols_fora <= max_goals:
            freq_historica[max_goals, gols_fora] += 1
        elif gols_casa <= max_goals and gols_fora > max_goals:
            freq_historica[gols_casa, max_goals] += 1
        else:
            freq_historica[max_goals, max_goals] += 1
    
    # Normalizando para obter probabilidades
    if np.sum(freq_historica) > 0:
        prob_historica = freq_historica / np.sum(freq_historica)
    else:
        prob_historica = np.zeros_like(freq_historica)
    
    # Combinando probabilidades base com históricas
    prob_ajustada = (1 - weight) * prob_base.values + weight * prob_historica
    
    # Normalizando para garantir que a soma seja 1
    prob_ajustada = prob_ajustada / np.sum(prob_ajustada)
    
    # Convertendo para DataFrame
    df_prob_ajustada = pd.DataFrame(prob_ajustada)
    df_prob_ajustada.columns = prob_base.columns
    df_prob_ajustada.index = prob_base.index
    
    return df_prob_ajustada

def calculate_market_probabilities(matriz_prob):
    """
    Calcula probabilidades para diferentes mercados de apostas
    
    Args:
        matriz_prob: DataFrame com probabilidades de placares
        
    Returns:
        Dicionário com probabilidades para diferentes mercados
    """
    max_gols = matriz_prob.shape[0] - 1
    probabilidades = {}
    
    # Resultado (1X2)
    prob_vitoria_casa = 0
    prob_empate = 0
    prob_vitoria_fora = 0
    
    # Over/Under
    prob_over = {i: 0 for i in [0.5, 1.5, 2.5, 3.5, 4.5]}
    
    # Ambas marcam
    prob_ambas_marcam = 0
    
    # Calculando probabilidades para cada mercado
    for i in range(max_gols+1):
        for j in range(max_gols+1):
            prob = matriz_prob.iloc[i, j]
            
            # Resultado
            if i > j:
                prob_vitoria_casa += prob
            elif i == j:
                prob_empate += prob
            else:
                prob_vitoria_fora += prob
            
            # Over/Under
            total_gols = i + j
            for limite in prob_over.keys():
                if total_gols > limite:
                    prob_over[limite] += prob
            
            # Ambas marcam
            if i > 0 and j > 0:
                prob_ambas_marcam += prob
    
    # Organizando resultados
    probabilidades['1'] = prob_vitoria_casa
    probabilidades['X'] = prob_empate
    probabilidades['2'] = prob_vitoria_fora
    
    for limite, prob in prob_over.items():
        probabilidades[f'Over {limite}'] = prob
        probabilidades[f'Under {limite}'] = 1 - prob
    
    probabilidades['Ambas Marcam Sim'] = prob_ambas_marcam
    probabilidades['Ambas Marcam Não'] = 1 - prob_ambas_marcam
    
    return probabilidades

def find_most_probable_scores(matriz_prob, n=5):
    """
    Encontra os n placares mais prováveis
    
    Args:
        matriz_prob: DataFrame com probabilidades de placares
        n: Número de placares a retornar
        
    Returns:
        Lista de tuplas (placar, probabilidade)
    """
    placares = []
    
    for i in range(matriz_prob.shape[0]):
        for j in range(matriz_prob.shape[1]):
            placar = f"{i}-{j}"
            prob = matriz_prob.iloc[i, j]
            placares.append((placar, prob))
    
    # Ordenando por probabilidade (decrescente)
    placares_ordenados = sorted(placares, key=lambda x: x[1], reverse=True)
    
    return placares_ordenados[:n]

def calculate_expected_value(probabilidade, odd):
    """
    Calcula o valor esperado de uma aposta
    
    Args:
        probabilidade: Probabilidade estimada do evento
        odd: Odd decimal oferecida
        
    Returns:
        Valor esperado da aposta (>1 indica valor positivo)
    """
    return probabilidade * odd

def dixon_coles_adjustment(home_expected_goals, away_expected_goals, rho=-0.1):
    """
    Aplica o ajuste de Dixon-Coles à distribuição de Poisson para corrigir
    a dependência entre os gols marcados pelos times
    
    Args:
        home_expected_goals: Média de gols esperados para o time da casa
        away_expected_goals: Média de gols esperados para o time de fora
        rho: Parâmetro de correlação (geralmente entre -0.2 e 0)
        
    Returns:
        Função que calcula a probabilidade ajustada para um placar específico
    """
    def tau(x, y, lambda_x, lambda_y, rho):
        if x == 0 and y == 0:
            return 1 - lambda_x * lambda_y * rho
        elif x == 0 and y == 1:
            return 1 + lambda_x * rho
        elif x == 1 and y == 0:
            return 1 + lambda_y * rho
        elif x == 1 and y == 1:
            return 1 - rho
        else:
            return 1.0
    
    def dc_prob(x, y):
        """Calcula a probabilidade Dixon-Coles para o placar x-y"""
        lambda_x = home_expected_goals
        lambda_y = away_expected_goals
        
        # Probabilidade de Poisson
        p_x = stats.poisson.pmf(x, lambda_x)
        p_y = stats.poisson.pmf(y, lambda_y)
        
        # Ajuste de Dixon-Coles
        adjustment = tau(x, y, lambda_x, lambda_y, rho)
        
        return p_x * p_y * adjustment
    
    return dc_prob

def calculate_dixon_coles_matrix(home_expected_goals, away_expected_goals, max_goals=5, rho=-0.1):
    """
    Calcula a matriz de probabilidades usando o modelo Dixon-Coles
    
    Args:
        home_expected_goals: Média de gols esperados para o time da casa
        away_expected_goals: Média de gols esperados para o time de fora
        max_goals: Número máximo de gols a considerar
        rho: Parâmetro de correlação
        
    Returns:
        DataFrame com as probabilidades de cada placar
    """
    # Obter função de probabilidade Dixon-Coles
    dc_prob = dixon_coles_adjustment(home_expected_goals, away_expected_goals, rho)
    
    # Criar matriz de probabilidades
    probabilidades = np.zeros((max_goals+1, max_goals+1))
    
    # Calcular probabilidades para cada combinação de gols
    for i in range(max_goals+1):
        for j in range(max_goals+1):
            probabilidades[i, j] = dc_prob(i, j)
    
    # Normalizar para garantir que a soma seja 1
    probabilidades = probabilidades / np.sum(probabilidades)
    
    # Converter para DataFrame
    df_prob = pd.DataFrame(probabilidades)
    df_prob.columns = [f'Fora {i}' for i in range(max_goals+1)]
    df_prob.index = [f'Casa {i}' for i in range(max_goals+1)]
    
    return df_prob

def calculate_kelly_criterion(probability, odd, fraction=1.0):
    """
    Calcula a fração ótima de banca a apostar usando o Critério de Kelly
    
    Args:
        probability: Probabilidade estimada do evento
        odd: Odd decimal oferecida
        fraction: Fração do Kelly a usar (1.0 = Kelly completo)
        
    Returns:
        Fração da banca a apostar (0 se não houver valor)
    """
    # Probabilidade implícita da odd
    implied_prob = 1 / odd
    
    # Vantagem (edge)
    edge = (probability * odd - 1) / (odd - 1)
    
    # Se não há vantagem, não apostar
    if edge <= 0:
        return 0
    
    # Cálculo do Kelly
    kelly = edge / (odd - 1)
    
    # Aplicar fração do Kelly (para reduzir variância)
    kelly = kelly * fraction
    
    return kelly
