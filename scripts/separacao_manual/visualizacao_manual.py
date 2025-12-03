"""
Script para visualização e separação manual de dados de acelerômetro/giroscópio
Plota os dados ao longo do tempo (eixo X em horas) e permite identificar períodos de movimento vs parado
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path

# Configurações
PESSOA_ID = 11  # ID da pessoa a analisar
DATA_DIR = Path("DATA/Downsampling_data")

def carregar_dados_pessoa(pessoa_id):
    """
    Carrega dados de acelerômetro e giroscópio de uma pessoa específica
    
    Args:
        pessoa_id: ID da pessoa (número)
    
    Returns:
        tuple: (DataFrame acelerômetro, DataFrame giroscópio)
    """
    accel_file = DATA_DIR / "ds_acelerometro" / f"ds_acelerometro_{pessoa_id}.csv"
    gyro_file = DATA_DIR / "ds_giroscopio" / f"ds_giroscopio_{pessoa_id}.csv"
    
    # Carregar dados
    df_accel = pd.read_csv(accel_file)
    df_accel['timestamp'] = pd.to_datetime(df_accel['timestamp'])
    
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

def calcular_magnitude(df):
    """
    Calcula a magnitude do vetor de aceleração
    
    Args:
        df: DataFrame com colunas x, y, z
    
    Returns:
        Series: Magnitude do vetor
    """
    return np.sqrt(df['x']**2 + df['y']**2 + df['z']**2)

def plotar_dados_acelerometro(df, pessoa_id):
    """
    Plota os dados do acelerômetro em um único gráfico
    
    Args:
        df: DataFrame com dados sincronizados
        pessoa_id: ID da pessoa
    """
    fig, ax = plt.subplots(1, 1, figsize=(16, 6))
    fig.suptitle(f'Dados do Acelerômetro - Pessoa {pessoa_id}', fontsize=16, fontweight='bold')
    
    # Plotar os 3 eixos
    ax.plot(df['timestamp'], df['x'], color='blue', linewidth=0.8, alpha=0.7, label='X')
    ax.plot(df['timestamp'], df['y'], color='orange', linewidth=0.8, alpha=0.7, label='Y')
    ax.plot(df['timestamp'], df['z'], color='green', linewidth=0.8, alpha=0.7, label='Z')
    
    ax.set_ylabel('Aceleração', fontsize=11)
    ax.set_xlabel('Amostras', fontsize=12)
    ax.set_title('Dados do Acelerômetro', fontsize=12)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # Rotacionar labels do eixo X
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Salvar gráfico
    output_dir = Path("outputs") / "separacao_manual"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"acelerometro_pessoa_{pessoa_id}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"   [OK] Grafico acelerometro salvo: {output_path}")
    
    plt.close()

def plotar_dados_giroscopio(df, pessoa_id):
    """
    Plota os dados do giroscópio em um único gráfico
    
    Args:
        df: DataFrame com dados sincronizados
        pessoa_id: ID da pessoa
    """
    fig, ax = plt.subplots(1, 1, figsize=(16, 6))
    fig.suptitle(f'Dados do Giroscópio - Pessoa {pessoa_id}', fontsize=16, fontweight='bold')
    
    # Plotar os 3 eixos
    ax.plot(df['timestamp'], df['gx'], color='blue', linewidth=0.8, alpha=0.7, label='X')
    ax.plot(df['timestamp'], df['gy'], color='orange', linewidth=0.8, alpha=0.7, label='Y')
    ax.plot(df['timestamp'], df['gz'], color='green', linewidth=0.8, alpha=0.7, label='Z')
    
    ax.set_ylabel('Giroscópio', fontsize=11)
    ax.set_xlabel('Amostras', fontsize=12)
    ax.set_title('Dados do Giroscópio', fontsize=12)
    ax.legend(loc='upper left', fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # Rotacionar labels do eixo X
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Salvar gráfico
    output_dir = Path("outputs") / "separacao_manual"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"giroscopio_pessoa_{pessoa_id}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"   [OK] Grafico giroscopio salvo: {output_path}")
    
    plt.close()

def separar_manual_movimento(df, threshold_variacao=1.0):
    """
    Separa automaticamente períodos de movimento vs parado baseado em variação
    (pode ser ajustado manualmente depois)
    
    Args:
        df: DataFrame com dados sincronizados
        threshold_variacao: Limiar de variação para considerar movimento
    
    Returns:
        DataFrame: Dados com coluna 'estado' (parado ou movimento)
    """
    # Calcular magnitude
    magnitude = calcular_magnitude(df)
    
    # Calcular variação em janelas móveis
    window_size = 50 # ~50 amostras por janela
    variacao = magnitude.rolling(window=window_size, center=True).std()
    
    # Classificar baseado no threshold
    df['magnitude'] = magnitude
    df['variacao'] = variacao
    df['estado'] = df['variacao'].apply(
        lambda x: 'movimento' if x > threshold_variacao else 'parado'
    )
    
    # Estatísticas
    total_pontos = len(df)
    parado = (df['estado'] == 'parado').sum()
    movimento = (df['estado'] == 'movimento').sum()
    
    print("\n" + "="*60)
    print("ESTATISTICAS DA SEPARACAO")
    print("="*60)
    print(f"Total de pontos: {total_pontos}")
    print(f"Parado: {parado} pontos ({parado/total_pontos*100:.1f}%)")
    print(f"Movimento: {movimento} pontos ({movimento/total_pontos*100:.1f}%)")
    print(f"Threshold de variacao usado: {threshold_variacao}")
    print("="*60)
    
    return df

def plotar_separacao(df, pessoa_id):
    """
    Plota os dados com a separação parado/movimento destacada
    
    Args:
        df: DataFrame com coluna 'estado'
        pessoa_id: ID da pessoa
    """
    fig, axes = plt.subplots(2, 1, figsize=(16, 8))
    fig.suptitle(f'Separação Manual: Parado vs Movimento - Pessoa {pessoa_id}', 
                 fontsize=16, fontweight='bold')
    
    # Plot 1: Magnitude com cores por estado
    ax1 = axes[0]
    
    # Plotar parado em cinza
    mask_parado = df['estado'] == 'parado'
    ax1.scatter(df.loc[mask_parado, 'timestamp'], 
                df.loc[mask_parado, 'magnitude'],
                c='gray', s=5, alpha=0.6, label='Parado')
    
    # Plotar movimento em vermelho
    mask_movimento = df['estado'] == 'movimento'
    ax1.scatter(df.loc[mask_movimento, 'timestamp'], 
                df.loc[mask_movimento, 'magnitude'],
                c='red', s=5, alpha=0.6, label='Movimento')
    
    ax1.set_ylabel('Magnitude (m/s²)', fontsize=11)
    ax1.set_title('Magnitude do Acelerômetro', fontsize=12)
    ax1.legend(loc='upper right')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # Plot 2: Variação (critério de separação)
    ax2 = axes[1]
    ax2.plot(df['timestamp'], df['variacao'], color='blue', linewidth=0.8, alpha=0.7)
    ax2.set_ylabel('Variação (desvio padrão)', fontsize=11)
    ax2.set_xlabel('Tempo (HH:MM)', fontsize=12)
    ax2.set_title('Variação da Magnitude (critério de separação)', fontsize=12)
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    
    # Rotacionar labels
    for ax in axes:
        plt.setp(ax.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Salvar gráfico
    output_dir = Path("outputs") / "separacao_manual"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"separacao_pessoa_{pessoa_id}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n[OK] Grafico de separacao salvo em: {output_path}")
    
    plt.close()

def analisar_pessoa(pessoa_id):
    """
    Analisa uma pessoa específica
    """
    print(f"\n{'='*60}")
    print(f"PESSOA {pessoa_id}")
    print(f"{'='*60}")
    
    try:
        # 1. Carregar dados
        print("\n[1/3] Carregando dados...")
        df_accel, df_gyro = carregar_dados_pessoa(pessoa_id)
        print(f"   [OK] Acelerometro: {len(df_accel)} pontos")
        print(f"   [OK] Giroscopio: {len(df_gyro)} pontos")
        
        # 2. Sincronizar dados
        print("\n[2/3] Sincronizando dados...")
        df_combined = sincronizar_dados(df_accel, df_gyro)
        print(f"   [OK] Dados sincronizados: {len(df_combined)} pontos")
        
        # 3. Plotar dados brutos do acelerômetro
        print("\n[3/3] Gerando graficos...")
        plotar_dados_acelerometro(df_combined, pessoa_id)
        plotar_dados_giroscopio(df_combined, pessoa_id)
        
        return True
    except Exception as e:
        print(f"\n[ERRO] Falha ao processar pessoa {pessoa_id}: {e}")
        return False

def main():
    """
    Função principal - processa todas as pessoas de 11 a 38
    """
    print("="*60)
    print("VISUALIZACAO DE DADOS - ACELEROMETRO E GIROSCOPIO")
    print("="*60)
    print(f"Processando pessoas: 11 a 38")
    print(f"Diretorio de dados: {DATA_DIR}")
    print("="*60)
    
    sucessos = 0
    erros = 0
    
    # Processar todas as pessoas de 11 a 38
    for pessoa_id in range(11, 39):
        resultado = analisar_pessoa(pessoa_id)
        if resultado:
            sucessos += 1
        else:
            erros += 1
    
    print("\n" + "="*60)
    print("ANALISE CONCLUIDA!")
    print("="*60)
    print(f"Total processado: {sucessos + erros}")
    print(f"Sucessos: {sucessos}")
    print(f"Erros: {erros}")
    print(f"\nGraficos salvos em: outputs/separacao_manual/")

if __name__ == "__main__":
    main()
