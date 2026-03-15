# Serhii Zeibel / 529
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal as sp_signal, fft


# Допоміжна функція для збереження графіка
def save_figure(fig, file_name, figures_dir, dpi_value=600):
    """
    Зберігає рисунок у папку figures.
    """
    fig.savefig(os.path.join(figures_dir, file_name + ".png"), dpi=dpi_value)
    plt.close(fig)


def quantize_signal(signal, M):
    """
    Квантування сигналу на M рівнів.
    """
    signal_min = np.min(signal)
    signal_max = np.max(signal)

    delta = (signal_max - signal_min) / (M - 1)

    # Індекси рівнів квантування
    q_index = np.round((signal - signal_min) / delta).astype(int)
    q_index = np.clip(q_index, 0, M - 1)

    # Квантований сигнал
    q_signal = signal_min + q_index * delta

    return q_signal, q_index, delta, signal_min, signal_max


def build_quantization_table(M, signal_min, delta):
    """
    Формує таблицю квантування.
    """
    amplitudes = signal_min + np.arange(M) * delta
    n_bits = int(np.log2(M))
    codes = [format(i, f"0{n_bits}b") for i in range(M)]

    return amplitudes, codes


def build_bit_sequence(q_index, n_bits):
    """
    Формує бітову послідовність із індексів рівнів.
    """
    bit_string_list = [format(i, f"0{n_bits}b") for i in q_index]
    bit_sequence_str = "".join(bit_string_list)
    bit_sequence = np.array([int(bit) for bit in bit_sequence_str], dtype=int)

    return bit_sequence, bit_sequence_str


def plot_quant_table(amplitudes, codes, M, figures_dir, width_cm, height_cm, font_size, dpi_value):
    """
    Побудова таблиці квантування без розбиття на частини.
    """
    title = f"Таблиця квантування для M = {M}"

    if M <= 16:
        fig_w, fig_h = 12, 8
        table_font = 10
        y_scale = 1.4
    elif M == 64:
        fig_w, fig_h = 12, 16
        table_font = 8
        y_scale = 1.0
    else:  # M == 256
        fig_w, fig_h = 12, 36
        table_font = 6
        y_scale = 0.75

    table_data = []
    for i in range(len(amplitudes)):
        table_data.append([f"{amplitudes[i]:.4f}", codes[i]])

    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.axis("off")

    table = ax.table(
        cellText=table_data,
        colLabels=["Значення сигналу", "Кодова послідовність"],
        cellLoc="center",
        colLoc="center",
        bbox=[0.03, 0.02, 0.94, 0.94]
    )

    table.auto_set_font_size(False)
    table.set_fontsize(table_font)
    table.scale(1, y_scale)

    ax.set_title(title, fontsize=font_size, pad=10)

    save_figure(fig, title, figures_dir, 300)


def plot_bit_sequence(bit_sequence, M, figures_dir, width_cm, height_cm, font_size, line_width, dpi_value):
    """
    Побудова графіка бітової послідовності.
    """
    title = f"Кодова послідовність сигналу при кількості рівнів квантування {M}"

    fig, ax = plt.subplots(figsize=(width_cm / 2.54, height_cm / 2.54))

    x = np.arange(len(bit_sequence))
    ax.bar(x, bit_sequence, width=1.0)

    ax.set_xlabel("Біти", fontsize=font_size)
    ax.set_ylabel("Амплітуда сигналу", fontsize=font_size)
    ax.set_title(title, fontsize=font_size)
    ax.set_ylim(0, 1.05)
    ax.grid(True)

    save_figure(fig, title, figures_dir, dpi_value)


