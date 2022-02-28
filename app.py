from flask import Flask, render_template, session, url_for, request, redirect, flash, redirect, url_for, abort, g
import sqlite3
from FDataBase import FDataBase
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import redirect

from UserLogin import UserLogin
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from FDataBase import FDataBase

app = Flask(__name__)
app.config['DATABASE'] = 'blog.db'
app.config['SECRET_KEY'] = '9af0aeaefe52af54f4aaabed1501b1db2bd2f29b'

login_manager = LoginManager(app)

# Данный декоратор формирует экземпляр класса UserLogin
# при каждом запросе от клиента
@login_manager.user_loader
def load_user(user_id):
    db = get_db()
    dbase = FDataBase(db)
    print("load_user")
    return UserLogin().fromDB(user_id, dbase)

def connect_db():
    conn = sqlite3.connect(app.config['DATABASE'])
    conn.row_factory = sqlite3.Row
    return conn

def create_db():
    db = connect_db()
    with app.open_resource('sq_db.sql', 'r') as file:
        db.cursor().executescript(file.read())
    db.commit
    db.close

def get_db():
    """Соединение с БД, если оно еще не установлено"""
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db

@app.route('/')                
@app.route('/home')
def index():
    return render_template("index.html")    

@app.route('/about')               
def about():
    return render_template("about.html")

@app.route('/create-article', methods=['POST','GET'])
@login_required
def create_article():
    db = get_db()
    dbase = FDataBase(db)
    
    if request.method == 'POST':
        if len(request.form['title']) > 5 and len(request.form['intro']) > 5:
            us_info = dbase.getUser(int(current_user.get_id()))
            res = dbase.addArticle(request.form['title'], request.form['intro'], request.form['text'], us_info[1])
            if not res:
                flash('Ошибка при добавлении статьи в БД!', category="error")
            else:
                flash('Статья успешно добавлена!', category='success')
        else:
            flash('Ошибка!', category="error")
    return render_template("create-article.html")

@app.route('/materials')               
def materials():
    db = get_db()
    dbase = FDataBase(db)
    return render_template("materials.html", articles=dbase.getArticles())

@app.route('/materials/<int:id>')           #Делаем динамическую подстановку 'id'
@login_required
def material_detail(id):
    db = get_db()
    dbase = FDataBase(db)
    return render_template("material_detail.html", article=dbase.seeArticle(id))

@app.route('/materials/<int:id>/update', methods=['POST','GET'])                
def material_update(id):
    db = get_db()
    dbase = FDataBase(db)
    if request.method == 'POST':
        try:
            dbase.updArticle(request.form['title'], request.form['intro'], request.form['text'], id)
            flash('Статья успешно обновлена :)', category="success")
            return redirect('/materials')
        except:
            return "При редактировании статьи произошла ошибка"

    return render_template("material_update.html", article=dbase.seeArticle(id))

@app.route('/materials/<int:id>/delete')           
def material_delete(id):
    db = get_db()
    dbase = FDataBase(db)
    try:
        dbase.delArticle(id)
        flash('Статья успешно удалена!', category="error")
        return redirect('/materials')
    except:
        return 'Ошибка при удалении статьи'

@app.route('/login', methods=['POST', 'GET'])
def login():
    db = get_db()
    dbase = FDataBase(db)
    if request.method == "POST":
        user = dbase.getUserByEmail(request.form['email'])
        if user and check_password_hash(user['pwd'], request.form['pwd']):
            # Создаем экземпляр класса и передаем всю ин-фу о юзере
            userlogin = UserLogin().create(user)
            # Авторизуем данного юзера с помощью функции login_user
            login_user(userlogin)
            flash(f"Вы вошли в аккаунт под именем: {user['name']}", category='success')
            return redirect(url_for('materials'))
        else:
            flash('Неверный логин или пароль', category='error')

    return render_template("login.html")

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash(f"Вы вышли из аккаунта!", category="success")
    return redirect(url_for('login'))

@app.route('/register', methods=['POST', 'GET'])
def register():
    db = get_db()
    dbase = FDataBase(db)
    if request.method == 'POST':
        if len(request.form['name']) > 4 and len(request.form['email']) > 4 \
        and len(request.form['pwd']) > 4 and request.form['pwd'] == request.form['pwd2'] :
            hash = generate_password_hash(request.form['pwd'])
            res = dbase.addUser(request.form['name'], request.form['email'], hash)
            if res:
                flash('Вы успешно зарегистрированы!', category='success')
                return redirect(url_for('login'))
            else:
                flash('Ошибка при добавлении в БД!', category='error')
        else:
            flash('Минимальная длина полей - 4 символа!', category='error')
    return render_template("register.html")


@app.errorhandler(404)
def page_not_dound(error):
    return render_template('page404.html', title='Страница не найдена!')

@app.errorhandler(401)
def page_not_dound(error):
    return render_template('page401.html', title='Упс!')

@app.teardown_appcontext
def close_db(error):
    """Закрываем соединение с БД, если оно было установлено"""
    if hasattr(g, 'link_db'):
        g.link_db.close()

# Проверяем, является ли данный файл основным файлом для запуска
# Если да, то запускаем как Flask-приложение
if __name__ == '__main__':
    app.run(debug=True)         