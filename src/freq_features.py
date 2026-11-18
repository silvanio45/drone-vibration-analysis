import numpy as np

FS = 10000          # taxa de amostragem do AccData (Hz) ---> foi capturada em get_data (io_utils.py [fs_acc])
FMIN = 10.0         # frequências abaixo disso (deriva, resíduo de DC) são ignoradas (Hz)

# Bandas (Hz), escolhidas olhando o espectro médio por condição e por SP (notebook 3_dominio_frec)
BANDAS = [(10, 45), (45, 150), (150, 600), (600, 5000)]


def espectro(w, fs=FS):
    """FFT de magnitude de janelas de sinal real.

    w : array (n_janelas, N) ou (N,)
    Retorna f (N//2 + 1,) em Hz e mag (n_janelas, N//2 + 1) em unidades do sinal.
    Um seno de amplitude A (centrado num bin) aparece com magnitude A.
    """
    # obriga w a ser uma array de duas dim.
    w = np.atleast_2d(np.asarray(w, dtype=float))
    # pega o número de amostras por janelas (número de colunas)
    N = w.shape[1]

    # remove a média do sinal, eliminando a componente DC (a freq de 0Hz)
    x = w - w.mean(axis=1, keepdims=True)           
    # janela de Hann para reduzir spectral leakage
    janela = np.hanning(N)                
    # fft unilateral, devido a simetria    
    X = np.fft.rfft(x * janela, axis=1)              

    # calcula as amplitudes estimadas de cada componente de frequencia
    # corrije o ganho devido o uso da janela de hann (dividindo pela soma dos coeficientes da janela)
    # multiplica por dois pela soma de +f e -f
    mag = 2.0 * np.abs(X) / janela.sum()             
    # dc e nyquist não têm par negativo
    mag[:, 0] /= 2.0                                 
    if N % 2 == 0:
        mag[:, -1] /= 2.0

    # calcula as frequências correspondentes a cada amplitude em mag
    f = np.fft.rfftfreq(N, d=1.0 / fs)               
    return f, mag


def nome_banda(lo, hi):
    return f"pot_{lo:g}_{hi:g}"


def feat_espectrais(f, mag, bandas=BANDAS, fmin=FMIN):
    """Características espectrais por janela.

    f    : eixo de frequências (Hz), vindo de `espectro`
    mag  : magnitudes (n_janelas, len(f))
    Retorna dict de arrays (uma entrada por janela), pronto para pd.DataFrame:
      f_dom        frequência do maior pico (Hz), com f >= fmin
      mag_pico     magnitude desse pico (unidade do sinal)
      pot_<lo>_<hi> soma de mag**2 na banda lo <= f < hi (a última banda inclui fs/2)
      centroide    sum(f*p) / sum(p) (Hz), com f >= fmin
      entropia     entropia de Shannon de p/sum(p), normalizada em [0, 1], com f >= fmin
    """
    # obriga mag a ser uma array de duas dim. (n_janelas, len(f))
    mag = np.atleast_2d(mag)
    # potência espectral de cada componente (proporcional à potência, não igual à temporal)
    p = mag ** 2
    # máscara das frequências a partir de fmin, ignora deriva e resíduo de DC
    util = f >= fmin
    # guarda só a parte útil do eixo, da potência e da magnitude
    fu, pu, mu = f[util], p[:, util], mag[:, util]

    # índice do maior pico de cada janela (um por linha)
    i = mu.argmax(axis=1)
    # frequência dominante e magnitude do pico dominante de cada janela
    # mu[np.arange(len(mu)), i] pega, em cada linha, a coluna do pico
    saida = {"f_dom": fu[i], "mag_pico": mu[np.arange(len(mu)), i]}

    # potência em cada banda, soma de mag**2 dos bins dentro da banda
    for lo, hi in bandas:
        # intervalo semiaberto [lo, hi) para um bin na fronteira não ser contado duas vezes
        # a última banda inclui o bin de fs/2 (nyquist)
        m = (f >= lo) & ((f <= hi) if hi >= f[-1] else (f < hi))
        saida[nome_banda(lo, hi)] = p[:, m].sum(axis=1)

    # potência total da parte útil, usada para normalizar centroide e entropia
    total = pu.sum(axis=1)
    # centroide: centro de massa do espectro de potência (em Hz)
    # média das frequências ponderada pela potência de cada uma
    saida["centroide"] = (pu * fu).sum(axis=1) / total

    # fração da potência em cada bin, vira uma distribuição de probabilidade (soma 1)
    # total[:, None] vira coluna para dividir cada linha pelo seu próprio total
    pn = pu / total[:, None]
    # entropia de shannon, o 1e-12 evita log(0) nos bins sem energia
    h = -(pn * np.log2(pn + 1e-12)).sum(axis=1)
    # divide pelo máximo possível (espectro plano), a entropia fica entre 0 e 1
    # perto de 0: energia concentrada em poucos picos, perto de 1: espalhada como ruído
    saida["entropia"] = h / np.log2(len(fu))
    return saida
