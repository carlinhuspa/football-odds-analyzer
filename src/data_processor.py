import re
import pandas as pd
import numpy as np
from datetime import datetime

def process_odds_text(odds_text):
    """
    Processa texto contendo odds de diferentes mercados.
    
    Args:
        odds_text (str): Texto com odds no formato "mercado, odd" por linha
        
    Returns:
        dict: Dicionário com dados processados das odds
    """
    if not odds_text:
        return {'market_odds': {}}
    
    lines = odds_text.strip().split('\n')
    market_odds = {}
    
    for line in lines:
        if ',' not in line:
            continue
            
        parts = line.split(',', 1)
        if len(parts) != 2:
            continue
            
        market = parts[0].strip()
        try:
            odd = float(parts[1].strip())
            market_odds[market] = odd
        except ValueError:
            continue
    
    # Calcular probabilidades implícitas
    implied_probs = {}
    for market, odd in market_odds.items():
        implied_probs[market] = 1 / odd if odd > 0 else 0
    
    # Calcular overround para mercados 1X2
    overround = 0
    if '1' in implied_probs and 'X' in implied_probs and '2' in implied_probs:
        overround = implied_probs['1'] + implied_probs['X'] + implied_probs['2'] - 1
    
    return {
        'market_odds': market_odds,
        'implied_probs': implied_probs,
        'overround': overround
    }

def process_historical_matches_text(historical_text):
    """
    Processa texto contendo histórico de confrontos entre times.
    
    Args:
        historical_text (str): Texto com histórico de jogos
        
    Returns:
        dict: Dicionário com dados processados do histórico
    """
    if not historical_text:
        return {}
    
    lines = historical_text.strip().split('\n')
    matches = []
    
    # Padrão para extrair data e resultado
    # Formato esperado: "21/12/2024, Time A 5-1 Time B"
    pattern = r'(\d{2}/\d{2}/\d{4}),\s*(.*?)\s+(\d+)-(\d+)\s+(.*)'
    
    for line in lines:
        match = re.match(pattern, line)
        if match:
            date_str, home_team, home_goals, away_goals, away_team = match.groups()
            
            try:
                date = datetime.strptime(date_str, '%d/%m/%Y')
                home_goals = int(home_goals)
                away_goals = int(away_goals)
                
                matches.append({
                    'date': date,
                    'home_team': home_team.strip(),
                    'away_team': away_team.strip(),
                    'home_goals': home_goals,
                    'away_goals': away_goals,
                    'total_goals': home_goals + away_goals,
                    'goal_diff': home_goals - away_goals,
                    'result': 'H' if home_goals > away_goals else ('D' if home_goals == away_goals else 'A'),
                    'both_scored': home_goals > 0 and away_goals > 0,
                    'over_2_5': (home_goals + away_goals) > 2.5
                })
            except (ValueError, TypeError):
                continue
    
    # Se não houver jogos válidos, retornar dicionário vazio
    if not matches:
        return {}
    
    # Calcular estatísticas do histórico
    total_matches = len(matches)
    home_wins = sum(1 for m in matches if m['result'] == 'H')
    draws = sum(1 for m in matches if m['result'] == 'D')
    away_wins = sum(1 for m in matches if m['result'] == 'A')
    
    both_scored = sum(1 for m in matches if m['both_scored'])
    over_2_5 = sum(1 for m in matches if m['over_2_5'])
    
    avg_home_goals = sum(m['home_goals'] for m in matches) / total_matches
    avg_away_goals = sum(m['away_goals'] for m in matches) / total_matches
    avg_total_goals = sum(m['total_goals'] for m in matches) / total_matches
    
    # Extrair resultados para ajuste de probabilidades
    match_results = [(m['home_goals'], m['away_goals']) for m in matches]
    
    # Contar frequência de placares
    score_counts = {}
    for m in matches:
        score = f"{m['home_goals']}-{m['away_goals']}"
        score_counts[score] = score_counts.get(score, 0) + 1
    
    # Ordenar placares por frequência
    common_scores = sorted(score_counts.items(), key=lambda x: x[1], reverse=True)
    
    return {
        'matches': matches,
        'total_matches': total_matches,
        'home_wins_pct': home_wins / total_matches if total_matches > 0 else 0,
        'draws_pct': draws / total_matches if total_matches > 0 else 0,
        'away_wins_pct': away_wins / total_matches if total_matches > 0 else 0,
        'both_scored_pct': both_scored / total_matches if total_matches > 0 else 0,
        'over_2_5_pct': over_2_5 / total_matches if total_matches > 0 else 0,
        'avg_home_goals': avg_home_goals,
        'avg_away_goals': avg_away_goals,
        'avg_total_goals': avg_total_goals,
        'match_results': match_results,
        'common_scores': common_scores[:5]  # Top 5 placares mais comuns
    }

def process_statistics_text(statistics_text):
    """
    Processa texto contendo estatísticas dos times.
    
    Args:
        statistics_text (str): Texto com estatísticas dos times
        
    Returns:
        dict: Dicionário com dados processados das estatísticas
    """
    if not statistics_text:
        return {}
    
    lines = statistics_text.strip().split('\n')
    stats = {}
    
    # Processar cada linha no formato "chave: valor"
    for line in lines:
        if ':' not in line:
            continue
            
        key, value = line.split(':', 1)
        key = key.strip().lower().replace(' ', '_')
        value = value.strip()
        
        # Tentar converter para número se possível
        try:
            if '.' in value:
                stats[key] = float(value)
            else:
                stats[key] = int(value)
        except ValueError:
            stats[key] = value
    
    # Extrair e calcular métricas importantes
    home_team = stats.get('time_da_casa', stats.get('home_team', 'Time da Casa'))
    away_team = stats.get('time_visitante', stats.get('away_team', 'Time Visitante'))
    
    # Gols esperados baseados nas estatísticas
    home_expected_goals = stats.get('gols_marcados_casa', stats.get('home_expected_goals', 1.5))
    away_expected_goals = stats.get('gols_marcados_fora', stats.get('away_expected_goals', 1.0))
    
    # Posições na tabela
    home_position = stats.get('posicao_casa', stats.get('home_position', 10))
    away_position = stats.get('posicao_fora', stats.get('away_position', 10))
    
    # Adicionar informações calculadas
    stats.update({
        'home_team': home_team,
        'away_team': away_team,
        'home_expected_goals': home_expected_goals,
        'away_expected_goals': away_expected_goals,
        'home_position': home_position,
        'away_position': away_position
    })
    
    return stats

def extract_team_names(text):
    """
    Tenta extrair nomes dos times de um texto.
    
    Args:
        text (str): Texto contendo informações sobre os times
        
    Returns:
        tuple: (time_casa, time_fora) ou (None, None) se não encontrados
    """
    # Padrões comuns para identificar confrontos
    patterns = [
        r'([A-Za-z\s]+)\s+vs\s+([A-Za-z\s]+)',
        r'([A-Za-z\s]+)\s+x\s+([A-Za-z\s]+)',
        r'([A-Za-z\s]+)\s+-\s+([A-Za-z\s]+)'
    ]
    
    for pattern in patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            return matches.group(1).strip(), matches.group(2).strip()
    
    return None, None
