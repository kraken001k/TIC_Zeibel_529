import random

# Практична робота №10
# Кодування Геммінґа (12, 8)

CHUNK_LENGTH = 8
assert CHUNK_LENGTH % 8 == 0, "Довжина блоку має бути кратна 8"

# Для (12, 8): контрольні біти стоять на позиціях 1, 2, 4, 8
CHECK_BITS = [i for i in range(1, CHUNK_LENGTH + 1) if not i & (i - 1)]


def getCharsToBin(chars):
    """
    Перетворення символів у бінарний формат.
    Кожен символ кодується 8 бітами.
    """
    assert not len(chars) * 8 % CHUNK_LENGTH, (
        "Довжина кодових даних повинна бути кратною довжині блоку кодування"
    )
    return "".join([bin(ord(c))[2:].zfill(8) for c in chars])


def getChunkIterator(text_bin, chunk_size=CHUNK_LENGTH):
    """
    Поблоковий вивід бінарних даних.
    """
    for i in range(0, len(text_bin), chunk_size):
        yield text_bin[i:i + chunk_size]


def getCheckBitsData(value_bin):
    """
    Отримання інформації про контрольні біти з бінарного блоку даних
    при кодуванні.
    """
    check_bits_count_map = {k: 0 for k in CHECK_BITS}

    for index, value in enumerate(value_bin, 1):
        if int(value):
            bin_char_list = list(bin(index)[2:].zfill(8))
            bin_char_list.reverse()

            for degree in [2 ** int(i) for i, bit in enumerate(bin_char_list) if int(bit)]:
                if degree in check_bits_count_map:
                    check_bits_count_map[degree] += 1

    check_bits_value_map = {}
    for check_bit, count in check_bits_count_map.items():
        check_bits_value_map[check_bit] = 0 if not count % 2 else 1

    return check_bits_value_map


def getSetEmptyCheckBits(value_bin):
    """
    Додавання порожніх контрольних бітів у бінарні дані.
    """
    for bit in CHECK_BITS:
        value_bin = value_bin[:bit - 1] + "0" + value_bin[bit - 1:]
    return value_bin


def getSetCheckBits(value_bin):
    """
    Встановлення значень контрольних бітів.
    """
    value_bin = getSetEmptyCheckBits(value_bin)
    check_bits_data = getCheckBitsData(value_bin)

    for check_bit, bit_value in check_bits_data.items():
        value_bin = (
            value_bin[:check_bit - 1]
            + str(bit_value)
            + value_bin[check_bit:]
        )

    return value_bin


def getCheckBits(value_bin):
    """
    Отримання інформації про контрольні біти з бінарного блоку даних
    при декодуванні.
    """
    check_bits = {}

    for index, value in enumerate(value_bin, 1):
        if index in CHECK_BITS:
            check_bits[index] = int(value)

    return check_bits


def getExcludeCheckBits(value_bin):
    """
    Видалення контрольних бітів.
    """
    clean_value_bin = ""

    for index, char_bin in enumerate(list(value_bin), 1):
        if index not in CHECK_BITS:
            clean_value_bin += char_bin

    return clean_value_bin


def getSetErrors(encoded):
    """
    Додавання однієї випадкової помилки в кожен закодований блок.
    """
    result = ""
    encoded_chunk_length = CHUNK_LENGTH + len(CHECK_BITS)

    for chunk in getChunkIterator(encoded, encoded_chunk_length):
        if not chunk:
            continue

        num_bit = random.randint(1, len(chunk))
        chunk = (
            chunk[:num_bit - 1]
            + str(int(chunk[num_bit - 1]) ^ 1)
            + chunk[num_bit:]
        )
        result += chunk

    return result


def getCheckAndFixError(encoded_chunk):
    """
    Пошук та виправлення помилки при передачі.
    """
    check_bits_encoded = getCheckBits(encoded_chunk)

    check_item = getExcludeCheckBits(encoded_chunk)
    check_item = getSetCheckBits(check_item)
    check_bits = getCheckBits(check_item)

    if check_bits_encoded != check_bits:
        invalid_bits = []

        for check_bit_encoded, value in check_bits_encoded.items():
            if check_bits[check_bit_encoded] != value:
                invalid_bits.append(check_bit_encoded)

        num_bit = sum(invalid_bits)

        if 1 <= num_bit <= len(encoded_chunk):
            encoded_chunk = (
                encoded_chunk[:num_bit - 1]
                + str(int(encoded_chunk[num_bit - 1]) ^ 1)
                + encoded_chunk[num_bit:]
            )

    return encoded_chunk


def getDiffIndexList(value_bin1, value_bin2):
    """
    Список індексів позицій, в яких було допущено помилки.
    """
    diff_index_list = []

    for index, char_bin_items in enumerate(zip(list(value_bin1), list(value_bin2)), 1):
        if char_bin_items[0] != char_bin_items[1]:
            diff_index_list.append(index)

    return diff_index_list


