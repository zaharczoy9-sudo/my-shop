from flask import Flask, request, redirect, render_template_string, session, jsonify, send_from_directory
from functools import wraps
from database import init_db, get_products, get_product, add_product, update_product, delete_product
from config import ADMIN_IDS, SECRET

app = Flask(__name__)
app.secret_key = SECRET

def admin_required(f):
    @wraps(f)
    def wrapper(*a, **k):
        if not session.get("is_admin"):
            return redirect("/login")
        return f(*a, **k)
    return wrapper

# ─── Шаблоны страниц ───

LOGIN_PAGE = """
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Вход в админку</title>
<style>
body{font-family:system-ui;display:flex;justify-content:center;align-items:center;min-height:100vh;margin:0;background:#f5f5f5}
.box{background:#fff;padding:30px;border-radius:12px;box-shadow:0 2px 10px rgba(0,0,0,.1);text-align:center}
input{padding:10px;width:250px;border:1px solid #ddd;border-radius:8px;font-size:16px}
button{padding:10px 30px;background:#2aabee;color:#fff;border:0;border-radius:8px;font-size:16px;cursor:pointer;margin-top:10px}
.err{color:red;margin-top:10px}
</style></head><body>
<div class="box">
<h2>🔐 Вход в админку</h2>
<p>Введите ваш Telegram ID</p>
<form method="post">
<input name="tg_id" type="number" placeholder="Например: 123456789" required>
<br><button>Войти</button>
</form>
{% if error %}<p class="err">{{ error }}</p>{% endif %}
</div></body></html>
"""

ADMIN_PAGE = """
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Админка магазина</title>
<style>
body{font-family:system-ui;max-width:900px;margin:20px auto;padding:0 15px}
table{width:100%;border-collapse:collapse;margin-top:15px}
td,th{border:1px solid #ddd;padding:8px;text-align:left}
.btn{display:inline-block;padding:6px 14px;background:#2aabee;color:#fff;border:0;border-radius:6px;cursor:pointer;text-decoration:none;font-size:14px}
.btn-del{background:#e53935}
.btn-out{background:#999;float:right}
</style></head><body>
<h1>📦 Товары</h1>
<a href="/add" class="btn">+ Добавить товар</a>
<a href="/logout" class="btn btn-out">Выйти</a>
<table>
<tr><th>ID</th><th>Фото</th><th>Название</th><th>Цена</th><th>Остаток</th><th>Действия</th></tr>
{% for p in products %}
<tr>
  <td>{{ p.id }}</td>
  <td>{% if p.photo_url %}<img src="{{ p.photo_url }}" width="60" style="border-radius:6px">{% else %}—{% endif %}</td>
  <td>{{ p.name }}</td>
  <td>{{ p.price }} ₽</td>
  <td>{{ p.stock }}</td>
  <td>
    <a href="/edit/{{ p.id }}" class="btn">✏️ Ред.</a>
    <a href="/delete/{{ p.id }}" class="btn btn-del" onclick="return confirm('Удалить?')">🗑</a>
  </td>
</tr>
{% endfor %}
</table>
{% if not products %}<p style="color:#999;margin-top:20px">Товаров пока нет. Добавьте первый!</p>{% endif %}
</body></html>
"""

FORM_PAGE = """
<!doctype html><html><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{{ title }}</title>
<style>
body{font-family:system-ui;max-width:500px;margin:20px auto;padding:0 15px}
label{display:block;margin:10px 0 4px;font-weight:bold}
input,textarea{width:100%;padding:10px;border:1px solid #ddd;border-radius:8px;font-size:16px;box-sizing:border-box}
textarea{height:80px}
.btn{padding:10px 30px;background:#2aabee;color:#fff;border:0;border-radius:8px;font-size:16px;cursor:pointer;margin-top:15px}
a{color:#2aabee}
</style></head><body>
<h1>{{ title }}</h1>
<form method="post">
<label>Название товара</label>
<input name="name" value="{{ p.name or '' }}" required placeholder="Например: Худи оверсайз">

<label>Описание</label>
<textarea name="description" placeholder="Размер, цвет, материал...">{{ p.description or '' }}</textarea>

<label>Цена (₽)</label>
<input name="price" type="number" step="0.01" value="{{ p.price or '' }}" required placeholder="2990">

<label>Ссылка на фото</label>
<input name="photo_url" value="{{ p.photo_url or '' }}" placeholder="https://...">

<label>Количество в наличии</label>
<input name="stock" type="number" value="{{ p.stock or 0 }}" placeholder="10">

<button class="btn">💾 Сохранить</button>
</form>
<p><a href="/">← Назад к списку</a></p>
</body></html>
"""

# ─── Маршруты ───

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        try:
            tg_id = int(request.form["tg_id"])
            if tg_id in ADMIN_IDS:
                session["is_admin"] = True
                return redirect("/")
            else:
                return render_template_string(LOGIN_PAGE, error="Неверный ID")
        except ValueError:
            return render_template_string(LOGIN_PAGE, error="Введите число")
    return render_template_string(LOGIN_PAGE, error=None)

@app.route("/logout")
def logout():
    session.pop("is_admin", None)
    return redirect("/login")

@app.route("/")
@admin_required
def index():
    return render_template_string(ADMIN_PAGE, products=get_products())

@app.route("/add", methods=["GET", "POST"])
@admin_required
def add():
    if request.method == "POST":
        add_product(
            request.form["name"],
            request.form.get("description", ""),
            float(request.form["price"]),
            request.form.get("photo_url", ""),
            int(request.form.get("stock", 0))
        )
        return redirect("/")
    return render_template_string(FORM_PAGE, title="Новый товар", p={})

@app.route("/edit/<int:pid>", methods=["GET", "POST"])
@admin_required
def edit(pid):
    p = get_product(pid)
    if not p:
        return "Товар не найден", 404
    if request.method == "POST":
        update_product(
            pid,
            request.form["name"],
            request.form.get("description", ""),
            float(request.form["price"]),
            request.form.get("photo_url", ""),
            int(request.form.get("stock", 0))
        )
        return redirect("/")
    return render_template_string(FORM_PAGE, title="Редактировать товар", p=p)

@app.route("/delete/<int:pid>")
@admin_required
def delete(pid):
    delete_product(pid)
    return redirect("/")

@app.route("/api/products")
def api_products():
    return jsonify([dict(p) for p in get_products()])

@app.route("/shop")
def shop_page():
    return send_from_directory("webapp", "index.html")
