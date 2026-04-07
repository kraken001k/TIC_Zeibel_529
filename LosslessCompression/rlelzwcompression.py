import math
import collections
import matplotlib.pyplot as plt


# Налаштування файлів
# ---------------------------------------------------
# Файл із 8 послідовностями, які були створені в ПЗ-5
SEQUENCES_FILE = "sequence.txt"

# Файл, у який будуть записані результати ПЗ-6
RESULTS_FILE = "results_rle_lzw.txt"

# Назва рисунка з підсумковою таблицею
FIGURE_FILE = "Результати стиснення методами RLE та LZW.png"

# У ПЗ-6 за умовою вважаємо, що 1 символ = 16 біт
BITS_PER_SYMBOL = 16


# Зчитування послідовностей із файлу sequence.txt
def read_sequences(filename):
    """
    Зчитує послідовності з файлу sequence.txt.

    У файлі дані збережені у вигляді:
    Послідовність 1:
    010101...

    Послідовність 2:
    ABCDEF...

    Тому функція:
    - пропускає порожні рядки,
    - пропускає службові рядки "Послідовність N:",
    - залишає тільки самі послідовності.
    """
    sequences = []

    with open(filename, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file.readlines()]

    for line in lines:
        # Пропускаємо порожні рядки
        if not line:
            continue

        # Пропускаємо заголовки типу "Послідовність 1:"
        if line.startswith("Послідовність"):
            continue

        # Додаємо тільки саму послідовність
        sequences.append(line)

    return sequences


# Аналіз послідовності
def analyze_sequence(sequence):
    """
    Для однієї послідовності обчислює:
    - кількість входжень кожного символу,
    - ймовірність появи кожного символу,
    - ентропію за формулою Шеннона.
    """
    # Підрахунок, скільки разів зустрічається кожен символ
    counts = collections.Counter(sequence)

    # Ймовірність появи символу = кількість його входжень / довжина послідовності
    probability = {symbol: count / len(sequence) for symbol, count in counts.items()}

    # Формула ентропії Шеннона
    entropy = -sum(p * math.log2(p) for p in probability.values())

    # Якщо через похибку вийшло дуже мале число біля нуля,
    # то замінюємо його на 0.0
    if abs(entropy) < 1e-12:
        entropy = 0.0

    return counts, probability, entropy


# RLE-кодування
def encode_rle(sequence):
    """
    Виконує RLE-кодування послідовності.

    Ідея RLE:
    замість серії однакових символів записується:
    [кількість повторів][символ]

    Наприклад:
    1110110000 -> 31102140

    Функція повертає:
    1) encoded_string - закодований рядок
    2) result - список кортежів вигляду (символ, кількість)
    """
    # Якщо рядок порожній, то нічого кодувати
    if not sequence:
        return "", []

    # count - довжина поточної серії однакових символів
    count = 1

    # Тут будемо зберігати кортежі (символ, кількість повторів)
    result = []

    # Проходимо по всій послідовності
    for i, item in enumerate(sequence):
        # Для першого символу просто пропускаємо перевірку,
        # бо в нього ще немає попереднього елемента
        if i == 0:
            continue

        # Якщо поточний символ такий самий, як попередній,
        # збільшуємо довжину серії
        if item == sequence[i - 1]:
            count += 1
        else:
            # Якщо символ змінився, значить серія завершилась
            # Зберігаємо попередній символ і довжину його серії
            result.append((sequence[i - 1], count))

            # Починаємо рахувати нову серію
            count = 1

    # Після завершення циклу не забуваємо додати останню серію
    result.append((sequence[-1], count))

    # Перетворюємо список кортежів у рядок формату:
    # [('1', 3), ('0', 1)] -> "3110"
    encoded = []
    for symbol, cnt in result:
        encoded.append(f"{cnt}{symbol}")

    return "".join(encoded), result


# RLE-декодування
def decode_rle(sequence):
    """
    Виконує декодування RLE.

    На вхід отримує список кортежів:
    [('1', 3), ('0', 1), ('1', 2), ('0', 4)]

    На виході повертає:
    1110110000
    """
    result = []

    for item in sequence:
        symbol = item[0]
        count = item[1]

        # Відновлюємо серію символів
        result.append(symbol * count)

    # Об'єднуємо всі відновлені частини в один рядок
    return "".join(result)