def encode(source):
    """
    Кодування даних.
    Повертає оригінальну послідовність у бітах та закодовану послідовність.
    """
    text_bin = getCharsToBin(source)
    result = ""

    for chunk_bin in getChunkIterator(text_bin):
        chunk_bin = getSetCheckBits(chunk_bin)
        result += chunk_bin

    return text_bin, result


def decode(encoded, fix_errors=True):
    """
    Декодування даних.
    fix_errors=True — з виправленням помилок.
    fix_errors=False — без виправлення помилок.
    """
    decoded_value = ""
    fixed_encoded_list = []
    encoded_chunk_length = CHUNK_LENGTH + len(CHECK_BITS)

    for encoded_chunk in getChunkIterator(encoded, encoded_chunk_length):
        if fix_errors:
            encoded_chunk = getCheckAndFixError(encoded_chunk)

        fixed_encoded_list.append(encoded_chunk)

    clean_chunk_list = []

    for encoded_chunk in fixed_encoded_list:
        encoded_chunk = getExcludeCheckBits(encoded_chunk)
        clean_chunk_list.append(encoded_chunk)

    for clean_chunk in clean_chunk_list:
        for i in range(0, len(clean_chunk), 8):
            clean_char = clean_chunk[i:i + 8]
            if len(clean_char) == 8:
                decoded_value += chr(int(clean_char, 2))

    return decoded_value


def read_sequences(filename="sequence.txt"):
    """
    Зчитування послідовностей з файлу sequence.txt.
    """
    sequences = []
    current_sequence = ""

    with open(filename, "r", encoding="utf-8") as file:
        for line in file:
            line = line.strip()

            if not line:
                continue

            if line.startswith("Послідовність"):
                if current_sequence:
                    sequences.append(current_sequence)
                    current_sequence = ""
            else:
                current_sequence += line

    if current_sequence:
        sequences.append(current_sequence)

    return sequences


def write_result_block(file, source, source_bin, encoded, decoded,
                       encoded_with_error, diff_index_list,
                       decoded_with_error, decoded_without_error):
    """
    Запис результатів.
    """
    file.write("//////////////////////////////////////////////////////////////////////\n")
    file.write(f"Оригінальна послідовність: {source}\n")
    file.write(f"Оригінальна послідовність в бітах: {source_bin}\n")
    file.write(f"Розмір оригінальної послідовності: {len(source_bin)} bits\n")
    file.write(f"Довжина блоку кодування: {CHUNK_LENGTH}\n")
    file.write(f"Позиції контрольних біт: {CHECK_BITS}\n")
    file.write(f"Відносна надмірність коду: {len(CHECK_BITS) / CHUNK_LENGTH}\n")
    file.write("--------------------Кодування--------------------\n")
    file.write(f"Закодовані дані: {encoded}\n")
    file.write(f"Розмір закодованих даних: {len(encoded)} bits\n")
    file.write("--------------------Декодування--------------------\n")
    file.write(f"Декодовані дані: {decoded}\n")
    file.write(f"Розмір декодованих даних: {len(decoded) * 8} bits\n")
    file.write("--------------------Внесення помилки--------------------\n")
    file.write(f"Закодовані дані з помилками: {encoded_with_error}\n")
    file.write(f"Кількість помилок: {len(diff_index_list)}\n")
    file.write(f"Індекси помилок: {diff_index_list}\n")
    file.write("--------------------Декодування даних без виправлення помилки--------------------\n")
    file.write(f"Декодовані дані без виправлення помилки: {decoded_with_error}\n")
    file.write("--------------------Декодування даних з виправленням помилки--------------------\n")
    file.write(f"Декодовані дані з виправленням помилки: {decoded_without_error}\n")
    file.write("//////////////////////////////////////////////////////////////////////\n\n")


if __name__ == "__main__":
    # random.seed(10)

    original_sequences = read_sequences("sequence.txt")

    with open("result_hamming.txt", "w", encoding="utf-8") as result_file:
        for sequence in original_sequences:
            # За завданням обмежуємо послідовність першими 10 символами
            source = sequence[:10]

            source_bin, encoded = encode(source)

            decoded = decode(encoded)

            encoded_with_error = getSetErrors(encoded)

            diff_index_list = getDiffIndexList(encoded, encoded_with_error)

            decoded_with_error = decode(encoded_with_error, fix_errors=False)

            decoded_without_error = decode(encoded_with_error)

            write_result_block(
                result_file,
                source,
                source_bin,
                encoded,
                decoded,
                encoded_with_error,
                diff_index_list,
                decoded_with_error,
                decoded_without_error,
            )

    print("Результати збережено у файл result_hamming.txt")
