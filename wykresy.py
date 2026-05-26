import pandas as pd
import matplotlib.pyplot as plt

INPUT_FILE = "Zescrapowane dane.xlsx"

df = pd.read_excel(INPUT_FILE)
df = df.dropna(subset=["price", "area_m2", "rooms", "city"])
df = df[df["price"].between(50000, 20000000)]
df = df[df["area_m2"].between(10, 400)]
df = df[df["rooms"].between(1, 6)]

df["rooms"] = df["rooms"].astype(int)
df["city_cap"] = df["city"].str.capitalize()

cities = sorted(df["city_cap"].unique())
n_cities = len(cities)

ncols = 3
nrows = -(-n_cities // ncols)

fig, axes = plt.subplots(
    nrows, ncols,
    figsize=(5 * ncols, 3.5 * nrows),
    constrained_layout=True,
)
fig.get_layout_engine().set(hspace=0.35, wspace=0.3)

axes_flat = axes.flatten()

room_labels = {1: "1 pokój", 2: "2 pokoje", 3: "3 pokoje",
               4: "4 pokoje", 5: "5 pokoi",  6: "6 pokoi"}
room_order = [1, 2, 3, 4, 5, 6]

for idx, city in enumerate(cities):
    ax = axes_flat[idx]
    city_df = df[df["city_cap"] == city]

    groups = []
    labels = []
    for r in room_order:
        subset = city_df[city_df["rooms"] == r]["price"] / 1_000
        if not subset.empty:
            groups.append(subset.values)
            labels.append(room_labels[r])

    if not groups:
        ax.set_visible(False)
        continue

    bp = ax.boxplot(
        groups,
        vert=False,
        patch_artist=True,
        widths=0.55,
        flierprops=dict(marker=".", markerfacecolor="black",
                        markeredgecolor="black", markersize=4, linestyle="none"),
        medianprops=dict(color="black", linewidth=1.5),
        whiskerprops=dict(color="black", linewidth=0.8),
        capprops=dict(color="black", linewidth=0.8),
        boxprops=dict(linewidth=0.8),
    )

    for patch in bp["boxes"]:
        patch.set_facecolor("lightgreen")
        patch.set_edgecolor("black")

    ax.set_yticks(range(1, len(labels) + 1))
    ax.set_yticklabels(labels, fontsize=8)
    ax.set_title(city, fontsize=10, fontweight="bold", pad=6)

    # "Cena w tys." pod każdym subplotem
    ax.set_xlabel("Cena w tys.", fontsize=8)

    ax.tick_params(axis="x", labelsize=7)
    ax.grid(axis="x", linestyle="--", linewidth=0.4, alpha=0.6)
    ax.set_axisbelow(True)

    if idx % ncols == 0:
        ax.set_ylabel("Liczba pokoi", fontsize=8)

for i in range(n_cities, len(axes_flat)):
    axes_flat[i].set_visible(False)

fig.suptitle("Cena mieszkania wg liczby pokoi – podział na miasta",
             fontsize=13, fontweight="bold", y=1.03)

OUTPUT_PNG = "boxplot_mieszkania.png"
plt.savefig(OUTPUT_PNG, dpi=150, bbox_inches="tight")
plt.show()
print(f"Zapisano: {OUTPUT_PNG}")