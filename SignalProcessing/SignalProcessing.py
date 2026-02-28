# Serhii Zeibel / 529
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, fft

# Параметри варіант 3
n = 500
Fs = 1000
F_max = 7

# Генерація випадкового сигналу
random_signal = np.random.normal(0, 10, n)

# Формування часової осі
t = np.arange(n) / Fs

# Розрахунок ФНЧ
w = F_max / (Fs / 2)
sos = signal.butter(3, w, 'low', output='sos')

# Фільтрація сигналу
filtered_signal = signal.sosfiltfilt(sos, random_signal)

# Розрахунок спектру
spectrum = fft.fft(filtered_signal)
spectrum_shifted = np.abs(fft.fftshift(spectrum))

freqs = fft.fftfreq(n, 1/Fs)
freqs_shifted = fft.fftshift(freqs)

# Графік сигналу
title_signal = f"Сигнал з максимальною частотою F_max = {F_max} Гц"

fig1, ax1 = plt.subplots(figsize=(21/2.54, 14/2.54))
ax1.plot(t, filtered_signal, linewidth=1)

ax1.set_xlabel("Час (секунди)", fontsize=14)
ax1.set_ylabel("Амплітуда сигналу", fontsize=14)
plt.title(title_signal, fontsize=14)

ax1.grid(True)

fig1.savefig("./figures/" + title_signal + ".png", dpi=600)
plt.close(fig1)

# Графік спектра
title_spectrum = f"Спектр сигналу з максимальною частотою F_max = {F_max} Гц"

fig2, ax2 = plt.subplots(figsize=(21/2.54, 14/2.54))
ax2.plot(freqs_shifted, spectrum_shifted, linewidth=1)

ax2.set_xlabel("Частота (Гц)", fontsize=14)
ax2.set_ylabel("Амплітуда спектру", fontsize=14)
plt.title(title_spectrum, fontsize=14)

ax2.grid(True)

fig2.savefig("./figures/" + title_spectrum + ".png", dpi=600)
plt.close(fig2)

print("У папці figures збережено 2 рисунки.")
