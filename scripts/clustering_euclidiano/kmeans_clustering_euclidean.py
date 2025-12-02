import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
import os
from datetime import datetime

# Config
N_CLUSTERS = 3          # Número de clusters desejados (muito baixo, baixo, alto movimento)
PESSOA_INICIAL = 38     # Começar com a pessoa 11 (primeira do downsampling)

def carregar_dados_pessoa_downsampled(pessoa_id):
    """
    Carrega dados de acelerômetro e giroscópio de uma pessoa específica (dados com downsampling)
    
    Args:
        pessoa_id: ID da pessoa (número)
    
    Returns:
        tuple: (DataFrame acelerômetro, DataFrame giroscópio)
    """
    # Caminhos dos arquivos com downsampling
    accel_file = f'DATA/Downsampling_data/ds_acelerometro/ds_acelerometro_{pessoa_id}.csv'
    gyro_file = f'DATA/Downsampling_data/ds_giroscopio/ds_giroscopio_{pessoa_id}.csv'
    
    # Carregar acelerômetro (CSV com cabeçalho)
    df_accel = pd.read_csv(accel_file)
    df_accel['timestamp'] = pd.to_datetime(df_accel['timestamp'])
    
    # Carregar giroscópio (CSV com cabeçalho)
    df_gyro = pd.read_csv(gyro_file)
    df_gyro['timestamp'] = pd.to_datetime(df_gyro['timestamp'])
    
    return df_accel, df_gyro

def sincronizar_dados(df_accel, df_gyro):
    """
    Sincroniza dados de acelerômetro e giroscópio baseado em timestamps
    
    Args:
        df_accel: DataFrame com dados do acelerômetro
        df_gyro: DataFrame com dados do giroscópio
    
    Returns:
        DataFrame: Dados sincronizados
    """
    # Renomear colunas do giroscópio para evitar conflito
    df_gyro = df_gyro.rename(columns={'x': 'gx', 'y': 'gy', 'z': 'gz'})
    
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

