import re
import pandas as pd
import numpy as np
from datetime import datetime

def extract_football_stats_from_text(text):
    """
    Extrai automaticamente estatísticas de futebol de um texto.
    
    Args:
        text (str): Texto contendo estatísticas de futebol
        
    Returns:
        dict: Dicionário com as informações extraídas
    """
    # Inicializar dicionário para armazenar os dados extraídos
    extracted_data = {
        'teams': {},
        'odds': {},
        'head_to_head': {},
        'team_stats': {},
        'match_predictions': {}
    }
    
    # Extrair nomes dos times
    teams = extract_team_names(text)
    if teams:
        extracted_data['teams']['home'] = teams[0]
        extracted_data['teams']['away'] = teams[1]
    
    # Extrair odds
    extracted_data['odds'] = extract_odds(text)
    
    # Extrair estatísticas de confrontos diretos
    extracted_data['head_to_head'] = extract_head_to_head_stats(text)
    
    # Extrair estatísticas dos times
    extracted_data['team_stats'] = extract_team_stats(text, teams)
    
    # Extrair previsões para a partida
    extracted_data['match_predictions'] = extract_match_predictions(text)
    
    return extracted_data

def extract_team_names(text):
    """
    Extrai os nomes dos times do texto.
    
    Args:
        text (str): Texto contendo estatísticas de futebol
        
    Returns:
        tuple: (time_casa, time_visitante) ou (None, None) se não encontrados
    """
    # Padrões para identificar confrontos
    patterns = [
        r'([A-Za-z\s]+)\s+x\s+([A-Za-z\s]+)',
        r'([A-Za-z\s]+)\s+vs\s+([A-Za-z\s]+)',
        r'([A-Za-z\s]+)\s+-\s+([A-Za-z\s]+)'
    ]
    
    for pattern in patterns:
        matches = re.search(pattern, text, re.IGNORECASE)
        if matches:
            return matches.group(1).strip(), matches.group(2).strip()
    
    # Tentar encontrar em outros formatos comuns
    try:
        # Procurar por padrões como "Time da Casa: Arsenal"
        home_match = re.search(r'Time da Casa:?\s*([A-Za-z\s]+)', text, re.IGNORECASE)
        away_match = re.search(r'Time Visitante:?\s*([A-Za-z\s]+)', text, re.IGNORECASE)
        
        if home_match and away_match:
            return home_match.group(1).strip(), away_match.group(1).strip()
    except:
        pass
    
    return None, None

