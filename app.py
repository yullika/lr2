from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import telebot
import threading
import os

app = Flask(__name__)
app.secret_key = '345890ryh72'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# Модели базы данных
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(150), nullable=False)
    role = db.Column(db.String(50), nullable=False)  # 'manager' or 'director'

class MessageStats(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    message_count = db.Column(db.Integer, default=0)

def update_message_stats(user_id):
    stat = MessageStats.query.filter_by(user_id=user_id).first()
    if stat:
        stat.message_count += 1
    else:
        stat = MessageStats(user_id=user_id, message_count=1)
        db.session.add(stat)
    db.session.commit()

# Инициализация бота
bot = telebot.TeleBot("7215978807:AAHv7CQEs31qHLOKEQ4PYEaFlZebSdUz7oU")

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('index'))
        else:
            flash('Неверные учетные данные', 'danger')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

@app.route('/')
@login_required
def index():
    return render_template('index.html', role=current_user.role)

@app.route('/add_fact', methods=['GET', 'POST'])
@login_required
def add_fact():
    if current_user.role == 'manager':
        if request.method == 'POST':
            fact = request.form.get('fact')
            if fact:
                # Вставка факта в базу данных
                flash('Факт успешно добавлен!', 'success')
                return redirect(url_for('index'))
            else:
                flash('Введите факт!', 'danger')
    else:
        flash('У вас нет прав для этой операции', 'danger')
    return render_template('add_fact.html')

@app.route('/view_stats')
@login_required
def view_stats():
    if current_user.role == 'director':
        stats = MessageStats.query.all()  # Получение статистики
        return render_template('view_stats.html', stats=stats)
    else:
        flash('У вас нет прав для этой операции', 'danger')
        return redirect(url_for('index'))

# Запуск бота в отдельном потоке
def run_bot():
    bot.polling(none_stop=True)

if __name__ == '__main__':
    db.create_all()  # Создание таблиц
    threading.Thread(target=run_bot).start()
    app.run(host='0.0.0.0', port=5000)
