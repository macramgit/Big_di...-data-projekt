import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

INPUT_FILE = "Zescrapowane dane.xlsx"

df = pd.read_excel(INPUT_FILE)

# czyszczenie
df = df.dropna(subset=["price", "area_m2", "rooms", "city"])
df = df[df["price"].between(50000, 20000000)]
df = df[df["area_m2"].between(10, 400)]
df = df[df["rooms"].between(1, 6)]

df["rooms"] = df["rooms"].astype(int)
df["city_cap"] = df["city"].str.capitalize()

# WYKRES 1 cena wg liczby pokoi, podział na miasta
cities = sorted(df["city_cap"].unique())
n_cities = len(cities)
ncols = 3
nrows = -(-n_cities // ncols)

fig1, axes = plt.subplots(nrows, ncols, figsize=(5 * ncols, 3.5 * nrows), constrained_layout=True)
fig1.get_layout_engine().set(hspace=0.35, wspace=0.3)
axes_flat = axes.flatten()

room_labels = {1: "1 pokój", 2: "2 pokoje", 3: "3 pokoje",
               4: "4 pokoje", 5: "5 pokoi",  6: "6 pokoi"}
room_order = [1, 2, 3, 4, 5, 6]

for idx, city in enumerate(cities):
    ax = axes_flat[idx]
    city_df = df[df["city_cap"] == city]

    groups, labels = [], []
    for r in room_order:
        subset = city_df[city_df["rooms"] == r]["price"] / 1000
        if not subset.empty:
            groups.append(subset.values)
            labels.append(room_labels[r])

    if not groups:
        ax.set_visible(False)
        continue

    bp = ax.boxplot(
        groups, vert=False, patch_artist=True, widths=0.55,
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
    ax.set_xlabel("Cena w tys.", fontsize=8)
    ax.tick_params(axis="x", labelsize=7)
    ax.grid(axis="x", linestyle="--", linewidth=0.4, alpha=0.6)
    ax.set_axisbelow(True)
    if idx % ncols == 0:
        ax.set_ylabel("Liczba pokoi", fontsize=8)

for i in range(n_cities, len(axes_flat)):
    axes_flat[i].set_visible(False)

fig1.suptitle("Cena mieszkania wg liczby pokoi – podział na miasta",
              fontsize=13, fontweight="bold", y=1.03)

fig1.savefig("boxplot_mieszkania.png", dpi=150, bbox_inches="tight")
print("Zapisano: boxplot_mieszkania.png")

# WYKRES 2 struktura powierzchni wg miasta
bins   = [0, 38, 60, 90, 1000]
labels = ["poniżej 38 m²", "38-60 m²", "60-90 m²", "ponad 90 m²"]
colors = ["#444444", "#448844", "#44aa44", "#44ff44"]

df["pow_kat"] = pd.cut(df["area_m2"], bins=bins, labels=labels)

grouped = (
    df.groupby(["city_cap", "pow_kat"], observed=True)
    .size()
    .reset_index(name="n")
)
grouped["p"] = grouped.groupby("city_cap")["n"].transform(lambda x: 100 * x / x.sum())

pivot = grouped.pivot(index="city_cap", columns="pow_kat", values="p").fillna(0)
pivot = pivot[labels]
pivot = pivot.sort_index(ascending=False)

fig2, ax2 = plt.subplots(figsize=(10, 7))

y = np.arange(len(pivot))
lefts = np.zeros(len(pivot))
for cat, color in zip(labels, colors):
    vals = pivot[cat].values
    ax2.barh(y, vals, left=lefts, height=0.6, color=color, edgecolor="none")
    lefts += vals

for xv in [25, 50, 75, 90, 100]:
    ax2.axvline(xv, color="black", linewidth=0.9, zorder=5)

ax2.set_yticks(y)
ax2.set_yticklabels(pivot.index.tolist(), fontsize=10)
ax2.set_xticks([25, 50, 75, 90, 100])
ax2.set_xticklabels([25, 50, 75, 90, 100], fontsize=9)
ax2.set_xlim(0, 100)
ax2.set_ylabel("miasto", fontsize=10)
ax2.grid(False)

legend_patches = [mpatches.Patch(color=c, label=l)
                  for c, l in zip(reversed(colors), reversed(labels))]
ax2.legend(handles=legend_patches, title="Powierzchnia:", title_fontsize=10,
           fontsize=9, loc="lower right", bbox_to_anchor=(1.28, 0.3), frameon=False)

fig2.suptitle("Struktura powierzchni mieszkań wg miasta",
              fontsize=12, fontweight="bold", y=1.02)
plt.tight_layout()

fig2.savefig("barplot_powierzchnia.png", dpi=150, bbox_inches="tight")
print("Zapisano: barplot_powierzchnia.png")

plt.show()