# LZW-кодування
def encode_lzw(sequence):
    """
    Виконує LZW-кодування.

    Початковий словник містить усі Unicode-символи з кодами 0..65535.
    Далі нові підрядки додаються до словника під час роботи алгоритму.

    Функція повертає:
    1) result - список кодів
    2) size_bits - розмір закодованої послідовності в бітах
    3) log_lines - текстові рядки для запису словника у файл
    """
    # Створюємо початковий словник Unicode
    dictionary = {}
    for i in range(65536):
        dictionary[chr(i)] = i

    # current - поточний рядок, який намагаємось знайти у словнику
    current = ""

    # Сюди записуються коди закодованої послідовності
    result = []

    # Загальний розмір закодованих даних у бітах
    size_bits = 0

    # Рядки для виводу в results_rle_lzw.txt
    log_lines = []

    # Посимвольно читаємо вхідну послідовність
    for c in sequence:
        # Пробуємо розширити поточний рядок новим символом
        new_str = current + c

        # Якщо такий рядок уже є в словнику,
        # просто продовжуємо його накопичувати
        if new_str in dictionary:
            current = new_str
        else:
            # Якщо такого рядка в словнику ще немає,
            # то записуємо код для current
            code = dictionary[current]
            result.append(code)

            # Базові Unicode-символи кодуються 16 бітами,
            # нові словникові елементи - 17 бітами
            element_bits = 16 if code < 65536 else 17
            size_bits += element_bits

            # Зберігаємо інформацію для логування у файл
            log_lines.append(f"Code: {code}, Element: {current}, Bits: {element_bits}")

            # Додаємо новий рядок у словник
            dictionary[new_str] = len(dictionary)

            # Починаємо новий current із поточного символу
            current = c

    # Після завершення циклу треба окремо записати останній current
    if current:
        code = dictionary[current]
        result.append(code)

        last_bits = 16 if code < 65536 else 17
        size_bits += last_bits

        log_lines.append(f"Code: {code}, Element: {current}, Bits: {last_bits}")

    return result, size_bits, log_lines


# LZW-декодування
def decode_lzw(sequence):
    """
    Виконує декодування LZW.

    На вхід отримує список числових кодів.
    На виході повертає відновлений рядок.
    """
    if not sequence:
        return ""

    # Початковий словник: код -> символ
    dictionary = {}
    for i in range(65536):
        dictionary[i] = chr(i)

    # Перший код відразу перетворюємо у символ
    previous = dictionary[sequence[0]]
    result = previous

    # Обробляємо решту кодів
    for code in sequence[1:]:
        if code in dictionary:
            current = dictionary[code]
        else:
            # Спеціальний випадок LZW:
            # коли коду ще немає в словнику
            current = previous + previous[0]

        # Додаємо знайдений фрагмент до результату
        result += current

        # Додаємо новий елемент у словник
        dictionary[len(dictionary)] = previous + current[0]

        # Оновлюємо previous
        previous = current

    return result


