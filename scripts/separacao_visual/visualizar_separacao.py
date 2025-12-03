"""
Visualizador de períodos de sono sobre dados de acelerômetro.

Plota os dados X/Y/Z em cores distintas, com períodos de sono sombreados
em cinza por trás e linhas pontilhadas vermelhas marcando início/fim.
"""

from pathlib import Path
from datetime import datetime, timedelta
import sys
import re

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

DATA_DIR = Path("DATA/SemDownsampling_data")
OUTPUT_BASE = Path("outputs/separacao_visual")


def carregar_dados_pessoa(pessoa_id: int):
    """Carrega dados de acelerômetro e giroscópio."""
    accel_path = DATA_DIR / "acelerometro" / f"acelerometro_{pessoa_id}.csv"
    gyro_path = DATA_DIR / "giroscopio" / f"giroscopio_{pessoa_id}.csv"
    
    df_accel = pd.read_csv(accel_path)
    df_gyro = pd.read_csv(gyro_path)
    
    df_accel['timestamp'] = pd.to_datetime(df_accel['timestamp'])
    df_gyro['timestamp'] = pd.to_datetime(df_gyro['timestamp'])
    
    return df_accel, df_gyro


def carregar_periodos_sono(pessoa_id: int):
    """Carrega períodos de sono do arquivo periodos_sono.txt."""
    pessoa_dir = OUTPUT_BASE / f"pessoa_{pessoa_id}"
    file = pessoa_dir / "periodos_sono.txt"
    if not file.exists():
        return []
    
    periodos = []
    with file.open('r', encoding='utf-8') as f:
        for linha in f:
            texto = linha.strip()
            if not texto or texto.startswith('=') or 'Períodos' in texto:
                continue
            # Extrair pares HH:MM usando regex
            times = re.findall(r"(\d{1,2}:\d{2})", texto)
            if len(times) >= 2:
                periodos.append((times[0], times[1]))
    return periodos


def converter_periodos_para_timestamps(periodos, data_base):
    """Converte strings HH:MM para timestamps pandas."""
    periodos_dt = []
    for inicio_str, fim_str in periodos:
        try:
            hi, mi = map(int, inicio_str.split(':'))
            hf, mf = map(int, fim_str.split(':'))
        except Exception:
            continue
        
        inicio_dt = datetime.combine(data_base, datetime.min.time()).replace(hour=hi, minute=mi)
        fim_dt = datetime.combine(data_base, datetime.min.time()).replace(hour=hf, minute=mf)
        
        # Se fim <= início, assumir dia seguinte
        if fim_dt <= inicio_dt:
            fim_dt += timedelta(days=1)
        
        periodos_dt.append((pd.Timestamp(inicio_dt), pd.Timestamp(fim_dt)))
    return periodos_dt


def plotar_visualizacao(df_accel, periodos, pessoa_id):
    """
    Cria gráfico com dados do acelerômetro (X/Y/Z), períodos de sono
    sombreados em cinza e linhas pontilhadas vermelhas nos limites.
    """
    data_base = df_accel['timestamp'].iloc[0].date()
    periodos_dt = converter_periodos_para_timestamps(periodos, data_base)
    
    # Criar figura
    fig, ax = plt.subplots(figsize=(14, 6))
    fig.suptitle(f'Dados do Acelerômetro - Pessoa {pessoa_id}', fontsize=14, fontweight='bold')
    
    # Desenhar sombreamento dos períodos de sono (por trás)
    for inicio, fim in periodos_dt:
        ax.axvspan(inicio, fim, color='lightgray', alpha=0.4, zorder=1)
    
    # Plotar linhas X, Y, Z (por cima do sombreamento)
    ax.plot(df_accel['timestamp'], df_accel['x'], color='#FF8C00', linewidth=1.0, label='X', zorder=3)
    ax.plot(df_accel['timestamp'], df_accel['y'], color='#1E90FF', linewidth=1.0, label='Y', zorder=3)
    ax.plot(df_accel['timestamp'], df_accel['z'], color='#32CD32', linewidth=1.0, label='Z', zorder=3)
    
    # Desenhar linhas pontilhadas vermelhas nos limites dos períodos
    for inicio, fim in periodos_dt:
        ax.axvline(inicio, color='red', linestyle='--', linewidth=1.5, zorder=4)
        ax.axvline(fim, color='red', linestyle='--', linewidth=1.5, zorder=4)
    
    # Configurar eixos
    ax.set_xlabel('Horário', fontsize=11)
    ax.set_ylabel('Aceleração', fontsize=11)
    ax.grid(True, alpha=0.3, zorder=0)
    ax.legend(loc='upper left', framealpha=0.9)
    
    # Formatação do eixo X
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
    ax.xaxis.set_major_locator(mdates.HourLocator(interval=1))
    plt.setp(ax.xaxis.get_majorticklabels(), rotation=0, ha='center')
    
    plt.tight_layout()
    
    # Salvar figura
    pessoa_dir = OUTPUT_BASE / f"pessoa_{pessoa_id}"
    pessoa_dir.mkdir(parents=True, exist_ok=True)
    output_file = pessoa_dir / "visualizacao_periodos_sono.png"
    plt.savefig(output_file, dpi=150, bbox_inches='tight')
    print(f"\n✓ Visualização salva em: {output_file}")
    
    plt.close()


def main():
    """Função principal - pode ser chamada standalone ou importada."""
    if len(sys.argv) > 1:
        try:
            pessoa_id = int(sys.argv[1])
        except Exception:
            pessoa_id = None
    else:
        pessoa_id = None
    
    # Se não foi passado argumento, pedir via input
    while pessoa_id is None:
        try:
            pessoa_id = int(input('Digite o ID da pessoa (11-38): '))
            if pessoa_id < 11 or pessoa_id > 38:
                print('ID fora do intervalo')
                pessoa_id = None
        except Exception:
            print('Entrada inválida')
    
    print(f"\nCarregando dados da pessoa {pessoa_id}...")
    df_accel, df_gyro = carregar_dados_pessoa(pessoa_id)
    print(f"✓ {len(df_accel)} amostras carregadas")
    
    periodos = carregar_periodos_sono(pessoa_id)
    if not periodos:
        print('⚠ Nenhum período de sono encontrado.')
        print('Execute separacao_interativa.py primeiro.')
        return
    
    print(f"✓ {len(periodos)} período(s) de sono encontrado(s):")
    for i, (a, b) in enumerate(periodos, 1):
        print(f"  Período {i}: {a} até {b}")
    
    print('\nGerando visualização...')
    plotar_visualizacao(df_accel, periodos, pessoa_id)
    print('✓ Concluído!')


if __name__ == '__main__':
    main()
