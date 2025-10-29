# 🎯 Projeto K-means: Clusterização de Dados de Sensores

## 📖 Descrição
Projeto de clusterização K-means aplicado a dados de acelerômetro e giroscópio. O objetivo é identificar padrões de comportamento em dados de movimento, agrupando conjuntos de leituras temporais em clusters.

## 📁 Estrutura do Projeto

```
Kluster/
├── acelerometro/              # Dados de acelerômetro (CSV)
├── giroscopio/                # Dados de giroscópio (TXT)
├── kmeans_clustering.py       # ⭐ Script principal - análise individual
├── kmeans_todas_pessoas.py    # ⭐ Script para todas as pessoas
├── kmeans_exploratorio.py     # ⭐ Script exploratório (cotovelo, janelas)
├── EXPLICACAO.md              # 📚 Explicação detalhada do projeto
└── README.md                  # Este arquivo
```

## 🚀 Como Usar

### 1. Instalação de Dependências

As bibliotecas necessárias já estão instaladas no ambiente virtual:
- pandas
- numpy
- matplotlib
- scikit-learn

### 2. Scripts Disponíveis

#### 🔹 Script 1: Análise Individual
Analisa uma pessoa específica com visualização detalhada.

```bash
python kmeans_clustering.py
```

**Saída:**
- `clustering_pessoa_3.png` - Gráfico com resultados
- Estatísticas no terminal

**Personalizar:**
```python
# No arquivo kmeans_clustering.py, linha 258:
PESSOA_INICIAL = 5  # Altere para outra pessoa
```

---

#### 🔹 Script 2: Análise Comparativa
Processa todas as 13 pessoas e gera comparações.

```bash
python kmeans_todas_pessoas.py
```

**Saída:**
- `clustering_todas_pessoas_individual.png` - Grid com todas as pessoas
- `clustering_todas_pessoas_comparativo.png` - Gráficos comparativos
- Relatório estatístico completo no terminal

---

#### 🔹 Script 3: Análise Exploratória
Testa diferentes parâmetros (K e tamanho de janela).

```bash
python kmeans_exploratorio.py
```

**Saída:**
- `metodo_cotovelo.png` - Análise do melhor K
- `comparacao_janelas_pessoa_3.png` - Comparação de janelas

**Personalizar:**
```python
# No arquivo kmeans_exploratorio.py, linha 224:
PESSOA_ID = 4  # Altere para outra pessoa
```

## 📊 Entendendo os Resultados

### Gráfico Principal
- **Eixo X**: Índice do conjunto de pontos (temporal)
- **Eixo Y**: Cluster predito (0 ou 1)
- **Cores**: Azul = Cluster 0, Vermelho = Cluster 1

### Métricas

#### Inércia (Within-cluster sum of squares)
- Medida de compactação dos clusters
- **Menor = melhor** (clusters mais bem definidos)
- Valores variam com quantidade de dados

#### Silhouette Score
- Medida de separação entre clusters
- Escala: -1 a 1
- **> 0.5 = Bom**
- **> 0.7 = Excelente**

### Interpretação dos Clusters

Para a **Pessoa 3** (exemplo):
- **Cluster 0** (22%): Possível estado de baixa atividade/repouso
- **Cluster 1** (78%): Possível estado de alta atividade/movimento

## 📋 Pessoas Disponíveis

IDs válidos: `3, 4, 5, 6, 11, 12, 14, 15, 16, 18, 23, 32, 35`

## 🔧 Parâmetros Configuráveis

### No código dos scripts:

```python
SAMPLING_RATE = 0.5    # Taxa de amostragem (segundos)
N_CLUSTERS = 2          # Número de clusters
WINDOW_SIZE = 2         # Pontos por conjunto
```

### Recomendações:
- **K=2**: Bom ponto de partida (silhouette ~0.41 para pessoa 3)
- **Janela=2**: Melhor silhouette score
- **Janelas maiores**: Mais contexto temporal, menos granularidade

## 📈 Resultados Principais

### Análise da Pessoa 3
- ✅ 718 conjuntos de pontos
- ✅ Silhouette score: 0.416
- ✅ Distribuição: 22% Cluster 0 / 78% Cluster 1

