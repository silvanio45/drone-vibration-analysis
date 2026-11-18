
from src.io_utils import ler_acc
import numpy as np


def get_matriz_acc(arquivo, list_janelas):
    g = list_janelas[list_janelas["arquivo"] == arquivo]
    sinal = ler_acc(arquivo)
    matriz = []
    for _, row in g.iterrows():
        matriz.append(sinal[row["ini"]:row["fim"]])
    return np.array(matriz)