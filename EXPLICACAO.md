# Explicação: Clusterização K-means de Dados de Sensores

## 📋 Objetivo
Realizar clusterização K-means em dados de acelerômetro e giroscópio, agrupando conjuntos de pontos temporais em 2 clusters.

## 🔍 O que foi feito?

### 1. **Entendimento dos Dados**
- **Acelerômetro**: Arquivos CSV com colunas `timestamp, x, y, z` (medições de aceleração nos 3 eixos)
- **Giroscópio**: Arquivos TXT com colunas `timestamp, gx, gy, gz` (medições de rotação nos 3 eixos)
- Cada pessoa tem um par de arquivos (acelerômetro + giroscópio)

### 2. **Conceito Principal: Conjuntos de Pontos**
**Importante**: Cada "ponto do cluster" NÃO é uma única leitura do sensor, mas sim um **conjunto de múltiplas leituras**.

#### Por que isso?
- Taxa de amostragem de 0.5s significa que queremos agrupar 2 leituras consecutivas
- Cada conjunto representa um pequeno intervalo temporal de comportamento
- **Exemplo**: Se temos 1000 leituras, criamos 500 conjuntos (2 leituras por conjunto)

#### Estrutura de um conjunto:
```
Conjunto 1 = [
    Leitura 1: [accel_x1, accel_y1, accel_z1, gyro_x1, gyro_y1, gyro_z1],
    Leitura 2: [accel_x2, accel_y2, accel_z2, gyro_x2, gyro_y2, gyro_z2]
]
→ Isso vira um vetor de 12 features
```

### 3. **Pipeline de Processamento**

#### Etapa 1: Carregamento dos Dados
```python
df_accel = pd.read_csv('acelerometro_X.csv')  # Acelerômetro
df_gyro = pd.read_csv('giroscopio_X.txt')      # Giroscópio
```

#### Etapa 2: Sincronização Temporal
- Problema: Os sensores podem ter timestamps ligeiramente diferentes
- Solução: Usar `merge_asof` para combinar leituras com timestamps próximos
- Tolerância: 0.1 segundo

```python
df_combined = pd.merge_asof(df_accel, df_gyro, 
                            on='timestamp', 
                            direction='nearest',
                            tolerance=pd.Timedelta(seconds=0.1))
```

#### Etapa 3: Criação de Janelas (Features)
- Agrupar cada 2 leituras consecutivas em um único vetor
- Cada conjunto tem 12 features:
  - 6 da primeira leitura (3 acelerômetro + 3 giroscópio)
  - 6 da segunda leitura (3 acelerômetro + 3 giroscópio)

```python
# Exemplo de uma janela:
janela = [
    accel_x1, accel_y1, accel_z1, gyro_x1, gyro_y1, gyro_z1,  # Leitura 1
    accel_x2, accel_y2, accel_z2, gyro_x2, gyro_y2, gyro_z2   # Leitura 2
]
```

#### Etapa 4: Normalização
- Usar `StandardScaler` para normalizar as features
- Por quê? Features têm escalas diferentes (acelerômetro vs giroscópio)
- Fórmula: `z = (x - média) / desvio_padrão`

#### Etapa 5: Aplicação do K-means
```python
kmeans = KMeans(n_clusters=2, random_state=42)
labels = kmeans.fit_predict(features_normalized)
```

- `n_clusters=2`: Queremos 2 grupos
- `random_state=42`: Para reprodutibilidade
- Retorna: Array de labels (0 ou 1) para cada conjunto

### 4. **Interpretação dos Resultados**

#### Gráfico Principal (Eixo Y = Label, Eixo X = Conjunto)
- **Eixo X**: Índice do conjunto de pontos (temporal, do início ao fim da coleta)
- **Eixo Y**: Cluster predito (0 ou 1)
- **Cores**: Azul = Cluster 0, Vermelho = Cluster 1

**O que isso mostra?**
- Padrões temporais de comportamento
- Mudanças entre estados/atividades ao longo do tempo
- Exemplo: Pessoa alternando entre movimento intenso (cluster 1) e repouso (cluster 0)

#### Métrica: Inércia
- Medida de quão compactos são os clusters
- **Menor inércia = clusters mais bem definidos**
- Fórmula: Soma das distâncias quadráticas de cada ponto ao centro do seu cluster

