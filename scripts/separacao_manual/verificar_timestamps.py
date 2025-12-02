import pandas as pd
import numpy as np

# Carregar dados da pessoa 13
df_a = pd.read_csv('DATA/Downsampling_data/ds_acelerometro/ds_acelerometro_13.csv')
df_g = pd.read_csv('DATA/Downsampling_data/ds_giroscopio/ds_giroscopio_13.csv')

df_a['timestamp'] = pd.to_datetime(df_a['timestamp'])
df_g['timestamp'] = pd.to_datetime(df_g['timestamp'])

print('='*60)
print('PESSOA 13 - COMPARAÇÃO ACELEROMETRO vs GIROSCOPIO')
print('='*60)

print('\nACELEROMETRO:')
print(f'  Inicio: {df_a["timestamp"].min()}')
print(f'  Fim: {df_a["timestamp"].max()}')
print(f'  Total: {len(df_a)} pontos')
print(f'  Primeiras amostras:')
print(df_a[['timestamp', 'x', 'y', 'z']].head(3))

print('\nGIROSCOPIO:')
print(f'  Inicio: {df_g["timestamp"].min()}')
print(f'  Fim: {df_g["timestamp"].max()}')
print(f'  Total: {len(df_g)} pontos')
print(f'  Primeiras amostras:')
print(df_g[['timestamp', 'x', 'y', 'z']].head(3))

print('\n' + '='*60)
print('ANALISE DE MAGNITUDE')
print('='*60)

# Calcular magnitude do acelerômetro (com gravidade)
mag_a_bruto = np.sqrt(df_a['x']**2 + df_a['y']**2 + df_a['z']**2)

# Calcular magnitude do acelerômetro SEM gravidade
df_a['x_limpo'] = df_a['x'] - df_a['x'].rolling(window=200, center=True).mean()
df_a['y_limpo'] = df_a['y'] - df_a['y'].rolling(window=200, center=True).mean()
df_a['z_limpo'] = df_a['z'] - df_a['z'].rolling(window=200, center=True).mean()
df_a['x_limpo'] = df_a['x_limpo'].fillna(0)
df_a['y_limpo'] = df_a['y_limpo'].fillna(0)
df_a['z_limpo'] = df_a['z_limpo'].fillna(0)
mag_a_limpo = np.sqrt(df_a['x_limpo']**2 + df_a['y_limpo']**2 + df_a['z_limpo']**2)

# Calcular magnitude do giroscópio
mag_g = np.sqrt(df_g['x']**2 + df_g['y']**2 + df_g['z']**2)

print(f'\nACELEROMETRO (com gravidade):')
print(f'  Média: {mag_a_bruto.mean():.3f}')
print(f'  Desvio padrão: {mag_a_bruto.std():.3f}')

print(f'\nACELEROMETRO (sem gravidade):')
print(f'  Média: {mag_a_limpo.mean():.3f}')
print(f'  Desvio padrão: {mag_a_limpo.std():.3f}')

print(f'\nGIROSCOPIO:')
print(f'  Média: {mag_g.mean():.3f}')
print(f'  Desvio padrão: {mag_g.std():.3f}')

print('\n' + '='*60)
print('CONCLUSAO')
print('='*60)
if df_a["timestamp"].min() == df_g["timestamp"].min():
    print('✓ Timestamps coincidem - CORRETO')
else:
    print('✗ Timestamps NÃO coincidem - PROBLEMA!')
    print(f'  Diferença: {abs((df_a["timestamp"].min() - df_g["timestamp"].min()).total_seconds())} segundos')
