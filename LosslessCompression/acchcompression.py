import math
import collections
import matplotlib.pyplot as plt


# Налаштування файлів
# ---------------------------------------------------
# Файл із 8 послідовностями, які були створені в ПЗ-5
SEQUENCES_FILE = "sequence.txt"

# Файл, у який будемо записувати результати ПЗ-7
RESULTS_FILE = "results_AC_CH.txt"

# Назва рисунка з підсумковою таблицею
FIGURE_FILE = "Результати стиснення методами AC та CH.png"


# Зчитування послідовностей із sequence.txt
def read_sequences(filename):
    """
    Зчитує послідовності з файлу sequence.txt.

    У файлі дані мають формат:
    Послідовність 1:
    010101...

    Послідовність 2:
    ABCDEF...

    Тому:
    - порожні рядки пропускаємо,
    - рядки типу "Послідовність N:" пропускаємо,
    - залишаємо лише самі рядки-послідовності.
    """
    sequences = []

    with open(filename, "r", encoding="utf-8") as file:
        lines = [line.strip() for line in file.readlines()]

    for line in lines:
        if not line:
            continue
        if line.startswith("Послідовність"):
            continue
        sequences.append(line)

    return sequences


# Аналіз послідовності
def analyze_sequence(sequence):
    """
    Для заданої послідовності обчислює:
    - довжину,
    - множину унікальних символів,
    - розмір алфавіту,
    - кількість входжень кожного символу,
    - імовірності символів,
    - ентропію.
    """
    sequence_length = len(sequence)
    unique_chars = set(sequence)
    alphabet_size = len(unique_chars)

    # Підрахунок входжень кожного символу
    counts = collections.Counter(sequence)

    # Імовірність кожного символу
    probability = {symbol: count / sequence_length for symbol, count in counts.items()}

    # Ентропія за формулою Шеннона
    entropy = -sum(p * math.log2(p) for p in probability.values())

    # Прибираємо можливий -0.0 через похибку обчислень
    if abs(entropy) < 1e-12:
        entropy = 0.0

    return sequence_length, unique_chars, alphabet_size, counts, probability, entropy


# Перетворення дробового числа в двійковий код
def float_bin(point, size_cod):
    """
    Перетворює число point з діапазону [0, 1)
    у двійковий рядок довжиною size_cod.

    Використовується в арифметичному кодуванні.
    """
    binary_code = ""

    for _ in range(size_cod):
        point = point * 2

        if point > 1:
            binary_code += "1"
            integer_part = int(point)
            point = point - integer_part
        elif point < 1:
            binary_code += "0"
        else:
            binary_code += "1"
            break

    return binary_code


# Арифметичне кодування (AC)
def encode_ac(uniq_chars, probabilitys, alphabet_size, sequence):
    """
    Виконує арифметичне кодування послідовності.

    Повертає:
    1) encoded_data_ac - службові дані, необхідні для декодування:
       [point, alphabet_size, alphabet, probability]
    2) bin_code - двійкове представлення закодованої послідовності
    """
    # Перетворюємо множину символів у список
    # Сортуємо, щоб порядок був стабільним під час кодування і декодування
    alphabet = sorted(list(uniq_chars))

    # Список імовірностей у тому ж порядку, що і список alphabet
    probability = [probabilitys[symbol] for symbol in alphabet]

    # unity зберігає:
    # [символ, нижня межа інтервалу, верхня межа інтервалу]
    unity = []
    probability_range = 0.0

    for i in range(alphabet_size):
        low = probability_range
        probability_range = probability_range + probability[i]
        high = probability_range
        unity.append([alphabet[i], low, high])

    # Послідовно звужуємо інтервал для всіх символів,
    # крім останнього
    for i in range(len(sequence) - 1):
        for j in range(len(unity)):
            if sequence[i] == unity[j][0]:
                probability_low = unity[j][1]
                probability_high = unity[j][2]
                diff = probability_high - probability_low

                for k in range(len(unity)):
                    unity[k][1] = probability_low
                    unity[k][2] = probability[k] * diff + probability_low
                    probability_low = unity[k][2]
                break

    # Для останнього символу знаходимо фінальний інтервал
    low = 0
    high = 0

    for i in range(len(unity)):
        if unity[i][0] == sequence[-1]:
            low = unity[i][1]
            high = unity[i][2]
            break

    # Беремо середню точку кінцевого інтервалу
    point = (low + high) / 2

    # Кількість біт для представлення point
    size_cod = math.ceil(math.log((1 / (high - low)), 2) + 1)

    # Перетворення точки у двійковий код
    bin_code = float_bin(point, size_cod)

    return [point, alphabet_size, alphabet, probability], bin_code


