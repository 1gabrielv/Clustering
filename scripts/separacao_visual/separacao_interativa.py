"""
Script para separação interativa de períodos DORMINDO vs ACORDADO
Permite visualizar os dados e marcar manualmente os períodos de sono
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from pathlib import Path
from datetime import datetime
import importlib.util

# Configurações
DATA_DIR = Path("DATA/SemDownsampling_data")
OUTPUT_BASE = Path("outputs/separacao_visual")

def carregar_dados_pessoa(pessoa_id):
    """Carrega dados de acelerômetro e giroscópio"""
    accel_file = DATA_DIR / "acelerometro" / f"acelerometro_{pessoa_id}.csv"
    gyro_file = DATA_DIR / "giroscopio" / f"giroscopio_{pessoa_id}.csv"
    
    df_accel = pd.read_csv(accel_file)
    df_accel['timestamp'] = pd.to_datetime(df_accel['timestamp'])
    
    df_gyro = pd.read_csv(gyro_file)
    df_gyro['timestamp'] = pd.to_datetime(df_gyro['timestamp'])
    
    return df_accel, df_gyro

def plotar_dados_para_analise(df_accel, df_gyro, pessoa_id):
    """Plota dados para análise visual - X, Y, Z separados por cor"""
    fig, axes = plt.subplots(2, 1, figsize=(16, 10))
    
    # Acelerômetro - X, Y, Z separados
    ax1 = axes[0]
    ax1.plot(df_accel['timestamp'], df_accel['x'], 'orange', linewidth=0.5, alpha=0.7, label='X')
    ax1.plot(df_accel['timestamp'], df_accel['y'], 'blue', linewidth=0.5, alpha=0.7, label='Y')
    ax1.plot(df_accel['timestamp'], df_accel['z'], 'green', linewidth=0.5, alpha=0.7, label='Z')
    ax1.set_title(f'Dados do Acelerômetro - Pessoa {pessoa_id}', fontsize=14, fontweight='bold')
    ax1.set_ylabel('Aceleração', fontsize=12)
    ax1.set_xlabel('Amostras', fontsize=12)
    ax1.legend(loc='upper left')
    ax1.grid(True, alpha=0.3)
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    # Giroscópio - X, Y, Z separados
    ax2 = axes[1]
    ax2.plot(df_gyro['timestamp'], df_gyro['x'], 'orange', linewidth=0.5, alpha=0.7, label='X')
    ax2.plot(df_gyro['timestamp'], df_gyro['y'], 'blue', linewidth=0.5, alpha=0.7, label='Y')
    ax2.plot(df_gyro['timestamp'], df_gyro['z'], 'green', linewidth=0.5, alpha=0.7, label='Z')
    ax2.set_title(f'Dados do Giroscópio - Pessoa {pessoa_id}', fontsize=14, fontweight='bold')
    ax2.set_ylabel('Rotação', fontsize=12)
    ax2.set_xlabel('Amostras', fontsize=12)
    ax2.legend(loc='upper left')
    ax2.grid(True, alpha=0.3)
    ax2.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax2.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.setp(ax2.xaxis.get_majorticklabels(), rotation=45, ha='right')
    
    plt.tight_layout()
    
    # Salvar gráfico
    output_dir = OUTPUT_BASE / f"pessoa_{pessoa_id}"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"analise_visual_pessoa_{pessoa_id}.png"
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"\n[OK] Gráfico salvo: {output_path}")
    
    plt.show()
    plt.close()

def obter_periodos_sono(df_accel):
    """Interface para marcar períodos de sono manualmente"""
    print("\n" + "="*80)
    print("MARCAÇÃO DE PERÍODOS DE SONO")
    print("="*80)
    
    # Mostrar informações do período
    inicio_dados = df_accel['timestamp'].min()
    fim_dados = df_accel['timestamp'].max()
    
    print(f"\nPeríodo total dos dados:")
    print(f"  Início: {inicio_dados.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Fim:    {fim_dados.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"  Duração: {(fim_dados - inicio_dados).total_seconds() / 3600:.1f} horas")
    
    periodos_sono = []
    
    print("\n" + "-"*80)
    print("Digite os períodos de SONO no formato HH:MM")
    print("Pressione ENTER sem digitar nada para finalizar")
    print("-"*80)
    
    periodo_num = 1
    while True:
        print(f"\n--- Período de Sono #{periodo_num} ---")
        
        # Obter hora de início do sono
        inicio_str = input("  Hora de INÍCIO do sono (HH:MM ou HHMM) ou ENTER para finalizar: ").strip()
        if not inicio_str:
            break
        
        # Obter hora de fim do sono
        fim_str = input("  Hora de FIM do sono (HH:MM or HHMM): ").strip()
        if not fim_str:
            print("  [AVISO] Período incompleto. Ignorando...")
            continue

        def _normalize_time_input(s: str) -> str:
            """Normaliza entradas de tempo.

            Aceita formatos 'HH:MM' ou 'HHMM' (também 'HMM' será padronizado para '0H:MM').
            Retorna string no formato 'HH:MM' ou levanta ValueError.
            """
            s = str(s).strip()
            if not s:
                raise ValueError('Entrada vazia')

            # Se já contém ':', validar e padronizar
            if ':' in s:
                parts = s.split(':')
                if len(parts) != 2 or not parts[0].isdigit() or not parts[1].isdigit():
                    raise ValueError('Formato com dois campos separados por ":" inválido')
                h = parts[0].zfill(2)
                m = parts[1].zfill(2)
                return f"{h}:{m}"

            # Caso sem ':', extrair apenas dígitos
            digits = ''.join(ch for ch in s if ch.isdigit())
            if len(digits) == 4:
                return digits[:2] + ':' + digits[2:]
            if len(digits) == 3:
                digits = digits.zfill(4)
                return digits[:2] + ':' + digits[2:]

            raise ValueError('Formato inválido. Use HH:MM ou HHMM (ex.: 23:15 ou 2315)')

        try:
            # Converter para datetime usando a data do dataset
            data_base = inicio_dados.date()

            inicio_norm = _normalize_time_input(inicio_str)
            fim_norm = _normalize_time_input(fim_str)

            inicio_sono = pd.to_datetime(f"{data_base} {inicio_norm}", format="%Y-%m-%d %H:%M")
            fim_sono = pd.to_datetime(f"{data_base} {fim_norm}", format="%Y-%m-%d %H:%M")
            
            # Se fim < início, assumir que é no dia seguinte
            if fim_sono <= inicio_sono:
                from datetime import timedelta
                fim_sono = fim_sono + timedelta(days=1)
            
            periodos_sono.append((inicio_sono, fim_sono))
            print(f"  [OK] Período adicionado: {inicio_sono.strftime('%H:%M')} até {fim_sono.strftime('%H:%M')}")
            periodo_num += 1

        except Exception as e:
            print(f"  [ERRO] Formato inválido: {e}")
            print("  Use o formato HH:MM (ex: 22:30) ou HHMM (ex: 2230).")
    
    return periodos_sono

def separar_dados(df_accel, df_gyro, periodos_sono):
    """Separa dados em DORMINDO e ACORDADO"""
    # Inicializar coluna de estado
    df_accel['estado'] = 'ACORDADO'
    df_gyro['estado'] = 'ACORDADO'
    
    # Marcar períodos de sono
    for inicio, fim in periodos_sono:
        # Acelerômetro
        mask_accel = (df_accel['timestamp'] >= inicio) & (df_accel['timestamp'] <= fim)
        df_accel.loc[mask_accel, 'estado'] = 'DORMINDO'
        
        # Giroscópio
        mask_gyro = (df_gyro['timestamp'] >= inicio) & (df_gyro['timestamp'] <= fim)
        df_gyro.loc[mask_gyro, 'estado'] = 'DORMINDO'
    
    # Criar DataFrames separados
    accel_dormindo = df_accel[df_accel['estado'] == 'DORMINDO'].copy()
    accel_acordado = df_accel[df_accel['estado'] == 'ACORDADO'].copy()
    
    gyro_dormindo = df_gyro[df_gyro['estado'] == 'DORMINDO'].copy()
    gyro_acordado = df_gyro[df_gyro['estado'] == 'ACORDADO'].copy()
    
    # Remover coluna auxiliar
    for df in [accel_dormindo, accel_acordado, gyro_dormindo, gyro_acordado]:
        if 'estado' in df.columns:
            df.drop('estado', axis=1, inplace=True)
    
    return accel_dormindo, accel_acordado, gyro_dormindo, gyro_acordado

def salvar_dados_separados(pessoa_id, accel_dormindo, accel_acordado, gyro_dormindo, gyro_acordado, periodos_sono):
    """Salva dados separados em estrutura organizada de pastas"""
    pessoa_dir = OUTPUT_BASE / f"pessoa_{pessoa_id}"
    
    # Criar estrutura de pastas (padrão: dados<ID>)
    dados_dir = pessoa_dir / f"dados{pessoa_id}"
    acordado_dir = dados_dir / "acordado"
    dormindo_dir = dados_dir / "dormindo"
    periodos_dir = pessoa_dir / "periodos_sono"
    
    for dir_path in [acordado_dir, dormindo_dir, periodos_dir]:
        dir_path.mkdir(parents=True, exist_ok=True)
    
    # Salvar dados ACORDADO (com sufixo _acordado)
    accel_acordado.to_csv(acordado_dir / f"acelerometro{pessoa_id}_acordado.csv", index=False)
    gyro_acordado.to_csv(acordado_dir / f"giroscopio{pessoa_id}_acordado.csv", index=False)
    
    # Salvar dados DORMINDO (com sufixo _dormindo)
    accel_dormindo.to_csv(dormindo_dir / f"acelerometro{pessoa_id}_dormindo.csv", index=False)
    gyro_dormindo.to_csv(dormindo_dir / f"giroscopio{pessoa_id}_dormindo.csv", index=False)
    
    # Salvar períodos de sono (arquivo com ID)
    with open(periodos_dir / f"periodos_sono{pessoa_id}.txt", 'w', encoding='utf-8') as f:
        f.write(f"Períodos de sono - Pessoa {pessoa_id}\n")
        f.write("="*50 + "\n")
        for i, (inicio, fim) in enumerate(periodos_sono, 1):
            f.write(f"Período {i}: {inicio.strftime('%H:%M')} até {fim.strftime('%H:%M')}\n")
    
    print("\n" + "="*80)
    print("ARQUIVOS SALVOS:")
    print("="*80)
    print(f"  Pasta raiz: {pessoa_dir}")
    print(f"\n  {dados_dir.name}/acordado/:")
    print(f"    - acelerometro{pessoa_id}_acordado.csv ({len(accel_acordado)} amostras)")
    print(f"    - giroscopio{pessoa_id}_acordado.csv ({len(gyro_acordado)} amostras)")
    print(f"\n  {dados_dir.name}/dormindo/:")
    print(f"    - acelerometro{pessoa_id}_dormindo.csv ({len(accel_dormindo)} amostras)")
    print(f"    - giroscopio{pessoa_id}_dormindo.csv ({len(gyro_dormindo)} amostras)")
    print(f"\n  periodos_sono/:")
    print(f"    - periodos_sono{pessoa_id}.txt")


def gerar_visualizacao_final(df_accel, df_gyro, periodos_sono, pessoa_id):
    """Gera o gráfico final usando `visualizar_separacao.py`.

    periodos_sono: lista de tuplas (datetime inicio, datetime fim)
    """
    # construir lista no formato esperado pela visualização: [("HH:MM","HH:MM"), ...]
    periodos_str = [(p[0].strftime('%H:%M'), p[1].strftime('%H:%M')) for p in periodos_sono]

    # localizar o arquivo visualizar_separacao.py
    base_dir = Path(__file__).parent
    vis_path = base_dir / 'visualizar_separacao.py'
    if not vis_path.exists():
        print(f"Arquivo de visualização não encontrado: {vis_path}")
        return

    spec = importlib.util.spec_from_file_location('visualizar_separacao', str(vis_path))
    vis_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(vis_mod)

    # chamar a função de plotagem (agora recebe apenas acelerômetro + períodos)
    try:
        vis_mod.plotar_visualizacao(df_accel, periodos_str, pessoa_id)
    except Exception as e:
        print(f"Erro ao gerar visualização final: {e}")

def processar_pessoa(pessoa_id):
    """Processa uma pessoa completa"""
    print("\n" + "="*80)
    print(f"PESSOA {pessoa_id}")
    print("="*80)
    
    # 1. Carregar dados
    print("\n[1/4] Carregando dados...")
    df_accel, df_gyro = carregar_dados_pessoa(pessoa_id)
    print(f"  [OK] Acelerômetro: {len(df_accel)} amostras")
    print(f"  [OK] Giroscópio: {len(df_gyro)} amostras")
    
    # 2. Plotar para análise
    print("\n[2/4] Gerando gráfico para análise visual...")
    plotar_dados_para_analise(df_accel, df_gyro, pessoa_id)
    
    # 3. Obter períodos de sono
    print("\n[3/4] Marcação de períodos de sono...")
    periodos_sono = obter_periodos_sono(df_accel)
    
    if not periodos_sono:
        print("\n[AVISO] Nenhum período de sono foi marcado. Abortando...")
        return
    
    # 4. Separar e salvar
    print("\n[4/4] Separando dados e salvando...")
    accel_dormindo, accel_acordado, gyro_dormindo, gyro_acordado = separar_dados(
        df_accel, df_gyro, periodos_sono
    )
    salvar_dados_separados(pessoa_id, accel_dormindo, accel_acordado, gyro_dormindo, gyro_acordado, periodos_sono)

    # Gerar visualização final automaticamente
    print('\n[5/5] Gerando gráfico final com períodos de sono...')
    gerar_visualizacao_final(df_accel, df_gyro, periodos_sono, pessoa_id)
    
    print("\n" + "="*80)
    print(f"PESSOA {pessoa_id} - CONCLUÍDA!")
    print("="*80)

def main():
    """Função principal"""
    print("="*80)
    print("SEPARAÇÃO INTERATIVA - DORMINDO vs ACORDADO")
    print("="*80)
    print("\nEste script permite separar manualmente os períodos de sono.")
    print("Você verá um gráfico e depois poderá marcar os horários de sono.")
    
    while True:
        print("\n" + "-"*80)
        pessoa_id = input("\nDigite o ID da pessoa (11-38) ou 'sair' para encerrar: ").strip()
        
        if pessoa_id.lower() == 'sair':
            print("\nEncerrando...")
            break
        
        try:
            pessoa_id = int(pessoa_id)
            if pessoa_id < 11 or pessoa_id > 38:
                print("[ERRO] ID deve estar entre 11 e 38")
                continue
            
            processar_pessoa(pessoa_id)
            
        except ValueError:
            print("[ERRO] ID inválido. Digite um número entre 11 e 38")
        except Exception as e:
            print(f"[ERRO] Falha ao processar: {e}")

if __name__ == "__main__":
    main()
