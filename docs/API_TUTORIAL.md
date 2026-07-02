# Tutorial Prático de Consumo da API: Patent AI Lab

Este tutorial ensina como consumir a API do **Patent AI Lab** passo a passo. Vamos explorar como coletar dados brutos, realizar cálculos analíticos em memória usando **Pandas** e utilizar os endpoints de inteligência preditiva.

---

## 1. Configuração e Autenticação

A API possui duas categorias de rotas:
1. **Rotas Públicas (Sem autenticação)**: Leitura de patentes, estatísticas e indicadores.

2. **Rotas Protegidas (Exigem chave de API)**: Alterações e consultas ao dicionário de termos tecnológico.

As rotas protegidas exigem o envio da chave no cabeçalho HTTP `X-API-Key`.

### Setup Inicial em Python
Para executar este tutorial, certifique-se de que possui as bibliotecas `requests` e `pandas` instaladas:
```bash
pip install requests pandas numpy scipy
```

Defina as credenciais de acesso no seu script:
```python
import os
import requests
import pandas as pd
import numpy as np

API_BASE_URL = "https://apipatent.onrender.com"
API_KEY = "chave" # Substitua pela sua chave configurada no .env da API

# Headers padrão para requisições autenticadas
HEADERS = {
    "X-API-Key": API_KEY,
    "Content-Type": "application/json"
}
```

---

## 2. Tutorial Prático 1: Análise Local com Dados Brutos (Camada Genérica)

A melhor prática para evitar lentidão e excesso de requisições ao servidor é baixar o conjunto de dados uma única vez na inicialização e efetuar cálculos em memória com o **Pandas**.

### Passo 1: Baixando os dados brutos
Vamos baixar a lista de patentes com embeddings e a lista de termos/co-ocorrências.

```python
# 1. Obter patentes com embeddings
r_patents = requests.get(f"{API_BASE_URL}/patents")
r_patents.raise_for_status()
df_patents = pd.DataFrame(r_patents.json())

# Converter a coluna embedding de lista de floats para numpy array
if not df_patents.empty and "embedding" in df_patents.columns:
    df_patents["embedding"] = df_patents["embedding"].apply(
        lambda x: np.array(x, dtype=np.float32) if x else None
    )

print(f"Carregadas {len(df_patents)} patentes com embeddings.")

# 2. Obter mapeamento de termos e patentes
r_terms = requests.get(f"{API_BASE_URL}/terms/associations")
r_terms.raise_for_status()
df_terms = pd.DataFrame(r_terms.json())

print(f"Carregadas {len(df_terms)} associações de termos.")
```

### Passo 2: Calculando Indicadores com Pandas (Sem tocar no Banco)

#### Exemplo A: Calcular a Taxa de Crescimento (Growth %) de um Termo
Queremos saber a variação de registros entre o último mês e o penúltimo mês da série temporal de um determinado termo.

```python
def calcular_crescimento_termo(termo: str, df: pd.DataFrame) -> float:
    # 1. Filtrar pelo termo desejado
    df_filtrado = df[df["term"] == termo]
    if df_filtrado.empty:
        return 0.0
        
    # 2. Agrupar por ano_mes e contar ocorrências
    historico = (df_filtrado
                 .groupby("year_month").size()
                 .reset_index(name="count")
                 .sort_values("year_month"))
                 
    if len(historico) < 2:
        return 0.0
        
    # 3. Pegar os dois últimos registros da série
    ultimo_contagem = historico.iloc[-1]["count"]
    penultimo_contagem = historico.iloc[-2]["count"]
    
    if penultimo_contagem == 0:
        return 0.0
        
    # 4. Calcular variação percentual
    crescimento = ((ultimo_contagem - penultimo_contagem) / penultimo_contagem) * 100
    return float(crescimento)

growth_ai = calcular_crescimento_termo("electric motor", df_terms)
print(f"Taxa de crescimento do termo 'electric motor': {growth_ai:.2f}%")
```

#### Exemplo B: Calcular Correlação de Pearson entre dois Termos
Queremos saber se a evolução do termo A está correlacionada com a evolução temporal do termo B.

```python
from scipy.stats import pearsonr

def calcular_correlacao_termos(termo_a: str, termo_b: str, df: pd.DataFrame):
    # 1. Montar a matriz temporal de termos (frequência de cada termo por mês)
    matriz_temporal = df.groupby(["year_month", "term"]).size().unstack(fill_value=0)
    
    if termo_a not in matriz_temporal.columns or termo_b not in matriz_temporal.columns:
        return None, None
        
    # 2. Coletar os vetores de frequência temporal
    vetor_a = matriz_temporal[termo_a].values
    vetor_b = matriz_temporal[termo_b].values
    
    if vetor_a.std() == 0 or vetor_b.std() == 0 or len(vetor_a) < 3:
        return None, None
        
    # 3. Calcular coeficiente r e p-value
    r, p = pearsonr(vetor_a, vetor_b)
    return r, p

r, p = calcular_correlacao_termos("lidar", "autonomous", df_terms)
if r is not None:
    print(f"Correlação de Pearson entre 'lidar' e 'autonomous': r = {r:+.3f} (p-value: {p:.5f})")
else:
    print("Dados insuficientes para calcular correlação.")
```

---

## 3. Tutorial Prático 2: Consumindo Indicadores Prontos (Camada Otimizada)

Caso o seu cliente seja leve e não precise processar dados brutos, você pode usar cálculos pré-processados da API.

### Buscar estatísticas rápidas
```python
r = requests.get(f"{API_BASE_URL}/stats")
stats = r.json()
print("Estatísticas Gerais:")
print(f"- Total de Patentes: {stats['total_patents']}")
print(f"- Termos no Dicionário: {stats['total_terms']}")
print(f"- Período Histórico: {stats['min_date']} até {stats['max_date']}")
```

### Consultar Previsões de Séries Temporais (IA)
Busca a previsão estatística de registros para os próximos meses de um termo tecnológico.

```python
termo = "battery"
r = requests.get(f"{API_BASE_URL}/predictions/{termo}")
if r.status_code == 200:
    data = r.json()
    print(f"\nPrevisões de IA para '{termo}':")
    # Mostrar os primeiros 3 meses previstos
    for ponto in data["predictions"][:3]:
        print(f"  Mês: {ponto['target_year_month']} | Previsto: {ponto['predicted_count']:.1f} (Pessimista: {ponto['pessimistic_count']:.1f} - Otimista: {ponto['optimistic_count']:.1f})")
else:
    print(f"Sem previsões prontas para '{termo}'.")
```

### Consultar Indicadores de um Termo
Busca crescimento, densidade, fusão semântica e pontuação futura de um termo específico.

```python
r = requests.get(f"{API_BASE_URL}/terms/battery/indicators")
if r.status_code == 200:
    ind = r.json()
    print(f"\nIndicadores de 'battery':")
    print(f"  - Futuro Score: {ind['future_score']}")
    print(f"  - Crescimento (Growth): {ind['growth']:.1f}%")
    print(f"  - Densidade de Patentes: {ind['density']}")
    print(f"  - Fusão Semântica (Co-termos): {ind['fusion']}")
```


