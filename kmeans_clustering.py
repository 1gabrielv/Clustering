import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
from datetime import datetime

# Config
SAMPLING_RATE = 0.5     # Taxa de amostragem em segundos (nao sabemos se é isso ainda)
N_CLUSTERS = 3          # Número de clusters desejados

PESSOA_INICIAL = 3      # Começar com a pessoa 3 (exemplo)

def carregar_dados_pessoa(pessoa_id):
    """
    Carrega dados de acelerômetro e giroscópio de uma pessoa específica
    
    Args:
        pessoa_id: ID da pessoa (número)
    
    Returns:
        tuple: (DataFrame acelerômetro, DataFrame giroscópio)
    """
    # Caminhos dos arquivos
    accel_file = f'acelerometro/acelerometro_{pessoa_id}.csv'
    
    # O giroscópio tem nomenclatura diferente para pessoa 3
    if pessoa_id == 3:
        gyro_file = f'giroscopio/giroscopio_{pessoa_id}-1.txt'
    else:
        gyro_file = f'giroscopio/giroscopio_{pessoa_id}.txt'
    
    # Carregar acelerômetro (CSV com cabeçalho)
    df_accel = pd.read_csv(accel_file)
    df_accel['timestamp'] = pd.to_datetime(df_accel['timestamp'])
    
    # Carregar giroscópio (TXT sem cabeçalho)
    df_gyro = pd.read_csv(gyro_file, header=None, names=['timestamp', 'gx', 'gy', 'gz'])
    df_gyro['timestamp'] = pd.to_datetime(df_gyro['timestamp'])
    
    return df_accel, df_gyro

def sincronizar_dados(df_accel, df_gyro, sampling_rate=0.5):
    """
    Sincroniza dados de acelerômetro e giroscópio baseado em timestamps
    e cria janelas de tempo com múltiplos pontos
    
    Args:
        df_accel: DataFrame com dados do acelerômetro
        df_gyro: DataFrame com dados do giroscópio
        sampling_rate: Taxa de amostragem em segundos
    
    Returns:
        DataFrame: Dados sincronizados e agrupados
    """
    # Merge dos dados usando o timestamp mais próximo
    df_accel = df_accel.sort_values('timestamp').reset_index(drop=True)
    df_gyro = df_gyro.sort_values('timestamp').reset_index(drop=True)
    
    # Fazer merge_asof para combinar timestamps próximos
    df_combined = pd.merge_asof(
        df_accel, 
        df_gyro, 
        on='timestamp', 
        direction='nearest',
        tolerance=pd.Timedelta(seconds=0.1)
    )
    
    # Remover linhas com valores NaN
    df_combined = df_combined.dropna()
    
    return df_combined

def criar_features_janela(df, window_size=2):
    """
    Cria features agrupando múltiplos pontos consecutivos em uma janela
    
    Args:
        df: DataFrame com dados sincronizados
        window_size: Número de pontos por janela (cluster point)
    
    Returns:
        numpy array: Features para clustering (cada linha = 1 janela com múltiplos pontos)
    """
    features_list = []
    timestamps_list = []
    
    # Percorrer os dados em janelas
    for i in range(0, len(df) - window_size + 1, window_size):
        window = df.iloc[i:i+window_size]
        
        # Concatenar todos os valores da janela em um único vetor de features
        feature_vector = []
        for _, row in window.iterrows():
            # Adicionar acelerômetro (x, y, z)
            feature_vector.extend([row['x'], row['y'], row['z']])
            # Adicionar giroscópio (gx, gy, gz)
            feature_vector.extend([row['gx'], row['gy'], row['gz']])
        
        features_list.append(feature_vector)
        # usar timestamp médio da janela como referência temporal
        try:
            window_ts = window['timestamp'].mean()
        except Exception:
            window_ts = window['timestamp'].iloc[0]
        timestamps_list.append(pd.to_datetime(window_ts))
    
    return np.array(features_list), np.array(timestamps_list)

def aplicar_kmeans(features, n_clusters=2):
    """
    Aplica K-means clustering nas features
    
    Args:
        features: Array de features
        n_clusters: Número de clusters
    
    Returns:
        tuple: (modelo KMeans treinado, labels dos clusters, features normalizadas)
    """
    # Normalizar features
    scaler = StandardScaler()
    features_normalized = scaler.fit_transform(features)
    
    # Aplicar K-means
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    labels = kmeans.fit_predict(features_normalized)
    
    return kmeans, labels, features_normalized


