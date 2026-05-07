import os
import io
from PIL import Image


# Вхідні зображення для обробки.
# Файли повинні знаходитись в одній папці зі скриптом.
IMAGES = [
    "3_1.bmp",
    "3_2.bmp",
    "3_3.bmp"
]


# Папка для збереження результатів роботи програми.
RESULTS_DIR = "Results"


# Перша таблиця квантування.
# Використовується для більшого стиснення зображення.
QUANTIZATION_TABLE_50 = [
    16, 11, 10, 16, 24, 40, 51, 61,
    12, 12, 14, 19, 26, 58, 60, 55,
    14, 13, 16, 24, 40, 57, 69, 56,
    14, 17, 22, 29, 51, 87, 80, 62,
    18, 22, 37, 56, 68, 109, 103, 77,
    24, 35, 55, 64, 81, 104, 113, 92,
    49, 64, 78, 87, 103, 121, 120, 101,
    72, 92, 95, 98, 112, 100, 103, 99
]


# Друга таблиця квантування.
# Має менші значення, тому зберігає більше деталей зображення.
QUANTIZATION_TABLE_90 = [
    3, 2, 2, 3, 5, 8, 10, 12,
    2, 2, 3, 4, 5, 12, 12, 11,
    3, 3, 3, 5, 8, 11, 14, 11,
    3, 3, 4, 6, 10, 17, 16, 12,
    4, 4, 7, 11, 14, 22, 21, 15,
    5, 7, 11, 13, 16, 21, 23, 18,
    10, 13, 16, 17, 21, 24, 24, 20,
    14, 18, 19, 20, 22, 20, 21, 20
]


# Набір таблиць квантування, які застосовуються до кожного зображення.
QUANTIZATION_TABLES = {
    "q50": QUANTIZATION_TABLE_50,
    "q90": QUANTIZATION_TABLE_90
}


def prepare_image(image_path):
    """
    Відкриває зображення, переводить його у формат RGB
    та обрізає до квадратної форми.
    """

    img = Image.open(image_path).convert("RGB")

    width, height = img.size

    # Обираємо меншу сторону зображення, але не більше 1024 пікселів.
    size = min(width, height, 1024)

    # Обрізаємо зображення до квадрата.
    img = img.crop((0, 0, size, size))

    return img


def encode_to_asf(img, image_name, table_name, qtable):
    """
    Кодує зображення з використанням заданої таблиці квантування
    та зберігає результат у файл ASF.
    """

    asf_path = os.path.join(
        RESULTS_DIR,
        f"{image_name}_encoded_{table_name}.asf"
    )

    # Байтовий потік використовується для тимчасового збереження
    # закодованих даних перед записом у файл.
    buffer = io.BytesIO()

    # Збереження зображення з явно заданою таблицею квантування.
    img.save(
        buffer,
        format="JPEG",
        qtables=[qtable, qtable],
        subsampling=0,
        optimize=True
    )

    # Запис результату кодування у файл ASF.
    with open(asf_path, "wb") as file:
        file.write(buffer.getvalue())

    return asf_path


def decode_from_asf(asf_path, image_name, table_name, qtable):
    """
    Декодує зображення з ASF-файлу
    та зберігає декодований результат у форматі JPEG.
    """

    decoded_path = os.path.join(
        RESULTS_DIR,
        f"{image_name}_decoded_{table_name}.jpg"
    )

    # Відкриття закодованого зображення.
    decoded_img = Image.open(asf_path).convert("RGB")

    # Збереження декодованого зображення.
    decoded_img.save(
        decoded_path,
        "JPEG",
        qtables=[qtable, qtable],
        subsampling=0,
        optimize=True
    )

    return decoded_path


def write_result(report, image_path, original_size, table_name,
                 asf_path, decoded_path):
    """
    Записує інформацію про розміри файлів
    та коефіцієнт стиснення у results_jpeg.txt.
    """

    asf_size = os.path.getsize(asf_path)
    decoded_size = os.path.getsize(decoded_path)

    compression_ratio = original_size / asf_size if asf_size != 0 else 0

    report.write(f"Таблиця квантування: {table_name}\n")
    report.write(f"Вхідне зображення: {image_path}\n")
    report.write(f"Початковий розмір: {original_size} байт\n")
    report.write(f"Файл результату стиснення: {asf_path}\n")
    report.write(f"Розмір ASF-файлу: {asf_size} байт\n")
    report.write(f"Декодоване JPEG-зображення: {decoded_path}\n")
    report.write(f"Розмір декодованого файлу: {decoded_size} байт\n")
    report.write(f"Коефіцієнт стиснення: {compression_ratio:.2f}\n\n")


def main():
    """
    Основна функція програми.
    Обробляє вхідні зображення, створює файли результатів
    та формує текстовий звіт.
    """

    os.makedirs(RESULTS_DIR, exist_ok=True)

    created_asf = 0
    created_decoded = 0

    with open("results_jpeg.txt", "w", encoding="utf-8") as report:
        report.write("Практична робота №8\n")
        report.write("Стиснення з втратами. JPEG\n")
        report.write("Використано 2 різні таблиці квантування\n")
        report.write("Створено ASF-файли як результат кодування\n\n")

        for image_path in IMAGES:
            if not os.path.exists(image_path):
                print(f"Файл не знайдено: {image_path}")
                continue

            original_size = os.path.getsize(image_path)
            img = prepare_image(image_path)

            image_name = os.path.splitext(os.path.basename(image_path))[0]

            report.write(f"Файл: {image_path}\n")
            report.write(f"Початковий розмір: {original_size} байт\n\n")

            for table_name, qtable in QUANTIZATION_TABLES.items():
                asf_path = encode_to_asf(
                    img,
                    image_name,
                    table_name,
                    qtable
                )
                created_asf += 1

                decoded_path = decode_from_asf(
                    asf_path,
                    image_name,
                    table_name,
                    qtable
                )
                created_decoded += 1

                write_result(
                    report,
                    image_path,
                    original_size,
                    table_name,
                    asf_path,
                    decoded_path
                )

            report.write("-" * 50 + "\n\n")

    print("Готово!")
    print("Створено файл results_jpeg.txt")
    print("Створено папку Results з результатами")
    print(f"Створено ASF-файлів: {created_asf}")
    print(f"Створено декодованих JPEG: {created_decoded}")
    print("Використано 2 різні таблиці квантування")


if __name__ == "__main__":
    main()