def calcular_features_janela(df, window_size=10): #botar janela para 7 
    """
    Calcula features baseadas em janelas temporais SEM sobreposição.
    Para cada janela, calcula:
    - Variação (desvio padrão) do acelerômetro (indica mudança de movimento - CHAVE!)
    - Magnitude média do acelerômetro (indica intensidade do movimento)
    - Variação (desvio padrão) do giroscópio (indica mudança de rotação)
    - Magnitude média do giroscópio (indica rotação)
    
    Args:
        df: DataFrame com dados sincronizados (deve ter colunas: x, y, z, gx, gy, gz)
        window_size: Tamanho da janela (número de pontos)
    
    Returns:
        tuple: (array de features, array de timestamps correspondentes)
    """
    features = []
    timestamps = []
    
    # Janelas SEM sobreposição (cada ponto pertence a apenas uma janela)
    for i in range(0, len(df) - window_size + 1, window_size):  # Step = window_size (sem overlap)
        window = df.iloc[i:i+window_size]
        
        # Magnitude do acelerômetro em cada ponto da janela
        accel_mag = np.sqrt(window['x']**2 + window['y']**2 + window['z']**2)
        
        # Magnitude do giroscópio em cada ponto da janela
        gyro_mag = np.sqrt(window['gx']**2 + window['gy']**2 + window['gz']**2)
        
        # Features estatísticas da janela (priorizar variação sobre magnitude)
        feature_vector = [
            accel_mag.std(),       # 1º: Variação do acelerômetro (MAIS IMPORTANTE!)
            accel_mag.mean(),      # 2º: Magnitude média do acelerômetro
            gyro_mag.std(),        # 3º: Variação do giroscópio
            gyro_mag.mean()        # 4º: Magnitude média do giroscópio
        ]
        
        features.append(feature_vector)
        
        # Timestamp médio da janela
        ts_medio = window['timestamp'].iloc[len(window)//2]
        timestamps.append(ts_medio)
    
    return np.array(features), np.array(timestamps)

def aplicar_kmeans(features, n_clusters=3):
    """
    Aplica K-means clustering nas features
    
    Args:
        features: Array de features (distâncias euclidianas)
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

def map_clusters_to_movement(labels, features):
    """
    Mapeia cada cluster para um rótulo de movimento baseado na VARIAÇÃO (std) do acelerômetro.
    A variação é o melhor indicador: parado tem variação baixa, movimento tem variação alta.
    
    Retorna um dicionário {cluster_id: movimento_str} e um array de rótulos por ponto.
    """
    unique_clusters = np.unique(labels)
    cluster_mean_std = {}
    
    # Usar a PRIMEIRA feature (std do acelerômetro) para ordenar - é o mais importante!
    for c in unique_clusters:
        cluster_mean_std[c] = features[labels == c, 0].mean()  # Feature 0 = std accel
    
    # Ordenar clusters por variação média (ascendente: menor variação = mais parado)
    ordered = sorted(cluster_mean_std.items(), key=lambda x: x[1])
    ordered_ids = [c for c, _ in ordered]
    
    # Rótulos para 3 clusters ordenados por variação (do menor para o maior)
    movement_names_3 = [
        'muito baixo movimento (parado)',  # Menor variação = parado/dormindo
        'baixo movimento',                  # Variação média = movimento leve
        'alto movimento'                    # Maior variação = movimento intenso
    ]
    
    if len(ordered_ids) == 3:
        assigned = {cid: movement_names_3[i] for i, cid in enumerate(ordered_ids)}
    else:
        # Gerar rótulos genéricos se não houver exatamente 3 clusters
        assigned = {cid: f'movimento_{i}' for i, cid in enumerate(ordered_ids)}
    
    labels_movement = np.array([assigned[c] for c in labels])
    
    # Debug: mostrar como os clusters foram mapeados
    print("\n   [DEBUG] Mapeamento por variacao (std acelerometro):")
    for i, (cid, std_val) in enumerate(ordered):
        label = movement_names_3[i] if len(ordered_ids) == 3 else f'movimento_{i}'
        print(f"      Cluster {cid} (std media: {std_val:.4f}) -> {label}")
    
    return assigned, labels_movement

def plotar_resultados(labels, pessoa_id, timestamps, cluster_name_map, movement_labels):
    """
    Plota os resultados do clustering com timestamps formatados
    
    Args:
        labels: Labels preditos pelo K-means
        pessoa_id: ID da pessoa
        timestamps: Array de timestamps
        cluster_name_map: Dicionário mapeando cluster_id para nome do movimento
        movement_labels: Array de rótulos de movimento por ponto
    """
    fig = plt.figure(figsize=(16, 6))
    
    # Plot 1: Labels ao longo do tempo (usar timestamps formatados no eixo X)
    ax1 = plt.subplot(1, 2, 1)
    
    # Definir cores por rótulo de movimento
    palette = {
        'muito baixo movimento (parado)': 'gray',
        'baixo movimento': 'blue',
        'alto movimento': 'red'
    }
    
    # Fallback para rótulos genéricos
    default_colors = ['tab:blue', 'tab:orange', 'tab:red', 'gray']
    colors = [palette.get(m, default_colors[i % len(default_colors)]) for i, m in enumerate(movement_labels)]
    
    ax1.scatter(timestamps, movement_labels, c=colors, alpha=0.7, s=40)
    ax1.set_xlabel('Hora (HH:MM:SS)', fontsize=12)
    ax1.set_ylabel('Rotulo de Movimento', fontsize=12)
    ax1.set_title(f'K-means Clustering - Pessoa {pessoa_id}\n(Baseado em variacao - sem sobreposicao de janelas)', fontsize=14)
    
    # Formatar eixo X para mostrar hora:minuto:segundo
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M:%S'))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=30, ha='right')
    ax1.grid(True, alpha=0.3)
    
    # Plot 2: Distribuição por rótulo de movimento
    ax2 = plt.subplot(1, 2, 2)
    unique_mov, counts = np.unique(movement_labels, return_counts=True)
    mov_colors = [palette.get(m, 'tab:blue') for m in unique_mov]
    ax2.bar(unique_mov, counts, color=mov_colors, alpha=0.7)
    ax2.set_xlabel('Rotulo de Movimento', fontsize=12)
    ax2.set_ylabel('Numero de Janelas', fontsize=12)
    ax2.set_title('Distribuicao por Rotulo de Movimento', fontsize=14)
    ax2.grid(True, alpha=0.3, axis='y')
    
    # Adicionar valores nas barras
    for i, count in enumerate(counts):
        ax2.text(i, count, str(count), ha='center', va='bottom', fontsize=11, fontweight='bold')
    
    plt.tight_layout()
    output_path = f'outputs/ClusterK3_euclidiano_ComDownsampling_individual/clustering_euclidean_pessoa_{pessoa_id}.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"\n   [OK] Grafico salvo como '{output_path}'")

def analisar_pessoa(pessoa_id, n_clusters=3):
    """
    Análise completa de clusterização para uma pessoa usando distância euclidiana
    
    Args:
        pessoa_id: ID da pessoa
        n_clusters: Número de clusters
    """
    print(f"\n{'='*60}")
    print(f"ANALISE - PESSOA {pessoa_id}")
    print(f"{'='*60}")
    
    # 1. Carregar dados
    print("\n[1/5] Carregando dados (downsampled)...")
    df_accel, df_gyro = carregar_dados_pessoa_downsampled(pessoa_id)
    print(f"   [OK] Acelerometro: {len(df_accel)} pontos")
    print(f"   [OK] Giroscopio: {len(df_gyro)} pontos")
    
    # 2. Sincronizar dados
    print("\n[2/5] Sincronizando dados de acelerometro e giroscopio...")
    df_combined = sincronizar_dados(df_accel, df_gyro)
    print(f"   [OK] Dados sincronizados: {len(df_combined)} pontos")
    
    # 3. Calcular features baseadas em janelas temporais
    print(f"\n[3/5] Calculando features em janelas temporais (SEM sobreposicao)...")
    features, timestamps = calcular_features_janela(df_combined, window_size=10)
    print(f"   [OK] {len(features)} janelas processadas (cada janela e unica)")
    print(f"   [OK] Features por janela: 4 (std_accel, mag_accel, std_gyro, mag_gyro)")
    print(f"   [OK] Variacao acelerometro media: {features[:, 0].mean():.4f} (feature principal)")
    
    # 4. Aplicar K-means
    print(f"\n[4/5] Aplicando K-means (k={n_clusters})...")
    kmeans, labels, features_normalized = aplicar_kmeans(features, n_clusters)
    print(f"   [OK] Clustering concluido")
    print(f"   [OK] Inercia: {kmeans.inertia_:.2f}")
    
    # 5. Plotar resultados
    print("\n[5/5] Gerando visualizacao e rotulando clusters por movimento...")
    cluster_map, movement_labels = map_clusters_to_movement(labels, features)
    plotar_resultados(labels, pessoa_id, timestamps, cluster_map, movement_labels)
    
    # Estatísticas
    print(f"\n{'='*60}")
    print("ESTATISTICAS")
    print(f"{'='*60}")
    
    # Mostrar mapeamento de clusters
    print("\nAnalise detalhada dos clusters:")
    for cluster_id, movimento in cluster_map.items():
        mask = labels == cluster_id
        count = mask.sum()
        std_accel_media = features[mask, 0].mean()     # Feature 0: variação acelerômetro
        mag_accel_media = features[mask, 1].mean()     # Feature 1: magnitude acelerômetro
        std_gyro_media = features[mask, 2].mean()      # Feature 2: variação giroscópio
        percentage = (count / len(labels)) * 100
        print(f"\n  Cluster {cluster_id} -> {movimento}")
        print(f"     Janelas: {count} ({percentage:.1f}%)")
        print(f"     Variacao acelerometro: {std_accel_media:.4f} (criterio principal)")
        print(f"     Magnitude acelerometro: {mag_accel_media:.4f}")
        print(f"     Variacao giroscopio: {std_gyro_media:.4f}")
    
    return df_combined, features, labels, kmeans, timestamps, movement_labels

def analisar_todas_pessoas(n_clusters=3):
    """
    Análise de clusterização para todas as pessoas (11 a 38)
    
    Args:
        n_clusters: Número de clusters
    """
    # IDs das pessoas disponíveis (downsampled)
    pessoas = list(range(11, 39))
    
    resultados = []
    sucessos = 0
    erros = 0
    
    print("\n" + "="*60)
    print("ANALISE DE TODAS AS PESSOAS (DOWNSAMPLED)")
    print("="*60)
    
    for pessoa_id in pessoas:
        try:
            df_combined, features, labels, kmeans, timestamps, movimento = analisar_pessoa(
                pessoa_id, n_clusters
            )
            resultados.append({
                'pessoa_id': pessoa_id,
                'data': df_combined,
                'features': features,
                'labels': labels,
                'kmeans': kmeans,
                'timestamps': timestamps,
                'movimento': movimento
            })
            sucessos += 1
        except Exception as e:
            print(f"\n[ERRO] Erro ao processar pessoa {pessoa_id}: {e}")
            erros += 1
            continue
    
    # Estatísticas finais
    print("\n" + "="*60)
    print("ESTATISTICAS FINAIS")
    print("="*60)
    print(f"Total de pessoas processadas: {len(resultados)}/28")
    print(f"Pessoas com sucesso: {sucessos}")
    print(f"Pessoas com erro: {erros}")
    
    if resultados:
        # Calcular distribuição geral
        dist_geral = {
            'muito baixo movimento (parado)': 0,
            'baixo movimento': 0,
            'alto movimento': 0
        }
        
        total_janelas = 0
        for r in resultados:
            movimento = r['movimento']
            unique, counts = np.unique(movimento, return_counts=True)
            for mov, count in zip(unique, counts):
                if mov in dist_geral:
                    dist_geral[mov] += count
                total_janelas += count
        
        # Normalizar distribuição
        for k in dist_geral:
            dist_geral[k] = dist_geral[k] / total_janelas if total_janelas > 0 else 0
        
        print("\nDISTRIBUICAO GERAL DOS CLUSTERS:")
        print(f"   [PARADO] Muito baixo movimento (parado): {dist_geral['muito baixo movimento (parado)']:.1%}")
        print(f"   [BAIXO] Baixo movimento: {dist_geral['baixo movimento']:.1%}")
        print(f"   [ALTO] Alto movimento: {dist_geral['alto movimento']:.1%}")
        
        print("\nCRITERIO DE ORDENACAO: Variacao (std_accel)")
        print("   - Menor variacao = 'parado' (deteccao de sono/inatividade)")
        print("   - Maior variacao = 'alto movimento'")
        
        # Mostrar exemplos de valores de std
        exemplo = resultados[0]
        features = exemplo['features']
        labels = exemplo['labels']
        
        print(f"\nEXEMPLO - Pessoa {exemplo['pessoa_id']} (valores de std_accel):")
        for i in range(3):
            mask = labels == i
            if mask.any():
                movimento = exemplo['movimento']
                label = movimento[mask][0]
                std_medio = features[mask, 0].mean()
                print(f"   Cluster {i} ({label}): std_accel medio = {std_medio:.3f}")
    
    return resultados

if __name__ == "__main__":
    print("\n" + "="*60)
    print("CLUSTERIZACAO K-MEANS - VARIACAO COMO CRITERIO")
    print("="*60)
    print(f"Numero de clusters: {N_CLUSTERS}")
    print(f"Metodo: Janelas temporais SEM sobreposicao")
    print(f"Features: std_accel (principal), mag_accel, std_gyro, mag_gyro")
    print(f"Criterio: Variacao do acelerometro (detecta parado vs movimento)")
    print(f"Dados: Downsampled (50% dos pontos originais)")
    print(f"Tamanho da janela: 10 pontos (SEM overlap)")
    
    # Opção: Processar todas as pessoas de uma vez
    print("\n" + "-"*60)
    print("Processando TODAS as pessoas (11-38)")
    print("-"*60)
    
    # Processar todas as pessoas (11 a 38)
    resultados = analisar_todas_pessoas(n_clusters=N_CLUSTERS)
    
    print("\n" + "="*60)
    print("ANALISE CONCLUIDA!")
    print("="*60)
    print(f"Total de pessoas processadas: {len(resultados)}")
    print(f"Graficos salvos em: outputs/ClusterK3_euclidiano_ComDownsampling_individual/")
