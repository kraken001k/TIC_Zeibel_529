from random import randint
import numpy as np
import matplotlib.pyplot as plt
import os
from math import sin, cos, pi
import scipy.fft

# Практична робота №11
# Двійкова модуляція та прийом двійкових сигналів
# Варіант 3: ASK = 50 Гц, PSK = 50 Гц, FSK1 = 50 Гц, FSK2 = 25 Гц

ASK_FREQUENCY = 50
PSK_FREQUENCY = 50
FSK_FREQUENCY_1 = 50
FSK_FREQUENCY_2 = 25

# Основні параметри моделювання
SAMPLE_RATE = 1000      # частота дискретизації, Гц
SIGNAL_LENGTH = 1000    # загальна кількість відліків сигналу
BITS_COUNT = 10         # кількість бітів у повідомленні
BIT_LENGTH = 100        # кількість відліків на один біт


def plot(x, y, axis_x="", axis_y="", title=""):
    """Побудова графіка та збереження результату у папку figures."""

    fig, ax = plt.subplots(figsize=(21 / 2.54, 14 / 2.54))
    ax.plot(x, y, linewidth=1)
    ax.set_xlabel(axis_x, fontsize=14)
    ax.set_ylabel(axis_y, fontsize=14)
    plt.title(title, fontsize=14)

    # Якщо папки для графіків ще немає, вона створюється автоматично.
    isdir = os.path.isdir('./figures/')
    if not isdir:
        os.mkdir('./figures/')

    fig.savefig('./figures/' + title + '.png', dpi=600)
    plt.close(fig)


def spectrum(sequence):
    """Розрахунок спектра сигналу за допомогою швидкого перетворення Фур'є."""

    y_spectrum = np.abs(scipy.fft.fftshift(scipy.fft.fft(sequence)))
    x_spectrum = scipy.fft.fftshift(scipy.fft.fftfreq(len(sequence), 1 / len(sequence)))

    # Оскільки спектр симетричний, для відображення використовується права частина.
    middle = round(len(x_spectrum) / 2)
    return x_spectrum[middle:], y_spectrum[middle:]


def create_sequence():
    """Формування випадкової цифрової послідовності з 10 бітів."""

    sequence = np.zeros(SIGNAL_LENGTH)

    # Кожен біт займає 100 відліків, тому загальна довжина сигналу дорівнює 1000.
    for i in range(BITS_COUNT):
        bit = randint(0, 1)
        start = i * BIT_LENGTH
        end = start + BIT_LENGTH
        sequence[start:end] = bit

    return sequence


def ask_modulation(frequency, sequence):
    """Формування сигналу з амплітудною модуляцією."""

    sequence_ask = np.zeros(SIGNAL_LENGTH)

    # При ASK гармонійне коливання присутнє тільки для біта 1.
    for i in range(0, len(sequence)):
        sequence_ask[i] = sequence[i] * cos(2 * pi * frequency * i / SAMPLE_RATE)

    return sequence_ask


def ask_demodulation(frequency, sequence):
    """Демодуляція ASK сигналу методом накопичення та порогового рішення."""

    ask_product = np.zeros(SIGNAL_LENGTH)
    ask_demodulated_signal = np.zeros(SIGNAL_LENGTH)
    threshold = np.ones(SIGNAL_LENGTH) * 25
    sequence_demodulated = np.zeros(SIGNAL_LENGTH)

    # Прийнятий сигнал множиться на опорне коливання з тією самою частотою.
    for i in range(0, len(sequence)):
        ask_product[i] = sequence[i] * cos(2 * pi * frequency * i / SAMPLE_RATE)

    # Для кожного біта окремо виконується накопичення значень.
    for i in range(0, BITS_COUNT):
        s = 0
        start = i * BIT_LENGTH
        end = start + BIT_LENGTH

        for t in range(start, end):
            s = s + ask_product[t]
            ask_demodulated_signal[t] = s

    # Порогове рішення: якщо накопичене значення більше порогу, приймається 1.
    ask_demodulated = 1 / 2 * (np.sign(ask_demodulated_signal - threshold) + 1)

    # На всьому інтервалі біта записується прийняте значення цього біта.
    for i in range(0, BITS_COUNT):
        start = i * BIT_LENGTH
        end = start + BIT_LENGTH
        sequence_demodulated[start:end] = ask_demodulated[end - 1]

    return ask_demodulated_signal, sequence_demodulated


def psk_modulation(frequency, sequence):
    """Формування сигналу з фазовою модуляцією."""

    sequence_psk = np.zeros(SIGNAL_LENGTH)

    # При PSK значення біта визначає зміну фази несучого коливання.
    for i in range(0, len(sequence)):
        sequence_psk[i] = sin(2 * pi * frequency * i / SAMPLE_RATE + sequence[i] * pi + pi)

    return sequence_psk


