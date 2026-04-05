from flask import Flask, render_template, request, jsonify, session, redirect
import mysql.connector
import time, re, random

app = Flask(__name__)
app.secret_key = "secret_key_123"

DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "Rom2132412",
    "database": "lab3_db"
}

# ================== SORT ==================
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

# ================== DB ==================
def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def init_db():
    con = get_db()
    cur = con.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users(
            id INT AUTO_INCREMENT PRIMARY KEY,
            username VARCHAR(50) UNIQUE,
            password VARCHAR(255)
        )
    """)
    cur.execute("""
        CREATE TABLE IF NOT EXISTS arrays(
            id INT AUTO_INCREMENT PRIMARY KEY,
            user_id INT,
            original TEXT,
            sorted TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
    """)
    con.commit()
    cur.close()
    con.close()

# ================== PARSE ==================
def parse_array(text):
    """Преобразует строку с числами в список целых чисел"""
    # Находим все числа в строке (включая отрицательные)
    numbers = re.findall(r'-?\d+', text)

    if not numbers:
        raise ValueError("Массив не содержит чисел")

    # Преобразуем в целые числа
    result = [int(x) for x in numbers]

    # Проверяем, что массив не пустой
    if len(result) == 0:
        raise ValueError("Массив пуст")

    return result

# ================== AUTH ==================
@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")

    data = request.get_json()
    con = get_db()
    cur = con.cursor(dictionary=True)

    cur.execute(
        "SELECT * FROM users WHERE username=%s AND password=%s",
        (data["username"], data["password"])
    )
    user = cur.fetchone()
    cur.close()
    con.close()

    if not user:
        return jsonify(success=False, error="Неверный логин или пароль")

    # Исправление: проверяем оба возможных названия поля
    user_id = user.get("Id") or user.get("id")
    if not user_id:
        return jsonify(success=False, error="Ошибка: поле ID не найдено")

    session["user_id"] = user_id
    session["username"] = user["Username"] or user["username"]
    return jsonify(success=True)

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    con = get_db()
    cur = con.cursor()
    try:
        cur.execute(
            "INSERT INTO users(username,password) VALUES(%s,%s)",
            (data["username"], data["password"])
        )
        con.commit()
    except:
        return jsonify(success=False, error="Пользователь существует")
    finally:
        cur.close()
        con.close()
    return jsonify(success=True)

@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify(success=True)

# ================== UI ==================
@app.route("/")
def index():
    if "user_id" not in session:
        return redirect("/login")
    return render_template("index.html", username=session["username"])

# ================== API ==================
@app.route("/api/generate", methods=["POST"])
def generate():
    d = request.get_json()
    arr = [random.randint(d["min"], d["max"]) for _ in range(d["size"])]
    return jsonify(success=True, array=arr)

@app.route("/api/sort", methods=["POST"])
def sort_array():
    try:
        original_arr = parse_array(request.get_json()["array"])
        # Создаём копию для сортировки, чтобы не изменять оригинал
        arr_to_sort = original_arr.copy()
    except Exception as e:
        return jsonify(success=False, error=str(e))

    t = time.time()
    sorted_arr = bitonic_sort(arr_to_sort)
    return jsonify(success=True, original=original_arr, sorted=sorted_arr, time=round(time.time()-t, 6))

@app.route("/api/save", methods=["POST"])
def save():
    if "user_id" not in session:
        return jsonify(success=False)

    arr = parse_array(request.get_json()["array"])
    con = get_db()
    cur = con.cursor()
    cur.execute("""
        INSERT INTO arrays(user_id,original,sorted)
        VALUES(%s,%s,%s)
    """, (
        session["user_id"],
        ",".join(map(str, arr)),
        ",".join(map(str, bitonic_sort(arr)))
    ))
    con.commit()
    cur.close()
    con.close()
    return jsonify(success=True)


@app.route("/api/my_arrays")
def my_arrays():
    if "user_id" not in session:
        return jsonify(success=False, error="Не авторизован")

    con = get_db()
    cur = con.cursor(dictionary=True)
    cur.execute("""
        SELECT original, sorted, created_at
        FROM arrays WHERE user_id = %s
        ORDER BY created_at DESC
    """, (session["user_id"],))
    rows = cur.fetchall()
    cur.close()
    con.close()

    # Возвращаем в правильном формате
    arrays_list = []
    for r in rows:
        arrays_list.append({
            "original": r["original"],
            "sorted": r["sorted"],
            "created_at": str(r["created_at"])
        })

    return jsonify({"success": True, "arrays": arrays_list})

# ================== RUN ==================
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
