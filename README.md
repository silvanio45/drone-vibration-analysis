# Análise de sinais de vibração de drones e classificação de condições das hélices

Projeto da disciplina **CIN0020 — Sinais e Sistemas (2026.2)**.

Análise de sinais reais de aceleração de drones nos domínios do tempo e da frequência, comparando hélices saudáveis e defeituosas, com uma classificação binária por aprendizado de máquina como aplicação final.

## Integrantes

- [Silvanio da Silva Assunção]
- [Nome 2]
- [Nome 3]

## Objetivo

- Extrair e interpretar características temporais (média, RMS, potência média, desvio padrão, pico absoluto, pico a pico, fator de crista).
- Extrair e interpretar características espectrais via FFT (frequência dominante, magnitude do pico, potência em bandas, centroide e entropia espectral).
- Demonstrar o efeito da duração do trecho (resolução espectral, Δf = fs/N) e da amostragem (aliasing).
- Comparar a utilidade das representações temporal, espectral e combinada em um classificador binário (saudável × defeituosa).

## Dataset

**DronePropB — Ground Testing Dataset for Commercial Drones with Defective Propellers** (Mendeley Data).

- DOI: [10.17632/xkvfjmm8zg.1](https://doi.org/10.17632/xkvfjmm8zg.1)
- O dataset **não está versionado** neste repositório.

### Como obter

1. Acesse o link acima e baixe o dataset.
2. Extraia os arquivos em `data/raw/`, mantendo a estrutura original.
3. Confira o caminho esperado pelos notebooks: `data/raw/[ESTRUTURA DE PASTAS]`.

### Registros utilizados

| Registro (arquivo) | Condição da hélice | Rótulo | Sensor/eixo | fs (Hz) | Justificativa |
|---|---|---|---|---|---|
| [arquivo 1] | [saudável] | 0 | [ ] | [ ] | [ ] |
| [arquivo 2] | [defeituosa] | 1 | [ ] | [ ] | [ ] |

Parâmetros de janelamento: tamanho da janela = [N amostras / s], sobreposição = [ ], taxa de amostragem = [ Hz ].

## Estrutura do repositório

```
drone-vibration-analysis/
├── data/
│   ├── raw/            # dataset original (não versionado)
│   └── processed/      # janelas e tabelas de características
├── notebooks/          # análises com texto explicativo
├── src/                # funções reutilizáveis
├── results/
│   ├── figures/        # gráficos gerados
│   └── tables/         # tabelas geradas (CSV)
├── report/             # relatórios em PDF
├── slides/             # apresentação final em PDF
├── requirements.txt
└── README.md
```

## Instalação

Requer Python 3.10 ou superior.

```bash
git clone https://github.com/silvanio45/drone-vibration-analysis.git
cd drone-vibration-analysis
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Para usar o ambiente nos notebooks do VS Code, selecione o kernel `.venv` em **Select Kernel**.

### Google Colab

Na primeira célula do notebook:

```python
!git clone https://github.com/silvanio45/drone-vibration-analysis.git
%cd drone-vibration-analysis
!pip install -r requirements.txt
```

Depois, coloque o dataset em `data/raw/` (por upload ou Google Drive).

## Ordem de execução dos notebooks

| Notebook | Conteúdo | Seção do projeto | Entrega |
|---|---|---|---|
| `01_selecao_e_preparacao.ipynb` | Metadados, tabela de registros, verificação e janelamento | 3.1 | 1ª |
| `02_dominio_tempo.ipynb` | Sinais no tempo e características temporais | 3.2 | 1ª |
| `03_dominio_frequencia.ipynb` | FFT, espectros, características espectrais, comparação entre domínios | 3.3 (1–5) e 3.4 | 1ª |
| `04_resolucao_e_aliasing.ipynb` | Efeito do tamanho do trecho e da amostragem | 3.3 (6–7) | 1ª |
| `05_investigacao_adicional.ipynb` | Pergunta adicional do grupo | 3.6 | 1ª |
| `06_classificacao.ipynb` | Modelos A (tempo), B (frequência) e C (combinado) | 3.5 | 2ª |

Execute em ordem. Cada notebook deve rodar do início ao fim (*Restart and Run All*).

## Pergunta adicional do grupo

[Descreva aqui a pergunta escolhida e o método usado.]

## Classificação

- Tarefa: binária, hélice saudável × defeituosa. Classe positiva: [defeituosa].
- Algoritmo: [ ] — hiperparâmetros: [ ].
- Divisão treino/teste: por registro de origem, sem janelas do mesmo registro nos dois conjuntos. [Descrever a divisão.]
- Padronização ajustada apenas no treino.
- Modelos: (A) temporais, (B) espectrais, (C) combinados, com o mesmo algoritmo e o mesmo protocolo.

## Resultados

- Figuras: `results/figures/`
- Tabelas: `results/tables/`
- Relatórios em PDF: `report/`
- Slides: `slides/`

## Referências

- DronePropB, Mendeley Data, DOI: 10.17632/xkvfjmm8zg.1
- Plano de Ensino CIN0020 — 2026.2