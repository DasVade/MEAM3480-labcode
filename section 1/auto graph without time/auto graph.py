import re
import sys
from pathlib import Path

import pandas as pd
import matplotlib.pyplot as plt


# --------- user settings ----------
DT_SECONDS = 0.5   # 你的 loop delay(500) + 采样开销，先用 0.5s；不准就改成 1.0
TEMP_REGEX = re.compile(r"T\(C\):\s*([-+]?\d+(?:\.\d+)?)")  # 匹配 "T(C): 14.31"
TIME_COL_CANDIDATES = ("time", "t", "timestamp", "seconds", "sec")
TEMP_COL_CANDIDATES = ("temp", "temperature", "tempC", "tC")
# ---------------------------------


def read_table(path: Path) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        # 尝试自动识别分隔符
        return pd.read_csv(path, engine="python")
    elif suffix in (".xlsx", ".xls"):
        return pd.read_excel(path)
    else:
        raise ValueError(f"Unsupported file type: {suffix} (use .csv or .xlsx)")


def find_column(df: pd.DataFrame, candidates) -> str | None:
    cols_lower = {c.lower(): c for c in df.columns}
    for cand in candidates:
        if cand.lower() in cols_lower:
            return cols_lower[cand.lower()]
    return None


def extract_temps_from_any_cell(df: pd.DataFrame) -> pd.Series:
    temps = []
    for _, row in df.iterrows():
        found = None
        for val in row.values:
            if pd.isna(val):
                continue
            s = str(val)
            m = TEMP_REGEX.search(s)
            if m:
                found = float(m.group(1))
                break
        if found is not None:
            temps.append(found)
    return pd.Series(temps, name="tempC")


def main():
    if len(sys.argv) < 2:
        print("Usage: python plot_temp.py <data.csv|data.xlsx>")
        sys.exit(1)

    path = Path(sys.argv[1]).expanduser().resolve()
    df = read_table(path)

    # 1) 优先：如果文件本来就有 time/temp 列（比如你以后输出 CSV: time,temp,heater）
    time_col = find_column(df, TIME_COL_CANDIDATES)
    temp_col = find_column(df, TEMP_COL_CANDIDATES)

    if temp_col is not None:
        tempC = pd.to_numeric(df[temp_col], errors="coerce").dropna().reset_index(drop=True)
        if time_col is not None:
            t = pd.to_numeric(df[time_col], errors="coerce").dropna().reset_index(drop=True)
            # 对齐长度
            n = min(len(t), len(tempC))
            t = t.iloc[:n]
            tempC = tempC.iloc[:n]
        else:
            t = pd.Series(range(len(tempC)), name="time_s") * DT_SECONDS
    else:
        # 2) 否则：像你现在这种“整行文本”，从任意单元格里抠 T(C):
        tempC = extract_temps_from_any_cell(df)
        if tempC.empty:
            raise RuntimeError("No temperatures found. Make sure your file contains lines like 'T(C): 14.31'.")
        t = pd.Series(range(len(tempC)), name="time_s") * DT_SECONDS

    out_df = pd.DataFrame({"time_s": t, "tempC": tempC})

    # --------- plot ----------
    plt.figure()
    plt.plot(out_df["time_s"], out_df["tempC"])
    plt.xlabel("Time (s)")
    plt.ylabel("Temperature (°C)")
    plt.title("Temperature vs Time")
    plt.grid(True)

    out_png = path.with_suffix(".temp_plot.png")
    plt.savefig(out_png, dpi=200, bbox_inches="tight")
    print(f"Saved plot to: {out_png}")

    # 也把提取后的数据另存一份干净 CSV
    out_clean = path.with_suffix(".clean_temp.csv")
    out_df.to_csv(out_clean, index=False)
    print(f"Saved cleaned data to: {out_clean}")


if __name__ == "__main__":
    main()