# Scripts - Clustering K-Means

Esta pasta contém os scripts Python organizados por tipo de processamento.

## Estrutura

### 📁 preprocessing/
Scripts de pré-processamento de dados:
- **downsampling_script.py**: Reduz dados em 50% (pega 1 a cada 2 linhas)
  - Processa pessoas 11-38
  - Input: `acelerometro/` e `giroscopio/`
  - Output: `DATA/Downsampling_data/ds_acelerometro/` e `ds_giroscopio/`

### 📁 clustering_euclidiano/
Scripts de clustering baseado em distância euclidiana:
- **kmeans_clustering_euclidean.py**: Script principal de clustering
  - Janelas temporais SEM sobreposição (10 pontos)
  - Ordenação por variação (std) do acelerômetro
  - Features: [std_accel, mag_accel, std_gyro, mag_gyro]
  - 3 clusters: muito baixo movimento (parado), baixo movimento, alto movimento
  - Output: `outputs/ClusterK3euclidianoComDownsampling/`

- **kmeans_clustering_original.py**: Versão original (mantida para referência)

## Como usar

### 1. Pré-processamento (Downsampling)
```bash
python scripts/preprocessing/downsampling_script.py
```

### 2. Clustering Euclidiano
```bash
python scripts/clustering_euclidiano/kmeans_clustering_euclidean.py
```

Ou use o notebook interativo: `notebooks/clustering_euclidiano_analise.ipynb`

## Melhorias Implementadas

✅ **Janelas sem sobreposição**: Cada ponto pertence a apenas um cluster
✅ **Ordenação por variação**: Std do acelerômetro como critério principal
✅ **Detecção de repouso**: Cluster "parado" detecta corretamente baixa variação (sono/inatividade)
✅ **Processamento completo**: 28 pessoas (11-38) processadas com sucesso

## Resultados

**Distribuição geral:**
- 🔴 Parado: 45.8%
- 🔵 Baixo movimento: 42.5%
- 🟢 Alto movimento: 11.6%
