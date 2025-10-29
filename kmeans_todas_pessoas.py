"""
Script para análise comparativa de clusterização K-means para todas as pessoas
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os

# Configurações
SAMPLING_RATE = 0.5
N_CLUSTERS = 2
WINDOW_SIZE = 2

def carregar_dados_pessoa(pessoa_id):
    """Carrega dados de uma pessoa"""
    accel_file = f'acelerometro/acelerometro_{pessoa_id}.csv'
    if pessoa_id == 3:
        gyro_file = f'giroscopio/giroscopio_{pessoa_id}-1.txt'
    else:
        gyro_file = f'giroscopio/giroscopio_{pessoa_id}.txt'
    
    df_accel = pd.read_csv(accel_file)
    df_accel['timestamp'] = pd.to_datetime(df_accel['timestamp'])
    
    df_gyro = pd.read_csv(gyro_file, header=None, names=['timestamp', 'gx', 'gy', 'gz'])
    df_gyro['timestamp'] = pd.to_datetime(df_gyro['timestamp'])
    
    return df_accel, df_gyro

def sincronizar_dados(df_accel, df_gyro):
    """Sincroniza dados dos dois sensores"""
    df_accel = df_accel.sort_values('timestamp').reset_index(drop=True)
    df_gyro = df_gyro.sort_values('timestamp').reset_index(drop=True)
    
    df_combined = pd.merge_asof(
        df_accel, df_gyro, on='timestamp', 
        direction='nearest', tolerance=pd.Timedelta(seconds=0.1)
    )
    
    return df_combined.dropna()

def criar_features_janela(df, window_size=2):
    """Cria features em janelas"""
    features_list = []
    
    for i in range(0, len(df) - window_size + 1, window_size):
        window = df.iloc[i:i+window_size]
        feature_vector = []
        for _, row in window.iterrows():
            feature_vector.extend([row['x'], row['y'], row['z']])
            feature_vector.extend([row['gx'], row['gy'], row['gz']])
        features_list.append(feature_vector)
    
    return np.array(features_list)

def aplicar_kmeans(features, n_clusters=2):
    """Aplica K-means"""
    scaler = StandardScaler()
    features_normalized = scaler.fit_transform(features)
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(features_normalized)
    return kmeans, labels, features_normalized

def processar_pessoa(pessoa_id):
    """Processa uma pessoa e retorna os resultados"""
    try:
        df_accel, df_gyro = carregar_dados_pessoa(pessoa_id)
        df_combined = sincronizar_dados(df_accel, df_gyro)
        features = criar_features_janela(df_combined, WINDOW_SIZE)
        kmeans, labels, _ = aplicar_kmeans(features, N_CLUSTERS)
        
        return {
            'pessoa_id': pessoa_id,
            'n_pontos': len(features),
            'labels': labels,
            'inercia': kmeans.inertia_,
            'cluster_0': np.sum(labels == 0),
            'cluster_1': np.sum(labels == 1)
        }
    except Exception as e:
        print(f"Erro ao processar pessoa {pessoa_id}: {e}")
        return None

def plotar_todas_pessoas():
    """Processa e plota resultados de todas as pessoas"""
    pessoas = [3, 4, 5, 6, 11, 12, 14, 15, 16, 18, 23, 32, 35]
    resultados = []
    
    print("\n" + "="*70)
    print("PROCESSANDO TODAS AS PESSOAS")
    print("="*70)
    
    for pessoa_id in pessoas:
        print(f"Processando pessoa {pessoa_id}...", end=" ")
        resultado = processar_pessoa(pessoa_id)
        if resultado:
            resultados.append(resultado)
            print(f"✓ ({resultado['n_pontos']} conjuntos)")
        else:
            print("✗ Erro")
    
    # Criar visualização comparativa
    fig = plt.figure(figsize=(18, 10))
    
    # 1. Plot individual de cada pessoa
    n_pessoas = len(resultados)
    n_cols = 4
    n_rows = (n_pessoas + n_cols - 1) // n_cols
    
    for idx, resultado in enumerate(resultados, 1):
        ax = plt.subplot(n_rows, n_cols, idx)
        labels = resultado['labels']
        x = np.arange(len(labels))
        colors = ['blue' if label == 0 else 'red' for label in labels]
        
        ax.scatter(x, labels, c=colors, alpha=0.5, s=10)
        ax.set_title(f"Pessoa {resultado['pessoa_id']}", fontsize=10, fontweight='bold')
        ax.set_xlabel('Conjunto', fontsize=8)
        ax.set_ylabel('Cluster', fontsize=8)
        ax.set_yticks([0, 1])
        ax.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('clustering_todas_pessoas_individual.png', dpi=300, bbox_inches='tight')
    print("\n✓ Gráfico individual salvo: clustering_todas_pessoas_individual.png")
    
    # 2. Gráfico comparativo de distribuição
    fig, axes = plt.subplots(2, 2, figsize=(16, 10))
    
    # 2a. Distribuição de clusters por pessoa
    ax1 = axes[0, 0]
    pessoas_ids = [r['pessoa_id'] for r in resultados]
    cluster_0_counts = [r['cluster_0'] for r in resultados]
    cluster_1_counts = [r['cluster_1'] for r in resultados]
    
    x = np.arange(len(pessoas_ids))
    width = 0.35
    
    ax1.bar(x - width/2, cluster_0_counts, width, label='Cluster 0', color='blue', alpha=0.7)
    ax1.bar(x + width/2, cluster_1_counts, width, label='Cluster 1', color='red', alpha=0.7)
    ax1.set_xlabel('Pessoa', fontsize=12)
    ax1.set_ylabel('Número de Conjuntos', fontsize=12)
    ax1.set_title('Distribuição de Clusters por Pessoa', fontsize=14, fontweight='bold')
    ax1.set_xticks(x)
    ax1.set_xticklabels(pessoas_ids)
    ax1.legend()
    ax1.grid(True, alpha=0.3, axis='y')
    
    # 2b. Percentual de Cluster 1 por pessoa
    ax2 = axes[0, 1]
    percentuais = [(r['cluster_1'] / r['n_pontos']) * 100 for r in resultados]
    colors_bar = ['red' if p > 50 else 'blue' for p in percentuais]
    
    ax2.bar(pessoas_ids, percentuais, color=colors_bar, alpha=0.7)
    ax2.axhline(y=50, color='black', linestyle='--', linewidth=1, label='50%')
    ax2.set_xlabel('Pessoa', fontsize=12)
    ax2.set_ylabel('% Cluster 1', fontsize=12)
    ax2.set_title('Percentual do Cluster 1 por Pessoa', fontsize=14, fontweight='bold')
    ax2.legend()
    ax2.grid(True, alpha=0.3, axis='y')
    
    # 2c. Inércia por pessoa
    ax3 = axes[1, 0]
    inercias = [r['inercia'] for r in resultados]
    ax3.plot(pessoas_ids, inercias, marker='o', linewidth=2, markersize=8, color='green')
    ax3.set_xlabel('Pessoa', fontsize=12)
    ax3.set_ylabel('Inércia', fontsize=12)
    ax3.set_title('Qualidade do Clustering (Inércia)', fontsize=14, fontweight='bold')
    ax3.grid(True, alpha=0.3)
    
    # 2d. Número total de conjuntos por pessoa
    ax4 = axes[1, 1]
    n_pontos = [r['n_pontos'] for r in resultados]
    ax4.bar(pessoas_ids, n_pontos, color='purple', alpha=0.7)
    ax4.set_xlabel('Pessoa', fontsize=12)
    ax4.set_ylabel('Número de Conjuntos', fontsize=12)
    ax4.set_title('Total de Conjuntos de Pontos por Pessoa', fontsize=14, fontweight='bold')
    ax4.grid(True, alpha=0.3, axis='y')
    
    plt.tight_layout()
    plt.savefig('clustering_todas_pessoas_comparativo.png', dpi=300, bbox_inches='tight')
    print("✓ Gráfico comparativo salvo: clustering_todas_pessoas_comparativo.png")
    
    # Relatório estatístico
    print("\n" + "="*70)
    print("RELATÓRIO ESTATÍSTICO")
    print("="*70)
    print(f"{'Pessoa':<10} {'N° Conj.':<12} {'Cluster 0':<12} {'Cluster 1':<12} {'% Clust 1':<12} {'Inércia':<10}")
    print("-"*70)
    
    for r in resultados:
        perc_c1 = (r['cluster_1'] / r['n_pontos']) * 100
        print(f"{r['pessoa_id']:<10} {r['n_pontos']:<12} {r['cluster_0']:<12} {r['cluster_1']:<12} {perc_c1:<12.1f} {r['inercia']:<10.2f}")
    
    # Estatísticas gerais
    print("\n" + "-"*70)
    avg_inercia = np.mean([r['inercia'] for r in resultados])
    avg_perc_c1 = np.mean([(r['cluster_1'] / r['n_pontos']) * 100 for r in resultados])
    print(f"Média - Inércia: {avg_inercia:.2f} | % Cluster 1: {avg_perc_c1:.1f}%")
    print("="*70)
    
    plt.show()

if __name__ == "__main__":
    plotar_todas_pessoas()
    print("\n✓ Análise completa de todas as pessoas finalizada!")
