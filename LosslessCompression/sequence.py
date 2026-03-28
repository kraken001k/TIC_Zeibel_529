import random
import string
import math
import collections
import os
import matplotlib.pyplot as plt

# Початкові вхідні дані
# //////////////////////////////////////////////////////////

# Прізвище студента
SURNAME = "ZEIBEL"

# Номер групи
GROUP = "529"

# Номер у журналі
JOURNAL_NUMBER = 3

# Довжина кожної згенерованої послідовності
N_SEQUENCE = 100


# Підготовка файлів
# ///////////////////////////////////////////////////////////////

# Шлях до текстового файлу з характеристиками послідовностей
RESULTS_FILE = "results_sequence.txt"

# Шлях до текстового файлу, де будуть самі послідовності
SEQUENCES_FILE = "sequence.txt"

# Шлях до зображення з таблицею характеристик
FIGURE_FILE = "Характеристики сформованих послідовностей.png"


# Фіксація випадковості
# //////////////////////////////////////////////////////////

# Встановлюємо seed, щоб випадкові результати були однаковими
# при кожному запуску програми
random.seed(42)


# Функції генерації послідовностей
# //////////////////////////////////////////////////////////////

def generate_sequence_1():
    """
    Генерує бінарну послідовність із 100 символів.
    Кількість символів '1' дорівнює номеру в журналі,
    решта символів — '0'.

    Потім усі символи випадково перемішуються.
    """
    list1 = ['1'] * JOURNAL_NUMBER
    list0 = ['0'] * (N_SEQUENCE - JOURNAL_NUMBER)

    # Об'єднуємо всі символи в один список
    sequence_list = list1 + list0

    # Перемішуємо порядок елементів
    random.shuffle(sequence_list)

    # Перетворюємо список символів у рядок
    return ''.join(sequence_list)


def generate_sequence_2():
    """
    Генерує послідовність, у якій:
    - на початку записане прізвище студента,
    - решта позицій заповнюються символами '0'.

    Перемішування тут немає.
    """
    list1 = list(SURNAME)
    list0 = ['0'] * (N_SEQUENCE - len(SURNAME))
    sequence_list = list1 + list0
    return ''.join(sequence_list)


def generate_sequence_3():
    """
    Генерує послідовність із символів прізвища та '0',
    але на відміну від generate_sequence_2(),
    порядок елементів випадково перемішується.
    """
    list1 = list(SURNAME)
    list0 = ['0'] * (N_SEQUENCE - len(SURNAME))
    sequence_list = list1 + list0
    random.shuffle(sequence_list)
    return ''.join(sequence_list)


def generate_sequence_4():
    """
    Генерує послідовність шляхом циклічного повторення:
    символи прізвища + цифри групи,
    поки не буде досягнута довжина 100 символів.
    """
    # Наприклад: ['Z', 'E', 'I', 'B', 'E', 'L', '5', '2', '9']
    letters = list(SURNAME) + list(GROUP)

    # Розмір базового набору символів
    n_letters = len(letters)

    # Скільки повних повторів цього набору поміститься у 100 символів
    n_repeats = N_SEQUENCE // n_letters

    # Скільки символів ще залишиться добрати
    remainder = N_SEQUENCE % n_letters

    # Формуємо послідовність із повних повторів
    sequence_list = letters * n_repeats

    # Додаємо ще кілька перших символів, якщо є залишок
    sequence_list += letters[:remainder]

    return ''.join(map(str, sequence_list))


def generate_sequence_5():
    """
    Генерує послідовність із елементів:
    - перші дві букви прізвища
    - усі цифри групи

    Усього 5 різних елементів.
    Оскільки 100 / 5 = 20, кожен елемент зустрічається 20 разів,
    тобто всі мають однакову ймовірність 0.2.
    """
    elements = list(SURNAME[:2]) + list(GROUP)   # ['Z', 'E', '5', '2', '9']
    count_each = N_SEQUENCE // len(elements)     # 100 // 5 = 20
    sequence_list = []

    # Додаємо кожен символ по 20 разів
    for el in elements:
        sequence_list.extend([el] * count_each)

    # Перемішуємо, щоб символи не йшли блоками
    random.shuffle(sequence_list)
    return ''.join(sequence_list)


