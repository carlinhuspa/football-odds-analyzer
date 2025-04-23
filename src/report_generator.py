def generate_technical_report(home_team, away_team, home_expected_goals, away_expected_goals, 
                       prob_matrix, market_probs, top_scores, market_odds, market_ev):
    """
    Gera um relatório técnico detalhado com os resultados da análise
    
    Args:
        home_team: Nome do time da casa
        away_team: Nome do time visitante
        home_expected_goals: Gols esperados do time da casa
        away_expected_goals: Gols esperados do time visitante
        prob_matrix: Matriz de probabilidades de placares
        market_probs: Probabilidades por mercado
        top_scores: Placares mais prováveis
        market_odds: Odds de mercado
        market_ev: Valor esperado por mercado
        
    Returns:
        String com o relatório técnico formatado em Markdown
    """
    report = f"""# Relatório Técnico: {home_team} vs {away_team}

## 1. Parâmetros do Modelo

- Gols esperados do {home_team} (casa): {home_expected_goals:.2f}
- Gols esperados do {away_team} (fora): {away_expected_goals:.2f}

## 2. Probabilidades por Mercado

| Mercado | Probabilidade | Odd | Valor Esperado |
|---------|---------------|-----|----------------|
"""
    
    # Adicionar probabilidades de mercados principais
    main_markets = ['1', 'X', '2', 'Over 2.5', 'Under 2.5', 'Ambas Marcam Sim', 'Ambas Marcam Não']
    for market in main_markets:
        if market in market_probs:
            prob = market_probs[market]
            odd = market_odds.get(market, "-")
            ev = market_ev.get(market, "-")
            if isinstance(ev, (int, float)):
                ev_str = f"{ev:.2f}"
            else:
                ev_str = ev
            report += f"| {market} | {prob:.2%} | {odd} | {ev_str} |\n"
    
    # Adicionar outros mercados relevantes
    other_markets = [m for m in market_probs.keys() if m not in main_markets]
    for market in other_markets:
        prob = market_probs[market]
        odd = market_odds.get(market, "-")
        ev = market_ev.get(market, "-")
        if isinstance(ev, (int, float)):
            ev_str = f"{ev:.2f}"
        else:
            ev_str = ev
        report += f"| {market} | {prob:.2%} | {odd} | {ev_str} |\n"
    
    # Adicionar placares mais prováveis
    report += f"""
## 3. Placares Mais Prováveis

| Placar | Probabilidade |
|--------|---------------|
"""
    
    for placar, prob in top_scores:
        report += f"| {placar} | {prob:.2%} |\n"
    
    # Adicionar análise de valor
    report += f"""
## 4. Análise de Valor nas Apostas

Apostas com valor positivo (Valor Esperado > 1):

"""
    
    value_bets = {k: v for k, v in market_ev.items() if isinstance(v, (int, float)) and v > 1}
    
    if value_bets:
        for market, ev in sorted(value_bets.items(), key=lambda x: x[1], reverse=True):
            prob = market_probs[market]
            odd = market_odds.get(market, "-")
            report += f"- **{market}**: Probabilidade {prob:.2%}, Odd {odd}, Valor Esperado {ev:.2f}\n"
    else:
        report += "Nenhuma aposta com valor positivo identificada.\n"
    
    # Adicionar conclusões
    report += f"""
## 5. Conclusões

1. O resultado mais provável é **{get_most_probable_result(market_probs)}** com {get_result_probability(market_probs):.2%} de probabilidade.

2. O placar mais provável é **{top_scores[0][0]}** com {top_scores[0][1]:.2%} de probabilidade.

3. A probabilidade de o jogo ter mais de 2.5 gols é de {market_probs.get('Over 2.5', 0):.2%}.

4. A probabilidade de ambas as equipes marcarem é de {market_probs.get('Ambas Marcam Sim', 0):.2%}.
"""
    
    if value_bets:
        best_bet = max(value_bets.items(), key=lambda x: x[1])
        report += f"\n5. A aposta com melhor valor é **{best_bet[0]}** com valor esperado de {best_bet[1]:.2f}.\n"
    
    return report

