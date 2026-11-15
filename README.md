# Análise de sinais de vibração de drones e classificação de condições das hélices

Projeto da disciplina **CIN0020 — Sinais e Sistemas (2026.2)**.

Análise de sinais reais de aceleração de drones nos domínios do tempo e da frequência, comparando hélices saudáveis e defeituosas, com uma classificação binária por aprendizado de máquina como aplicação final.

## Integrantes

- Silvanio da Silva Assunção
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
- O dataset **não está versionado** neste repositório (`.mat` no `.gitignore`).

### Como obter

1. Acesse o link acima e baixe o dataset.
2. Extraia os 111 arquivos `.mat` em `data/raw/DADOS/` (a pasta deve se chamar exatamente `DADOS`).
3. Os notebooks e o módulo `src/io_utils.py` esperam o caminho `data/raw/DADOS/*.mat`.

### Estrutura dos arquivos

Cada `.mat` tem as variáveis `AccData` (sinal `Vib_Data`, vetor de tempo `t`, `samplingRate`) e, em 108 dos 111 arquivos, `IMUData` (3 canais) e `BatteryVolt`.

Nome do arquivo: `F#_SV#_SP#_C#[_R#].mat`.

> O significado dos códigos `F`, `SV`, `SP` e `C` não foi encontrado na documentação consultada do DronePropB. A leitura adotada (`F0` saudável, `F1` a `F3` grupos de falha, `SV` severidade, `SP` velocidade, `R` repetição) segue a convenção do dataset irmão DronePropA e **não está confirmada** para o B. O código `C` não tem significado conhecido e foi usado apenas para formar pares de comparação.

### Sensor utilizado

`AccData`, 1 canal, fs = 10 kHz (Nyquist de 5 kHz), unidade **não documentada** (tratada como u.a.). Provavelmente é o acelerômetro piezoelétrico descrito no dataset, mas isso não está confirmado nos arquivos. A IMU (`IMUData`, 1 kHz) não foi usada.

### Registros utilizados

| Etapa | Registros |
|---|---|
| Arquivos lidos | 111 (30 saudáveis `F0`, 81 defeituosos `F1` a `F3`), 0 falhas |
| Cópias idênticas removidas | 9 (saudáveis `C2` idênticos aos `C1` de mesmo `SP` e `R`, verificado por hash do sinal) |
| `SP0` excluído | 3 (só existe para saudáveis, não permite comparação) |
| **Usados** | **99** (18 saudáveis e 81 defeituosos) |

Tabelas completas: `results/tables/registros.csv` (todos) e `results/tables/registros_selecionados.csv` (usados).

**Critério de par comparável:** mesmo `SP` e mesmo `C`. Nos saudáveis, `C2` era cópia de `C1`, então os defeituosos `C2` não têm saudável próprio.

**Validação nos 99 registros:** nenhum NaN, nenhuma saturação (os extremos ocorrem em 1 ou 2 amostras por registro), razão entre o maior e o menor desvio padrão por janela de 2 s de no máximo 1,95 (limiar adotado: 3). Nenhum recorte foi aplicado.

### Janelamento

- Janela de **2 s = 20000 amostras** (fs = 10 kHz), sem sobreposição, resolução espectral Δf = 0,5 Hz.
- **2370 janelas**: 480 saudáveis e 1890 defeituosas (cerca de 20% saudáveis).
- Cada janela guarda o arquivo de origem e o `id` do registro (grupo de sinais idênticos), usado na divisão treino/teste.
- Tabela: `data/processed/janelas.csv` (só índices de início e fim, os sinais são relidos do `.mat`).

## Estrutura do repositório

```
drone-vibration-analysis/
├── data/
│   ├── raw/            # dataset original (não versionado)
│   └── processed/      # janelas e tabelas de características
├── notebooks/          # análises com texto explicativo
├── src/
│   └── io_utils.py     # leitura, metadados, rótulo, id e funções auxiliares
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

Depois, coloque o dataset em `data/raw/DADOS/` (por upload ou Google Drive). Nos notebooks, use `sys.path.append(".")` no lugar de `".."`.

## Ordem de execução dos notebooks

| Notebook | Conteúdo | Seção do projeto | Entrega |
|---|---|---|---|
| `01_selecao_e_preparacao.ipynb` | Metadados, tabela de registros, verificação e janelamento | 3.1 | 1ª |
| `02_dominio_tempo.ipynb` | Sinais no tempo e características temporais | 3.2 | 1ª |
| `03_dominio_frequencia.ipynb` | FFT, espectros, características espectrais, comparação entre domínios | 3.3 (1–5) e 3.4 | 1ª |
| `04_resolucao_e_aliasing.ipynb` | Efeito do tamanho do trecho e da amostragem | 3.3 (6–7) | 1ª |
| `05_investigacao_adicional.ipynb` | Pergunta adicional do grupo | 3.6 | 1ª |
| `06_classificacao.ipynb` | Modelos A (tempo), B (frequência) e C (combinado) | 3.5 | 2ª |

Execute em ordem. Cada notebook deve rodar do início ao fim (*Restart and Run All*). O notebook 01 gera as tabelas que os seguintes leem.

## Pergunta adicional do grupo

[Descreva aqui a pergunta escolhida e o método usado.]

Pergunta em estudo: a velocidade (`SP`) desloca os picos espectrais? Como ponto de partida, a frequência do maior pico do `AccData` entre 30 e 80 Hz nos registros `SP1` é de 56,3 Hz (desvio de 0,45 Hz) nos saudáveis e varia de 50,7 a 57,0 Hz (desvio de 1,8 a 4,9 Hz) nos defeituosos, sem tendência clara com a severidade.

## Classificação

- Tarefa: binária, hélice saudável × defeituosa. Classe positiva: defeituosa (`y = 1`).
- Algoritmo: [ ] — hiperparâmetros: [ ].
- Divisão treino/teste: por registro de origem (`id`), sem janelas do mesmo registro nos dois conjuntos. [Descrever a divisão.]
- Padronização ajustada apenas no treino.
- Modelos: (A) temporais, (B) espectrais, (C) combinados, com o mesmo algoritmo e o mesmo protocolo.
- Desbalanceamento: cerca de 20% das janelas são saudáveis, então precisão, recall e F1 importam mais que a acurácia.

## Resultados

- Figuras: `results/figures/`
- Tabelas: `results/tables/`
- Relatórios em PDF: `report/`
- Slides: `slides/`

## Referências

- DronePropB, Mendeley Data, DOI: 10.17632/xkvfjmm8zg.1
- Ismail, M. A. A.; Elshaar, M. E.; Abdallah, A.; Quan, Q. DronePropA: Motion trajectories dataset for defective drones. Data in Brief, v. 60, 2025, DOI: 10.1016/j.dib.2025.111589 (dataset irmão, usado como referência para a convenção de nomes)
- Plano de Ensino CIN0020 — 2026.2