### 5. **Análise dos Resultados Obtidos**

#### Pessoa 3 (Exemplo Individual):
- **718 conjuntos** de pontos criados
- **Cluster 0**: 158 conjuntos (22.0%) - Possível estado de repouso/baixa atividade
- **Cluster 1**: 560 conjuntos (78.0%) - Possível estado de movimento/alta atividade
- **Inércia**: 6819.15

#### Análise Comparativa (Todas as 13 Pessoas):

**Pessoas com alta atividade (>70% Cluster 1):**
- Pessoa 3: 78.0%
- Pessoa 5: 74.9%
- Pessoa 15: 80.0%
→ Indicam comportamento predominantemente ativo

**Pessoas com baixa atividade (<20% Cluster 1):**
- Pessoa 6: 6.8%
- Pessoa 14: 10.2%
- Pessoa 16: 10.1%
- Pessoa 23: 15.5%
→ Indicam comportamento predominantemente em repouso

**Pessoas balanceadas (40-60% Cluster 1):**
- Pessoa 4: 59.4%
- Pessoa 11: 40.4%
- Pessoa 18: 43.6%
→ Alternância equilibrada entre estados

### 6. **Arquivos Gerados**

1. **`kmeans_clustering.py`**: Script para análise de uma pessoa
2. **`kmeans_todas_pessoas.py`**: Script para análise comparativa
3. **`clustering_pessoa_3.png`**: Visualização individual da pessoa 3
4. **`clustering_todas_pessoas_individual.png`**: Grid com todas as pessoas
5. **`clustering_todas_pessoas_comparativo.png`**: Gráficos comparativos

### 7. **Como Usar os Scripts**

#### Análise de uma pessoa:
```bash
python kmeans_clustering.py
```
- Padrão: Analisa pessoa 3
- Para mudar: Altere `PESSOA_INICIAL = 3` no código

#### Análise de todas as pessoas:
```bash
python kmeans_todas_pessoas.py
```
- Processa automaticamente todas as 13 pessoas
- Gera relatório estatístico completo

### 8. **Possíveis Interpretações**

#### Cluster 0 vs Cluster 1:
Dependendo do contexto do experimento, os clusters podem representar:
- **Repouso vs Movimento**
- **Caminhada vs Corrida**
- **Sentado vs Em pé**
- **Atividade leve vs Atividade intensa**

**Como descobrir?**
- Analisar os valores médios dos centroides dos clusters
- Comparar magnitudes de aceleração/rotação
- Validar com vídeos ou anotações do experimento

### 9. **Métricas de Qualidade**

#### Inércia (Within-cluster sum of squares):
- Pessoa 32: 416.31 (melhor - clusters bem separados)
- Pessoa 5: 49788.96 (pior - clusters mais dispersos)
- **Interpretação**: Depende do número de pontos e variabilidade dos dados

#### Silhouette Score (Opcional - não implementado):
- Medida de -1 a 1
- Valores próximos de 1 = clusters bem definidos
- Valores próximos de 0 = sobreposição de clusters

### 10. **Limitações e Melhorias Futuras**

#### Limitações:
- K=2 é fixo (não testamos outros valores)
- Janela de 2 pontos é arbitrária
- Não considera a sequência temporal (K-means trata cada conjunto independentemente)

#### Melhorias possíveis:
1. **Testar diferentes valores de K**: Use método do cotovelo ou silhouette
2. **Variar o tamanho da janela**: Testar 3, 4, 5 pontos por conjunto
3. **Adicionar features temporais**: Velocidade, aceleração, jerk
4. **Usar algoritmos temporais**: Hidden Markov Models, DTW
5. **PCA para visualização**: Reduzir 12 dimensões para 2D
6. **Validação com ground truth**: Comparar com atividades reais anotadas

## 🎯 Resumo

Criamos um sistema que:
1. ✅ Agrupa 2 leituras consecutivas em conjuntos de pontos
2. ✅ Aplica K-means para separar em 2 clusters
3. ✅ Plota Y = label predito, X = conjunto de ponto
4. ✅ Analisa uma pessoa primeiro, depois todas
5. ✅ Gera visualizações e relatórios estatísticos

**Resultado**: Identificamos padrões de comportamento distintos nos dados de movimento, permitindo distinguir entre diferentes estados de atividade física.