def _mean_accel_magnitude_per_window(features, window_size):
    """
    Calcula a magnitude média do acelerômetro por janela a partir do vetor de features.
    Espera que as features sejam organizadas como (x,y,z,gx,gy,gz) repetido por ponto na janela.
    Retorna um vetor com uma magnitude média por janela.
    """
    mags = []
    n_vals = window_size
    for row in features:
        accel_vals = []
        for i in range(0, n_vals * 6, 6):
            x, y, z = row[i], row[i+1], row[i+2]
            accel_vals.append(np.sqrt(x**2 + y**2 + z**2))
        mags.append(np.mean(accel_vals))
    return np.array(mags)


def map_clusters_to_movement(labels, features, window_size):
    """
    Mapeia cada cluster para um rótulo de movimento baseado na magnitude média do acelerômetro.
    Retorna um dicionário {cluster_id: movimento_str} e um array de rótulos por janela.
    """
    mags = _mean_accel_magnitude_per_window(features, window_size)
    unique_clusters = np.unique(labels)
    cluster_mean_mag = {}
    for c in unique_clusters:
        cluster_mean_mag[c] = mags[labels == c].mean()

    # ordenar clusters por magnitude média (ascendente)
    ordered = sorted(cluster_mean_mag.items(), key=lambda x: x[1])
    ordered_ids = [c for c, _ in ordered]

    # rótulos padrão para 3 clusters (do menor para o maior)
    movement_names_3 = [
        'muito baixo movimento (parado)',
        'baixo movimento',
        'alto movimento'
    ]

    if len(ordered_ids) == 3:
        assigned = {cid: movement_names_3[i] for i, cid in enumerate(ordered_ids)}
    else:
        # gerar rótulos genéricos se não houver exatamente 3 clusters
        assigned = {cid: f'movimento_{i}' for i, cid in enumerate(ordered_ids)}

    labels_movement = np.array([assigned[c] for c in labels])
    return assigned, labels_movement

def plotar_resultados(labels, pessoa_id, timestamps, cluster_name_map, movement_labels, window_size=2):
    """
    Plota os resultados do clustering
    
    Args:
        labels: Labels preditos pelo K-means
        pessoa_id: ID da pessoa
        window_size: Tamanho da janela usada
    """
    plt.figure(figsize=(14, 6))

    # Plot 1: Labels ao longo do tempo (usar timestamps no eixo X)
    plt.subplot(1, 2, 1)
    # definir cores por rótulo de movimento
    unique_mov = list(np.unique(movement_labels))
    palette = {
        'muito baixo movimento (parado)': 'gray',
        'baixo movimento': 'blue',
        'alto movimento': 'red'
    }
    # fallback para rótulos genéricos
    default_colors = ['tab:blue', 'tab:orange', 'tab:red', 'gray']
    colors = [palette.get(m, default_colors[i % len(default_colors)]) for i, m in enumerate(movement_labels)]

    plt.scatter(timestamps, movement_labels, c=colors, alpha=0.7, s=40)
    plt.xlabel('Timestamp', fontsize=12)
    plt.ylabel('Rótulo de Movimento', fontsize=12)
    plt.title(f'K-means Clustering - Pessoa {pessoa_id}\n(Cada ponto = {window_size} leituras)', fontsize=14)
    plt.xticks(rotation=30)
    plt.grid(True, alpha=0.3)

    # Plot 2: Distribuição por rótulo de movimento
    plt.subplot(1, 2, 2)
    unique_mov, counts = np.unique(movement_labels, return_counts=True)
    mov_colors = [palette.get(m, 'tab:blue') for m in unique_mov]
    plt.bar(unique_mov, counts, color=mov_colors, alpha=0.7)
    plt.xlabel('Rótulo de Movimento', fontsize=12)
    plt.ylabel('Número de Janelas', fontsize=12)
    plt.title('Distribuição por Rótulo de Movimento', fontsize=14)
    plt.grid(True, alpha=0.3, axis='y')

    # Adicionar valores nas barras
    for i, count in enumerate(counts):
        plt.text(i, count, str(count), ha='center', va='bottom', fontsize=11, fontweight='bold')

    plt.tight_layout()
    plt.savefig(f'clustering_pessoa_{pessoa_id}.png', dpi=300, bbox_inches='tight')
    plt.show()

    print(f"\n✓ Gráfico salvo como 'clustering_pessoa_{pessoa_id}.png'")

