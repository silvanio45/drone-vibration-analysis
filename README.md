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
3. O módulo `src/io_utils.py` calcula o caminho `data/raw/DADOS/` a partir da própria posição, então funciona de qualquer pasta de trabalho.

### Estrutura dos arquivos

Cada `.mat` tem a variável `AccData` (campos `Vib_Data`, `t`, `samplingRate` e `DATE`) e, em 108 dos 111 arquivos, `IMUData` (3 canais) e `BatteryVolt`. Os 3 arquivos sem IMU são `F0_SV0_SP0_C4_R1` a `R3`.

Nome do arquivo: `F#_SV#_SP#_C#[_R#].mat`.

> O significado dos códigos `F`, `SV`, `SP` e `C` não foi encontrado na documentação consultada do DronePropB. A leitura adotada (`F0` saudável, `F1` a `F3` grupos de falha, `SV` severidade, `SP` velocidade, `R` repetição) segue a convenção do dataset irmão DronePropA e **não está confirmada** para o B. O código `C` não tem significado conhecido e foi usado apenas para formar pares de comparação.

### Sensor utilizado

`AccData`, 1 canal, fs = 10 kHz (Nyquist de 5 kHz), unidade **não documentada** (tratada como u.a.). Provavelmente é o acelerômetro piezoelétrico descrito no dataset, mas isso não está confirmado nos arquivos. A IMU (`IMUData`, 1 kHz) não foi usada: tem rampa de partida e parada, offset de gravidade em um canal, 18 registros com fs calculada até 0,03% abaixo de 1000 Hz e falta em 3 registros.

### Registros utilizados

| Etapa | Registros |
|---|---|
| Arquivos lidos | 111 (30 saudáveis `F0`, 81 defeituosos `F1` a `F3`), 0 falhas |
| Cópias idênticas removidas | 9 (saudáveis `C2` idênticos aos `C1` de mesmo `SP` e `R`, verificado por hash do sinal) |
| `SP0` excluído | 3 (só existe para saudáveis, não permite comparação) |
| **Usados** | **99** (18 saudáveis e 81 defeituosos) |

Tabelas completas: `results/tables/registros.csv` (todos) e `results/tables/registros_selecionados.csv` (usados).

**Critério de par comparável:** mesmo `SP`, mesmo `C`, mesmo sensor (`AccData`, 10 kHz) e mesmo janelamento (janelas de 2 s). A duração total nem sempre é igual: no `C3`, os defeituosos têm 20 s e os saudáveis têm 20 s (`R1`) ou 60 s (`R2`, `R3`). Isso muda o número de janelas por registro (10 ou 30), mas não o cálculo de cada janela. Nos saudáveis, `C2` era cópia de `C1`, então os defeituosos `C2` não têm saudável próprio e são comparados com os saudáveis `C1` do mesmo `SP`. Tabelas: `results/tables/registros_selecionados_resumo.csv` e `results/tables/grupos_comparacao.csv` (notebook 1, seção 1.6).

**Validação nos 99 registros:** nenhum NaN, nenhuma saturação (os extremos ocorrem em 1 ou 2 amostras por registro), razão entre o maior e o menor desvio padrão por janela de 2 s de no máximo 1,95 (limiar adotado: 3). Nenhum recorte foi aplicado.

### Janelamento

- Janela de **2 s = 20000 amostras** (fs = 10 kHz), sem sobreposição, resolução espectral Δf = 0,5 Hz.
- **2370 janelas**: 480 saudáveis e 1890 defeituosas (cerca de 20% saudáveis).
- Cada janela guarda o arquivo de origem e o `id` do registro (grupo de sinais idênticos), usado na divisão treino/teste.
- Tabela: `data/processed/janelas.csv` (só índices de início `ini` e fim `fim`, os sinais são relidos do `.mat`).

## Estrutura do repositório

```
drone-vibration-analysis/
├── data/
│   ├── raw/                  # dataset original (não versionado)
│   └── processed/
│       ├── janelas.csv       # índices das 2370 janelas
│       └── features_tempo.csv  # características temporais por janela
├── notebooks/                # análises com texto explicativo
├── src/
│   └── io_utils.py           # leitura, metadados, rótulo, id e funções auxiliares
├── results/
│   ├── figures/              # gráficos gerados
│   └── tables/               # tabelas geradas (CSV)
├── report/
│   ├── main.tex              # relatório parcial (LaTeX, compilar no Overleaf)
│   ├── figuras/              # figuras do relatório
│   └── figuras_relatorio.py  # gera as figuras do relatório a partir dos dados
├── slides/                   # apresentação final em PDF
├── requirements.txt
└── README.md
```

### Módulo `src/io_utils.py`

