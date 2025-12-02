"""
Exportador simples: lê o CSV downsampled do acelerômetro e salva um CSV limpo
com exatamente as colunas: time, x, y, z.

Uso:
  .\.venv\Scripts\python.exe DATA\SuperDownsample_Data\view_downsample.py --id 11

Opções:
  --id    ID da pessoa (padrão: 11)
  --out   Caminho de saída opcional (se não fornecido, salva em
          DATA/SuperDownsample_Data/clean_acelerometro_<id>.csv)
"""
from pathlib import Path
import pandas as pd
import argparse
import sys

BASE_DIR = Path(__file__).resolve().parent
ACCEL_DIR = BASE_DIR / "ds_acelerometro_10x"


def find_time_column(cols):
    candidates = [c for c in cols if 'time' in c.lower() or 'timestamp' in c.lower()]
    if candidates:
        return candidates[0]
    # fallback: first column
    return cols[0]


def find_axis_column(cols, axis):
    axis = axis.lower()
    # exact match
    for c in cols:
        if c.lower() == axis:
            return c
    # endswith _x, acc_x, ax, etc.
    for c in cols:
        cl = c.lower()
        if cl.endswith('_' + axis) or cl.startswith(axis + '_'):
            return c
    # contains axis as separate token
    for c in cols:
        cl = c.lower()
        if (' ' + axis + ' ') in (' ' + cl + ' '):
            return c
    # final fallback: look for single letter column included
    for c in cols:
        if len(c) == 1 and c.lower() == axis:
            return c
    return None


def main():
    parser = argparse.ArgumentParser(description='Exportar CSV limpo com columns: time,x,y,z')
    parser.add_argument('--id', type=int, default=11, help='ID da pessoa (padrão: 11)')
    parser.add_argument('--out', type=str, help='Caminho de saída do CSV')
    args = parser.parse_args()

    pid = args.id
    csv_in = ACCEL_DIR / f"ds_acelerometro_{pid}_10x.csv"
    if not csv_in.exists():
        print(f'Arquivo de entrada não encontrado: {csv_in}')
        sys.exit(1)

    df = pd.read_csv(csv_in)
    cols = list(df.columns)

    time_col = find_time_column(cols)
    x_col = find_axis_column(cols, 'x')
    y_col = find_axis_column(cols, 'y')
    z_col = find_axis_column(cols, 'z')

    if not (x_col and y_col and z_col):
        print('Não foi possível localizar colunas x, y, z no arquivo. Colunas encontradas:')
        print(cols)
        sys.exit(1)

    out_df = df[[time_col, x_col, y_col, z_col]].copy()
    out_df.columns = ['time', 'x', 'y', 'z']

    # converter time para datetime se possível
    try:
        out_df['time'] = pd.to_datetime(out_df['time'])
    except Exception:
        pass

    if args.out:
        out_path = Path(args.out)
    else:
        out_path = BASE_DIR / f"clean_acelerometro_{pid}.csv"

    out_df.to_csv(out_path, index=False)
    print(f'Arquivo exportado: {out_path}')


if __name__ == '__main__':
    main()