def extract_odds(text):
    """
    Extrai as odds de diferentes mercados do texto.
    
    Args:
        text (str): Texto contendo estatísticas de futebol
        
    Returns:
        dict: Dicionário com as odds extraídas
    """
    odds = {}
    
    # Extrair odds 1X2
    try:
        # Procurar por padrões como "odds para vitória: 1.56"
        home_win = re.search(r'odds para vitória.*?(\d+[.,]\d+)', text, re.IGNORECASE)
        draw = re.search(r'odds para empate.*?(\d+[.,]\d+)', text, re.IGNORECASE)
        away_win = re.search(r'odds para vitória do visitante.*?(\d+[.,]\d+)', text, re.IGNORECASE)
        
        # Se não encontrar no formato acima, procurar em outros formatos
        if not home_win:
            home_win = re.search(r'vitória.*?(\d+[.,]\d+)', text, re.IGNORECASE)
        if not draw:
            draw = re.search(r'empate.*?(\d+[.,]\d+)', text, re.IGNORECASE)
        if not away_win:
            away_win = re.search(r'vitória do.*?visitante.*?(\d+[.,]\d+)', text, re.IGNORECASE)
        
        # Tentar outro formato comum
        if not (home_win and draw and away_win):
            # Procurar por padrões como "1.56 para vitória"
            home_win = re.search(r'(\d+[.,]\d+).*?vitória', text, re.IGNORECASE)
            draw = re.search(r'(\d+[.,]\d+).*?empate', text, re.IGNORECASE)
            away_win = re.search(r'(\d+[.,]\d+).*?vitória do.*?visitante', text, re.IGNORECASE)
        
        # Tentar outro formato ainda mais genérico
        if not (home_win and draw and away_win):
            # Procurar por padrões como "Arsenal (1.56)"
            odds_pattern = r'(\d+[.,]\d+)'
            all_odds = re.findall(odds_pattern, text)
            if len(all_odds) >= 3:
                # Assumir que as primeiras três odds são 1X2
                home_win_val = float(all_odds[0].replace(',', '.'))
                draw_val = float(all_odds[1].replace(',', '.'))
                away_win_val = float(all_odds[2].replace(',', '.'))
                
                # Verificar se são odds válidas (entre 1.01 e 20.0)
                if 1.01 <= home_win_val <= 20.0 and 1.01 <= draw_val <= 20.0 and 1.01 <= away_win_val <= 20.0:
                    odds['1'] = home_win_val
                    odds['X'] = draw_val
                    odds['2'] = away_win_val
        
        # Extrair valores se encontrados
        if home_win:
            odds['1'] = float(home_win.group(1).replace(',', '.'))
        if draw:
            odds['X'] = float(draw.group(1).replace(',', '.'))
        if away_win:
            odds['2'] = float(away_win.group(1).replace(',', '.'))
    except:
        pass
    
    # Extrair odds Over/Under
    try:
        over_pattern = r'[Oo]ver\s+(\d+[.,]\d+).*?(\d+[.,]\d+)'
        under_pattern = r'[Uu]nder\s+(\d+[.,]\d+).*?(\d+[.,]\d+)'
        
        over_matches = re.findall(over_pattern, text)
        under_matches = re.findall(under_pattern, text)
        
        # Procurar especificamente por over 2.5
        over_25_pattern = r'[Oo]ver\s+2[.,]5.*?(\d+[.,]\d+)'
        over_25_match = re.search(over_25_pattern, text)
        if over_25_match:
            odds['Over 2.5'] = float(over_25_match.group(1).replace(',', '.'))
        
        # Processar todas as correspondências de over
        for match in over_matches:
            try:
                limit = float(match[0].replace(',', '.'))
                odd = float(match[1].replace(',', '.'))
                if 1.01 <= odd <= 20.0:  # Verificar se é uma odd válida
                    odds[f'Over {limit}'] = odd
            except:
                continue
        
        # Processar todas as correspondências de under
        for match in under_matches:
            try:
                limit = float(match[0].replace(',', '.'))
                odd = float(match[1].replace(',', '.'))
                if 1.01 <= odd <= 20.0:  # Verificar se é uma odd válida
                    odds[f'Under {limit}'] = odd
            except:
                continue
    except:
        pass
    
    # Extrair odds BTTS (Ambas Marcam)
    try:
        btts_yes_pattern = r'[Aa]mbas\s+[Mm]arcam\s+[Ss]im.*?(\d+[.,]\d+)'
        btts_no_pattern = r'[Aa]mbas\s+[Mm]arcam\s+[Nn]ão.*?(\d+[.,]\d+)'
        
        # Padrão alternativo
        alt_btts_yes_pattern = r'BTTS.*?[Ss]im.*?(\d+[.,]\d+)'
        alt_btts_no_pattern = r'BTTS.*?[Nn]ão.*?(\d+[.,]\d+)'
        
        btts_yes_match = re.search(btts_yes_pattern, text) or re.search(alt_btts_yes_pattern, text)
        btts_no_match = re.search(btts_no_pattern, text) or re.search(alt_btts_no_pattern, text)
        
        if btts_yes_match:
            odds['Ambas Marcam Sim'] = float(btts_yes_match.group(1).replace(',', '.'))
        if btts_no_match:
            odds['Ambas Marcam Não'] = float(btts_no_match.group(1).replace(',', '.'))
    except:
        pass
    
    return odds

