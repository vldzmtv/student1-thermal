import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("results/temperature.csv")
plt.figure(figsize=(9, 5))
plt.plot(
    df["time_s"],
    df["T_min_K"],
    "o-",
    label="Расчёт OpenFOAM"
)
plt.axline(
    (0, 423.15),
    slope=113.8,
    linestyle="--",
    color="red",
    label="Аналитическая зависимость (113,8 К/с)"
)

plt.xlabel("Время, с")
plt.ylabel("Температура, К")
plt.title("Кейс 00: нагрев адиабатного куба")
plt.grid(True)
plt.legend()
plt.tight_layout()
plt.savefig("results/T_vs_time.png", dpi=200)
plt.close()
