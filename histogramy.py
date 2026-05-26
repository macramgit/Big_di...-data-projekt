import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import gaussian_kde

df = pd.read_excel('./scraped.xlsx')

SKIP_COLUMNS = {'offer_url', 'title', 'location_raw', 'price_raw', 'info_raw', 'description', 'scrape_date'}

labels = {
    'city': ['warszawa', 'krakow', 'wroclaw', 'poznan', 'gdansk', 'lodz'],
    'rooms': ['1', '2', '3', '4', '5', '6', '7', '8', '9'],
}

columns = [c for c in df.columns if c not in SKIP_COLUMNS]

for column in columns:
    fig, ax = plt.subplots(figsize=(23, 6))
    data = df[column].dropna()

    if column in labels:
        counts = data.value_counts().sort_index()
        col_labels = [str(labels[column][i]) if isinstance(i, int) else str(i) for i in counts.index]
        bars = ax.bar(col_labels, counts.values, edgecolor='black')
        ax.set_xticks(range(len(col_labels)))
        ax.set_xticklabels(col_labels, rotation=45, ha='right')
        ax.bar_label(bars, padding=3)

    elif pd.api.types.is_numeric_dtype(data):
        if data.nunique() <= 30:
            counts = data.value_counts().sort_index()
            col_labels = [str(v) for v in counts.index]
            bars = ax.bar(col_labels, counts.values, edgecolor='black')
            ax.set_xticks(range(len(col_labels)))
            ax.set_xticklabels(col_labels, rotation=45, ha='right')
            ax.bar_label(bars, padding=3)
        else:
            counts, edges, bars = ax.hist(data, bins='auto', edgecolor='black')
            centers = (edges[:-1] + edges[1:]) / 2
            ax.set_xticks(centers)
            ax.set_xticklabels([f'{c:.0f}' for c in centers], rotation=90, fontsize=7)
            ax.bar_label(bars, labels=[int(v) if v > 0 else '' for v in counts], padding=3)

    else:
        counts = data.value_counts().sort_index()
        if len(counts) <= 50:
            bars = ax.bar(counts.index.astype(str), counts.values, edgecolor='black')
            ax.set_xticks(range(len(counts)))
            ax.set_xticklabels(counts.index.astype(str), rotation=45, ha='right')
            ax.bar_label(bars, padding=3)
        else:
            print(f"Skipping '{column}': too many unique string values ({len(counts)})")
            plt.close(fig)
            continue

    ax.set_title(f"{column}")
    ax.set_xlabel(column)
    ax.set_ylabel('frequency')
    plt.tight_layout()
    plt.savefig(f"./{column}.png", dpi=100)
    plt.close(fig)

data = df['area_m2'].dropna()
kde = gaussian_kde(data)
x = np.linspace(data.min(), data.max(), 500)

fig, ax = plt.subplots(figsize=(14, 6))
ax.fill_between(x, kde(x), alpha=0.5, color='lightgreen')
ax.plot(x, kde(x), color='black')
ax.axvline(data.median(), color='black', label=f'mediana: {data.median():.1f}')
ax.axvline(data.mean(), color='red', label=f'średnia: {data.mean():.1f}')
ax.set_xlabel('area_m2')
ax.set_ylabel('density')
ax.legend()
plt.tight_layout()
plt.savefig('density_area_m2.png', dpi=100)

data = df['price'].dropna()
kde = gaussian_kde(data)
x = np.linspace(data.min(), data.max(), 500)

fig, ax = plt.subplots(figsize=(14, 6))
ax.fill_between(x, kde(x), alpha=0.5, color='lightgreen')
ax.plot(x, kde(x), color='black')
ax.axvline(data.median(), color='black', label=f'mediana: {data.median():.1f}')
ax.axvline(data.mean(), color='red', label=f'średnia: {data.mean():.1f}')
ax.set_xlabel('price')
ax.set_ylabel('density')
ax.legend()
plt.tight_layout()
plt.savefig('density_price.png', dpi=100)

data = df['price_per_m2'].dropna()
kde = gaussian_kde(data)
x = np.linspace(data.min(), data.max(), 500)

fig, ax = plt.subplots(figsize=(14, 6))
ax.fill_between(x, kde(x), alpha=0.5, color='lightgreen')
ax.plot(x, kde(x), color='black')
ax.axvline(data.median(), color='black', label=f'mediana: {data.median():.1f}')
ax.axvline(data.mean(), color='red', label=f'średnia: {data.mean():.1f}')
ax.set_xlabel('price')
ax.set_ylabel('density')
ax.legend()
plt.tight_layout()
plt.savefig('density_price_per_m2.png', dpi=100)
