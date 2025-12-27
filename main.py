from flask import Flask, render_template, request, url_for, redirect, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from datetime import datetime, timedelta, date
from werkzeug.security import generate_password_hash, check_password_hash
import secrets

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///flask.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = 'qwerty'
db = SQLAlchemy(app)
migrate = Migrate(app, db, render_as_batch=True)


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(128), unique=True, nullable=False)
    word = db.Column(db.String(256), nullable=False)
    token = db.Column(db.String(32))
    token_expiration = db.Column(db.DateTime)

    def set_password(self, password):
        """Устанавливает хешированный пароль"""
        self.word = generate_password_hash(password)

    def check_password(self, password):
        """Проверяет пароль"""
        return check_password_hash(self.word, password)

    def generate_token(self):
        """Генерирует токен и устанавливает срок его действия"""
        self.token = secrets.token_hex(16)
        self.token_expiration = datetime.utcnow() + timedelta(minutes=30)
        return self.token

class Money(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.String(64), nullable=False)
    users = db.Column(db.String(64), nullable=True)
    title = db.Column(db.String(64), nullable=False)
    sum_ = db.Column(db.Integer, nullable=False)
    balance = db.Column(db.Integer, nullable=False)
    cat = db.Column(db.String(64), nullable=False)
    status = db.Column(db.String(64), nullable=False)
    change = db.Column(db.Date)

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    card = db.Column(db.Integer, nullable=False)
    operation = db.Column(db.String(1), nullable=False)
    sum_ = db.Column(db.Integer, nullable=False)
    change = db.Column(db.Date)

@app.route('/', methods=["GET", "POST"])
def home():
    if session.get("token") and session.get("user_id"):
        return redirect(url_for("money"))
    else:
        return render_template("home.html")
@app.route('/register', methods=["post", "get"])
def reg():
    if request.method == "GET":
        return render_template("reg.html")
    else:
        # Создаём нового пользователя
        try:
            l = request.form["login"]
            e = request.form["email"]
            w = request.form["word"]
            if not l or not e or not w:
                flash("Вы заполнили не все поля")
                return render_template("reg.html")
            user = User(username=l, email=e)
            user.set_password(w)  # Хешируем пароль
            user.generate_token()  # Генерируем токен
            db.session.add(user)
            db.session.commit()
            flash("Вы зарегистрированы")
            return redirect(url_for("login"))
        except Exception:
            flash("Этот пользователь уже существует")
            return render_template("reg.html")


