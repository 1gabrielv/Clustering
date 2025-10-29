"""
Script Interativo - Exploração de Parâmetros K-means

Este script permite testar diferentes configurações:
- Número de clusters (K)
- Tamanho da janela
- Pessoas específicas
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score

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
    """Sincroniza dados"""
    df_accel = df_accel.sort_values('timestamp').reset_index(drop=True)
    df_gyro = df_gyro.sort_values('timestamp').reset_index(drop=True)
    df_combined = pd.merge_asof(
        df_accel, df_gyro, on='timestamp', 
        direction='nearest', tolerance=pd.Timedelta(seconds=0.1)
    )
    return df_combined.dropna()

def criar_features_janela(df, window_size):
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

def metodo_cotovelo(features, max_k=10):
    """
    Método do Cotovelo para determinar o melhor K
    Plota inércia vs número de clusters
    """
    scaler = StandardScaler()
    features_normalized = scaler.fit_transform(features)
    
    inercias = []
    silhouettes = []
    K_range = range(2, max_k + 1)
    
    print(f"\nCalculando métricas para K de 2 a {max_k}...")
    for k in K_range:
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features_normalized)
        inercias.append(kmeans.inertia_)
        
        # Silhouette score (só funciona com K >= 2)
        if k >= 2 and k < len(features):
            score = silhouette_score(features_normalized, labels)
            silhouettes.append(score)
        else:
            silhouettes.append(0)
        
        print(f"  K={k}: Inércia={kmeans.inertia_:.2f}, Silhouette={silhouettes[-1]:.3f}")
    
    # Plot
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Gráfico do cotovelo
    ax1.plot(K_range, inercias, 'bo-', linewidth=2, markersize=8)
    ax1.set_xlabel('Número de Clusters (K)', fontsize=12)
    ax1.set_ylabel('Inércia', fontsize=12)
    ax1.set_title('Método do Cotovelo', fontsize=14, fontweight='bold')
    ax1.grid(True, alpha=0.3)
    
    # Silhouette score
    ax2.plot(K_range, silhouettes, 'ro-', linewidth=2, markersize=8)
    ax2.set_xlabel('Número de Clusters (K)', fontsize=12)
    ax2.set_ylabel('Silhouette Score', fontsize=12)
    ax2.set_title('Silhouette Score vs K', fontsize=14, fontweight='bold')
    ax2.axhline(y=0.5, color='green', linestyle='--', label='Bom threshold (0.5)')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig('metodo_cotovelo.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\n✓ Gráfico salvo: metodo_cotovelo.png")

def comparar_tamanhos_janela(pessoa_id, k=2, max_window=6):
    """
    Compara diferentes tamanhos de janela
    """
    print(f"\n{'='*70}")
    print(f"COMPARAÇÃO DE TAMANHOS DE JANELA - Pessoa {pessoa_id}")
    print(f"{'='*70}")
    
    df_accel, df_gyro = carregar_dados_pessoa(pessoa_id)
    df_combined = sincronizar_dados(df_accel, df_gyro)
    
    resultados = []
    
    for window_size in range(2, max_window + 1):
        features = criar_features_janela(df_combined, window_size)
        
        if len(features) < k:
            print(f"Window {window_size}: Poucos conjuntos ({len(features)}), pulando...")
            continue
        
        scaler = StandardScaler()
        features_normalized = scaler.fit_transform(features)
        
        kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)
        labels = kmeans.fit_predict(features_normalized)
        
        if k >= 2 and k < len(features):
            silhouette = silhouette_score(features_normalized, labels)
        else:
            silhouette = 0
        
        resultados.append({
            'window_size': window_size,
            'n_conjuntos': len(features),
            'inercia': kmeans.inertia_,
            'silhouette': silhouette
        })
        
        print(f"Window {window_size}: {len(features)} conjuntos, "
              f"Inércia={kmeans.inertia_:.2f}, Silhouette={silhouette:.3f}")
    
    # Plot comparativo
    fig, axes = plt.subplots(1, 3, figsize=(16, 5))
    
    window_sizes = [r['window_size'] for r in resultados]
    n_conjuntos = [r['n_conjuntos'] for r in resultados]
    inercias = [r['inercia'] for r in resultados]
    silhouettes = [r['silhouette'] for r in resultados]
    
    axes[0].bar(window_sizes, n_conjuntos, color='blue', alpha=0.7)
    axes[0].set_xlabel('Tamanho da Janela', fontsize=12)
    axes[0].set_ylabel('Número de Conjuntos', fontsize=12)
    axes[0].set_title('Conjuntos Gerados', fontsize=14, fontweight='bold')
    axes[0].grid(True, alpha=0.3, axis='y')
    
    axes[1].plot(window_sizes, inercias, 'ro-', linewidth=2, markersize=8)
    axes[1].set_xlabel('Tamanho da Janela', fontsize=12)
    axes[1].set_ylabel('Inércia', fontsize=12)
    axes[1].set_title('Inércia vs Tamanho da Janela', fontsize=14, fontweight='bold')
    axes[1].grid(True, alpha=0.3)
    
    axes[2].plot(window_sizes, silhouettes, 'go-', linewidth=2, markersize=8)
    axes[2].set_xlabel('Tamanho da Janela', fontsize=12)
    axes[2].set_ylabel('Silhouette Score', fontsize=12)
    axes[2].set_title('Silhouette vs Tamanho da Janela', fontsize=14, fontweight='bold')
    axes[2].axhline(y=0.5, color='orange', linestyle='--', label='Threshold 0.5')
    axes[2].legend()
    axes[2].grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(f'comparacao_janelas_pessoa_{pessoa_id}.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print(f"\n✓ Gráfico salvo: comparacao_janelas_pessoa_{pessoa_id}.png")

def analise_exploratoria_completa(pessoa_id):
    """
    Análise exploratória completa:
    1. Método do cotovelo para determinar melhor K
    2. Comparação de tamanhos de janela
    """
    print("\n" + "="*70)
    print(f"ANÁLISE EXPLORATÓRIA COMPLETA - Pessoa {pessoa_id}")
    print("="*70)
    
    # Carregar dados
    print("\nCarregando dados...")
    df_accel, df_gyro = carregar_dados_pessoa(pessoa_id)
    df_combined = sincronizar_dados(df_accel, df_gyro)
    
    # Usar janela padrão de 2 para análise inicial
    features = criar_features_janela(df_combined, window_size=2)
    print(f"✓ {len(features)} conjuntos criados (janela=2)")
    
    # 1. Método do cotovelo
    print("\n" + "-"*70)
    print("PARTE 1: Determinando o melhor número de clusters (K)")
    print("-"*70)
    metodo_cotovelo(features, max_k=8)
    
    # 2. Comparar tamanhos de janela
    print("\n" + "-"*70)
    print("PARTE 2: Comparando diferentes tamanhos de janela")
    print("-"*70)
    comparar_tamanhos_janela(pessoa_id, k=2, max_window=5)
    
    print("\n" + "="*70)
    print("ANÁLISE EXPLORATÓRIA CONCLUÍDA!")
    print("="*70)
    print("\nDicas:")
    print("• No método do cotovelo, procure por um 'cotovelo' na curva de inércia")
    print("• Silhouette score > 0.5 indica boa separação entre clusters")
    print("• Janelas maiores capturam mais contexto temporal")
    print("• Janelas menores permitem mais granularidade")

if __name__ == "__main__":
    # Escolha a pessoa para análise
    PESSOA_ID = 3
    
    print("\n" + "="*70)
    print("EXPLORAÇÃO DE PARÂMETROS K-MEANS")
    print("="*70)
    print(f"Pessoa analisada: {PESSOA_ID}")
    
    # Executar análise exploratória completa
    analise_exploratoria_completa(PESSOA_ID)
    
    print("\n" + "-"*70)
    print("Para analisar outra pessoa, altere PESSOA_ID no código")
    print("Pessoas disponíveis: 3, 4, 5, 6, 11, 12, 14, 15, 16, 18, 23, 32, 35")
    print("-"*70)
