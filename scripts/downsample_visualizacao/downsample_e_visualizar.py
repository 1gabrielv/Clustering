"""
Script para fazer downsample dos dados (10x menor) e visualizar DataFrame
com tempo e valores de acelerômetro (x, y, z)
"""

import pandas as pd
from pathlib import Path

# Configurações
DATA_DIR = Path("DATA/Downsampling_data")
OUTPUT_DIR = Path("DATA/SuperDownsample_Data")

def fazer_downsample(df, fator=10):
    """
    Faz downsample dos dados por um fator especificado
    
    Args:
        df: DataFrame original
        fator: Fator de redução (padrão: 10)
    
    Returns:
        DataFrame com downsample aplicado
    """
    # Pega uma amostra a cada 'fator' linhas
    df_downsampled = df.iloc[::fator].reset_index(drop=True)
    return df_downsampled

def processar_acelerometro(pessoa_id):
    """
    Processa dados do acelerômetro de uma pessoa:
    1. Carrega os dados originais
    2. Faz downsample 10x
    3. Salva os dados reduzidos
    4. Retorna DataFrame para visualização
    
    Args:
        pessoa_id: ID da pessoa
    
    Returns:
        DataFrame com timestamp, x, y, z
    """
    # Carregar dados originais
    accel_file = DATA_DIR / "ds_acelerometro" / f"ds_acelerometro_{pessoa_id}.csv"
    df_original = pd.read_csv(accel_file)
    
    print(f"\nPessoa {pessoa_id}:")
    print(f"  Dados originais: {len(df_original)} amostras")
    
    # Fazer downsample 10x
    df_downsampled = fazer_downsample(df_original, fator=10)
    print(f"  Após downsample 10x: {len(df_downsampled)} amostras")
    
    # Criar diretório de saída se não existir
    output_dir = OUTPUT_DIR / "ds_acelerometro_10x"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Salvar dados com downsample
    output_file = output_dir / f"ds_acelerometro_{pessoa_id}_10x.csv"
    df_downsampled.to_csv(output_file, index=False)
    print(f"  Salvo em: {output_file}")
    
    return df_downsampled

def processar_giroscopio(pessoa_id):
    """
    Processa dados do giroscópio de uma pessoa (mesmo processo do acelerômetro)
    
    Args:
        pessoa_id: ID da pessoa
    
    Returns:
        DataFrame com timestamp, x, y, z
    """
    # Carregar dados originais
    gyro_file = DATA_DIR / "ds_giroscopio" / f"ds_giroscopio_{pessoa_id}.csv"
    df_original = pd.read_csv(gyro_file)
    
    # Fazer downsample 10x
    df_downsampled = fazer_downsample(df_original, fator=10)
    
    # Criar diretório de saída se não existir
    output_dir = OUTPUT_DIR / "ds_giroscopio_10x"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Salvar dados com downsample
    output_file = output_dir / f"ds_giroscopio_{pessoa_id}_10x.csv"
    df_downsampled.to_csv(output_file, index=False)
    
    return df_downsampled

def visualizar_dataframe(df, tipo_sensor="Acelerômetro", num_linhas=20):
    """
    Visualiza o DataFrame com formatação bonita
    
    Args:
        df: DataFrame para visualizar
        tipo_sensor: Nome do sensor ("Acelerômetro" ou "Giroscópio")
        num_linhas: Número de linhas para exibir
    """
    print("\n" + "="*80)
    print(f"DATAFRAME - {tipo_sensor.upper()}")
    print("="*80)
    
    # Configurar pandas para exibir todas as colunas
    pd.set_option('display.max_columns', None)
    pd.set_option('display.width', None)
    pd.set_option('display.max_colwidth', None)
    
    # Exibir primeiras linhas
    print(f"\nPrimeiras {num_linhas} linhas:")
    print(df.head(num_linhas).to_string())
    
    # Estatísticas básicas
    print("\n" + "-"*80)
    print("ESTATÍSTICAS:")
    print("-"*80)
    print(f"Total de amostras: {len(df)}")
    print(f"\nResumo estatístico:")
    print(df[['x', 'y', 'z']].describe())

def main():
    """
    Função principal - processa todas as pessoas automaticamente
    """
    print("="*80)
    print("DOWNSAMPLE E VISUALIZAÇÃO DE DADOS (SUPER DOWNsample)")
    print("="*80)
    print("Reduzindo dados em 10x e salvando em DATA/SuperDownsample_Data...")
    print("="*80)

    # Processar todas as pessoas (11 a 38)
    print("\nProcessando todas as pessoas (11-38)...")
    for pid in range(11, 39):
        print(f"\n--- Pessoa {pid} ---")
        try:
            df_accel = processar_acelerometro(pid)
            df_gyro = processar_giroscopio(pid)
        except Exception as e:
            print(f"  [ERRO] Falha ao processar pessoa {pid}: {e}")

    print("\n" + "="*80)
    print("CONCLUÍDO! Todos os arquivos salvos em:")
    print(OUTPUT_DIR)
    print("="*80)

if __name__ == "__main__":
    main()
