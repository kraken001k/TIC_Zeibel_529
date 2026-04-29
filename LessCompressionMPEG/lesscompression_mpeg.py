import numpy as np
import cv2
import matplotlib.pyplot as plt
import math
import os
import random


# Функція сегментації кадру на блоки
# Повертає кількість блоків по висоті та ширині
def segmentImage(anchor, blockSize=16):
    h, w = anchor.shape
    hSegments = int(h / blockSize)
    wSegments = int(w / blockSize)
    return hSegments, wSegments


# Функція обчислення центру блоку
# x, y — координати лівого верхнього кута блоку
def getCenter(x, y, blockSize):
    return int(x + blockSize / 2), int(y + blockSize / 2)


# Функція формування зони пошуку схожого блоку
# у першому (опорному) кадрі
def getAnchorSearchArea(x, y, anchor, blockSize, searchArea):
    h, w = anchor.shape

    # Знаходимо центр поточного блоку
    cx, cy = getCenter(x, y, blockSize)

    # Обчислюємо початкові координати області пошуку
    sx = max(0, cx - int(blockSize / 2) - searchArea)
    sy = max(0, cy - int(blockSize / 2) - searchArea)

    # Вирізаємо область пошуку з опорного кадру
    anchorSearch = anchor[
        sy:min(sy + searchArea * 2 + blockSize, h),
        sx:min(sx + searchArea * 2 + blockSize, w)
    ]

    return anchorSearch


# Функція отримання блоку із зони пошуку
# p — центр потрібного блоку
def getBlockZone(p, aSearch, tBlock, blockSize):
    px, py = p

    # Переходимо від центру блоку до координат його лівого верхнього кута
    px, py = px - int(blockSize / 2), py - int(blockSize / 2)
    px, py = max(0, px), max(0, py)

    # Вирізаємо блок
    aBlock = aSearch[py:py + blockSize, px:px + blockSize]

    # Якщо розмір блоку на межі кадру виявився меншим,
    # доповнюємо його нулями до потрібного розміру
    if aBlock.shape != tBlock.shape:
        fixed = np.zeros_like(tBlock)
        h = min(aBlock.shape[0], tBlock.shape[0])
        w = min(aBlock.shape[1], tBlock.shape[1])
        fixed[:h, :w] = aBlock[:h, :w]
        return fixed

    return aBlock


# Функція розрахунку MAD
# Mean Absolute Difference — середня абсолютна різниця
# Чим менше значення, тим блоки більш схожі
def getMAD(tBlock, aBlock):
    return np.sum(np.abs(
        np.subtract(tBlock.astype(np.float32), aBlock.astype(np.float32))
    )) / (tBlock.shape[0] * tBlock.shape[1])


# Функція пошуку найбільш схожого блоку
# Використовується покроковий пошук у 9 точках
def getBestMatch(tBlock, aSearch, blockSize):
    step = 4

    ah, aw = aSearch.shape
    acy, acx = int(ah / 2), int(aw / 2)

    minMAD = float("+inf")
    minP = (acx, acy)

    # Пошук виконується доти, доки крок не стане меншим за 1
    while step >= 1:
        pointList = [
            (acx, acy),                 # центр
            (acx + step, acy),          # праворуч
            (acx, acy + step),          # вниз
            (acx + step, acy + step),   # вниз-праворуч
            (acx - step, acy),          # ліворуч
            (acx, acy - step),          # вгору
            (acx - step, acy - step),   # вгору-ліворуч
            (acx + step, acy - step),   # вгору-праворуч
            (acx - step, acy + step)    # вниз-ліворуч
        ]

        # Перевіряємо всі 9 точок
        for point in pointList:
            aBlock = getBlockZone(point, aSearch, tBlock, blockSize)
            MAD = getMAD(tBlock, aBlock)

            if MAD < minMAD:
                minMAD = MAD
                minP = point

        # Переходимо до нової центральної точки
        acx, acy = minP

        # Зменшуємо крок пошуку
        step = int(step / 2)

    # Після завершення пошуку вирізаємо найкраще знайдений блок
    px, py = minP
    px, py = px - int(blockSize / 2), py - int(blockSize / 2)
    px, py = max(0, px), max(0, py)

    matchBlock = aSearch[py:py + blockSize, px:px + blockSize]

    # Якщо блок вийшов неповного розміру, доповнюємо його
    if matchBlock.shape != tBlock.shape:
        fixed = np.zeros_like(tBlock)
        h = min(matchBlock.shape[0], tBlock.shape[0])
        w = min(matchBlock.shape[1], tBlock.shape[1])
        fixed[:h, :w] = matchBlock[:h, :w]
        return fixed

    return matchBlock


