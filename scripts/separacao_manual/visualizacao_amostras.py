"""
Script para visualização simples de dados de acelerômetro/giroscópio
Mostra apenas os 3 eixos (X, Y, Z) em um gráfico simples
"""

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# Configurações
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
    df_gyro = pd.read_csv(gyro_file)
    
    return df_accel, df_gyro

def plotar_dados_acelerometro(df, pessoa_id):
    """
    Plota os dados do acelerômetro - gráfico simples com X, Y, Z
    
    Args:
        df: DataFrame com dados do acelerômetro
        pessoa_id: ID da pessoa
    """
    plt.figure(figsize=(12, 6))
    
    plt.plot(df['x'], label='X')
    plt.plot(df['y'], label='Y')
    plt.plot(df['z'], label='Z')
    
    plt.title(f"Dados do Acelerômetro - Pessoa {pessoa_id}")
    plt.xlabel("Amostras")
    plt.ylabel("Aceleração")
    plt.legend()
    plt.grid(True)
    
    # Salvar gráfico
    output_dir = Path("outputs") / "visualizacao_amostras"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"acelerometro_pessoa_{pessoa_id}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"   [OK] Grafico acelerometro salvo: {output_path}")
    
    plt.close()

def plotar_dados_giroscopio(df, pessoa_id):
    """
    Plota os dados do giroscópio - gráfico simples com X, Y, Z
    
    Args:
        df: DataFrame com dados do giroscópio
        pessoa_id: ID da pessoa
    """
    plt.figure(figsize=(120, 60))
    
    plt.plot(df['x'], label='X')
    plt.plot(df['y'], label='Y')
    plt.plot(df['z'], label='Z')
    
    plt.title(f"Dados do Giroscópio - Pessoa {pessoa_id}")
    plt.xlabel("Amostras")
    plt.ylabel("Giroscópio")
    plt.legend()
    plt.grid(True)
    
    # Salvar gráfico
    output_dir = Path("outputs") / "visualizacao_amostras"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"giroscopio_pessoa_{pessoa_id}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"   [OK] Grafico giroscopio salvo: {output_path}")
    
    plt.close()

def analisar_pessoa(pessoa_id):
    """
    Processa e plota dados de uma pessoa específica
    
    Args:
        pessoa_id: ID da pessoa
    
    Returns:
        bool: True se processado com sucesso, False caso contrário
    """
    try:
        print(f"\n{'='*60}")
        print(f"PESSOA {pessoa_id}")
        print('='*60)
        
        # Carregar dados
        print("\n[1/2] Carregando dados...")
        df_accel, df_gyro = carregar_dados_pessoa(pessoa_id)
        print(f"   [OK] Acelerometro: {len(df_accel)} pontos")
        print(f"   [OK] Giroscopio: {len(df_gyro)} pontos")
        
        # Gerar gráficos
        print("\n[2/2] Gerando graficos...")
        plotar_dados_acelerometro(df_accel, pessoa_id)
        plotar_dados_giroscopio(df_gyro, pessoa_id)
        
        return True
        
    except Exception as e:
        print(f"\n[ERRO] Falha ao processar pessoa {pessoa_id}: {str(e)}")
        return False

def main():
    """
    Função principal - processa todas as pessoas
    """
    print('='*60)
    print("VISUALIZACAO SIMPLES - ACELEROMETRO E GIROSCOPIO")
    print('='*60)
    print("Processando pessoas: 11 a 38")
    print(f"Diretorio de dados: {DATA_DIR}")
    print('='*60)
    
    # Range de pessoas a processar
    pessoas = range(11, 39)  # 11 a 38
    
    sucessos = 0
    erros = 0
    
    for pessoa_id in pessoas:
        if analisar_pessoa(pessoa_id):
            sucessos += 1
        else:
            erros += 1
    
    # Resumo final
    print("\n" + "="*60)
    print("ANALISE CONCLUIDA!")
    print("="*60)
    print(f"Total processado: {len(pessoas)}")
    print(f"Sucessos: {sucessos}")
    print(f"Erros: {erros}")
    print(f"\nGraficos salvos em: outputs/visualizacao_amostras/")

if __name__ == "__main__":
    main()
