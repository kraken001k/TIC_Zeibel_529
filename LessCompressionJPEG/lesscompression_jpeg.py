import os
from PIL import Image


# Список вхідних зображень.
IMAGES = [
    "3_1.bmp",
    "3_2.bmp",
    "3_3.bmp"
]


# Рівні якості JPEG для стиснення.
# За методичкою використовуємо 50% та 90%.
QUALITIES = [50, 90]


# Папка, куди будуть збережені результати.
# У ній має з’явитися 12 файлів:
# 6 стиснених JPEG + 6 декодованих JPEG.
RESULTS_DIR = "Results"


def prepare_image(image_path):
    """
    Відкриває зображення, переводить його в RGB
    та обрізає до квадратної форми.
    """

    img = Image.open(image_path).convert("RGB")

    width, height = img.size

    # Беремо меншу сторону, але не більше 1024 пікселів
    size = min(width, height, 1024)

    # Обрізаємо зображення до квадрата від лівого верхнього кута
    img = img.crop((0, 0, size, size))

    return img


def save_compressed_and_decoded(img, image_name, quality):
    """
    Створює два JPEG-файли для одного зображення:
    1. Стиснене JPEG-зображення
    2. Декодоване JPEG-зображення

    Повертає шляхи до створених файлів.
    """

    compressed_path = os.path.join(
        RESULTS_DIR,
        f"{image_name}_compressed_q{quality}.jpg"
    )

    decoded_path = os.path.join(
        RESULTS_DIR,
        f"{image_name}_decoded_q{quality}.jpg"
    )

    # Зберігаємо стиснене JPEG-зображення
    img.save(compressed_path, "JPEG", quality=quality, optimize=True)

    # етап декодування
    decoded_img = Image.open(compressed_path)

    # Зберігаємо декодоване зображення у JPEG
    decoded_img.save(decoded_path, "JPEG", quality=quality, optimize=True)

    return compressed_path, decoded_path


def write_result(report, image_path, original_size, quality,
                 compressed_path, decoded_path):
    """
    Записує інформацію про результати стиснення
    у файл results_jpeg.txt.
    """

    compressed_size = os.path.getsize(compressed_path)
    decoded_size = os.path.getsize(decoded_path)

    compression_ratio = original_size / compressed_size

    report.write(f"Якість JPEG: {quality}%\n")
    report.write(f"Стиснуте зображення: {compressed_path}\n")
    report.write(f"Розмір після стиснення: {compressed_size} байт\n")
    report.write(f"Декодоване зображення: {decoded_path}\n")
    report.write(f"Розмір декодованого файлу: {decoded_size} байт\n")
    report.write(f"Коефіцієнт стиснення: {compression_ratio:.2f}\n\n")


def main():
    """
    Основна функція програми.
    Обробляє всі зображення, створює папку Results
    та формує текстовий файл results_jpeg.txt.
    """

    os.makedirs(RESULTS_DIR, exist_ok=True)

    with open("results_jpeg.txt", "w", encoding="utf-8") as report:
        report.write("Практична робота №8\n")
        report.write("Стиснення з втратами. JPEG\n\n")

        for image_path in IMAGES:
            if not os.path.exists(image_path):
                print(f"Файл не знайдено: {image_path}")
                continue

            original_size = os.path.getsize(image_path)
            img = prepare_image(image_path)

            image_name = os.path.splitext(os.path.basename(image_path))[0]

            report.write(f"Файл: {image_path}\n")
            report.write(f"Початковий розмір: {original_size} байт\n\n")

            for quality in QUALITIES:
                compressed_path, decoded_path = save_compressed_and_decoded(
                    img,
                    image_name,
                    quality
                )

                write_result(
                    report,
                    image_path,
                    original_size,
                    quality,
                    compressed_path,
                    decoded_path
                )

            report.write("-" * 50 + "\n\n")

    print("Готово!")
    print("Створено файл results_jpeg.txt")
    print("Створено папку Results з результатами")


if __name__ == "__main__":
    main()
