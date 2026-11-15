import hashlib
import re
from pathlib import Path

import numpy as np
import scipy.io as sio

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data" / "raw" / "DADOS"

PADRAO = re.compile(r"F(\d+)_SV(\d+)_SP(\d+)_C(\d+)(?:_R(\d+))?")


def get_info_name(name):
    stem = Path(name).stem
    m = PADRAO.fullmatch(stem)
    if m is None:
        raise ValueError(f"Nome fora do padrão esperado: {stem}")
    f, sv, sp, c, r = m.groups()
    return {
        "F": int(f),
        "SV": int(sv),
        "SP": int(sp),
        "C": int(c),
        "R": int(r) if r is not None else None,
    }


def get_data(name):
    data = sio.loadmat(DATA_DIR / name, squeeze_me=True, struct_as_record=False)

    retorno = {
        "imu": None, "acc": None,
        "tem_imu": "IMUData" in data,
        "tem_acc": "AccData" in data,
        "fs_imu": np.nan, "fs_imu_decl": np.nan,
        "fs_acc": np.nan, "fs_acc_decl": np.nan,
        "n_imu_t": np.nan, "n_imu_sig": np.nan,
        "n_acc_t": np.nan, "n_acc_sig": np.nan,
        "dt_std_imu": np.nan, "dt_std_acc": np.nan,
        "nan_imu": np.nan, "nan_acc": np.nan,
    }

    if retorno["tem_imu"]:
        imu = data["IMUData"]
        retorno["imu"] = imu.Vib_Data
        retorno["fs_imu"] = 1 / np.mean(np.diff(imu.t))
        retorno["fs_imu_decl"] = imu.samplingRate
        retorno["n_imu_t"] = len(imu.t)
        retorno["n_imu_sig"] = imu.Vib_Data.shape[1]
        retorno["dt_std_imu"] = np.std(np.diff(imu.t))
        retorno["nan_imu"] = int(np.isnan(imu.Vib_Data).sum())

    if retorno["tem_acc"]:
        acc = data["AccData"]
        retorno["acc"] = acc.Vib_Data
        retorno["fs_acc"] = 1 / np.mean(np.diff(acc.t))
        retorno["fs_acc_decl"] = acc.samplingRate
        retorno["n_acc_t"] = len(acc.t)
        retorno["n_acc_sig"] = len(acc.Vib_Data)
        retorno["dt_std_acc"] = np.std(np.diff(acc.t))
        retorno["nan_acc"] = int(np.isnan(acc.Vib_Data).sum())

    retorno.update(get_info_name(name))
    return retorno


def get_rotulo(df):
    df["rotulo"] = np.where(df["F"] == 0, "saudavel", "defeituoso")
    df["y"] = (df["F"] > 0).astype(int)


def get_id(df):
    df["id"] = df["hash_acc"].factorize()[0]
    df["copias"] = df.duplicated("hash_acc")


def carregar(nome):
    d = sio.loadmat(DATA_DIR / nome, squeeze_me=True, struct_as_record=False)
    return d["IMUData"], d["AccData"]


def ler_acc(nome):
    d = sio.loadmat(
        DATA_DIR / nome,
        squeeze_me=True,
        struct_as_record=False,
        variable_names=["AccData"],
    )
    return d["AccData"].Vib_Data


def estat(x):
    return {
        "mean": x.mean(),
        "std": x.std(),
        "min": x.min(),
        "max": x.max(),
        "pct_no_max": 100 * np.mean(x == x.max()),
        "pct_no_min": 100 * np.mean(x == x.min()),
    }


def std_por_bloco(t, x, seg=1.0):
    fs = round(1 / np.mean(np.diff(t)))
    n = int(fs * seg)
    k = len(x) // n
    return x[: k * n].reshape(k, n).std(axis=1)


def fundamental(nome, t0=10, t1=30, fs=10000, fmin=30, fmax=80):
    x = ler_acc(nome)[int(t0 * fs):int(t1 * fs)]
    x = x - x.mean()
    w = np.hanning(len(x))
    X = np.abs(np.fft.rfft(x * w))
    f = np.fft.rfftfreq(len(x), d=1 / fs)
    m = (f >= fmin) & (f <= fmax)
    return f[m][np.argmax(X[m])]


def digest(x):
    if x is None:
        return None
    return hashlib.md5(np.ascontiguousarray(x).tobytes()).hexdigest()