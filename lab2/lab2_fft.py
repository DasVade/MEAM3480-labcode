#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


def load_csv(csv_path: str) -> pd.DataFrame:
    """
    Expect 4 columns: time, ax, ay, az
    Works whether header exists or not.
    """
    p = Path(csv_path)
    if not p.exists():
        raise FileNotFoundError(f"CSV not found: {p}")

    # Try with header first; if columns don't match, fallback to no-header
    df = pd.read_csv(p)
    cols = [c.strip().lower() for c in df.columns]
    if len(cols) < 4 or ("time" not in cols[0]):
        df = pd.read_csv(p, header=None)

    if df.shape[1] < 4:
        raise ValueError(f"CSV must have at least 4 columns (time, ax, ay, az). Got {df.shape[1]}")

    df = df.iloc[:, :4].copy()
    df.columns = ["time", "ax", "ay", "az"]
    df = df.apply(pd.to_numeric, errors="coerce").dropna()

    # Sort by time just in case
    df = df.sort_values("time").reset_index(drop=True)
    return df


def estimate_fs(time_s: np.ndarray) -> float:
    """
    Estimate sampling frequency from median dt (robust to small jitter).
    """
    dt = np.diff(time_s)
    dt = dt[np.isfinite(dt) & (dt > 0)]
    if dt.size == 0:
        raise ValueError("Time vector is invalid (non-increasing or too short).")
    Ts = np.median(dt)
    return 1.0 / Ts


def single_sided_fft(y: np.ndarray, fs: float):
    """
    Return frequency vector f (Hz) and single-sided amplitude spectrum P1.
    """
    y = np.asarray(y, dtype=float)
    N = y.size
    if N < 4:
        raise ValueError("Not enough samples for FFT.")

    Y = np.fft.fft(y)
    P2 = np.abs(Y / N)
    # Single-sided
    half = N // 2
    P1 = P2[: half + 1].copy()
    if P1.size > 2:
        P1[1:-1] *= 2.0  # Double except DC and Nyquist (if exists)
    f = fs * np.arange(0, half + 1) / N
    return f, P1


def main():
    if len(sys.argv) < 2:
        print("Usage: python lab2_fft.py your_data.csv")
        sys.exit(1)

    csv_path = sys.argv[1]
    df = load_csv(csv_path)

    t = df["time"].to_numpy()
    ax = df["ax"].to_numpy()
    ay = df["ay"].to_numpy()
    az = df["az"].to_numpy()

    # Magnitude (vector norm)
    amag = np.sqrt(ax**2 + ay**2 + az**2)

    # Subtract steady component (mean) — simplest form
    amag_detrend = amag - np.mean(amag)

    # Sampling frequency
    fs = estimate_fs(t)
    print(f"Estimated Fs = {fs:.3f} Hz (median dt = {1/fs:.6f} s), N = {len(t)} samples")

    # FFT
    f, P1 = single_sided_fft(amag_detrend, fs)

    # -------- Plot 1: Magnitude vs time --------
    plt.figure()
    plt.plot(t, amag_detrend)
    plt.xlabel("Time (s)")
    plt.ylabel("Acceleration Magnitude (detrended)")
    plt.title("Acceleration Magnitude vs Time (mean removed)")
    plt.grid(True)
    out1 = Path(csv_path).with_suffix("").as_posix() + "_magnitude.png"
    plt.savefig(out1, dpi=200, bbox_inches="tight")

    # -------- Plot 2: FFT --------
    plt.figure()
    plt.plot(f, P1)
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Amplitude")
    plt.title("Single-Sided Amplitude Spectrum (FFT)")
    plt.grid(True)

    # Optional: limit x-axis to something sensible (Nyquist is fs/2)
    plt.xlim(0, fs / 2)

    out2 = Path(csv_path).with_suffix("").as_posix() + "_fft.png"
    plt.savefig(out2, dpi=200, bbox_inches="tight")

    print(f"Saved:\n  {out1}\n  {out2}")
    plt.show()


if __name__ == "__main__":
    main()