# Арифметичне декодування (AC)
def decode_ac(encoded_data_ac, length_seq):
    """
    Виконує декодування арифметичного кодування.

    encoded_data_ac містить:
    [point, alphabet_size, alphabet, probability]

    length_seq - довжина вихідної послідовності.
    """
    point = encoded_data_ac[0]
    alphabet_size = encoded_data_ac[1]
    alphabet = encoded_data_ac[2]
    probability = encoded_data_ac[3]

    # Формуємо початкові інтервали символів
    unity = []
    probability_range = 0.0

    for i in range(alphabet_size):
        low = probability_range
        probability_range = probability_range + probability[i]
        high = probability_range
        unity.append([alphabet[i], low, high])

    decoded_sequence = ""

    # Відновлюємо символи послідовно
    for _ in range(length_seq):
        for j in range(len(unity)):
            if point > unity[j][1] and point < unity[j][2]:
                prob_low = unity[j][1]
                prob_high = unity[j][2]
                diff = prob_high - prob_low

                decoded_sequence += unity[j][0]

                for k in range(len(unity)):
                    unity[k][1] = prob_low
                    unity[k][2] = probability[k] * diff + prob_low
                    prob_low = unity[k][2]
                break

    return decoded_sequence


# Кодування Хаффмана (CH)
def encode_ch(uniq_chars, probabilitys, sequence):
    """
    Виконує кодування Хаффмана.

    Повертає:
    1) [encode, symbol_code] - службові дані для декодування
    2) encode - закодована бітова послідовність
    """
    # Алфавіт сортуємо для стабільного порядку
    alphabet = sorted(list(uniq_chars))
    probability = [probabilitys[symbol] for symbol in alphabet]

    # final містить пари [символ, імовірність]
    final = []
    for i in range(len(alphabet)):
        final.append([alphabet[i], probability[i]])

    # Сортуємо за зростанням імовірності
    final.sort(key=lambda x: x[1])

    tree = []

    # Спеціальний випадок: алфавіт із одного символу
    if len(alphabet) == 1:
        symbol_code = [[alphabet[0], "0"]]
        encode = "".join([symbol_code[0][1] for _ in sequence])
        return [encode, symbol_code], encode

    # Побудова дерева Хаффмана
    while len(final) > 1:
        left = final[0]
        final.pop(0)

        right = final[0]
        final.pop(0)

        total = left[1] + right[1]

        # Зберігаємо зв’язки вузлів дерева
        tree.append([left[0], right[0]])

        # Додаємо новий "об’єднаний" вузол назад
        final.append([left[0] + right[0], total])
        final.sort(key=lambda x: x[1])

    # Розвертаємо дерево, щоб правильно будувати коди
    tree.reverse()

    # Тут зберігатимуться коди символів
    symbol_code = []

    # Для кожного символу формуємо його код
    for i in range(len(alphabet)):
        code = ""

        for j in range(len(tree)):
            if alphabet[i] in tree[j][0]:
                code += "0"
                if alphabet[i] == tree[j][0]:
                    break
            else:
                code += "1"
                if alphabet[i] == tree[j][1]:
                    break

        symbol_code.append([alphabet[i], code])

    # Формуємо закодовану послідовність
    encode = ""
    for c in sequence:
        encode += [symbol_code[i][1] for i in range(len(alphabet)) if symbol_code[i][0] == c][0]

    return [encode, symbol_code], encode


# Декодування Хаффмана (CH)
def decode_ch(encoded_sequence):
    """
    Декодує послідовність, закодовану методом Хаффмана.

    encoded_sequence містить:
    [encode, symbol_code]
    """
    encode = list(encoded_sequence[0])
    symbol_code = encoded_sequence[1]

    sequence = ""
    count = 0
    flag = 0

    for i in range(len(encode)):
        for j in range(len(symbol_code)):
            if encode[i] == symbol_code[j][1]:
                sequence += str(symbol_code[j][0])
                flag = 1

        if flag == 1:
            flag = 0
        else:
            count += 1
            if count == len(encode):
                break
            else:
                encode.insert(i + 1, str(encode[i] + encode[i + 1]))
                encode.pop(i + 2)

    return sequence


