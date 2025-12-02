"""
Converte os CSVs limpos (time,x,y,z) em arquivos compatíveis com Excel
usando ponto-e-vírgula como separador e vírgula como separador decimal.

Saída: DATA/SuperDownsample_Data/excel_csv/acelerometro_<id>_excel.csv
"""
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
CLEAN_DIR = BASE_DIR / "clean"
OUT_DIR = BASE_DIR / "excel_csv"
OUT_DIR.mkdir(parents=True, exist_ok=True)


def convert_file(in_path: Path, out_path: Path):
    df = pd.read_csv(in_path)
    # Garantir colunas na ordem time,x,y,z
    expected = ['time', 'x', 'y', 'z']
    cols = df.columns.tolist()
    # Reordenar / selecionar
    df = df[[c for c in expected if c in cols]]

    # Converter numéricos para string com vírgula decimal
    for c in ['x', 'y', 'z']:
        if c in df.columns:
            # Formatar com 6 casas decimais e trocar '.' por ','
            df[c] = df[c].map(lambda v: ('{:.6f}'.format(v)).replace('.',','))

    # Garantir que time seja string sem mudança
    if 'time' in df.columns:
        df['time'] = df['time'].astype(str)

    # Salvar com ; como separador
    df.to_csv(out_path, sep=';', index=False)
    print(f'[OK] Gerado: {out_path}')


def main():
    files = sorted(CLEAN_DIR.glob('acelerometro_*.csv'))
    if not files:
        print('Nenhum arquivo clean/ encontrado.')
        return
    for f in files:
        pid = f.stem.split('_')[-1]
        out = OUT_DIR / f"acelerometro_{pid}_excel.csv"
        convert_file(f, out)
    print('\nConcluído. Arquivos em:')
    print(OUT_DIR)


if __name__ == '__main__':
    main()
