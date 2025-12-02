# Visualização por Amostras

Script para gerar gráficos de acelerômetro e giroscópio usando **número de amostras** no eixo X (ao invés de timestamp).

## Diferença para `visualizacao_manual.py`

- **visualizacao_manual.py**: Usa timestamp no eixo X (formato HH:MM)
- **visualizacao_amostras.py**: Usa índice de amostras no eixo X (0, 1, 2, 3...)

## Como usar

```bash
# No terminal (usando Python do .venv)
.\.venv\Scripts\python.exe .\scripts\separacao_manual\visualizacao_amostras.py
```

## Saída

Os gráficos são salvos em: `outputs/visualizacao_amostras/`

Para cada pessoa (11 a 38), gera:
- `acelerometro_pessoa_XX.png`
- `giroscopio_pessoa_XX.png`

Total: 56 arquivos
