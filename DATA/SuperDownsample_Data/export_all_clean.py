"""
Exportador em lote: gera CSVs limpos com colunas time,x,y,z para todas as pessoas (11-38).
Saída: DATA/SuperDownsample_Data/clean/acelerometro_<id>.csv
"""
from pathlib import Path
import pandas as pd
import sys

BASE_DIR = Path(__file__).resolve().parent
ACCEL_DIR = BASE_DIR / "ds_acelerometro_10x"
OUT_DIR = BASE_DIR / "clean"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def find_time_column(cols):
    candidates = [c for c in cols if 'time' in c.lower() or 'timestamp' in c.lower()]
    if candidates:
        return candidates[0]
    return cols[0]


def find_axis_column(cols, axis):
    axis = axis.lower()
    for c in cols:
        if c.lower() == axis:
            return c
    for c in cols:
        cl = c.lower()
        if cl.endswith('_' + axis) or cl.startswith(axis + '_'):
            return c
    for c in cols:
        cl = c.lower()
        if (' ' + axis + ' ') in (' ' + cl + ' '):
            return c
    for c in cols:
        if len(c) == 1 and c.lower() == axis:
            return c
    return None


def process_id(pid):
    csv_in = ACCEL_DIR / f"ds_acelerometro_{pid}_10x.csv"
    if not csv_in.exists():
        print(f"[SKIP] Arquivo não encontrado para pessoa {pid}: {csv_in}")
        return False
    df = pd.read_csv(csv_in)
    cols = list(df.columns)
    time_col = find_time_column(cols)
    x_col = find_axis_column(cols, 'x')
    y_col = find_axis_column(cols, 'y')
    z_col = find_axis_column(cols, 'z')
    if not (x_col and y_col and z_col):
        print(f"[ERROR] Colunas x/y/z não encontradas para pessoa {pid}. Colunas: {cols}")
        return False
    out_df = df[[time_col, x_col, y_col, z_col]].copy()
    out_df.columns = ['time', 'x', 'y', 'z']
    # tentar converter tempo
    try:
        out_df['time'] = pd.to_datetime(out_df['time'])
    except Exception:
        pass
    out_path = OUT_DIR / f"acelerometro_{pid}.csv"
    out_df.to_csv(out_path, index=False)
    print(f"[OK] {out_path}")
    return True


def main():
    successes = 0
    failures = 0
    for pid in range(11, 39):
        ok = process_id(pid)
        if ok:
            successes += 1
        else:
            failures += 1
    print('\nResumo:')
    print(f'  Sucessos: {successes}')
    print(f'  Falhas: {failures}')
    print(f'Arquivos gerados em: {OUT_DIR}')


if __name__ == '__main__':
    main()
