from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user, UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Length, Email, EqualTo
import os
import uuid
import secrets

app = Flask(__name__)
# Используем безопасный секретный ключ
app.config['SECRET_KEY'] = secrets.token_hex(32)
app.config['UPLOAD_FOLDER'] = os.path.join('static', 'images')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

# Простая in-memory "база" для демонстрации
USERS = {}
PATTERNS = [
   {'id': '1', 'title': 'Карпы Кои', 'image': 'https://i.pinimg.com/736x/cc/12/82/cc1282a80f00082545f159c0ff14b587.jpg', 'tags': ['рыба', 'водное', 'животные'], 'description': 'Схема вязания рыбок Кои.\n\nОчаровательная рыбка. Работа выполняется по спирали, без соединительных столбиков и воздушных петель в начале ряда.\n\nМАТЕРИАЛЫ:\nПряжа цвета 1 (белый)\nПряжа цвета 2 (розовый)\nБезопасные глазки\nНаполнитель\nИгла\nКрючок под размер пряжи\nНожницы\nБулавки для фиксации деталей\n\nСОКРАЩЕНИЯ:\nMR - волшебное кольцо\nSC - столбик без накида\nINC - прибавка\nDEC - убавка\nHDC - полустолбик с накидом\nDC - столбик с накидом\nTR - столбик с двумя накидами\nSLST - соединительный столбик\nR - ряд\n\nТЕЛО (цвет 1):\nR1: 5 sc в MR (5)\nR2: 5 inc (10)\nR3: 1 sc, 1 inc (15)\nR4: 2 sc, 1 inc (20)\nR5: 3 sc, 1 inc (25)\nR6-R9: 9 sc вокруг (4 ряда)\nВставить глазки между R4-R5 или R5-R6\nR10: 4 sc, 1 inc (30)\nR11-R13: 30 sc вокруг (3 ряда)\nR14: 4 sc, 1 dec (25)\nR15-R16: 25 sc вокруг (2 ряда)\nНачать наполнение\nR17: 3 sc, 1 dec (20)\nR18-R19: 20 sc вокруг (2 ряда)\nR20: 2 sc, 1 dec (15)\nR21-R22: 15 sc вокруг (2 ряда)\nR23: 1 sc, 1 dec (10)\nR24-R25: 10 sc вокруг (2 ряда)\nЗакончить наполнение\nR26: 5 dec (5)\nЗакрепить, закрыть отверстие\n\nВЕРХНИЙ ПЛАВНИК (цвет 1):\nR1: цепочка 11\nR2: со 2-й петли от крючка: 1 hdc, 1 dc, 2 tr, 2 dc, 2 hdc, 2 sc\nПришить к верху рыбы между R7 и R17\n\nБОКОВЫЕ ПЛАВНИКИ (2 шт, цвет 1):\nR1: цепочка 4\nR2: со 2-й петли: 3 sc\nR3: цепочка 1, поворот: inc (1 sc, 1 hdc), inc (2 dc), inc (1 hdc, 1 sc)\nПришить между R10-R12 ниже глаз\n\nХВОСТ (цвет 1):\nR1: MR, затем цепочка 9\nR2: со 2-й петли: sc 8, slst в MR\nR3: поворот, sc 6\nR4: цепочка 1, поворот, sc 6, slst в MR\nR5: поворот, sc 4\nR6: цепочка 1, поворот, sc 4, slst в MR\nR7: поворот, sc 4, цепочка 3\nR8: со 2-й петли: sc 6, slst в MR\nR9: поворот, sc 6, цепочка 3\nR10: со 2-й петли: sc 8, slst в MR\nПришить к задней части тела\n\nЗАПЛАТКИ (цвет 2, 4 варианта):\n\nЗаплатка 1:\nR1: цепочка 4\nR2: sc 3\nR3: цепочка 1, поворот, sc 2, inc\nR4: цепочка 1, поворот, sc 4, inc\nR5: цепочка 1, поворот, sc 5\nR6: цепочка 1, поворот, dec, sc, dec\n\nЗаплатка 2:\nR1: цепочка 5\nR2: sc 4\nR3: цепочка 1, поворот, sc 4, inc\nR4: цепочка 1, поворот, sc 4, 2 inc\nR5: цепочка 1, поворот, sc 5\n\nЗаплатка 3:\nR1: sc 6 в MR (6)\nR2: 1 sc, 1 inc (9)\nR3: 2 sc, 1 inc (12)\nR4: sc 3\nR5: цепочка 1, поворот, sc 3\nR6: цепочка 1, поворот, sc 2\n\nЗаплатка 4:\nR1: цепочка 4\nR2: sc 3, цепочка 1\nR3: цепочка 1, поворот, sc 4, цепочка 1\nR4: цепочка 1, поворот, sc 4\nR5: цепочка 1, поворот, sc 3\n\nПришить заплатки в любом порядке'},
    {'id': '2', 'title': 'Медуза', 'image': 'https://i.pinimg.com/736x/e3/57/4a/e3574a2484528d57236a0855773f39ff.jpg', 'tags': ['медуза','водное','животные'], 'description':'Схема вязания медузы.'},
    {'id': '3', 'title': 'Змея', 'image': 'https://i.pinimg.com/736x/59/a4/d6/59a4d6d622d084ebec60b95082e889d8.jpg', 'tags': ['рептилия','змея','животные'], 'description':'Схема вязания змеи.'},
    {'id': '4', 'title': 'Мухомор', 'image': 'https://i.pinimg.com/1200x/f5/db/fd/f5dbfd191728ba55763fb2cced0a2c38.jpg', 'tags': ['мухомор', 'грибы'], 'description': 'Схема вязания мухомора.'},
    {'id': '5', 'title': 'Козленок', 'image': 'https://i.pinimg.com/736x/7a/e0/34/7ae03451d0cad1ca44e2bbf5f11f3525.jpg', 'tags': ['козел', 'животные','млекопитающие'], 'description': 'Схема вязания козленка.'},
    {'id': '6', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '7', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '8', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '9', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '10', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '11', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '12', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '13', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '14', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '15', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '16', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '17', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '18', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '19', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '20', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '21', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '22', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '23', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '24', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '25', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '26', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '27', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '28', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '29', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '30', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '31', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '32', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '33', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},
    {'id': '34', 'title': 'Здесь будет новое фото', 'image': 'https://i.pinimg.com/736x/8f/97/f4/8f97f4654f8c2746596b6e5868f245d8.jpg', 'tags': ['новое фото'], 'description': 'Схема вязания чего-то.'},


]