def generate_sequence_6():
    """
    Генерує послідовність із:
    - перших двох букв прізвища
    - цифр групи

    Але тут ймовірності нерівні:
    - букви займають 70% усієї послідовності
    - цифри займають 30%
    """
    letters = list(SURNAME[:2])   # ['Z', 'E']
    digits = list(GROUP)          # ['5', '2', '9']

    # Кількість букв і цифр у послідовності
    n_letters = int(0.7 * N_SEQUENCE)  # 70
    n_digits = int(0.3 * N_SEQUENCE)   # 30

    sequence_list = []

    # Випадково додаємо 70 букв
    for _ in range(n_letters):
        sequence_list.append(random.choice(letters))

    # Випадково додаємо 30 цифр
    for _ in range(n_digits):
        sequence_list.append(random.choice(digits))

    # Перемішуємо всі символи
    random.shuffle(sequence_list)
    return ''.join(sequence_list)


def generate_sequence_7():
    """
    Генерує повністю випадкову послідовність довжиною 100 символів
    із англійських малих букв і цифр 0-9.
    """
    elements = string.ascii_lowercase + string.digits
    sequence_list = [random.choice(elements) for _ in range(N_SEQUENCE)]
    return ''.join(sequence_list)


def generate_sequence_8():
    """
    Генерує найпростішу послідовність:
    100 символів '1'.
    """
    return '1' * N_SEQUENCE



# Аналіз послідовності
# ///////////////////////////////////////////////////////

def analyze_sequence(sequence):
    """
    Обчислює основні характеристики послідовності:
    - розмір алфавіту
    - розмір у байтах і бітах
    - частоти та ймовірності символів
    - середню ймовірність
    - рівномірність розподілу
    - ентропію
    - надмірність джерела
    """

    # Кількість унікальних символів у послідовності
    sequence_alphabet_size = len(set(sequence))

    # Кількість символів у послідовності
    original_sequence_size_bytes = len(sequence)

    # Якщо вважати, що 1 символ = 1 байт = 8 біт
    original_sequence_size_bits = len(sequence) * 8

    # Підрахунок, скільки разів зустрічається кожен символ
    counts = collections.Counter(sequence)

    # Обчислення ймовірностей кожного символу
    probability = {symbol: count / len(sequence) for symbol, count in counts.items()}

    # Середнє значення ймовірностей
    mean_probability = sum(probability.values()) / len(probability)

    # Перевіряємо, чи всі ймовірності приблизно однакові
    # Допускаємо відхилення до 5% від середнього значення
    equal = all(
        abs(prob - mean_probability) < 0.05 * mean_probability
        for prob in probability.values()
    )

    # Визначаємо тип розподілу
    if equal:
        uniformity = "рівна"
    else:
        uniformity = "нерівна"

    # Формула ентропії Шеннона:
    # H = -sum(p * log2(p))
    entropy = -sum(p * math.log2(p) for p in probability.values())

    # Якщо через похибку обчислень отримали дуже мале число біля нуля,
    # замінюємо його на 0.0
    if abs(entropy) < 1e-12:
        entropy = 0.0

    # Надмірність джерела:
    # R = 1 - H / Hmax, де Hmax = log2(|A|)
    # Якщо алфавіт має лише 1 символ, то надмірність дорівнює 1
    if sequence_alphabet_size > 1:
        source_excess = 1 - entropy / math.log2(sequence_alphabet_size)
    else:
        source_excess = 1

    # Формуємо зручний рядок з імовірностями для виводу у файл
    probability_str = ', '.join(
        [f"{symbol}={prob:.4f}" for symbol, prob in sorted(probability.items())]
    )

    # Повертаємо всі характеристики у вигляді словника
    return {
        "alphabet_size": sequence_alphabet_size,
        "size_bytes": original_sequence_size_bytes,
        "size_bits": original_sequence_size_bits,
        "counts": counts,
        "probability": probability,
        "mean_probability": mean_probability,
        "uniformity": uniformity,
        "entropy": entropy,
        "source_excess": source_excess,
        "probability_str": probability_str,
    }


# Основна функція програми
# ///////////////////////////////////////////////////////////////