def psk_demodulation(frequency, sequence):
    """Демодуляція PSK сигналу методом накопичення."""

    psk_product = np.zeros(SIGNAL_LENGTH)
    psk_demodulated_signal = np.zeros(SIGNAL_LENGTH)
    threshold = np.ones(SIGNAL_LENGTH) * 25
    sequence_demodulated = np.zeros(SIGNAL_LENGTH)

    # Сигнал перемножується з опорним синусоїдальним коливанням.
    for i in range(0, len(sequence)):
        psk_product[i] = sequence[i] * sin(2 * pi * frequency * i / SAMPLE_RATE)

    # Накопичення виконується окремо на кожному бітовому інтервалі.
    for i in range(0, BITS_COUNT):
        s = 0
        start = i * BIT_LENGTH
        end = start + BIT_LENGTH

        for t in range(start, end):
            s = s + psk_product[t]
            psk_demodulated_signal[t] = s

    # Після накопичення виконується порівняння з пороговим значенням.
    psk_demodulated = 1 / 2 * (np.sign(psk_demodulated_signal - threshold) + 1)

    for i in range(0, BITS_COUNT):
        start = i * BIT_LENGTH
        end = start + BIT_LENGTH
        sequence_demodulated[start:end] = psk_demodulated[end - 1]

    return psk_demodulated_signal, sequence_demodulated


def fsk_modulation(frequency1, frequency2, sequence):
    """Формування сигналу з частотною модуляцією."""

    sequence_fsk = np.zeros(SIGNAL_LENGTH)

    # Для біта 1 використовується перша частота, для біта 0 — друга частота.
    for i in range(0, len(sequence)):
        sequence_fsk[i] = (sequence[i] * sin(2 * pi * frequency1 * i / SAMPLE_RATE) +
                           abs(sequence[i] - 1) * sin(2 * pi * frequency2 * i / SAMPLE_RATE))

    return sequence_fsk


def fsk_demodulation(frequency1, frequency2, sequence):
    """Демодуляція FSK сигналу з порівнянням двох частотних складових."""

    fsk_product1 = np.zeros(SIGNAL_LENGTH)
    fsk_product2 = np.zeros(SIGNAL_LENGTH)
    fsk_demodulated_signal1 = np.zeros(SIGNAL_LENGTH)
    fsk_demodulated_signal2 = np.zeros(SIGNAL_LENGTH)
    sequence_demodulated = np.zeros(SIGNAL_LENGTH)

    # Прийнятий сигнал перемножується з двома опорними коливаннями.
    for i in range(0, len(sequence)):
        fsk_product1[i] = sequence[i] * sin(2 * pi * frequency1 * i / SAMPLE_RATE)
        fsk_product2[i] = sequence[i] * sin(2 * pi * frequency2 * i / SAMPLE_RATE)

    # Для кожного біта накопичуються значення для двох можливих частот.
    for i in range(0, BITS_COUNT):
        s1 = 0
        s2 = 0
        start = i * BIT_LENGTH
        end = start + BIT_LENGTH

        for t in range(start, end):
            s1 = s1 + fsk_product1[t]
            fsk_demodulated_signal1[t] = s1

            s2 = s2 + fsk_product2[t]
            fsk_demodulated_signal2[t] = s2

    # Рішення приймається за більшою накопиченою складовою.
    fsk_demodulated = 1 / 2 * (np.sign(fsk_demodulated_signal1 - fsk_demodulated_signal2) + 1)

    for i in range(0, BITS_COUNT):
        start = i * BIT_LENGTH
        end = start + BIT_LENGTH
        sequence_demodulated[start:end] = fsk_demodulated[end - 1]

    return fsk_demodulated_signal1, fsk_demodulated_signal2, sequence_demodulated


def create_noise(mean, standard_deviation, length):
    """Генерація нормального білого шуму."""

    return np.random.normal(mean, standard_deviation, length)


def noise_stress(sequence, sequence_modulated, modulation, frequency):
    """Статистичне дослідження завадостійкості заданого типу модуляції."""

    error_modulated = []

    # Зовнішній цикл задає рівень шуму в каналі.
    for i in range(0, 20):
        p = 0

        # Для кожного рівня шуму виконується 200 повторень експерименту.
        for m in range(0, 200):
            noise = create_noise(0, 1, SIGNAL_LENGTH)
            sequence_noise = sequence_modulated + i * noise

            # Демодуляція виконується залежно від типу модуляції.
            if modulation == "ASK":
                ask_demodulated_signal, sequence_demodulated = ask_demodulation(frequency[0], sequence_noise)
            elif modulation == "PSK":
                psk_demodulated_signal, sequence_demodulated = psk_demodulation(frequency[0], sequence_noise)
            elif modulation == "FSK":
                fsk_demodulated_signal1, fsk_demodulated_signal2, sequence_demodulated = fsk_demodulation(
                    frequency[0], frequency[1], sequence_noise
                )

            # Оцінка помилки між початковою та прийнятою послідовністю.
            summa = abs(sum(sequence - sequence_demodulated))
            p = p + summa / SIGNAL_LENGTH

        error_modulated += [p / 200]

    return error_modulated


