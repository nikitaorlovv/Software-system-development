import time
import random
import math
import os
import unittest


def compare_and_swap(arr, i, j, direction):
    """Сравнивает и при необходимости меняет местами два элемента массива."""
    if (arr[i] > arr[j] and direction == True) or (arr[i] < arr[j] and direction == False):
        arr[i], arr[j] = arr[j], arr[i]


def bitonic_merge(arr, low, count, direction):
    """Сливает битонную последовательность в монотонную."""
    if count > 1:
        k = count // 2
        for i in range(low, low + k):
            compare_and_swap(arr, i, i + k, direction)
        bitonic_merge(arr, low, k, direction)
        bitonic_merge(arr, low + k, k, direction)


def bitonic_sort_recursive(arr, low, count, direction):
    """Рекурсивно строит битонную последовательность и затем сливает её."""
    if count > 1:
        k = count // 2
        bitonic_sort_recursive(arr, low, k, direction)
        bitonic_sort_recursive(arr, low + k, k, not direction)
        bitonic_merge(arr, low, count, direction)


def bitonic_sort(arr):
    """Основная функция битонной сортировки."""
    n = len(arr)
    if n <= 1:
        return arr

    next_power_of_2 = 1
    while next_power_of_2 < n:
        next_power_of_2 *= 2

    original_n = n
    if n != next_power_of_2:
        max_val = max(arr) if arr else 0
        arr.extend([max_val] * (next_power_of_2 - n))
        n = next_power_of_2

    bitonic_sort_recursive(arr, 0, n, True)

    if original_n != n:
        arr[:] = arr[:original_n]

    return arr


class TestBitonicSort(unittest.TestCase):
    """Юнит-тесты для битонной сортировки."""

    def test_empty_array(self):
        """Тест на пустой массив."""
        arr = []
        result = bitonic_sort(arr)
        self.assertEqual(result, [])

    def test_single_element(self):
        """Тест на массив из одного элемента."""
        arr = [5]
        result = bitonic_sort(arr.copy())
        self.assertEqual(result, [5])

    def test_sorted_array(self):
        """Тест на уже отсортированный массив."""
        arr = [1, 2, 3, 4, 5]
        result = bitonic_sort(arr.copy())
        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_reverse_sorted(self):
        """Тест на массив в обратном порядке."""
        arr = [5, 4, 3, 2, 1]
        result = bitonic_sort(arr.copy())
        self.assertEqual(result, [1, 2, 3, 4, 5])

    def test_random_array(self):
        """Тест на случайный массив."""
        arr = [3, 1, 4, 1, 5, 9, 2, 6, 5, 3]
        expected = sorted(arr)
        result = bitonic_sort(arr.copy())
        self.assertEqual(result, expected)

    def test_non_power_of_two(self):
        """Тест на массив не степени двойки."""
        arr = [7, 2, 9, 4, 1]
        expected = sorted(arr)
        result = bitonic_sort(arr.copy())
        self.assertEqual(result, expected)

    def test_duplicates(self):
        """Тест на массив с дубликатами."""
        arr = [2, 2, 2, 1, 3, 2, 1]
        expected = sorted(arr)
        result = bitonic_sort(arr.copy())
        self.assertEqual(result, expected)

    def test_negative_numbers(self):
        """Тест на отрицательные числа."""
        arr = [-1, -5, 3, 0, -2, 4]
        expected = sorted(arr)
        result = bitonic_sort(arr.copy())
        self.assertEqual(result, expected)

    def test_floats(self):
        """Тест на числа с плавающей точкой."""
        arr = [3.14, 1.5, 2.7, 0.9, 4.2]
        expected = sorted(arr)
        result = bitonic_sort(arr.copy())
        self.assertEqual(result, expected)


def run_tests():
    """Запуск всех тестов."""
    print("\n" + "=" * 60)
    print("   ЗАПУСК ЮНИТ-ТЕСТОВ БИТОННОЙ СОРТИРОВКИ")
    print("=" * 60)

    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestBitonicSort)
    runner = unittest.TextTestRunner(verbosity=2)

    result = runner.run(suite)

    print("=" * 60)
    print(f"✅ Всего тестов: {result.testsRun}")
    print(
        f"✅ Успешно: {len(result.failures) + len(result.errors) == 0 and result.testsRun or result.testsRun - len(result.failures) - len(result.errors)}")
    if result.failures or result.errors:
        print(f"❌ Ошибок: {len(result.failures)}")
        print(f"❌ Сбоев: {len(result.errors)}")
    else:
        print("🎉 ВСЕ ТЕСТЫ ПРОЙДЕНЫ УСПЕШНО!")
    print("=" * 60)


def validate_number(prompt, min_val=None, max_val=None, is_int=True):
    """Валидация ввода числа с повторными попытками."""
    while True:
        try:
            value = input(prompt).strip()
            if is_int:
                num = int(value)
            else:
                num = float(value)

            if min_val is not None and num < min_val:
                print(f"Ошибка: значение должно быть >= {min_val}")
                continue
            if max_val is not None and num > max_val:
                print(f"Ошибка: значение должно быть <= {max_val}")
                continue

            return num
        except ValueError:
            print("Ошибка: введите корректное число!")