def generate_humanized_interpretation(home_team, away_team, stats_data, historical_data, 
                                     market_probs, top_scores, market_ev):
    """
    Gera uma interpretação humanizada dos resultados da análise
    
    Args:
        home_team: Nome do time da casa
        away_team: Nome do time visitante
        stats_data: Dados estatísticos dos times
        historical_data: Dados históricos de confrontos
        market_probs: Probabilidades por mercado
        top_scores: Placares mais prováveis
        market_ev: Valor esperado por mercado
        
    Returns:
        String com a interpretação humanizada formatada em Markdown
    """
    # Obter resultado mais provável
    most_probable_result = get_most_probable_result(market_probs)
    result_probability = get_result_probability(market_probs)
    
    # Obter placares mais prováveis
    most_probable_score = top_scores[0][0]
    score_probability = top_scores[0][1]
    
    # Verificar se ambas marcam é provável
    both_score_prob = market_probs.get('Ambas Marcam Sim', 0)
    both_score_likely = both_score_prob > 0.5
    
    # Verificar se over 2.5 é provável
    over_prob = market_probs.get('Over 2.5', 0)
    over_likely = over_prob > 0.5
    
    # Obter apostas com valor
    value_bets = {k: v for k, v in market_ev.items() if isinstance(v, (int, float)) and v > 1}
    
    # Construir interpretação
    interpretation = f"""# Interpretação Humanizada: {home_team} vs {away_team}

## Análise do Confronto

Analisando os dados estatísticos e históricos do confronto entre **{home_team}** e **{away_team}**, chegamos a algumas conclusões importantes que vão além dos números brutos.

### O Que os Dados Nos Dizem

"""
    
    # Adicionar análise do resultado mais provável
    if most_probable_result == "Vitória do time da casa":
        interpretation += f"O **{home_team}** aparece como favorito claro neste confronto, com {result_probability:.0%} de probabilidade de vitória. "
        
        if stats_data.get('home_position', 0) < stats_data.get('away_position', 20):
            interpretation += f"Isso é esperado considerando que o {home_team} está melhor posicionado na tabela "
            interpretation += f"({stats_data.get('home_position', 0)}º vs {stats_data.get('away_position', 0)}º). "
        
        if stats_data.get('vitorias_pct_casa', 0) > 0.5:
            interpretation += f"Além disso, o {home_team} tem um bom aproveitamento em casa, vencendo {stats_data.get('vitorias_pct_casa', 0):.0%} dos seus jogos como mandante. "
    
    elif most_probable_result == "Empate":
        interpretation += f"Este confronto tem uma tendência significativa para **empate**, com {result_probability:.0%} de probabilidade. "
        
        if abs(stats_data.get('home_position', 10) - stats_data.get('away_position', 10)) < 3:
            interpretation += f"Os times estão próximos na tabela, o que pode explicar o equilíbrio esperado. "
        
        if historical_data.get('draws_pct', 0) > 0.3:
            interpretation += f"Historicamente, {historical_data.get('draws_pct', 0):.0%} dos confrontos entre estes times terminaram empatados. "
    
    else:  # Vitória visitante
        interpretation += f"Surpreendentemente, o **{away_team}** aparece com boa chance de vitória fora de casa ({result_probability:.0%}). "
        
        if stats_data.get('away_position', 20) < stats_data.get('home_position', 0):
            interpretation += f"Isso pode ser explicado pela melhor posição do {away_team} na tabela "
            interpretation += f"({stats_data.get('away_position', 0)}º vs {stats_data.get('home_position', 0)}º). "
        
        if stats_data.get('vitorias_pct_fora', 0) > 0.4:
            interpretation += f"O {away_team} tem se mostrado forte como visitante, vencendo {stats_data.get('vitorias_pct_fora', 0):.0%} dos seus jogos fora de casa. "
    
    interpretation += "\n\n"
    
    # Adicionar análise sobre gols
    if over_likely:
        interpretation += f"Há uma boa probabilidade ({over_prob:.0%}) de vermos **mais de 2.5 gols** nesta partida. "
        
        if both_score_likely:
            interpretation += f"Ambas as equipes têm {both_score_prob:.0%} de chance de marcar, o que sugere um jogo aberto e com oportunidades para os dois lados. "
        
        if stats_data.get('gols_marcados_casa', 0) > 1.5 and stats_data.get('gols_marcados_fora', 0) > 1:
            interpretation += f"O {home_team} marca em média {stats_data.get('gols_marcados_casa', 0):.1f} gols em casa, enquanto o {away_team} marca {stats_data.get('gols_marcados_fora', 0):.1f} gols fora, o que explica a expectativa de um jogo com muitos gols. "
    else:
        interpretation += f"Este confronto tende a ter **poucos gols**, com {(1-over_prob):.0%} de probabilidade de menos de 2.5 gols no total. "
        
        if not both_score_likely:
            interpretation += f"Há {(1-both_score_prob):.0%} de chance de pelo menos um dos times não marcar. "
        
        if stats_data.get('gols_sofridos_casa', 0) < 1 or stats_data.get('gols_sofridos_fora', 0) < 1:
            interpretation += f"As defesas têm se mostrado sólidas, com o {home_team} sofrendo apenas {stats_data.get('gols_sofridos_casa', 0):.1f} gols por jogo em casa e o {away_team} sofrendo {stats_data.get('gols_sofridos_fora', 0):.1f} gols por jogo fora. "
    
    interpretation += "\n\n"
    
    # Adicionar análise sobre placares prováveis
    interpretation += f"### Sobre os Placares Mais Prováveis\n\n"
    
    interpretation += f"O placar mais provável é **{most_probable_score}** com {score_probability:.1%} de probabilidade. "
    
    # Verificar se há contradição entre placar mais provável e ambas marcarem
    if both_score_likely and (most_probable_score.endswith("-0") or most_probable_score.startswith("0-")):
        interpretation += f"\n\n**Importante notar:** Embora o placar mais provável individualmente seja {most_probable_score}, a probabilidade de ambas as equipes marcarem é de {both_score_prob:.0%}. Isso pode parecer contraditório, mas faz sentido matematicamente porque:\n\n"
        interpretation += "1. O placar mais provável é apenas um entre muitas possibilidades\n"
        interpretation += "2. Quando somamos todos os placares onde ambas equipes marcam (como 1-1, 2-1, 1-2, 2-2, etc.), eles totalizam uma probabilidade maior\n"
        interpretation += f"3. Placares como {most_probable_score} têm probabilidade individual maior, mas coletivamente são menos prováveis que o conjunto de placares onde ambas marcam\n\n"
        
        # Sugerir placares alternativos onde ambas marcam
        both_score_placares = [p for p in top_scores if "0" not in p[0].split("-")]
        if both_score_placares:
            interpretation += f"Considerando a alta probabilidade de ambas marcarem, placares como **{both_score_placares[0][0]}** ({both_score_placares[0][1]:.1%}) também merecem atenção.\n\n"
    
    # Adicionar análise de valor nas apostas
    interpretation += f"### Oportunidades de Valor\n\n"
    
    if value_bets:
        interpretation += "Comparando nossas probabilidades calculadas com as odds oferecidas, identificamos algumas apostas com valor positivo:\n\n"
        
        for market, ev in sorted(value_bets.items(), key=lambda x: x[1], reverse=True)[:3]:
            prob = market_probs[market]
            odd = market_ev.get(market, "-")
            interpretation += f"- **{market}** (odd {odd}): Nossa análise indica {prob:.0%} de probabilidade, resultando em um valor esperado de {ev:.2f}\n"
        
        best_bet = max(value_bets.items(), key=lambda x: x[1])
        interpretation += f"\nA aposta com melhor relação risco/retorno é **{best_bet[0]}**.\n\n"
    else:
        interpretation += "Nossa análise não identificou apostas com valor positivo significativo neste jogo. Isso sugere que as odds estão bem alinhadas com as probabilidades reais, ou ligeiramente favoráveis à casa de apostas.\n\n"
    
    # Adicionar considerações finais
    interpretation += f"### Considerações Finais\n\n"
    
    interpretation += "É importante lembrar que o futebol é um esporte com alto grau de imprevisibilidade. Mesmo o placar mais provável tem menos de 10% de chance de ocorrer, o que demonstra a dificuldade de prever resultados exatos.\n\n"
    
    interpretation += "Nossa análise combina modelos matemáticos (distribuição de Poisson ajustada) com dados históricos e estatísticas atuais dos times, mas fatores como lesões de última hora, condições climáticas e dinâmicas de jogo podem alterar significativamente o resultado.\n\n"
    
    interpretation += "Use estas informações como um guia, mas sempre considere o contexto completo do jogo e aposte com responsabilidade."
    
    return interpretation

def get_most_probable_result(market_probs):
    """
    Determina o resultado mais provável com base nas probabilidades de mercado
    
    Args:
        market_probs: Dicionário com probabilidades por mercado
        
    Returns:
        String descrevendo o resultado mais provável
    """
    if '1' not in market_probs or 'X' not in market_probs or '2' not in market_probs:
        return "Resultado desconhecido"
    
    home_win_prob = market_probs['1']
    draw_prob = market_probs['X']
    away_win_prob = market_probs['2']
    
    if home_win_prob > draw_prob and home_win_prob > away_win_prob:
        return "Vitória do time da casa"
    elif draw_prob > home_win_prob and draw_prob > away_win_prob:
        return "Empate"
    else:
        return "Vitória do time visitante"

def get_result_probability(market_probs):
    """
    Retorna a probabilidade do resultado mais provável
    
    Args:
        market_probs: Dicionário com probabilidades por mercado
        
    Returns:
        Probabilidade do resultado mais provável
    """
    if '1' not in market_probs or 'X' not in market_probs or '2' not in market_probs:
        return 0
    
    home_win_prob = market_probs['1']
    draw_prob = market_probs['X']
    away_win_prob = market_probs['2']
    
    return max(home_win_prob, draw_prob, away_win_prob)
