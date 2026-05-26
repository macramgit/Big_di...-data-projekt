import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy.stats import gaussian_kde
from sklearn.linear_model import LinearRegression
from statsmodels.nonparametric.smoothers_lowess import lowess

df = pd.read_excel('scraped.xlsx')

mediana_globalna = df['price'].median()
srednia_globalna = df['price'].mean()
mediana_pow_globalna = df['area_m2'].median()
srednia_pow_globalna = df['area_m2'].mean()

# Mediana ceny według miasta
mediana_miasta = df.groupby('city')['price'].median().sort_values()
colors = plt.cm.tab20.colors
bar_colors = [colors[i % len(colors)] for i in range(len(mediana_miasta))]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(mediana_miasta.index, mediana_miasta.values, color=bar_colors, edgecolor='white')
for bar, val in zip(bars, mediana_miasta.values):
    ax.text(bar.get_width() - 5000, bar.get_y() + bar.get_height() / 2,
            f'{val:,.0f} zł', va='center', ha='right', fontsize=9, fontweight='bold')
ax.axvline(x=mediana_globalna, color='black', linewidth=1.5, label=f'Mediana globalna ({mediana_globalna:,.0f} zł)')
ax.axvline(x=srednia_globalna, color='red', linewidth=1.5, label=f'Średnia globalna ({srednia_globalna:,.0f} zł)')
ax.set_xlabel('Cena (zł) — mediana')
ax.set_title('Mediana ceny mieszkań według miasta')
ax.legend()
plt.tight_layout()
plt.savefig('wykres_miasta_cena.png')
plt.close()

# Boxplot ceny według liczby pokoi
pokoje = sorted(df['rooms'].dropna().unique())
data_groups = [df[df['rooms'] == r]['price'].dropna().values for r in pokoje]

fig, ax = plt.subplots(figsize=(12, 7))
bp = ax.boxplot(data_groups, patch_artist=True, labels=[int(r) for r in pokoje],
                medianprops=dict(color='black', linewidth=2), showfliers=False)
for patch in bp['boxes']:
    patch.set_facecolor('lightgreen')
    patch.set_edgecolor('black')
ax.axhline(y=mediana_globalna, color='black', linewidth=1.5, label=f'Mediana globalna ({mediana_globalna:,.0f} zł)')
ax.axhline(y=srednia_globalna, color='red', linewidth=1.5, label=f'Średnia globalna ({srednia_globalna:,.0f} zł)')
ax.set_xlabel('Liczba pokoi')
ax.set_ylabel('Cena (zł)')
ax.set_title('Rozkład ceny mieszkań według liczby pokoi')
ax.legend()
plt.tight_layout()
plt.savefig('boxplot_pokoje_cena.png')
plt.close()

# Mediana powierzchni według miasta
mediana_pow_miasta = df.groupby('city')['area_m2'].median().sort_values()
bar_colors3 = [colors[i % len(colors)] for i in range(len(mediana_pow_miasta))]

fig, ax = plt.subplots(figsize=(12, 6))
bars = ax.barh(mediana_pow_miasta.index, mediana_pow_miasta.values, color=bar_colors3, edgecolor='white')
for bar, val in zip(bars, mediana_pow_miasta.values):
    ax.text(bar.get_width() - 0.5, bar.get_y() + bar.get_height() / 2,
            f'{val:.1f}', va='center', ha='right', fontsize=9, fontweight='bold')
ax.axvline(x=mediana_pow_globalna, color='black', linewidth=1.5, label=f'Mediana globalna ({mediana_pow_globalna:.1f} m²)')
ax.axvline(x=srednia_pow_globalna, color='red', linewidth=1.5, label=f'Średnia globalna ({srednia_pow_globalna:.1f} m²)')
ax.set_xlabel('Powierzchnia (mediana)')
ax.set_title('Mediana powierzchni mieszkań według miasta')
ax.legend()
plt.tight_layout()
plt.savefig('wykres_miasta_powierzchnia.png')
plt.close()

dane4 = df[['area_m2', 'price_per_m2']].dropna()

dane4_zoom = dane4[
    (dane4['area_m2'] >= 40) & (dane4['area_m2'] <= 70) &
    (dane4['price_per_m2'] >= 40000) & (dane4['price_per_m2'] <= 50000)
]

fig, ax = plt.subplots(figsize=(10, 7))

ax.scatter(dane4_zoom['area_m2'], dane4_zoom['price_per_m2'],
           alpha=0.4, color='black', s=30)

if len(dane4_zoom) > 10:
    smooth = lowess(dane4_zoom['price_per_m2'], dane4_zoom['area_m2'], frac=0.3)
    ax.plot(smooth[:, 0], smooth[:, 1], color='blue', linewidth=2)

ax.set_xlim(40, 70)
ax.set_ylim(40000, 50000)
ax.set_xlabel('Powierzchnia')
ax.set_ylabel('Cena za m²')
ax.set_title('Cena za m² a powierzchnia (zoom: 40–70 m²)')
plt.tight_layout()
plt.savefig('scatter_zoom_powierzchnia_cena_m2.png')
plt.close()

# Scatter powierzchnia vs cena/m2
fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(dane4['area_m2'], dane4['price_per_m2'], alpha=0.1, color='black', s=20)

smooth5 = lowess(dane4['price_per_m2'], dane4['area_m2'], frac=0.3)
ax.plot(smooth5[:, 0], smooth5[:, 1], color='blue', linewidth=2)

ax.set_xlabel('Powierzchnia')
ax.set_ylabel('Cena za m²')
ax.set_title('Cena za m² a powierzchnia (pełny zakres)')
plt.tight_layout()
plt.savefig('scatter_powierzchnia_cena_m2.png')
plt.close()

# Scatter powierzchnia vs cena
dane6 = df[['area_m2', 'price']].dropna()

fig, ax = plt.subplots(figsize=(10, 7))
ax.scatter(dane6['area_m2'], dane6['price'], alpha=0.1, color='black', s=20)

smooth6 = lowess(dane6['price'], dane6['area_m2'], frac=0.3)
ax.plot(smooth6[:, 0], smooth6[:, 1], color='blue', linewidth=2)

ax.set_xlabel('Powierzchnia')
ax.set_ylabel('Cena')
ax.set_title('Cena a powierzchnia mieszkania')
plt.tight_layout()
plt.savefig('scatter_powierzchnia_cena.png')
plt.close()
