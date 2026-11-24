"""Figuras compactas para o relatório (largura da página A4, fonte legível).

Usa os mesmos dados e as mesmas funções dos notebooks 1 a 6:
- data/processed/features_tempo.csv e features_freq.csv (notebooks 2 e 3)
- results/tables/picos_sp_registros.csv (notebook 6)
- os sinais do AccData, para os pares, a resolução e o aliasing (notebooks 3 a 5)

Rodar da raiz do repositório, depois dos notebooks 1 a 6:
    python report/figuras_relatorio.py
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from scipy.signal import decimate
from scipy.stats import mannwhitneyu

from src.freq_features import FS, espectro
from src.io_utils import ler_acc

SAIDA = ROOT / "report" / "figuras"
SAIDA.mkdir(parents=True, exist_ok=True)
LARGURA = 6.85  # largura útil da página em polegadas (A4, margens de 1,8 cm)

plt.rcParams.update({
    "font.size": 7.5, "axes.titlesize": 8, "axes.labelsize": 7.5, "legend.fontsize": 7,
    "xtick.labelsize": 6.5, "ytick.labelsize": 6.5, "lines.linewidth": 0.7,
    "axes.grid": True, "grid.alpha": 0.3, "savefig.dpi": 300, "savefig.bbox": "tight",
})
COR = {"saudavel": "tab:blue", "defeituoso": "tab:red"}
ROT = {"saudavel": "saudável", "defeituoso": "defeituosa"}

janelas = pd.read_csv(ROOT / "data/processed/janelas.csv")
tempo = pd.read_csv(ROOT / "data/processed/features_tempo.csv")
freq = pd.read_csv(ROOT / "data/processed/features_freq.csv")


def janela(arquivo, jan):
    linha = janelas[(janelas["arquivo"] == arquivo) & (janelas["jan"] == jan)].iloc[0]
    return ler_acc(arquivo)[linha["ini"]:linha["fim"]].astype(float)


# 1. pares saudável x defeituosa: tempo (0,2 s) e espectro (janela de 20 a 22 s)
fig, eixos = plt.subplots(2, 3, figsize=(LARGURA, 3.3), layout="constrained")
for sp, (ax_t, ax_f) in enumerate(eixos.T, start=1):
    for cond, arq in [("saudavel", f"F0_SV0_SP{sp}_C1_R1.mat"), ("defeituoso", f"F1_SV3_SP{sp}_C1.mat")]:
        x = janela(arq, 10)
        t = 20 + np.arange(2000) / FS
        ax_t.plot(t, x[:2000], color=COR[cond], label=ROT[cond])
        f, mag = espectro(x, FS)
        ax_f.semilogy(f, mag[0], color=COR[cond], lw=0.5)
    ax_t.set(title=f"SP{sp}", xlabel="Tempo (s)")
    ax_f.set(xlim=(0, 600), xlabel="Frequência (Hz)")
eixos[0, 0].set_ylabel("Aceleração (u.a.)")
eixos[1, 0].set_ylabel("Magnitude (u.a.)")
eixos[0, 0].legend(loc="upper right")
fig.savefig(SAIDA / "rel_pares.png")
plt.close(fig)


# boxplots por SP, saudável e defeituosa lado a lado
def boxplots(dados, colunas, nomes, unidades, log, linhas, altura, arquivo):
    fig, eixos = plt.subplots(linhas, len(colunas) // linhas, figsize=(LARGURA, altura), layout="constrained")
    for ax, c, nome, un, lg in zip(np.ravel(eixos), colunas, nomes, unidades, log):
        for cond, desl in [("saudavel", -0.18), ("defeituoso", 0.18)]:
            v = [dados.loc[(dados["SP"] == sp) & (dados["rotulo"] == cond), c] for sp in (1, 2, 3)]
            ax.boxplot(v, positions=np.arange(3) + desl, widths=0.3, showfliers=False, patch_artist=True,
                       boxprops=dict(facecolor=COR[cond], alpha=0.35, edgecolor=COR[cond]),
                       medianprops=dict(color=COR[cond], lw=1.2), whiskerprops=dict(color=COR[cond]),
                       capprops=dict(color=COR[cond]))
        ax.set_xticks(range(3), ["SP1", "SP2", "SP3"])
        ax.set(title=nome, ylabel=un)
        if lg:
            ax.set_yscale("log")
    from matplotlib.patches import Patch
    fig.legend(handles=[Patch(facecolor=COR[c], alpha=0.35, edgecolor=COR[c], label=ROT[c]) for c in COR],
               loc="outside upper center", ncol=2)
    fig.savefig(SAIDA / arquivo)
    plt.close(fig)


# 2. boxplots temporais
boxplots(tempo, ["rms", "desvio", "pico_abs", "crista"],
         ["RMS", "Desvio padrão", "Pico absoluto", "Fator de crista"],
         ["u.a.", "u.a.", "u.a.", "adimensional"], [True, True, True, False], 1, 2.1, "rel_box_tempo.png")

# 3. boxplots espectrais
boxplots(freq, ["f_dom", "mag_pico", "centroide", "entropia", "pot_10_45", "pot_45_150", "pot_150_600", "pot_600_5000"],
         ["Frequência dominante", "Magnitude do pico", "Centroide", "Entropia",
          "Potência 10–45 Hz", "Potência 45–150 Hz", "Potência 150–600 Hz", "Potência 600–5000 Hz"],
         ["Hz", "u.a.", "Hz", "adimensional", "u.a.²", "u.a.²", "u.a.²", "u.a.²"],
         [False, False, False, False, True, True, True, True], 2, 3.6, "rel_box_freq.png")

# 4. resolução espectral (em cima) e aliasing (embaixo)
fig, eixos = plt.subplots(2, 2, figsize=(LARGURA, 3.6), layout="constrained")
x = janela("F0_SV0_SP1_C1_R1.mat", 10)
for ax, n, nome in [(eixos[0, 0], 2000, "0,2 s"), (eixos[0, 1], 20000, "2 s")]:
    f, mag = espectro(x[:n], FS)
    ax.plot(f, mag[0], ".-", ms=2, color="black")
    df = f"{FS / n:g}".replace(".", ",")
    ax.set(xlim=(30, 100), title=f"T = {nome}, N = {n}, Δf = {df} Hz", xlabel="Frequência (Hz)")
eixos[0, 0].set_ylabel("Magnitude (u.a.)")
x = janela("F0_SV0_SP2_C1_R1.mat", 10)
Q, fs2 = 16, FS / 16
f0, m0 = espectro(x, FS)
for ax, y, nome in [(eixos[1, 0], x[::Q], "sem filtro"),
                    (eixos[1, 1], decimate(x, Q, ftype="fir", zero_phase=True), "com filtro (decimate)")]:
    f, mag = espectro(y, fs2)
    ax.plot(f0, m0[0], color="gray", lw=0.5, label="original, 10 kHz")
    ax.plot(f, mag[0], color="tab:red", lw=0.6, label="625 Hz")
    for fap in (230.0, 131.0):  # 395 e 494 Hz dobrados por |f - k*625|
        ax.axvline(fap, color="black", ls="--", lw=0.6)
    ax.set(xlim=(0, 312.5), title=f"fs = 625 Hz, {nome}", xlabel="Frequência (Hz)")
eixos[1, 0].set_ylabel("Magnitude (u.a.)")
eixos[1, 0].legend(loc="upper right")
fig.savefig(SAIDA / "rel_resolucao_aliasing.png")
plt.close(fig)

# 5. AUC por característica (mediana por registro), mesmo protocolo do notebook 5
ident = ["arquivo", "id", "rotulo", "F", "SV", "SP", "C", "jan"]
dados = pd.concat([tempo, freq.drop(columns=ident)], axis=1)
colunas = [c for c in dados.columns if c not in ident]
reg = dados.groupby(["arquivo", "SP", "rotulo"], as_index=False)[colunas].median()
fig, ax = plt.subplots(figsize=(LARGURA, 2.0), layout="constrained")
for sp, cor in zip((1, 2, 3), ("tab:blue", "tab:orange", "tab:green")):
    g = reg[reg["SP"] == sp]
    s, d = g[g["rotulo"] == "saudavel"], g[g["rotulo"] == "defeituoso"]
    auc = [mannwhitneyu(d[c], s[c]).statistic / (len(d) * len(s)) for c in colunas]
    ax.plot(range(len(colunas)), auc, "o", ms=4, color=cor, label=f"SP{sp}")
ax.axhline(0.5, color="gray", lw=1)
ax.axvline(6.5, color="black", lw=0.6, ls=":")
ax.set_xticks(range(len(colunas)), colunas, rotation=45, ha="right")
ax.set(ylabel="AUC", ylim=(0, 1))
ax.text(3, 0.93, "tempo", ha="center")
ax.text(10.5, 0.93, "frequência", ha="center")
ax.legend(loc="lower right", ncol=3)
fig.savefig(SAIDA / "rel_auc.png")
plt.close(fig)

# 6. investigação adicional: f_base por registro
picos = pd.read_csv(ROOT / "results/tables/picos_sp_registros.csv")
estilo = {"saudável (setembro)": ("tab:blue", "o", -0.22), "saudável (novembro)": ("tab:cyan", "s", 0.0),
          "defeituosa (setembro)": ("tab:red", "^", 0.22)}
rng = np.random.default_rng(0)
fig, eixos = plt.subplots(1, 3, figsize=(LARGURA, 2.1), layout="constrained")
for ax, sp in zip(eixos, (1, 2, 3)):
    g = picos[picos["SP"] == sp]
    for grupo, (cor, mk, desl) in estilo.items():
        v = g.loc[g["grupo"] == grupo, "f_base"]
        ax.scatter(desl + rng.uniform(-0.05, 0.05, len(v)), v, color=cor, marker=mk, s=12,
                   edgecolor="white", linewidth=0.4, label=grupo, zorder=3)
        ax.hlines(v.median(), desl - 0.08, desl + 0.08, color="black", lw=1.5, zorder=4)
    ax.set(title=f"SP{sp}", xticks=[], xlim=(-0.4, 0.4))
eixos[0].set_ylabel("$f_{base}$ do registro (Hz)")
eixos[0].legend(loc="lower left", fontsize=6)
fig.savefig(SAIDA / "rel_picos_sp.png")
plt.close(fig)

print("figuras salvas em", SAIDA)
