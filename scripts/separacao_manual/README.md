# Separação Manual - Visualização de Dados de Acelerômetro

Este diretório contém ferramentas para visualização e separação manual de dados de acelerômetro/giroscópio.

## 📁 Arquivos

- `visualizacao_manual.py` - Script principal para visualização e separação de dados

## 🎯 Objetivo

Gerar gráficos dos dados do acelerômetro ao longo do tempo (eixo X em horas) e separar automaticamente os períodos em dois grupos:
- **Parado** - Baixa variação na magnitude do acelerômetro
- **Movimento** - Alta variação na magnitude do acelerômetro

## 📊 Saídas Geradas

O script gera 2 tipos de gráficos:

### 1. Visualização dos Dados Brutos
- 4 subplots mostrando:
  - Eixo X do acelerômetro ao longo do tempo
  - Eixo Y do acelerômetro ao longo do tempo
  - Eixo Z do acelerômetro ao longo do tempo
  - Magnitude do vetor de aceleração

### 2. Separação Parado vs Movimento
- 2 subplots mostrando:
  - Magnitude colorida por estado (cinza = parado, vermelho = movimento)
  - Variação (desvio padrão) usado como critério de separação

## 🚀 Como Usar

### 1. Executar para uma pessoa específica

```python
# Editar a variável PESSOA_ID no script
PESSOA_ID = 11  # ID da pessoa (11-38)

# Executar o script
python scripts/separacao_manual/visualizacao_manual.py
```

### 2. Ajustar o threshold de separação

```python
# No script, modificar o threshold_variacao
df_separado = separar_manual_movimento(df_combined, threshold_variacao=1.5)
```

**Dica:**
- Valores **maiores** = mais restritivo (menos amostras classificadas como "movimento")
- Valores **menores** = menos restritivo (mais amostras classificadas como "movimento")

## 📈 Exemplo de Output

```
============================================================
ESTATISTICAS DA SEPARACAO
============================================================
Total de pontos: 4856
Parado: 3156 pontos (65.0%)
Movimento: 1700 pontos (35.0%)
Threshold de variacao usado: 1.5
============================================================
```

## 🔧 Parâmetros Configuráveis

| Parâmetro | Localização | Descrição |
|-----------|-------------|-----------|
| `PESSOA_ID` | Início do script | ID da pessoa a analisar (11-38) |
| `threshold_variacao` | Função `main()` | Limiar para separar parado/movimento |
| `window_size` | Função `separar_manual_movimento()` | Tamanho da janela para cálculo de variação |

## 📂 Estrutura de Dados

O script espera encontrar os dados em:
```
DATA/Downsampling_data/
├── ds_acelerometro/
│   └── ds_acelerometro_{PESSOA_ID}.csv
└── ds_giroscopio/
    └── ds_giroscopio_{PESSOA_ID}.csv
```

## 💾 Saída

Os gráficos são salvos em:
```
output/separacao_manual/
├── visualizacao_pessoa_{PESSOA_ID}.png
└── separacao_pessoa_{PESSOA_ID}.png
```

## 🎨 Formato dos Gráficos

- **Eixo X**: Tempo em formato HH:MM (horas e minutos)
- **Eixo Y**: Aceleração (m/s²) ou Magnitude
- **Resolução**: 300 DPI (alta qualidade)
- **Cores**:
  - Azul: Eixo X
  - Laranja: Eixo Y
  - Verde: Eixo Z
  - Roxo: Magnitude
  - Cinza: Períodos parados
  - Vermelho: Períodos de movimento