| Função | O que faz |
|---|---|
| `get_info_name` | extrai `F`, `SV`, `SP`, `C` e `R` do nome do arquivo |
| `get_data` | lê um `.mat` e devolve sinais e checagens (fs, N, NaN) |
| `ler_acc` | lê só o `AccData` (usada nas janelas) |
| `get_id`, `get_rotulo` | marcam registros idênticos e criam o rótulo (`y = 1` defeituosa) |
| `estat`, `std_por_bloco`, `fundamental`, `digest` | estatísticas, desvio por bloco, frequência do pico entre 30 e 80 Hz e hash do sinal |

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

Depois, coloque o dataset em `data/raw/DADOS/` (por upload ou Google Drive). Nos notebooks, use `sys.path.append(".")` no lugar de `".."`, e troque os caminhos `../data/...` por `data/...`.

## Ordem de execução dos notebooks

| Notebook | Conteúdo | Seção do projeto | Entrega |
|---|---|---|---|
| `1_selecao_e_preparacao.ipynb` | Metadados, tabela de registros, verificação e janelamento | 3.1 | 1ª |
| `2_dominio_tempo.ipynb` | Sinais no tempo e características temporais | 3.2 | 1ª |
| `3_dominio_frec.ipynb` | FFT, espectros e características espectrais | 3.3 (1–5) | 1ª |
| `4_resolucao_e_aliasing.ipynb` | Efeito do tamanho do trecho e da amostragem | 3.3 (6–7) | 1ª |
| `5_comparacao_dominios.ipynb` | Comparação entre os domínios do tempo e da frequência | 3.4 | 1ª |
| `6_investigacao_picos_sp.ipynb` | Pergunta adicional: como a velocidade (`SP`) modifica os picos espectrais | 3.6 | 1ª |
| `7_classificacao.ipynb` (a fazer) | Modelos A (tempo), B (frequência) e C (combinado) | 3.5 | 2ª |

Execute em ordem. Cada notebook deve rodar do início ao fim (*Restart and Run All*). O notebook 1 gera `registros.csv`, `registros_selecionados.csv` e `janelas.csv`, que os seguintes leem.

## Domínio do tempo (3.2)

Para cada janela de 2 s foram calculadas, sobre as N = 20000 amostras x[n] do `AccData`:

| Medida | Definição | Unidade |
|---|---|---|
| Média | (1/N) Σ x[n] | u.a. |
| Potência média | (1/N) Σ x[n]² | u.a.² |
| RMS | √(potência média) | u.a. |
| Desvio padrão | √((1/N) Σ (x[n] − média)²), divisor N | u.a. |
| Pico absoluto | max \|x[n]\| | u.a. |
| Pico a pico | max x − min x | u.a. |
| Fator de crista | pico absoluto / RMS | adimensional |

Com divisor N no desvio, vale potência = média² + desvio², usado como teste de consistência. Saída: `data/processed/features_tempo.csv` (uma linha por janela, com `arquivo`, `id`, `rotulo` e as sete medidas). Figuras em `results/figures/`.

**Par ilustrativo** usado na figura temporal: `F0_SV0_SP1_C1_R1` (saudável) e `F1_SV3_SP1_C1` (defeituosa), mesmo `SP`, `C`, sensor e duração, trecho de 20,0 a 20,5 s. É um par entre vários possíveis, escolhido por já ter sido inspecionado, e não é apresentado como o mais representativo.

## Pergunta adicional do grupo (3.6)

**Como a velocidade (`SP`) modifica os picos espectrais?** Notebook `6_investigacao_picos_sp.ipynb`.

O maior pico de 30 a 200 Hz (`f1`) salta entre um pico e o seu dobro em SP1 e SP2. Por isso foi usado um pico de base `f_base`: o pico em f1/2, quando ele tem pelo menos 30% da magnitude de `f1`. Resumido pela mediana de cada registro, `f_base` sobe de 56,2 para 100,0 e 133,5 Hz de SP1 a SP3 na saudável, e de 53,0 para 95,5 e 130,2 Hz na defeituosa. Ele é de 2 a 6% menor na defeituosa nos três `SP` (AUC 0,22 / 0,15 / 0,38), e o sentido se mantém usando só os saudáveis gravados em setembro, o mesmo mês dos defeituosos. Nenhuma causa física ou rotação é atribuída aos picos.

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
- Relatório parcial: `report/main.tex` (as figuras são geradas por `python report/figuras_relatorio.py`, depois dos notebooks 1 a 6). Para o Overleaf, envie `report/relatorio_overleaf.zip` em *New Project → Upload Project*.
- Slides: `slides/`

## Referências

- DronePropB, Mendeley Data, DOI: 10.17632/xkvfjmm8zg.1
- Ismail, M. A. A.; Elshaar, M. E.; Abdallah, A.; Quan, Q. DronePropA: Motion trajectories dataset for defective drones. Data in Brief, v. 60, 2025, DOI: 10.1016/j.dib.2025.111589 (dataset irmão, usado como referência para a convenção de nomes)
- Plano de Ensino CIN0020 — 2026.2