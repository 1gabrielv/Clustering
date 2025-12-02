import pandas as pd
import os

# Configurações
PESSOAS = list(range(11, 39))  # De 11 a 38
OUTPUT_DIR = 'DATA/Downsampling_data'
ACCEL_DIR = os.path.join(OUTPUT_DIR, 'ds_acelerometro')
GYRO_DIR = os.path.join(OUTPUT_DIR, 'ds_giroscopio')
DOWNSAMPLE_RATE = 2  # Pegar 1 a cada 2 linhas (reduz pela metade)

def criar_pasta_saida():
    """Cria as pastas de saída se não existirem"""
    for pasta in [OUTPUT_DIR, ACCEL_DIR, GYRO_DIR]:
        if not os.path.exists(pasta):
            os.makedirs(pasta)
            print(f"✓ Pasta '{pasta}' criada com sucesso!")
        else:
            print(f"✓ Pasta '{pasta}' já existe.")

def fazer_downsampling(arquivo_entrada, arquivo_saida, tipo_sensor):
    """
    Faz downsampling de um arquivo CSV pegando 1 linha a cada 2
    
    Args:
        arquivo_entrada: caminho do arquivo original
        arquivo_saida: caminho para salvar o arquivo com downsampling
        tipo_sensor: 'acelerometro' ou 'giroscopio'
    """
    try:
        # Ler o arquivo
        if tipo_sensor == 'acelerometro':
            # CSV com cabeçalho
            df = pd.read_csv(arquivo_entrada)
        else:
            # CSV do giroscópio
            df = pd.read_csv(arquivo_entrada)
        
        # Fazer downsampling: pegar linhas de índice 0, 2, 4, 6... (a cada 2)
        df_downsampled = df.iloc[::DOWNSAMPLE_RATE]
        
        # Salvar o arquivo processado
        df_downsampled.to_csv(arquivo_saida, index=False)
        
        pontos_original = len(df)
        pontos_final = len(df_downsampled)
        
        return pontos_original, pontos_final, True
        
    except FileNotFoundError:
        return 0, 0, False
    except Exception as e:
        print(f"   ⚠ Erro ao processar {arquivo_entrada}: {e}")
        return 0, 0, False

def processar_pessoa(pessoa_id):
    """
    Processa acelerômetro e giroscópio de uma pessoa
    
    Args:
        pessoa_id: ID da pessoa (11 a 38)
    """
    print(f"\n{'='*60}")
    print(f"Processando Pessoa {pessoa_id}")
    print(f"{'='*60}")
    
    resultados = {'acelerometro': False, 'giroscopio': False}
    
    # Processar acelerômetro
    accel_input = f'acelerometro/acelerometro_{pessoa_id}.csv'
    accel_output = os.path.join(ACCEL_DIR, f'ds_acelerometro_{pessoa_id}.csv')
    
    print(f"\n[1/2] Acelerômetro...")
    pontos_orig, pontos_final, sucesso = fazer_downsampling(accel_input, accel_output, 'acelerometro')
    
    if sucesso:
        print(f"   ✓ {accel_input}")
        print(f"   → {accel_output}")
        print(f"   Pontos: {pontos_orig} → {pontos_final} (redução: {(1 - pontos_final/pontos_orig)*100:.1f}%)")
        resultados['acelerometro'] = True
    else:
        print(f"   ✗ Arquivo não encontrado: {accel_input}")
    
    # Processar giroscópio
    gyro_input = f'giroscopio/giroscopio_{pessoa_id}.csv'
    gyro_output = os.path.join(GYRO_DIR, f'ds_giroscopio_{pessoa_id}.csv')
    
    print(f"\n[2/2] Giroscópio...")
    pontos_orig, pontos_final, sucesso = fazer_downsampling(gyro_input, gyro_output, 'giroscopio')
    
    if sucesso:
        print(f"   ✓ {gyro_input}")
        print(f"   → {gyro_output}")
        print(f"   Pontos: {pontos_orig} → {pontos_final} (redução: {(1 - pontos_final/pontos_orig)*100:.1f}%)")
        resultados['giroscopio'] = True
    else:
        print(f"   ✗ Arquivo não encontrado: {gyro_input}")
    
    return resultados

def main():
    """Função principal"""
    print("\n" + "="*60)
    print("DOWNSAMPLING DE DADOS - ACELERÔMETRO E GIROSCÓPIO")
    print("="*60)
    print(f"Taxa de downsampling: 1 a cada {DOWNSAMPLE_RATE} linhas")
    print(f"Pessoas: {PESSOAS[0]} a {PESSOAS[-1]}")
    print(f"Pasta de saída: {OUTPUT_DIR}/")
    
    # Criar pasta de saída
    print(f"\n{'='*60}")
    print("Criando pasta de saída...")
    print(f"{'='*60}")
    criar_pasta_saida()
    
    # Estatísticas
    total_pessoas = len(PESSOAS)
    pessoas_processadas = 0
    acelerometros_ok = 0
    giroscopios_ok = 0
    
    # Processar cada pessoa
    for pessoa_id in PESSOAS:
        resultados = processar_pessoa(pessoa_id)
        
        if resultados['acelerometro'] or resultados['giroscopio']:
            pessoas_processadas += 1
        
        if resultados['acelerometro']:
            acelerometros_ok += 1
        
        if resultados['giroscopio']:
            giroscopios_ok += 1
    
    # Sumário final
    print(f"\n\n{'='*60}")
    print("SUMÁRIO FINAL")
    print(f"{'='*60}")
    print(f"Total de pessoas: {total_pessoas}")
    print(f"Pessoas processadas: {pessoas_processadas}")
    print(f"Arquivos de acelerômetro criados: {acelerometros_ok}")
    print(f"Arquivos de giroscópio criados: {giroscopios_ok}")
    print(f"\n✓ Arquivos salvos em:")
    print(f"   - {ACCEL_DIR}/")
    print(f"   - {GYRO_DIR}/")
    print(f"{'='*60}")

if __name__ == "__main__":
    main()