def main(ask, psk, fsk1, fsk2):
    """Основна функція виконання практичної роботи."""

    # Формування початкової цифрової послідовності та часової осі.
    sequence = create_sequence()
    x = np.arange(len(sequence)) / SAMPLE_RATE

    plot(x, sequence, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Згенерована випадкова послідовність")

    # Амплітудна модуляція та побудова її спектра.
    sequence_ask = ask_modulation(ask, sequence)
    plot(x, sequence_ask, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Амплітудна модуляція")

    x_spectrum, spectrum_sequence_ask = spectrum(sequence_ask)
    plot(x_spectrum, spectrum_sequence_ask, axis_x="Частота, Гц", axis_y="Амплітуда спектру",
         title="Спектр при амплітудній модуляції")

    # Фазова модуляція та побудова її спектра.
    sequence_psk = psk_modulation(psk, sequence)
    plot(x, sequence_psk, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Фазова модуляція")

    x_spectrum, spectrum_sequence_psk = spectrum(sequence_psk)
    plot(x_spectrum, spectrum_sequence_psk, axis_x="Частота, Гц", axis_y="Амплітуда спектру",
         title="Спектр при фазовій модуляції")

    # Частотна модуляція та побудова її спектра.
    sequence_fsk = fsk_modulation(fsk1, fsk2, sequence)
    plot(x, sequence_fsk, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Частотна модуляція")

    x_spectrum, spectrum_sequence_fsk = spectrum(sequence_fsk)
    plot(x_spectrum, spectrum_sequence_fsk, axis_x="Частота, Гц", axis_y="Амплітуда спектру",
         title="Спектр при частотній модуляції")

    # Генерація шуму та додавання його до модульованих сигналів.
    noise = create_noise(0, 1, SIGNAL_LENGTH)
    sequence_ask_noise = sequence_ask + noise
    sequence_psk_noise = sequence_psk + noise
    sequence_fsk_noise = sequence_fsk + noise

    plot(x, sequence_ask_noise, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Амплітудна модуляція з шумом")
    plot(x, sequence_psk_noise, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Фазова модуляція з шумом")
    plot(x, sequence_fsk_noise, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Частотна модуляція з шумом")

    # Демодуляція ASK сигналу з шумом.
    ask_demodulated_signal, sequence_demodulated = ask_demodulation(ask, sequence_ask_noise)
    plot(x, ask_demodulated_signal, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Демодульований сигнал з амплітудною модуляцією")
    plot(x, sequence_demodulated, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Демодульована послідовність з амплітудною модуляцією")

    # Демодуляція PSK сигналу з шумом.
    psk_demodulated_signal, sequence_demodulated = psk_demodulation(psk, sequence_psk_noise)
    plot(x, psk_demodulated_signal, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Демодульований сигнал з фазовою модуляцією")
    plot(x, sequence_demodulated, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Демодульована послідовність з фазовою модуляцією")

    # Демодуляція FSK сигналу з шумом.
    fsk_demodulated_signal1, fsk_demodulated_signal2, sequence_demodulated = fsk_demodulation(
        fsk1, fsk2, sequence_fsk_noise
    )
    plot(x, fsk_demodulated_signal1, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Демодульований сигнал 1 з частотною модуляцією")
    plot(x, fsk_demodulated_signal2, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Демодульований сигнал 2 з частотною модуляцією")
    plot(x, sequence_demodulated, axis_x="Час, c", axis_y="Амплітуда сигналу",
         title="Демодульована послідовність з частотною модуляцією")

    # Розрахунок залежності ймовірності помилки від рівня шуму.
    error_ask = noise_stress(sequence, sequence_ask, "ASK", [ask])
    error_psk = noise_stress(sequence, sequence_psk, "PSK", [psk])
    error_fsk = noise_stress(sequence, sequence_fsk, "FSK", [fsk1, fsk2])

    # Побудова спільного графіка завадостійкості для трьох типів модуляції.
    fig, ax = plt.subplots(figsize=(21 / 2.54, 14 / 2.54))
    ax.plot(np.arange(0, 20), error_ask, linewidth=1)
    ax.plot(np.arange(0, 20), error_psk, linewidth=1)
    ax.plot(np.arange(0, 20), error_fsk, linewidth=1)
    ax.set_xlabel('Діапазон змін шуму', fontsize=14)
    ax.set_ylabel('Ймовірність помилки', fontsize=14)
    ax.legend(['ASK', 'PSK', 'FSK'], loc=2)
    plt.title('Оцінка завадостійкості трьох видів модуляції', fontsize=14)

    isdir = os.path.isdir('./figures/')
    if not isdir:
        os.mkdir('./figures/')

    fig.savefig('./figures/' + 'Оцінка завадостійкості трьох видів модуляції' + '.png', dpi=600)
    plt.close(fig)


if __name__ == "__main__":
    main(ASK_FREQUENCY, PSK_FREQUENCY, FSK_FREQUENCY_1, FSK_FREQUENCY_2)