# Основна частина програми
def main():
    """
    Основна логіка програми:
    1. Зчитати всі послідовності з sequence.txt
    2. Для кожної послідовності:
       - порахувати ентропію
       - виконати RLE-кодування/декодування
       - виконати LZW-кодування/декодування
       - записати результати у текстовий файл
    3. Побудувати підсумкову таблицю у вигляді рисунка
    """
    original_sequences = read_sequences(SEQUENCES_FILE)

    # Тут збиратимемо короткі результати для підсумкової таблиці
    results = []

    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        for i, sequence in enumerate(original_sequences, start=1):
            # Аналіз оригінальної послідовності
            counts, probability, entropy = analyze_sequence(sequence)

            # За умовою ПЗ-6 1 символ = 16 біт
            original_size_bits = len(sequence) * BITS_PER_SYMBOL

            probability_str = ", ".join(
                [f"{symbol}={prob:.4f}" for symbol, prob in sorted(probability.items())]
            )

            file.write("/" * 70 + "\n")
            file.write(f"Оригінальна послідовність {i}: {sequence}\n")
            file.write(f"Розмір оригінальної послідовності: {original_size_bits} bits\n")
            file.write(f"Ймовірності: {probability_str}\n")
            file.write(f"Ентропія: {entropy:.4f}\n\n")

            # RLE-кодування та декодування
            file.write("_______________Кодування_RLE_______________\n")

            encoded_sequence_rle, encoded_rle = encode_rle(sequence)
            decoded_sequence_rle = decode_rle(encoded_rle)

            # У спрощеному варіанті також вважаємо,
            # що кожен символ закодованого рядка займає 16 біт
            encoded_rle_size_bits = len(encoded_sequence_rle) * BITS_PER_SYMBOL

            compression_ratio_rle_value = round(original_size_bits / encoded_rle_size_bits, 2)

            # Якщо КС < 1, це означає, що стиснення не відбулося
            if compression_ratio_rle_value < 1:
                compression_ratio_rle = "-"
            else:
                compression_ratio_rle = compression_ratio_rle_value

            file.write(f"Закодована RLE послідовність: {encoded_sequence_rle}\n")
            file.write(f"Розмір закодованої RLE послідовності: {encoded_rle_size_bits} bits\n")
            file.write(f"Коефіцієнт стиснення RLE: {compression_ratio_rle}\n")
            file.write(f"Декодована RLE послідовність: {decoded_sequence_rle}\n")
            file.write(f"Розмір декодованої RLE послідовності: {len(decoded_sequence_rle) * BITS_PER_SYMBOL} bits\n\n")

            # LZW-кодування та декодування
            file.write("_______________Кодування_LZW_______________\n")

            encoded_sequence_lzw, encoded_lzw_size_bits, lzw_log = encode_lzw(sequence)

            file.write("_______________Словник_______________\n")
            for line in lzw_log:
                file.write(line + "\n")

            decoded_sequence_lzw = decode_lzw(encoded_sequence_lzw)

            compression_ratio_lzw = round(original_size_bits / encoded_lzw_size_bits, 2)

            file.write(f"Закодована LZW послідовність: {''.join(map(str, encoded_sequence_lzw))}\n")
            file.write(f"Розмір закодованої LZW послідовності: {encoded_lzw_size_bits} bits\n")
            file.write(f"Коефіцієнт стиснення LZW: {compression_ratio_lzw}\n")
            file.write(f"Декодована LZW послідовність: {decoded_sequence_lzw}\n")
            file.write(f"Розмір декодованої LZW послідовності: {len(decoded_sequence_lzw) * BITS_PER_SYMBOL} bits\n\n")

            # Перевірка правильності декодування
            if decoded_sequence_rle != sequence:
                file.write("ПОМИЛКА: RLE декодування некоректне\n\n")

            if decoded_sequence_lzw != sequence:
                file.write("ПОМИЛКА: LZW декодування некоректне\n\n")

            # Додаємо дані для підсумкової таблиці
            results.append([
                round(entropy, 2),
                compression_ratio_rle,
                compression_ratio_lzw
            ])

    # Побудова таблиці з результатами
    n = len(original_sequences)

    # Створюємо фігуру
    fig, ax = plt.subplots(figsize=(14 / 1.54, n / 1.54))

    # Вимикаємо осі, бо потрібна тільки таблиця
    ax.axis("off")

    # Заголовки стовпців
    headers = ["Ентропія", "КС RLE", "КС LZW"]

    # Підписи рядків
    rows = [f"Послідовність {i}" for i in range(1, n + 1)]

    # Створюємо таблицю
    table = ax.table(
        cellText=results,
        colLabels=headers,
        rowLabels=rows,
        loc="center",
        cellLoc="center"
    )

    # Налаштовуємо вигляд таблиці
    table.set_fontsize(14)
    table.scale(0.8, 2)

    plt.tight_layout()

    # Зберігаємо рисунок
    fig.savefig(FIGURE_FILE, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print("Готово. Створено файли:")
    print(RESULTS_FILE)
    print(FIGURE_FILE)


# Точка входу в програму
if __name__ == "__main__":
    main()