# Основна функція програми
def main():
    """
    Основна логіка:
    1. Зчитати послідовності з sequence.txt
    2. Для кожної взяти тільки перші 10 символів
    3. Порахувати ентропію
    4. Закодувати і декодувати AC
    5. Закодувати і декодувати CH
    6. Зберегти результати у results_AC_CH.txt
    7. Побудувати підсумкову таблицю
    """
    original_sequences = read_sequences(SEQUENCES_FILE)

    # Сюди будемо збирати значення для підсумкової таблиці
    results = []

    # Очищаємо файл результатів перед новим записом
    with open(RESULTS_FILE, "w", encoding="utf-8") as file:
        file.write("")

    # Обробляємо всі 8 послідовностей
    for index, sequence in enumerate(original_sequences, start=1):
        # беремо лише перші 10 символів
        sequence = sequence[:10]

        # Аналіз послідовності
        sequence_length, unique_chars, alphabet_size, counts, probability, entropy = analyze_sequence(sequence)

        # Арифметичне кодування
        encoded_data_ac, encoded_sequence_ac = encode_ac(unique_chars, probability, alphabet_size, sequence)
        decoded_sequence_ac = decode_ac(encoded_data_ac, sequence_length)

        # bits per symbol для AC
        bps_ac = round(len(encoded_sequence_ac) / sequence_length, 2)

        # Кодування Хаффмана
        encoded_data_ch, encoded_sequence_ch = encode_ch(unique_chars, probability, sequence)
        decoded_sequence_ch = decode_ch(encoded_data_ch)

        # bits per symbol для CH
        bps_ch = round(len(encoded_sequence_ch) / sequence_length, 2)

        # Імовірності в текстовому вигляді
        probability_str = ", ".join(
            [f"{symbol}={prob:.4f}" for symbol, prob in sorted(probability.items())]
        )

        # Запис результатів у файл
        with open(RESULTS_FILE, "a", encoding="utf-8") as file:
            file.write("/" * 70 + "\n")
            file.write(f"Оригінальна послідовність {index}: {sequence}\n")
            file.write(f"Довжина послідовності: {sequence_length}\n")
            file.write(f"Розмір алфавіту: {alphabet_size}\n")
            file.write(f"Ймовірності: {probability_str}\n")
            file.write(f"Ентропія: {entropy:.4f}\n\n")

            file.write("_______________Арифметичне кодування_______________\n")
            file.write(f"Дані для декодування AC: {encoded_data_ac}\n")
            file.write(f"Закодована AC послідовність: {encoded_sequence_ac}\n")
            file.write(f"Значення bps AC: {bps_ac}\n")
            file.write(f"Декодована AC послідовність: {decoded_sequence_ac}\n\n")

            file.write("_______________Кодування Хаффмана_______________\n")
            file.write(f"Дані для декодування CH: {encoded_data_ch}\n")
            file.write(f"Закодована CH послідовність: {encoded_sequence_ch}\n")
            file.write(f"Коди символів CH: {encoded_data_ch[1]}\n")
            file.write(f"Значення bps CH: {bps_ch}\n")
            file.write(f"Декодована CH послідовність: {decoded_sequence_ch}\n\n")

            # Перевірка правильності декодування
            if decoded_sequence_ac != sequence:
                file.write("ПОМИЛКА: AC декодування некоректне\n")
            if decoded_sequence_ch != sequence:
                file.write("ПОМИЛКА: CH декодування некоректне\n")

            file.write("\n")

        # Додаємо дані для підсумкової таблиці
        results.append([round(entropy, 2), bps_ac, bps_ch])

    # Побудова таблиці з результатами
    n = len(original_sequences)
    fig, ax = plt.subplots(figsize=(14 / 1.54, n / 1.54))

    # Вимикаємо осі, бо потрібна тільки таблиця
    ax.axis("off")

    headers = ["Ентропія", "bps AC", "bps CH"]
    rows = [f"Послідовність {i}" for i in range(1, n + 1)]

    table = ax.table(
        cellText=results,
        colLabels=headers,
        rowLabels=rows,
        loc="center",
        cellLoc="center"
    )

    table.set_fontsize(14)
    table.scale(0.8, 2)

    plt.tight_layout()
    fig.savefig(FIGURE_FILE, dpi=300, bbox_inches="tight")
    plt.close(fig)

    print("Готово. Створено файли:")
    print(RESULTS_FILE)
    print(FIGURE_FILE)


# Точка входу
if __name__ == "__main__":
    main()
