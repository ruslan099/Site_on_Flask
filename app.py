from flask import Flask, render_template, url_for, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

from werkzeug.utils import redirect

app = Flask(__name__)           # Создаем объект на основе класса Flask и передаем в конструктор основной файл через __name__
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///blog.db'      #указываем название БД для работы
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False             #отключаем неработающий модуль
db = SQLAlchemy(app)               # Создаем объект на основе класса SQLalchemy и в конструктор передаем объект, созданный на основе класса Flask
db.init_app(app)

class Article(db.Model):        # Класс таблицы в базе данных, наследующий Все от объекта 'db'
    # Прописываем поля, которые будут стобцами таблицы
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    intro = db.Column(db.String(300), nullable=False)    # Поле для вступительного текста
    text = db.Column(db.Text, nullable=False)
    date = db.Column(db.DateTime, default=datetime.utcnow)  #Устанавливается дата публикации(автоматически)

    # Когда выбираем объект на основе класса Article, будет выдаваться сам объект(статья) + его id
    # Это нужно для показа самих статей
    def __repr__(self):
        return '<Article %r>' % self.id

@app.route('/')                 # Отслеживание перехода на главную страницу через Декоратор
@app.route('/home')
def index():
    return render_template("index.html")    # Подгрузка html файла

    
@app.route('/about')               
def about():
    return render_template("about.html")

@app.route('/create-article', methods=['POST','GET'])                 # Отслеживание перехода
def create_article():
    if request.method == "POST":                           #Проверяем какой метод отправки данных используется
        # С помощью метода request получаем данные из формы "Создание статьи"
        title = request.form['title']
        intro = request.form['intro']
        text = request.form['text']

        # Создаем объект на основе класса Article
        # и передаем в его конструктор данные полученные из формы выше
        article = Article(title=title, intro=intro, text=text)

        # Сохраняем созданный объект в базу данных
        try:
            db.session.add(article)     #Объект добавили
            db.session.commit()         #Объект сохранили
            return redirect('/materials')
        except:
            return "При добавлении статьи произошла ошибка"

    else:
        return render_template("create-article.html")

@app.route('/materials')               
def materials():
    # Создаем объект, через который будем получать все записи из базы данных
    articles = Article.query.order_by(Article.date.desc()).all()                #query - обращается через класс к таблице БД
    # Вытащили все записи из таблицы, отсортированные по полю 'date'
    return render_template("materials.html", articles=articles)       # Передаем полученный выше список в шаблон
    # Второй параметр отвечает за то, что мы в шаблоне будем иметь доступ к объекту,в котором есть список с нашими записями 
    # по имени 'articles'

@app.route('/materials/<int:id>')           #Делаем динамическую подстановку 'id'
def material_detail(id):
    article = Article.query.get(id)         #Выводим запись по ее id через метод 'get'
    return render_template("material_detail.html", article=article)       # Передаем полученный выше список в шаблон

# Делаем обработку адреса с удалением записи
@app.route('/materials/<int:id>/delete')           
def material_delete(id):
    # Получаем необходимую запись из таблицы и сохраняем в объект "article"
    article = Article.query.get_or_404(id)    #При работе с БД используем функцию "get_or_404" (в случае если не найдет, выдаст ошибку)    
    try:
        db.session.delete(article)          #С помощью метода "delete" удаляем указанную выше запись в объекте "article"
        db.session.commit()
        return redirect('/materials')
    except: 
        return "При удалении записи произошла ошибка!"

# Редактирование записи
@app.route('/materials/<int:id>/update', methods=['POST','GET'])                
def material_update(id):
    article = Article.query.get(id)     #Получаем всю запись из БД для дальнейшей подставновки перед редактированием
    if request.method == "POST": 
        # СРАЗУ устанавливаем данные из формы в указанный выше объект БД                          
        article.title = request.form['title']
        article.intro = request.form['intro']
        article.text = request.form['text']

        # Сохраняем созданный объект в базу данных
        try:
            db.session.commit()         #Объект сохранили
            
            return redirect('/materials')
        except:
            return "При редактировании статьи произошла ошибка"

    else:
        return render_template("material_update.html", article=article)


# -------------В разработке--------------
@app.route('/login')               
def login():
    return render_template("login.html")



# Проверяем, является ли данный файл основным файлом для запуска
# Если да, то запускаем как Flask-приложение
if __name__ == '__main__':
    app.run(debug=True)         #debug=True - выводим все ошибки прямо на сайт