@app.route('/login', methods=["post", "get"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        user = User.query.filter_by(username=request.form['login']).first()
        if user and user.check_password(request.form['word']):
            # Генерируем новый токен при входе
            token = user.generate_token()
            db.session.commit()  # Сохраняем токен в базе
            session["token"] = token  # Сохраняем токен в сессии
            session["user_id"] = user.id  # Сохраняем ID пользователя
            session["user"] = user.username
            flash('Вы успешно вошли')
            return redirect(url_for("money"))
        else:
            flash('Неверные данные')
            return render_template("login.html")


@app.before_request
def check_auth():
    # Список страниц, доступных без авторизации
    allowed_endpoints = ['login', 'reg', 'static', 'home', 'yandex']

    # Если запрос к разрешённой странице - пропускаем
    if request.endpoint in allowed_endpoints:
        return None

    # Получаем токен и ID пользователя из сессии
    token = session.get("token")
    user_id = session.get("user_id")

    if not token or not user_id:
        flash('Пожалуйста, войдите в систему')
        return redirect(url_for('home'))

    # Проверяем токен в базе данных
    user = User.query.filter_by(id=user_id, token=token).first()

    if not user:
        flash('Недействительный токен. Войдите заново')
        session.clear()
        return redirect(url_for('home'))

    # Проверяем срок действия токена
    if not user.token_expiration or datetime.utcnow() > user.token_expiration:
        flash('Срок действия сессии истёк. Войдите заново')
        session.clear()
        return redirect(url_for('home'))

    return None


@app.route("/logout")
def logout():
    session.clear()  # Очищаем всю сессию
    flash('Вы вышли из системы')
    return redirect(url_for('home'))

@app.route("/yandex_6400b448f7e4d776.html")
def yandex():
    return render_template("yandex_6400b448f7e4d776.html")

@app.route("/money", methods=["post", "get"])
def money():
    if request.method == 'POST':
        try:
            t = request.form["h"]
            s = int(request.form["s"])
            bal = int(request.form["bal"])
            cat = request.form["cat"]
            session["t"] = t
            session["s"] = s
            session["bal"] = bal
            session["cat"] = cat
            if not t or not cat:
                flash("Вы заполнили не все поля")
                return render_template("create.html")
            else:
                if s <= 0:
                    flash("Итоговая сумма не может быть меньше либо равной нулю.")
                    return render_template("create.html")
                elif bal < 0:
                    flash("Баланс не может быть меньше нуля.")
                    return render_template("create.html")
                elif bal >= s:
                    flash('Баланс не может быть больше либо равным итоговой сумме.')
                    return render_template("create.html")
                else:
                    capital = Money(title=t, sum_=s, balance=bal, cat = cat, status="не достигнута", change=date.today(), user=session["user"])
                    flash('Цель успешно добавлена')
                    db.session.add(capital)
                    transaction = Transactions(card=Money.query.all()[-1].id, operation='+', sum_=bal, change=date.today())
                    db.session.add(transaction)
                    db.session.commit()

        except ValueError:
            flash("Вы можете ввести только целое числовое значение.")
            return render_template("create.html")
    n = Money.query.filter_by(user=session["user"])
    n1 = Money.query.filter(Money.user != session["user"]).all()
    session["t"] = ''
    session["s"] = ''
    session["bal"] = ''
    session["cat"] = ''
    return render_template("money.html", n=n, n1=n1)

@app.route("/create", methods=["post", "get"])
def create():
    return render_template("create.html")

@app.route("/card/<c>")
def card(c):
    try:
        n = Money.query.get(c)
        tr = Transactions.query.filter_by(card=n.id)
        if Money.query.get(c).user == session["user"] or session["user"] in Money.query.get(c).users:
            return render_template("card.html", n=n, tr=tr)
        else:
            return render_template("404.html")
    except AttributeError:
        return render_template("404.html")

@app.route("/delete/<c>")
def del_card(c):
    try:
        if Money.query.get(c).user == session["user"]:
            n = Money.query.get(c)
            db.session.delete(n)
            db.session.query(Transactions).filter(Transactions.card==n.id).delete()
            db.session.commit()
            flash("Цель успешно удалена")
            return redirect(url_for('money'))
        else:
            return render_template("404.html")
    except AttributeError:
        return render_template("404.html")

@app.route("/add_user/<c>", methods=["post", "get"])
def add_user(c):
    try:
        if Money.query.get(c).user == session["user"]:
            if request.method == 'POST':
                n = Money.query.get(c)
                u = request.form["u"]
                if not User.query.filter_by(username=u).first():
                    flash("Такого пользователя не существует")
                    s = "/card/" + str(c)
                    return redirect(s)
                elif u == session["user"]:
                    flash("Вы не можете ввести свой логин")
                    s = "/card/" + str(c)
                    return redirect(s)
                elif not n.users:
                    n.users = u
                    db.session.commit()
                    flash("Пользователь добавлен")
                    s = "/card/" + str(c)
                    return redirect(s)
                elif u in n.users:
                    flash("Вы не можете ввести одного пользователя дважды")
                    s = "/card/" + str(c)
                    return redirect(s)
                else:
                    n.users += ', ' + u
                    db.session.commit()
                    flash("Пользователь добавлен")
                    s = "/card/" + str(c)
                    return redirect(s)
            else:
                return render_template("404.html")
        else:
            return render_template("404.html")
    except AttributeError:
        return render_template("404.html")

@app.route("/del_user/<c>/<us>", methods=["post", "get"])
def del_user(c, us):
    try:
        if Money.query.get(c).user == session["user"] or us == session["user"]:
            n = Money.query.get(c)
            all_users = list(n.users.split(', '))
            all_users.remove(us)
            n.users = ", ".join(all_users)
            db.session.commit()
            if Money.query.get(c).user == session["user"]:
                flash("Пользователь удалён")
                s = "/card/" + str(c)
                return redirect(s)
            else:
                flash("Вы вышли из накопления")
                return redirect("/money")
        else:
            return render_template("404.html")
    except Exception:
        return render_template("404.html")

@app.route("/update/<c>", methods=["post", "get"])
def upd_card(c):
    n = Money.query.get(c)
    try:
        if Money.query.get(c).user == session["user"]:
            if request.method == 'POST':
                try:
                    t = request.form["h"]
                    s = int(request.form["s"])
                    bal = int(request.form["bal"])
                    cat = request.form["cat"]
                    if not t or not cat:
                        flash("Вы заполнили не все поля")
                        return render_template("update.html", c=c, n=n)
                    else:
                        if s <= 0:
                            flash("Итоговая сумма не может быть меньше либо равной нулю.")
                            return render_template("update.html", c=c, n=n)
                        elif bal < 0:
                            flash("Баланс не может быть меньше нуля.")
                            return render_template("update.html", c=c, n=n)
                        elif bal >= s:
                            flash('Баланс не может быть больше либо равным итоговой сумме.')
                            return render_template("update.html", c=c, n=n)
                        else:
                            n = Money.query.get(c)
                            n.title = t
                            n.sum_ = s
                            tr = Transactions.query.filter_by(card=c)
                            n.balance = 0
                            for i in tr:
                                if i.operation == '+':
                                    n.balance += i.sum_
                                else:
                                    n.balance -= i.sum_
                                    if n.balance < 0:
                                        n.balance = 0
                            if n.balance > n.sum_:
                                n.balance = n.sum_
                                n.status = 'достигнута'
                            else:
                                n.status = 'не достигнута'
                            n.cat = cat
                            n.change = date.today()
                            db.session.commit()
                            flash("Цель успешно изменена")
                            s = "/card/" + str(c)
                            return redirect(s)
                except ValueError:
                    flash("Вы можете ввести только целое числовое значение.")
                    return render_template("update.html", c=c, n=n)
            else:
                return render_template("update.html", c=c, n=n)
        else:
            return render_template("404.html")
    except AttributeError:
        return render_template("404.html")

@app.route("/plus/<c>", methods=["post", "get"])
def plus_bal(c):
    try:
        if request.method == 'POST':
            n = Money.query.get(c)
            b = int(request.form["b"])
            n.balance += b
            if n.balance >= n.sum_:
                n.balance = n.sum_
                n.status = 'достигнута'
            n.change = date.today()
            tr = Transactions(card=n.id, operation='+', sum_= b, change = date.today())
            db.session.add(tr)
            db.session.commit()
            s = "/card/" + str(c)
            return redirect(s)
        else:
            return render_template("404.html")
    except AttributeError:
        return render_template("404.html")

@app.route("/minus/<c>", methods=["post", "get"])
def min_bal(c):
    try:
        if request.method == 'POST':
            n = Money.query.get(c)
            b = int(request.form["b"])
            n.balance -= b
            if n.balance < 0:
                n.balance = 0
            n.change = date.today()
            tr = Transactions(card=n.id, operation='-', sum_=b, change=date.today())
            db.session.add(tr)
            db.session.commit()
            s = "/card/" + str(c)
            return redirect(s)
        else:
            return render_template("404.html")
    except AttributeError:
        return render_template("404.html")

@app.errorhandler(404)
def not_found(e):
    return render_template("404.html"), 404
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)