class User(UserMixin):
    def __init__(self, id, username, password_hash, collections=None):
        self.id = id
        self.username = username
        self.password_hash = password_hash
        self.collections = collections or []

@login_manager.user_loader
def load_user(user_id):
    user = USERS.get(user_id)
    if not user:
        return None
    return User(user_id, user['username'], user['password_hash'], user.get('collections', []))

class RegisterForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired(), Length(3, 25)])
    password = PasswordField('Пароль', validators=[DataRequired(), Length(6, 128)])
    submit = SubmitField('Зарегистрироваться')

class LoginForm(FlaskForm):
    username = StringField('Имя пользователя', validators=[DataRequired()])
    password = PasswordField('Пароль', validators=[DataRequired()])
    submit = SubmitField('Войти')

@app.route('/')
def index():
    q = request.args.get('q','').lower()
    tag = request.args.get('tag','').lower()
    results = PATTERNS
    if q:
        results = [p for p in results if 
                   q in p['title'].lower() or 
                   q in p['description'].lower() or
                   any(q in t.lower() for t in p['tags'])]
    if tag:
        results = [p for p in results if tag in [t.lower() for t in p['tags']]]
    return render_template('index.html', patterns=results)

@app.route('/pattern/<id>')
def pattern(id):
    p = next((x for x in PATTERNS if x['id']==id), None)
    if not p:
        flash('Схема не найдена', 'error')
        return redirect(url_for('index'))
    return render_template('pattern.html', pattern=p)

@app.route('/register', methods=['GET','POST'])
def register():
    form = RegisterForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        if any(u['username']==username for u in USERS.values()):
            flash('Пользователь с таким именем уже существует','error')
            return redirect(url_for('register'))
        uid = str(uuid.uuid4())
        USERS[uid] = {'username': username, 'password_hash': generate_password_hash(password), 'collections': []}
        flash('Регистрация успешна. Войдите в систему.','success')
        return redirect(url_for('login'))
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        user_item = next(((uid,u) for uid,u in USERS.items() if u['username']==username), None)
        if user_item and check_password_hash(user_item[1]['password_hash'], password):
            uid = user_item[0]
            user = User(uid, username, user_item[1]['password_hash'], user_item[1].get('collections',[]))
            login_user(user)
            flash('Вход выполнен','success')
            return redirect(url_for('index'))
        flash('Неверное имя или пароль','error')
    return render_template('login.html', form=form)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Вы вышли','success')
    return redirect(url_for('index'))

@app.route('/save/<id>')
@login_required
def save(id):
    # Проверяем, существует ли схема
    pattern_exists = any(p['id'] == id for p in PATTERNS)
    if not pattern_exists:
        flash('Схема не найдена', 'error')
        return redirect(url_for('index'))
    
    # Проверяем, не сохранена ли уже
    if id not in current_user.collections:
        USERS[current_user.id]['collections'].append(id)
        current_user.collections.append(id)
        flash('Схема сохранена в подборки', 'success')
    else:
        flash('Схема уже сохранена', 'info')
    return redirect(url_for('profile'))

@app.route('/profile')
@login_required
def profile():
    saved = [p for p in PATTERNS if p['id'] in current_user.collections]
    return render_template('profile.html', saved=saved)

@app.route('/about')
def about():
    total_patterns = len(PATTERNS)
    return render_template('about.html', total_patterns=total_patterns)

if __name__ == '__main__':
    app.run(debug=True)