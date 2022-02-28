import sqlite3
from datetime import datetime

class FDataBase:
    def __init__(self, db):
        self.__db = db
        self.__cur = db.cursor()

    def getArticles(self):
        sql = """SELECT * FROM Article ORDER BY date DESC"""
        try:
            self.__cur.execute(sql)
            articles = self.__cur.fetchall()
            if articles: return articles
        except:
            print('Ошибка чтения БД')
        return []

    def addArticle(self, title, intro, text, author):
        try:
            tm = datetime.utcnow()
            time_format = "%Y-%m-%d %H:%M:%S"
            self.__cur.execute("INSERT INTO Article VALUES(NULL, ?, ?, ?, ?, ?)", (title, intro, text, f"{tm:{time_format}}", author))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка добавления статьи'+str(e))
            return False
        return True

    def seeArticle(self, id):
        try:
            self.__cur.execute(f"SELECT * FROM Article WHERE id={id}")
            article = self.__cur.fetchone()
            if article: return article
        except:
            print('Ошибка чтения БД')
        return False, False
    
    def delArticle(self, id):
        try:
            self.__cur.execute(f"DELETE FROM Article WHERE id={id}")
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка при удалении статьи'+str(e))
            return False
        return True

    def updArticle(self, title, intro, text, id):
        try:
            self.__cur.execute(f"UPDATE Article SET title=?, intro=?, text=? WHERE id={id}", (title, intro, text))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка обновления статьи: '+str(e))
            return False
        return True
    
    def addUser(self, name, email, hash):
        try:
            self.__cur.execute(f"SELECT COUNT() as 'count' FROM users WHERE email LIKE '{email}'")
            res = self.__cur.fetchone()
            if res['count'] > 0:
                print('Пользователь с таким email уже существует!')
                return False
            self.__cur.execute("INSERT INTO users VALUES (NULL, ?, ?, ?)", (name, email, hash))
            self.__db.commit()
        except sqlite3.Error as e:
            print('Ошибка добавления пользователя в БД: '+ str(e))
            return False
        return True

    def getUser(self, user_id):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE id  = {user_id} LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден")
                return False
            
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД: "+str(e))
        return False

    def getUserByEmail(self, email):
        try:
            self.__cur.execute(f"SELECT * FROM users WHERE email= '{email}' LIMIT 1")
            res = self.__cur.fetchone()
            if not res:
                print("Пользователь не найден!")
                return False
            
            return res
        except sqlite3.Error as e:
            print("Ошибка получения данных из БД: "+str(e))
        
        return False