# Головна функція
def main():
    # Параметри варіанту 3
    n = 500                 # Довжина сигналу у відліках
    Fs = 1000               # Частота дискретизації, Гц
    F_max = 7               # Максимальна частота сигналу, Гц
    F_filter = 14           # Полоса пропуску фільтра для відновлення, Гц
    Dt_values = [2, 4, 8, 16]  # Кроки дискретизації.
    M_values = [4, 16, 64, 256] # кількість рівнів квантування

    # Параметри оформлення графіків
    width_cm = 21
    height_cm = 14
    font_size = 14
    line_width = 1
    dpi_value = 600

    script_dir = os.path.dirname(os.path.abspath(__file__))
    figures_dir = os.path.join(script_dir, "figures")

    # ПРАКТИЧНА РОБОТА №2
    # Генерація випадкового сигналу
    # a = 0 (середнє), b = 10 (стандартне відхилення), n = 500 (кількість значень)
    random_signal = np.random.normal(0, 10, n)

    # Формування часової осі
    t = np.arange(n) / Fs

    # Розрахунок параметрів ФНЧ для обмеження сигналу частотою F_max
    # Нормована частота: w = F_max / (Fs / 2)
    w = F_max / (Fs / 2)

    # Фільтр Баттерворта 3-го порядку у форматі SOS
    sos = sp_signal.butter(3, w, "low", output="sos")

    # Фільтрація сигналу
    filtered_signal = sp_signal.sosfiltfilt(sos, random_signal)

    # Розрахунок спектра відфільтрованого сигналу
    spectrum = fft.fft(filtered_signal)
    spectrum_shifted = np.abs(fft.fftshift(spectrum))

    freqs = fft.fftfreq(n, 1 / Fs)
    freqs_shifted = fft.fftshift(freqs)

    # Побудова та збереження графіка сигналу
    title_signal = f"Сигнал з максимальною частотою F_max = {F_max} Гц"

    fig1, ax1 = plt.subplots(figsize=(width_cm / 2.54, height_cm / 2.54))
    ax1.plot(t, filtered_signal, linewidth=line_width)
    ax1.set_xlabel("Час (секунди)", fontsize=font_size)
    ax1.set_ylabel("Амплітуда сигналу", fontsize=font_size)
    ax1.set_title(title_signal, fontsize=font_size)
    ax1.grid(True)

    save_figure(fig1, title_signal, figures_dir, dpi_value)

    # Побудова та збереження графіка спектра
    title_spectrum = f"Спектр сигналу з максимальною частотою F_max = {F_max} Гц"

    fig2, ax2 = plt.subplots(figsize=(width_cm / 2.54, height_cm / 2.54))
    ax2.plot(freqs_shifted, spectrum_shifted, linewidth=line_width)
    ax2.set_xlabel("Частота (Гц)", fontsize=font_size)
    ax2.set_ylabel("Амплітуда спектру", fontsize=font_size)
    ax2.set_title(title_spectrum, fontsize=font_size)
    ax2.grid(True)

    save_figure(fig2, title_spectrum, figures_dir, dpi_value)

    # ПРАКТИЧНА РОБОТА №3
    # Підготовка списків для збереження результатів
    discrete_signals = []         # Дискретизовані сигнали
    discrete_spectrums = []       # Спектри дискретизованих сигналів
    discrete_freqs_shifted = []   # Частотні осі для спектрів дискретизованих сигналів
    restored_signals = []         # Відновлені аналогові сигнали після ФНЧ
    variance_errors_dt = []          # Дисперсії різниці (похибки)
    snr_ratios_dt = []               # Співвідношення сигнал-шум (відношення дисперсій)

    # Розрахунок параметрів ФНЧ для відновлення сигналу
    # Нормована частота фільтра відновлення: w = F_filter / (Fs / 2)
    w_restore = F_filter / (Fs / 2)
    sos_restore = sp_signal.butter(3, w_restore, "low", output="sos")

    # Дисперсія початкового (відфільтрованого) сигналу
    var_signal = np.var(filtered_signal)

    # Основний цикл по кроках дискретизації Dt
    for Dt in Dt_values:
        # Дискретизація сигналу (прорідження)-
        # Створюємо сигнал, заповнений нулями
        discrete_signal = np.zeros(n)

        # Записуємо значення лише через крок Dt
        for i in range(0, round(n / Dt)):
            idx = i * Dt
            if idx < n:
                discrete_signal[idx] = filtered_signal[idx]

        # Зберігаємо дискретизований сигнал
        discrete_signals.append(discrete_signal)

        # Розрахунок спектра дискретизованого сигналу
        d_spectrum = fft.fft(discrete_signal)
        d_spectrum_shifted = np.abs(fft.fftshift(d_spectrum))

        d_freqs = fft.fftfreq(n, 1 / Fs)
        d_freqs_shifted = fft.fftshift(d_freqs)

        # Зберігаємо спектр та частотну вісь
        discrete_spectrums.append(d_spectrum_shifted)
        discrete_freqs_shifted.append(d_freqs_shifted)

        # Відновлення аналогового сигналу з дискретного (через ФНЧ)
        restored_signal = sp_signal.sosfiltfilt(sos_restore, discrete_signal)

        # Зберігаємо відновлений сигнал
        restored_signals.append(restored_signal)

        #  Розрахунок похибки, дисперсії та ССШ
        # Різниця між відновленим та початковим (відфільтрованим) сигналом
        E1 = restored_signal - filtered_signal

        # Дисперсія різниці (похибки)
        var_error = np.var(E1)

        # Співвідношення сигнал-шум як відношення дисперсій
        if var_error == 0:
            snr_value = np.inf
        else:
            snr_value = var_signal / var_error

        # Зберігаємо результати
        variance_errors_dt.append(var_error)
        snr_ratios_dt.append(snr_value)

    # Відображення дискретизованих сигналів (2x2)
    title_discrete = "Сигнал з кроком дискретизації Dt = (2, 4, 8, 16)"

    fig3, ax3 = plt.subplots(2, 2, figsize=(width_cm / 2.54, height_cm / 2.54))

    s = 0
    for i in range(0, 2):
        for j in range(0, 2):
            ax3[i][j].plot(t, discrete_signals[s], linewidth=line_width)
            ax3[i][j].grid(True)
            s += 1

    fig3.supxlabel("Час (секунди)", fontsize=font_size)
    fig3.supylabel("Амплітуда сигналу", fontsize=font_size)
    fig3.suptitle(title_discrete, fontsize=font_size)

    save_figure(fig3, title_discrete, figures_dir, dpi_value)

    # Відображення спектрів дискретизованих сигналів (2x2)
    title_discrete_spec = "Спектри сигналів з кроком дискретизації Dt = (2, 4, 8, 16)"

    fig4, ax4 = plt.subplots(2, 2, figsize=(width_cm / 2.54, height_cm / 2.54))

    s = 0
    for i in range(0, 2):
        for j in range(0, 2):
            ax4[i][j].plot(discrete_freqs_shifted[s], discrete_spectrums[s], linewidth=line_width)
            ax4[i][j].grid(True)
            s += 1

    fig4.supxlabel("Частота (Гц)", fontsize=font_size)
    fig4.supylabel("Амплітуда спектру", fontsize=font_size)
    fig4.suptitle(title_discrete_spec, fontsize=font_size)

    save_figure(fig4, title_discrete_spec, figures_dir, dpi_value)

    # Відображення відновлених аналогових сигналів (2x2)
    title_restored = "Відновлені аналогові сигнали з кроком дискретизації Dt = (2, 4, 8, 16)"

    fig5, ax5 = plt.subplots(2, 2, figsize=(width_cm / 2.54, height_cm / 2.54))

    s = 0
    for i in range(0, 2):
        for j in range(0, 2):
            ax5[i][j].plot(t, restored_signals[s], linewidth=line_width)
            ax5[i][j].grid(True)
            s += 1

    fig5.supxlabel("Час (секунди)", fontsize=font_size)
    fig5.supylabel("Амплітуда сигналу", fontsize=font_size)
    fig5.suptitle(title_restored, fontsize=font_size)

    save_figure(fig5, title_restored, figures_dir, dpi_value)

    # Графік залежності дисперсії від кроку дискретизації ПЗ-3
    title_var = "Залежність дисперсії від кроку дискретизації"

    fig6, ax6 = plt.subplots(figsize=(width_cm / 2.54, height_cm / 2.54))
    ax6.plot(Dt_values, variance_errors_dt, linewidth=line_width)
    ax6.set_xlabel("Крок дискретизації", fontsize=font_size)
    ax6.set_ylabel("Дисперсія", fontsize=font_size)
    ax6.set_title(title_var, fontsize=font_size)
    ax6.grid(True)

    save_figure(fig6, title_var, figures_dir, dpi_value)

    # Графік співвідношення сигнал-шум від кроку дискретизації ПЗ-3
    title_snr = "Залежність співвідношення сигнал-шум від кроку дискретизації"

    fig7, ax7 = plt.subplots(figsize=(width_cm / 2.54, height_cm / 2.54))
    ax7.plot(Dt_values, snr_ratios_dt, linewidth=line_width)
    ax7.set_xlabel("Крок дискретизації", fontsize=font_size)
    ax7.set_ylabel("ССШ", fontsize=font_size)
    ax7.set_title(title_snr, fontsize=font_size)
    ax7.grid(True)

    save_figure(fig7, title_snr, figures_dir, dpi_value)

    # ПРАКТИЧНА РОБОТА №4
    quantized_signals = []
    variance_errors_m = []
    snr_ratios_m = []

    for M in M_values:
        n_bits = int(np.log2(M))

        # Квантування
        q_signal, q_index, delta, signal_min, signal_max = quantize_signal(filtered_signal, M)
        quantized_signals.append(q_signal)

        # Таблиця квантування
        amplitudes, codes = build_quantization_table(M, signal_min, delta)
        plot_quant_table(amplitudes, codes, M, figures_dir, width_cm, height_cm, font_size, dpi_value)

        # Бітова послідовність
        bit_sequence, bit_sequence_str = build_bit_sequence(q_index, n_bits)
        plot_bit_sequence(bit_sequence, M, figures_dir, width_cm, height_cm, font_size, line_width, dpi_value)

        # Похибка квантування
        error = q_signal - filtered_signal
        var_error = np.var(error)

        if var_error == 0:
            snr_value = np.inf
        else:
            snr_value = var_signal / var_error

        variance_errors_m.append(var_error)
        snr_ratios_m.append(snr_value)

        print(f"\nM = {M}")
        print(f"Крок квантування delta = {delta}")
        print(f"Кількість біт n_bits = {n_bits}")
        print(f"Довжина бітової послідовності = {len(bit_sequence)}")
        print(f"Дисперсія похибки = {var_error}")
        print(f"ССШ = {snr_value}")

    # Загальний рисунок цифрових сигналів
    title_quantized = "Цифрові сигнали для M = (4, 16, 64, 256)"

    fig8, ax8 = plt.subplots(2, 2, figsize=(width_cm / 2.54, height_cm / 2.54))

    s = 0
    for i in range(2):
        for j in range(2):
            ax8[i][j].plot(t, filtered_signal, linewidth=line_width, label="Початковий сигнал")
            ax8[i][j].step(t, quantized_signals[s], where="mid", linewidth=line_width, label=f"M={M_values[s]}")
            ax8[i][j].grid(True)
            ax8[i][j].legend(fontsize=8)
            s += 1

    fig8.supxlabel("Час (секунди)", fontsize=font_size)
    fig8.supylabel("Амплітуда сигналу", fontsize=font_size)
    fig8.suptitle(title_quantized, fontsize=font_size)

    save_figure(fig8, title_quantized, figures_dir, dpi_value)

    # Графік дисперсії для ПЗ 4
    title_var_m = "Залежність дисперсії від кількості рівнів квантування"

    fig9, ax9 = plt.subplots(figsize=(width_cm / 2.54, height_cm / 2.54))
    ax9.plot(M_values, variance_errors_m, linewidth=line_width)
    ax9.set_xlabel("Кількість рівнів квантування M", fontsize=font_size)
    ax9.set_ylabel("Дисперсія", fontsize=font_size)
    ax9.set_title(title_var_m, fontsize=font_size)
    ax9.grid(True)

    save_figure(fig9, title_var_m, figures_dir, dpi_value)

    # Графік ССШ для ПЗ 4
    title_snr_m = "Залежність співвідношення сигнал-шум від кількості рівнів квантування"

    fig10, ax10 = plt.subplots(figsize=(width_cm / 2.54, height_cm / 2.54))
    ax10.plot(M_values, snr_ratios_m, linewidth=line_width)
    ax10.set_xlabel("Кількість рівнів квантування M", fontsize=font_size)
    ax10.set_ylabel("ССШ", fontsize=font_size)
    ax10.set_title(title_snr_m, fontsize=font_size)
    ax10.grid(True)

    save_figure(fig10, title_snr_m, figures_dir, dpi_value)

    print("\nУ папці figures збережено всі графіки.")
    print("Кроки дискретизації Dt:", Dt_values)
    print("Дисперсії різниці для ПЗ 3:", variance_errors_dt)
    print("ССШ для ПЗ 3:", snr_ratios_dt)
    print("Рівні квантування M:", M_values)
    print("Дисперсії похибки для ПЗ 4:", variance_errors_m)
    print("ССШ для ПЗ 4:", snr_ratios_m)


if __name__ == "__main__":
    main()