# Основна функція блочного пошуку
# Формує прогнозований кадр
def blockSearchBody(anchor, target, blockSize, searchArea=7):
    h, w = anchor.shape

    # Кількість блоків по висоті та ширині
    hSegments, wSegments = segmentImage(anchor, blockSize)

    # Матриця для прогнозованого кадру
    predicted = np.ones((h, w)) * 255

    # Лічильник блоків
    bcount = 0

    # Перебір усіх блоків кадру
    for y in range(0, int(hSegments * blockSize), blockSize):
        for x in range(0, int(wSegments * blockSize), blockSize):
            bcount += 1

            # Поточний блок з цільового кадру
            targetBlock = target[y:y + blockSize, x:x + blockSize]

            # Формування області пошуку в опорному кадрі
            anchorSearchArea = getAnchorSearchArea(x, y, anchor, blockSize, searchArea)

            # Пошук найбільш схожого блоку
            anchorBlock = getBestMatch(targetBlock, anchorSearchArea, blockSize)

            # Заносимо знайдений блок у прогнозований кадр
            predicted[y:y + blockSize, x:x + blockSize] = anchorBlock

    assert bcount == int(hSegments * wSegments)
    return predicted


# Функція обчислення залишкового кадру
# residual = target - predicted
def getResidual(target, predicted):
    return np.subtract(target.astype(np.float32), predicted.astype(np.float32))


# Функція відновлення кадру
# reconstructed = residual + predicted
def getReconstructTarget(residual, predicted):
    return np.add(residual, predicted)


# Функція розрахунку середньої кількості біт на піксель
def getBitsPerPixel(im):
    h, w = im.shape
    bits = 0

    for row in im:
        for pixel in row:
            bits += math.log2(abs(float(pixel)) + 1)

    return bits / (h * w)


# Функція зчитування двох кадрів із відео
def getFrames(filename, first_frame, second_frame):
    cap = cv2.VideoCapture(filename)

    if not cap.isOpened():
        raise FileNotFoundError(f"Не вдалося відкрити відеофайл: {filename}")

    # Переходимо до першого кадру
    cap.set(cv2.CAP_PROP_POS_FRAMES, first_frame - 1)
    res1, fr1 = cap.read()

    # Переходимо до другого кадру
    cap.set(cv2.CAP_PROP_POS_FRAMES, second_frame - 1)
    res2, fr2 = cap.read()

    cap.release()

    if not res1 or not res2:
        raise ValueError("Не вдалося зчитати кадри з відео. Перевір файл або номери кадрів.")

    return fr1, fr2


# Функція збереження зображення з підтримкою кирилиці
def save_image_unicode(path, image):
    image = np.clip(image, 0, 255).astype(np.uint8)

    ext = os.path.splitext(path)[1]
    success, buffer = cv2.imencode(ext, image)

    if success:
        buffer.tofile(path)
    else:
        raise ValueError(f"Не вдалося зберегти файл: {path}")


