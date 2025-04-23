# Football Odds Analyzer

Um aplicativo completo para análise de odds e estatísticas de futebol, que combina modelos matemáticos avançados com interpretação humanizada dos resultados.

## Funcionalidades

- Processamento de odds, histórico de jogos e estatísticas de times
- Cálculo de probabilidades de placares usando modelos Poisson e Dixon-Coles
- Ajuste de probabilidades com base no histórico de confrontos
- Identificação de apostas com valor positivo
- Recomendações de apostas usando o Critério de Kelly
- Visualizações detalhadas (matriz de probabilidades, placares prováveis, etc.)
- Relatório técnico completo
- Interpretação humanizada dos resultados

## Requisitos

- Python 3.6+
- Bibliotecas listadas em `requirements.txt`

## Instalação

```bash
# Clonar o repositório
git clone https://github.com/seu-usuario/football-odds-analyzer.git
cd football-odds-analyzer

# Instalar dependências
pip install -r requirements.txt
```

## Execução

```bash
# Método 1: Usando o script de execução
./run.sh

# Método 2: Executando diretamente com Streamlit
streamlit run src/app.py
```

## Como usar

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

## Opções Avançadas

- **Modelo Dixon-Coles**: Ajusta a correlação entre gols dos times, geralmente mais preciso que o modelo Poisson padrão
- **Peso do histórico**: Controla quanto o histórico de confrontos influencia as probabilidades
- **Máximo de gols**: Define o número máximo de gols a considerar no modelo
- **Fração de Kelly**: Ajusta as recomendações de apostas (valores menores são mais conservadores)

## Estrutura do Projeto

```
football_odds_analyzer/
├── requirements.txt      # Dependências do projeto
├── run.sh                # Script para execução rápida
└── src/
    ├── app.py            # Aplicativo Streamlit principal
    ├── data_processor.py # Processamento de dados de entrada
    ├── analyzer.py       # Modelos matemáticos e estatísticos
    ├── visualizer.py     # Funções de visualização
    └── report_generator.py # Geração de relatórios
```

## Modelos Matemáticos

O aplicativo utiliza dois modelos principais:

1. **Distribuição de Poisson**: Modelo básico que assume independência entre os gols marcados pelos times
2. **Modelo Dixon-Coles**: Extensão do modelo de Poisson que ajusta a correlação entre os gols dos times

Ambos os modelos são calibrados com dados históricos para melhorar a precisão das previsões.

## Limitações

- A precisão das previsões depende da qualidade dos dados de entrada
- O futebol tem um alto grau de imprevisibilidade
- As odds de mercado já incorporam muita informação, tornando difícil encontrar valor consistente

## Aviso Legal

Este aplicativo foi desenvolvido para fins educacionais e de análise. As previsões são baseadas em modelos estatísticos e não garantem sucesso em apostas. Aposte com responsabilidade.

## Contribuições

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou enviar pull requests.

## Licença

MIT