### Análise Comparativa (13 pessoas)
- ✅ Total processado: 17.720 conjuntos
- ✅ Média Cluster 1: 40.6%
- ✅ Alta variabilidade entre pessoas (6.8% a 80%)

**Insights:**
- Pessoas 3, 5, 15: Predominantemente ativas (>70% Cluster 1)
- Pessoas 6, 14, 16, 23: Predominantemente em repouso (<20% Cluster 1)
- Pessoas 4, 11, 18: Comportamento balanceado (~40-60%)

## 🎓 Conceitos Importantes

### O que é um "Conjunto de Pontos"?
Cada ponto do cluster = **Múltiplas leituras consecutivas** agrupadas.

**Exemplo com janela=2:**
```
Conjunto = [
    Leitura 1: [ax, ay, az, gx, gy, gz],
    Leitura 2: [ax, ay, az, gx, gy, gz]
]
→ Vetor de 12 features
```

### Pipeline de Processamento:
1. **Carregamento**: Ler CSVs/TXTs
2. **Sincronização**: Combinar timestamps (merge_asof)
3. **Janelamento**: Agrupar leituras consecutivas
4. **Normalização**: StandardScaler
5. **Clustering**: K-means
6. **Visualização**: Gráficos e métricas

## 🔬 Análises Adicionais Possíveis

### 1. Método do Cotovelo
Determine o melhor K visualmente:
```bash
python kmeans_exploratorio.py
```

### 2. Testar Diferentes Janelas
Compare janelas de 2 a 5 pontos:
```python
comparar_tamanhos_janela(pessoa_id=3, k=2, max_window=5)
```

### 3. Análise de Features
Identifique quais sensores mais influenciam:
```python
# Adicione análise de importância de features
pca = PCA(n_components=2)
features_pca = pca.fit_transform(features_normalized)
```

## 📚 Documentação Completa

Para entendimento detalhado do código e metodologia, leia:
- **[EXPLICACAO.md](EXPLICACAO.md)** - Explicação completa com teoria e código

## 🎨 Visualizações Geradas

1. **clustering_pessoa_3.png**
   - Plot temporal do clustering
   - Distribuição de clusters

2. **clustering_todas_pessoas_individual.png**
   - Grid 4x4 com todas as pessoas
   - Visão rápida de padrões

3. **clustering_todas_pessoas_comparativo.png**
   - Distribuição por pessoa
   - Percentuais de clusters
   - Inércia e número de conjuntos

4. **metodo_cotovelo.png**
   - Inércia vs K
   - Silhouette score vs K

5. **comparacao_janelas_pessoa_3.png**
   - Número de conjuntos vs janela
   - Inércia vs janela
   - Silhouette vs janela

## ⚙️ Execução Rápida

### Caso de Uso 1: "Quero analisar a pessoa 5"
```bash
# Edite kmeans_clustering.py (linha 258)
PESSOA_INICIAL = 5

# Execute
python kmeans_clustering.py
```

### Caso de Uso 2: "Quero ver todas as pessoas"
```bash
python kmeans_todas_pessoas.py
```

### Caso de Uso 3: "Qual o melhor K para pessoa 11?"
```bash
# Edite kmeans_exploratorio.py (linha 224)
PESSOA_ID = 11

# Execute
python kmeans_exploratorio.py
```

## 🐛 Troubleshooting

### Erro: "ModuleNotFoundError"
```bash
# Ative o ambiente virtual
.\.venv\Scripts\Activate.ps1

# Reinstale dependências
pip install pandas numpy matplotlib scikit-learn
```

### Erro: "File not found"
Verifique se os arquivos de dados estão nos diretórios corretos:
- `acelerometro/acelerometro_X.csv`
- `giroscopio/giroscopio_X.txt` (ou `giroscopio_3-1.txt` para pessoa 3)

## 🎯 Próximos Passos Sugeridos

1. ✅ **Concluído**: Clustering básico K=2
2. 🔄 **Validar**: Comparar com atividades reais (ground truth)
3. 🚀 **Expandir**: Testar outros algoritmos (DBSCAN, Gaussian Mixture)
4. 📊 **Visualizar**: Adicionar PCA/t-SNE para 2D
5. 🧠 **Avançar**: Implementar modelos temporais (HMM, LSTM)

---

**Status**: ✅ Implementação completa e funcional  
**Última atualização**: Outubro 2025