# Основна функція програми
# Виконує:
# 1) кодування кадру
# 2) пошук залишкового кадру
# 3) відновлення кадру
# 4) розрахунок біт/піксель
# 5) збереження результатів
def main(anchorFrame, targetFrame, blockSize=16, outfile="Results", saveOutput=True):
    # Списки для збереження значень біт на піксель
    bitsAnchor = []
    bitsDiff = []
    bitsPredicted = []

    h, w, ch = anchorFrame.shape
    print("Розмір кадру:", h, w, ch)

    # Порожні матриці для накопичення RGB-компонент
    diffFrameRGB = np.zeros((h, w, ch))
    predictedFrameRGB = np.zeros((h, w, ch))
    residualFrameRGB = np.zeros((h, w, ch))
    restoreFrameRGB = np.zeros((h, w, ch))

    # Обробляємо окремо кожен канал: R, G, B
    for i in range(0, 3):
        # Виділяємо окрему кольорову компоненту
        anchorFrame_c = anchorFrame[:, :, i]
        targetFrame_c = targetFrame[:, :, i]

        # Різниця між двома сусідніми кадрами
        diffFrame = cv2.absdiff(anchorFrame_c, targetFrame_c)

        # Формуємо прогнозований кадр
        predictedFrame = blockSearchBody(anchorFrame_c, targetFrame_c, blockSize)

        # Обчислюємо залишковий кадр
        residualFrame = getResidual(targetFrame_c, predictedFrame)

        # Відновлюємо кадр
        reconstructTargetFrame = getReconstructTarget(residualFrame, predictedFrame)

        # Обчислюємо біт/піксель для трьох варіантів
        bitsAnchor.append(getBitsPerPixel(anchorFrame_c))
        bitsDiff.append(getBitsPerPixel(diffFrame))
        bitsPredicted.append(getBitsPerPixel(residualFrame))

        # Зберігаємо кожну компоненту у відповідний RGB-масив
        diffFrameRGB[:, :, i] = diffFrame
        predictedFrameRGB[:, :, i] = predictedFrame

        # Для візуалізації залишкового кадру додаємо 128,
        # щоб значення не були від’ємними
        residualFrameRGB[:, :, i] = residualFrame + 128

        restoreFrameRGB[:, :, i] = reconstructTargetFrame

    # Створюємо папку Results
    if not os.path.isdir(outfile):
        os.mkdir(outfile)

    # Збереження зображень
    if saveOutput:
        save_image_unicode(f"{outfile}/Перший кадр.png", anchorFrame)
        save_image_unicode(f"{outfile}/Другий кадр.png", targetFrame)
        save_image_unicode(f"{outfile}/Різниця між кадрами.png", diffFrameRGB)
        save_image_unicode(f"{outfile}/Кадр прогнозування.png", predictedFrameRGB)
        save_image_unicode(f"{outfile}/Залишковий кадр.png", residualFrameRGB)
        save_image_unicode(f"{outfile}/Відновлений кадр.png", restoreFrameRGB)

    # Побудова діаграми бітів на відлік / бітів на піксель
    barWidth = 0.25
    plt.figure(figsize=(14, 8))

    # Значення для діаграми:
    # перший елемент — сумарне RGB,
    # наступні три — окремо R, G, B
    P1 = [sum(bitsAnchor), bitsAnchor[0], bitsAnchor[1], bitsAnchor[2]]
    Diff = [sum(bitsDiff), bitsDiff[0], bitsDiff[1], bitsDiff[2]]
    Encoded = [sum(bitsPredicted), bitsPredicted[0], bitsPredicted[1], bitsPredicted[2]]

    # Положення груп стовпців
    br1 = np.arange(len(P1))
    br2 = [x + barWidth for x in br1]
    br3 = [x + barWidth for x in br2]

    # Три стовпці для кожної групи:
    # 1 — початковий кадр
    # 2 — різниця між кадрами
    # 3 — закодований кадр методом компенсації руху
    plt.bar(
        br1,
        P1,
        width=barWidth,
        edgecolor='grey',
        label='Початковий кадр'
    )

    plt.bar(
        br2,
        Diff,
        width=barWidth,
        edgecolor='grey',
        label='Різниця між кадрами'
    )

    plt.bar(
        br3,
        Encoded,
        width=barWidth,
        edgecolor='grey',
        label='Закодований кадр методом компенсації руху'
    )

    compression = round(sum(bitsAnchor) / sum(bitsPredicted), 2)

    plt.title(
        f'Діаграма бітів на відлік. Ступінь стиснення = {compression}',
        fontweight='bold',
        fontsize=15
    )

    plt.ylabel('Біт на відлік / біт на піксель', fontweight='bold', fontsize=15)

    plt.xticks(
        [r + barWidth for r in range(len(P1))],
        [
            'RGB сумарно',
            'Компонента R',
            'Компонента G',
            'Компонента B'
        ]
    )

    plt.legend()
    plt.grid(axis='y')

    plt.savefig(
        f'{outfile}/Діаграма бітів на відлік для RGB та компонент R G B.png',
        dpi=600
    )

    plt.close()

    # Виведення результатів у консоль
    print("Результати збережено у папку Results")
    print("Біт/піксель для початкового кадру:", P1)
    print("Біт/піксель для різниці між кадрами:", Diff)
    print("Біт/піксель для MPEG-кодування:", Encoded)
    print("Ступінь стиснення:", compression)


# Точка входу в програму
if __name__ == "__main__":
    # Назва відеофайлу
    video_name = "sample4.avi"

    # Випадковим чином обираємо перший кадр
    fr = random.randint(1, 3000)
    print("Випадково обраний перший кадр:", fr)

    # Зчитуємо два сусідні кадри
    frame1, frame2 = getFrames(video_name, fr, fr + 1)

    # Запускаємо основну обробку
    main(frame1, frame2, saveOutput=True)