def analisar_pessoa(pessoa_id, window_size=2, n_clusters=2):
    """
    Análise completa de clusterização para uma pessoa
    
    Args:
        pessoa_id: ID da pessoa
        window_size: Número de pontos por janela
        n_clusters: Número de clusters
    """
    print(f"\n{'='*60}")
    print(f"ANÁLISE - PESSOA {pessoa_id}")
    print(f"{'='*60}")
    
    # 1. Carregar dados
    print("\n[1/5] Carregando dados...")
    df_accel, df_gyro = carregar_dados_pessoa(pessoa_id)
    print(f"   ✓ Acelerômetro: {len(df_accel)} pontos")
    print(f"   ✓ Giroscópio: {len(df_gyro)} pontos")
    
    # 2. Sincronizar dados
    print("\n[2/5] Sincronizando dados de acelerômetro e giroscópio...")
    df_combined = sincronizar_dados(df_accel, df_gyro, SAMPLING_RATE)
    print(f"   ✓ Dados sincronizados: {len(df_combined)} pontos")
    
    # 3. Criar features em janelas
    print(f"\n[3/5] Criando features (janelas de {window_size} pontos)...")
    features, timestamps = criar_features_janela(df_combined, window_size)
    n_features_per_window = window_size * 6  # 3 acelerômetro + 3 giroscópio
    print(f"   ✓ {len(features)} conjuntos de pontos criados")
    print(f"   ✓ Cada conjunto tem {n_features_per_window} features ({window_size} pontos × 6 sensores)")
    
    # 4. Aplicar K-means
    print(f"\n[4/5] Aplicando K-means (k={n_clusters})...")
    kmeans, labels, features_normalized = aplicar_kmeans(features, n_clusters)
    print(f"   ✓ Clustering concluído")
    print(f"   ✓ Inércia: {kmeans.inertia_:.2f}")
    
    # 5. Plotar resultados
    print("\n[5/5] Gerando visualização e rotulando clusters por movimento...")
    cluster_map, movement_labels = map_clusters_to_movement(labels, features, window_size)
    plotar_resultados(labels, pessoa_id, timestamps, cluster_map, movement_labels, window_size)
    
    # Estatísticas
    print(f"\n{'='*60}")
    print("ESTATÍSTICAS")
    print(f"{'='*60}")
    unique, counts = np.unique(labels, return_counts=True)
    for cluster_id, count in zip(unique, counts):
        percentage = (count / len(labels)) * 100
        print(f"Cluster {cluster_id}: {count} conjuntos ({percentage:.1f}%)")
    
    return df_combined, features, labels, kmeans, timestamps

def analisar_todas_pessoas(window_size=2, n_clusters=2):
    """
    Análise de clusterização para todas as pessoas
    
    Args:
        window_size: Número de pontos por janela
        n_clusters: Número de clusters
    """
    # IDs das pessoas disponíveis
    pessoas = [3, 4, 5, 6, 11, 12, 14, 15, 16, 18, 23, 32, 35]
    
    resultados = {}
    
    print("\n" + "="*60)
    print("ANÁLISE DE TODAS AS PESSOAS")
    print("="*60)
    
    for pessoa_id in pessoas:
        try:
            df_combined, features, labels, kmeans, timestamps = analisar_pessoa(
                pessoa_id, window_size, n_clusters
            )
            resultados[pessoa_id] = {
                'data': df_combined,
                'features': features,
                'labels': labels,
                'kmeans': kmeans,
                'timestamps': timestamps
            }
        except Exception as e:
            print(f"\n⚠ Erro ao processar pessoa {pessoa_id}: {e}")
            continue
    
    # Sumário geral
    print(f"\n\n{'='*60}")
    print("SUMÁRIO GERAL")
    print(f"{'='*60}")
    print(f"Total de pessoas analisadas: {len(resultados)}/{len(pessoas)}")
    
    return resultados

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CLUSTERIZAÇÃO K-MEANS - ACELERÔMETRO E GIROSCÓPIO")
    print("="*60)
    print(f"Taxa de amostragem: {SAMPLING_RATE}s")
    print(f"Número de clusters: {N_CLUSTERS}")
    print(f"Tamanho da janela: 2 pontos (acelerômetro + giroscópio)")
    
    # Opção 1: Analisar apenas uma pessoa (recomendado para começar)
    print("\n" + "-"*60)
    print("Opção escolhida: Analisar uma pessoa primeiro")
    print("-"*60)
    
    df_combined, features, labels, kmeans, timestamps = analisar_pessoa(
        PESSOA_INICIAL, 
        window_size=2, 
        n_clusters=N_CLUSTERS
    )
    
    # Descomente a linha abaixo para analisar todas as pessoas
    # resultados = analisar_todas_pessoas(window_size=2, n_clusters=N_CLUSTERS)
    
    print("\n" + "="*60)
    print("ANÁLISE CONCLUÍDA!")
    print("="*60)
    print("\nPara analisar todas as pessoas, descomente a última linha do script.")