def validate_path(prompt):
    """Валидация пути к папке."""
    while True:
        path = input(prompt).strip()
        if os.path.isdir(path):
            return path
        else:
            print("Ошибка: введите корректный путь к существующей папке!")
            print("Пример: C:\\Users\\YourName\\Documents (Windows) или /home/user/docs (Linux/Mac)")


def get_array_length():
    """Получение длины массива с валидацией."""
    return validate_number("Введите длину массива (1-10000): ", 1, 10000)


def input_array_manually(length):
    """Ввод массива вручную."""
    arr = []
    print(f"\nВведите {length} элементов массива (по одному числу в строке):")
    for i in range(length):
        value = validate_number(f"Элемент {i + 1}: ", is_int=False)
        arr.append(value)
    return arr


def generate_random_array(size):
    """Генерация случайного массива."""
    return [random.randint(1, 1000) for _ in range(size)]


def save_results_to_file(folder_path, original_arr, sorted_arr, sorting_time, array_length):
    """Сохранение результатов сортировки в текстовый файл."""
    timestamp = time.strftime("%Y-%m-%d_%H-%M-%S")
    filename = f"bitonic_sort_results_{timestamp}.txt"
    filepath = os.path.join(folder_path, filename)

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 60 + "\n")
            f.write("   РЕЗУЛЬТАТЫ БИТОННОЙ СОРТИРОВКИ\n")
            f.write("=" * 60 + "\n\n")
            f.write(f"Дата и время: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Количество элементов: {array_length}\n")
            f.write(f"Время сортировки: {sorting_time:.6f} сек\n\n")

            f.write("ИСХОДНЫЙ МАССИВ:\n")
            f.write(f"{original_arr}\n\n")

            f.write("ОТСОРТИРОВАННЫЙ МАССИВ:\n")
            f.write(f"{sorted_arr}\n\n")

            f.write("-" * 60 + "\n")
            f.write("Орлов Никита, группа 444\n")
            f.write("-" * 60 + "\n")

        print(f"✅ Результаты сохранены в файл: {filepath}")
        return True
    except Exception as e:
        print(f"❌ Ошибка сохранения файла: {e}")
        return False


def print_menu():
    """Вывод главного меню."""
    print("\n" + "=" * 50)
    print("   Битонная сортировка (Орлов Никита, группа 444)")
    print("=" * 50)
    print("1. Начать работу")
    print("2. Запустить тесты")
    print("3. Выход")
    print("=" * 50)


def print_input_menu():
    """Вывод меню выбора способа ввода."""
    print("\nВыберите способ заполнения массива:")
    print("1. Ввести данные вручную")
    print("2. Случайный массив")
    print("3. Назад в главное меню")


def print_save_menu():
    """Вывод меню сохранения результатов."""
    print("\nХотите сохранить результаты в файл?")
    print("1. Да, сохранить в указанную папку")
    print("2. Нет, продолжить")


def measure_sorting_time(original_arr):
    """Измерение времени сортировки."""
    # Создаем копию для сортировки
    arr_copy = original_arr.copy()

    start_time = time.time()
    sorted_arr = bitonic_sort(arr_copy)
    end_time = time.time()

    sorting_time = end_time - start_time

    return sorted_arr, sorting_time


def main():
    """Главный цикл программы."""
    while True:
        print_menu()
        choice = validate_number("Ваш выбор (1-3): ", 1, 3)

        if choice == 3:
            print("\nДо свидания! 👋")
            break

        if choice == 2:
            run_tests()
            input("\nНажмите Enter для продолжения...")

        if choice == 1:
            while True:
                print_input_menu()
                input_choice = validate_number("Ваш выбор (1-3): ", 1, 3)

                if input_choice == 3:
                    break

                original_arr = []

                if input_choice == 1:
                    length = get_array_length()
                    original_arr = input_array_manually(length)
                elif input_choice == 2:
                    size = get_array_length()
                    print("Генерируем случайный массив")
                    original_arr = generate_random_array(size)
                    print(f"Случайный массив: {original_arr}")

                if original_arr:
                    print("\n" + "-" * 50)
                    print("🔄 Выполняется сортировка...")

                    sorted_arr, sorting_time = measure_sorting_time(original_arr)

                    print("\n✅ СОРТИРОВКА ЗАВЕРШЕНА!")
                    print("-" * 50)
                    print(f"Исходный массив:     {original_arr}")
                    print(f"Отсортированный:     {sorted_arr}")
                    print(f"Время сортировки:    {sorting_time:.6f} сек")
                    print(f"Количество элементов: {len(original_arr)}")
                    print("-" * 50)

                    # Предложение сохранить результаты
                    print_save_menu()
                    save_choice = validate_number("Ваш выбор (1-2): ", 1, 2)

                    if save_choice == 1:
                        folder_path = validate_path(
                            "Введите путь к папке для сохранения (Enter для текущей): ") or os.getcwd()
                        save_results_to_file(folder_path, original_arr, sorted_arr, sorting_time, len(original_arr))

                    # Пауза для просмотра результата
                    input("\nНажмите Enter для продолжения...")


if __name__ == "__main__":
    main()