def extract_head_to_head_stats(text):
    """
    Extrai estatísticas de confrontos diretos do texto.
    
    Args:
        text (str): Texto contendo estatísticas de futebol
        
    Returns:
        dict: Dicionário com estatísticas de confrontos diretos
    """
    h2h_stats = {}
    
    # Extrair número total de jogos
    try:
        total_matches_pattern = r'(\d+)\s*[Jj]ogos'
        total_matches_match = re.search(total_matches_pattern, text)
        if total_matches_match:
            h2h_stats['total_matches'] = int(total_matches_match.group(1))
    except:
        pass
    
    # Extrair percentuais de vitórias/empates/derrotas
    try:
        # Procurar por padrões como "63% Vitórias"
        home_wins_pattern = r'(\d+)%.*?[Vv]itórias'
        draws_pattern = r'(\d+)%.*?[Ee]mpates'
        away_wins_pattern = r'(\d+)%.*?[Dd]errotas'
        
        home_wins_match = re.search(home_wins_pattern, text)
        draws_match = re.search(draws_pattern, text)
        away_wins_match = re.search(away_wins_pattern, text)
        
        if home_wins_match:
            h2h_stats['home_wins_pct'] = int(home_wins_match.group(1)) / 100
        if draws_match:
            h2h_stats['draws_pct'] = int(draws_match.group(1)) / 100
        if away_wins_match:
            h2h_stats['away_wins_pct'] = int(away_wins_match.group(1)) / 100
    except:
        pass
    
    # Extrair estatísticas de gols
    try:
        # Procurar por padrões como "92% Mais de 1.5"
        over_15_pattern = r'(\d+)%\s*[Mm]ais\s*de\s*1[.,]5'
        over_25_pattern = r'(\d+)%\s*[Mm]ais\s*de\s*2[.,]5'
        over_35_pattern = r'(\d+)%\s*[Mm]ais\s*de\s*3[.,]5'
        btts_pattern = r'(\d+)%\s*AM'  # AM = Ambas Marcam
        
        over_15_match = re.search(over_15_pattern, text)
        over_25_match = re.search(over_25_pattern, text)
        over_35_match = re.search(over_35_pattern, text)
        btts_match = re.search(btts_pattern, text)
        
        if over_15_match:
            h2h_stats['over_15_pct'] = int(over_15_match.group(1)) / 100
        if over_25_match:
            h2h_stats['over_25_pct'] = int(over_25_match.group(1)) / 100
        if over_35_match:
            h2h_stats['over_35_pct'] = int(over_35_match.group(1)) / 100
        if btts_match:
            h2h_stats['btts_pct'] = int(btts_match.group(1)) / 100
    except:
        pass
    
    # Extrair resultados recentes
    try:
        # Procurar por padrões como "21/12 2024 Crystal Palace 1 Arsenal 5"
        recent_matches_pattern = r'(\d{2}/\d{2}\s+\d{4})\s+([A-Za-z\s]+)\s*(\d+)\s*([A-Za-z\s]+)\s*(\d+)'
        recent_matches = re.findall(recent_matches_pattern, text)
        
        if recent_matches:
            h2h_stats['recent_matches'] = []
            for match in recent_matches[:5]:  # Pegar os 5 mais recentes
                try:
                    date = match[0]
                    team1 = match[1].strip()
                    score1 = int(match[2])
                    team2 = match[3].strip()
                    score2 = int(match[4])
                    
                    h2h_stats['recent_matches'].append({
                        'date': date,
                        'home_team': team1,
                        'away_team': team2,
                        'home_goals': score1,
                        'away_goals': score2
                    })
                except:
                    continue
    except:
        pass
    
    return h2h_stats