def main():
    """
    Основний сценарій роботи програми:
    1. Генерує 8 різних послідовностей
    2. Записує їх у sequence.txt
    3. Аналізує кожну
    4. Записує характеристики у results_sequence.txt
    5. Будує таблицю та зберігає її як зображення
    """

    # Генерація всіх 8 послідовностей
    original_sequence_1 = generate_sequence_1()
    original_sequence_2 = generate_sequence_2()
    original_sequence_3 = generate_sequence_3()
    original_sequence_4 = generate_sequence_4()
    original_sequence_5 = generate_sequence_5()
    original_sequence_6 = generate_sequence_6()
    original_sequence_7 = generate_sequence_7()
    original_sequence_8 = generate_sequence_8()

    # Збираємо всі послідовності в один список для подальшої обробки
    original_sequences = [
        original_sequence_1,
        original_sequence_2,
        original_sequence_3,
        original_sequence_4,
        original_sequence_5,
        original_sequence_6,
        original_sequence_7,
        original_sequence_8,
    ]

    # Запис усіх послідовностей у файл sequence.txt
    with open(SEQUENCES_FILE, "w", encoding="utf-8") as seq_file:
        for i, sequence in enumerate(original_sequences, start=1):
            seq_file.write(f"Послідовність {i}:\n{sequence}\n\n")

    # Сюди будемо складати короткі результати для таблиці
    results = []

    # Аналіз і запис результатів у results_sequence.txt
    with open(RESULTS_FILE, "w", encoding="utf-8") as result_file:
        for i, sequence in enumerate(original_sequences, start=1):
            # Аналіз поточної послідовності
            analysis = analyze_sequence(sequence)

            # Детальний запис результатів у файл
            result_file.write(f"Послідовність {i}:\n")
            result_file.write(f"Згенерована послідовність: {sequence}\n")
            result_file.write(f"Розмір алфавіту: {analysis['alphabet_size']}\n")
            result_file.write(f"Розмір послідовності: {analysis['size_bytes']} байт ({analysis['size_bits']} біт)\n")
            result_file.write(f"Ймовірності: {analysis['probability_str']}\n")
            result_file.write(f"Середня ймовірність: {analysis['mean_probability']:.4f}\n")
            result_file.write(f"Тип ймовірності: {analysis['uniformity']}\n")
            result_file.write(f"Ентропія: {analysis['entropy']:.4f}\n")
            result_file.write(f"Надмірність джерела: {analysis['source_excess']:.4f}\n")
            result_file.write("-" * 60 + "\n")

            # Скорочена інформація для таблиці/рисунка
            results.append([
                analysis['alphabet_size'],
                round(analysis['entropy'], 2),
                round(analysis['source_excess'], 2),
                analysis['uniformity']
            ])

    # Побудова таблиці у вигляді рисунка
    #////////////////////////////////////////////////////////////////

    # Кількість послідовностей
    n = len(original_sequences)

    # Створюємо полотно для таблиці
    fig, ax = plt.subplots(figsize=(14 / 1.54, n / 1.54))

    # Ховаємо осі, бо потрібна тільки таблиця
    ax.axis('off')

    # Назви стовпців таблиці
    headers = ['Розмір алфавіту', 'Ентропія', 'Надмірність', 'Ймовірність']

    # Назви рядків таблиці
    rows = [f'Послідовність {i}' for i in range(1, n + 1)]

    # Створюємо таблицю
    table = ax.table(
        cellText=results,
        colLabels=headers,
        rowLabels=rows,
        loc='center',
        cellLoc='center'
    )

    # Налаштування розміру шрифту та масштабу таблиці
    table.set_fontsize(14)
    table.scale(0.8, 2)

    # Автоматично підганяє відступи
    plt.tight_layout()

    # Зберігаємо таблицю як зображення
    fig.savefig(FIGURE_FILE, dpi=300, bbox_inches='tight')

    # Закриваємо фігуру, щоб звільнити пам'ять
    plt.close(fig)

    # Повідомлення в консоль про успішне створення файлів
    print("Усі файли успішно створено:")
    print(SEQUENCES_FILE)
    print(RESULTS_FILE)
    print(FIGURE_FILE)


# Точка входу в програму
# ////////////////////////////////////////////////////////////

# Цей блок гарантує, що main() виконається лише тоді,
# коли файл запускають напряму, а не імпортують як модуль
if __name__ == "__main__":
    main()