def extract_team_stats(text, teams):
    """
    Extrai estatísticas dos times do texto.
    
    Args:
        text (str): Texto contendo estatísticas de futebol
        teams (tuple): Tupla contendo (time_casa, time_visitante)
        
    Returns:
        dict: Dicionário com estatísticas dos times
    """
    team_stats = {
        'home': {},
        'away': {}
    }
    
    if not teams or not teams[0] or not teams[1]:
        return team_stats
    
    home_team, away_team = teams
    
    # Extrair pontos por jogo
    try:
        # Procurar por padrões como "2.19 Pontos por jogo"
        home_ppg_pattern = r'(\d+[.,]\d+).*?[Pp]ontos\s*por\s*jogo.*?' + re.escape(home_team)
        away_ppg_pattern = r'(\d+[.,]\d+).*?[Pp]ontos\s*por\s*jogo.*?' + re.escape(away_team)
        
        # Padrões alternativos
        alt_home_ppg_pattern = re.escape(home_team) + r'.*?(\d+[.,]\d+).*?[Pp]PJ'
        alt_away_ppg_pattern = re.escape(away_team) + r'.*?(\d+[.,]\d+).*?[Pp]PJ'
        
        home_ppg_match = re.search(home_ppg_pattern, text) or re.search(alt_home_ppg_pattern, text)
        away_ppg_match = re.search(away_ppg_pattern, text) or re.search(alt_away_ppg_pattern, text)
        
        if home_ppg_match:
            team_stats['home']['points_per_game'] = float(home_ppg_match.group(1).replace(',', '.'))
        if away_ppg_match:
            team_stats['away']['points_per_game'] = float(away_ppg_match.group(1).replace(',', '.'))
    except:
        pass
    
    # Extrair percentuais de vitórias
    try:
        # Procurar por padrões como "63% Vitória"
        home_wins_pattern = r'(\d+)%.*?[Vv]itória.*?' + re.escape(home_team)
        away_wins_pattern = r'(\d+)%.*?[Vv]itória.*?' + re.escape(away_team)
        
        # Padrões alternativos
        alt_home_wins_pattern = re.escape(home_team) + r'.*?[Vv]itória.*?(\d+)%'
        alt_away_wins_pattern = re.escape(away_team) + r'.*?[Vv]itória.*?(\d+)%'
        
        home_wins_match = re.search(home_wins_pattern, text) or re.search(alt_home_wins_pattern, text)
        away_wins_match = re.search(away_wins_pattern, text) or re.search(alt_away_wins_pattern, text)
        
        if home_wins_match:
            team_stats['home']['win_percentage'] = int(home_wins_match.group(1)) / 100
        if away_wins_match:
            team_stats['away']['win_percentage'] = int(away_wins_match.group(1)) / 100
    except:
        pass
    
    # Extrair gols marcados/sofridos
    try:
        # Procurar por padrões como "1.94 Gols / Jogo"
        home_scored_pattern = r'(\d+[.,]\d+).*?[Gg]ols\s*[Mm]arcados.*?' + re.escape(home_team)
        home_conceded_pattern = r'(\d+[.,]\d+).*?[Gg]ols\s*[Ss]ofridos.*?' + re.escape(home_team)
        away_scored_pattern = r'(\d+[.,]\d+).*?[Gg]ols\s*[Mm]arcados.*?' + re.escape(away_team)
        away_conceded_pattern = r'(\d+[.,]\d+).*?[Gg]ols\s*[Ss]ofridos.*?' + re.escape(away_team)
        
        # Padrões alternativos
        alt_home_scored_pattern = re.escape(home_team) + r'.*?(\d+[.,]\d+).*?[Gg]ols\s*\/\s*[Jj]ogo'
        alt_away_scored_pattern = re.escape(away_team) + r'.*?(\d+[.,]\d+).*?[Gg]ols\s*\/\s*[Jj]ogo'
        
        home_scored_match = re.search(home_scored_pattern, text) or re.search(alt_home_scored_pattern, text)
        home_conceded_match = re.search(home_conceded_pattern, text)
        away_scored_match = re.search(away_scored_pattern, text) or re.search(alt_away_scored_pattern, text)
        away_conceded_match = re.search(away_conceded_pattern, text)
        
        if home_scored_match:
            team_stats['home']['goals_scored_per_game'] = float(home_scored_match.group(1).replace(',', '.'))
        if home_conceded_match:
            team_stats['home']['goals_conceded_per_game'] = float(home_conceded_match.group(1).replace(',', '.'))
        if away_scored_match:
            team_stats['away']['goals_scored_per_game'] = float(away_scored_match.group(1).replace(',', '.'))
        if away_conceded_match:
            team_stats['away']['goals_conceded_per_game'] = float(away_conceded_match.group(1).replace(',', '.'))
    except:
        pass
    
    # Extrair clean sheets
    try:
        # Procurar por padrões como "38% Clean Sheets"
        home_cs_pattern = r'(\d+)%.*?[Cc]lean\s*[Ss]heets.*?' + re.escape(home_team)
        away_cs_pattern = r'(\d+)%.*?[Cc]lean\s*[Ss]heets.*?' + re.escape(away_team)
        
        home_cs_match = re.search(home_cs_pattern, text)
        away_cs_match = re.search(away_cs_pattern, text)
        
        if home_cs_match:
            team_stats['home']['clean_sheets_percentage'] = int(home_cs_match.group(1)) / 100
        if away_cs_match:
            team_stats['away']['clean_sheets_percentage'] = int(away_cs_match.group(1)) / 100
    except:
        pass
    
    # Extrair xG (Expected Goals)
    try:
        # Procurar por padrões como "xG: 1.94"
        home_xg_pattern = r'xG.*?(\d+[.,]\d+).*?' + re.escape(home_team)
        away_xg_pattern = r'xG.*?(\d+[.,]\d+).*?' + re.escape(away_team)
        
        home_xg_match = re.search(home_xg_pattern, text)
        away_xg_match = re.search(away_xg_pattern, text)
        
        if home_xg_match:
            team_stats['home']['expected_goals'] = float(home_xg_match.group(1).replace(',',
(Content truncated due to size limit. Use line ranges to read in chunks)
