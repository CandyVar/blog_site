import os

from flask import Flask, render_template, request, make_response, jsonify, url_for, session
from flask import redirect
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from flask_restful import abort, Api
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from werkzeug.utils import secure_filename
from flask_socketio import SocketIO, join_room, leave_room, send
from create_room import generate_room_code
from db.DB import import_history_of_chat, downoload_users_datum, find_news_author, existing_room

from data.coment import Com
from db.DB import import_history_of_chat, downoload_users_datum, find_news_author
from forms.coment import ComForm
from forms.news import NewsForm
from forms.user import RegisterForm, LoginForm, AvatarForm
from forms.messages import MessageForm
from data.news import News
from data import db_session, news_api, news_resources
from data.users import User
from data.messages import Message
from data.rooms import Room

app = Flask(__name__, static_folder='static', static_url_path='/static')
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
app.config['STATIC_FOLDER'] = './static'
app.config['UPLOAD_FOLDER'] = 'static/img/up'
app.config['UPLOAD_FOLDER_COVERS'] = 'static/covers'
covers = app.config['UPLOAD_FOLDER_COVERS']
upload_folder = app.config['UPLOAD_FOLDER']
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db/blogs.db?check_same_thread=False'
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
login_manager = LoginManager()
login_manager.init_app(app)
socketio = SocketIO(app)
admins = 5
system = 100
com_sys = True


def ComSorter(com_list, id):
    if com_sys:
        listt = {'system': [], 'author': [], 'admins': [], 'base': []}
        for item in com_list[::-1]:
            if item.user.rank == system:
                listt['system'].append(item)
            elif item.user.id == id:
                listt['author'].append(item)
            elif item.user.rank >= admins and item.user.rank != system:
                listt['author'].append(item)
            else:
                listt['base'].append(item)
        return listt['system'] + listt['author'] + listt['admins'] + listt['base']
    else:
        return com_list[::-1]



@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/blog')
def test():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        if current_user.rank >= admins:
            news = db_sess.query(News)
        else:
            news = db_sess.query(News).filter(
                (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("blog.html", news=news[::-1], admins=admins, status=True)

@app.route('/blog/@<tag>')
def blog_teg(tag):
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        if current_user.rank >= admins:
            news = db_sess.query(News).filter((News.tag == tag))
        else:
            news = db_sess.query(News).filter((News.tag == tag))
            news = news.filter((News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True and News.tag == tag)
    return render_template("blog.html", news=news[::-1], admins=admins, status=True)




@app.route('/')
def test2():
    return render_template('Главная.html', title='Тест страница', status=True)


@app.route('/test3')
def test3():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("Страница-1.html", news=news[::-1], status=True)


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        user = db_sess.query(User).filter(User.email == form.email.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            return redirect("/")
        return render_template('login.html',
                               message="Неправильный логин или пароль",
                               form=form)
    return render_template('login.html', title='Авторизация', form=form)


@app.route("/1")
def index():
    db_sess = db_session.create_session()
    if current_user.is_authenticated:
        news = db_sess.query(News).filter(
            (News.user == current_user) | (News.is_private != True))
    else:
        news = db_sess.query(News).filter(News.is_private != True)
    return render_template("index.html", news=news[::-1])


@app.route("/main")
def main():
    return render_template("main_page.html")


@app.route('/avatar', methods=['POST', 'GET'])
def sample_file_upload():
    if request.method == 'GET':
        return render_template("avatar.html")
    elif request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
        if file:
            filename = str(current_user.id) + '.jpeg'
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(f'/profile/'{current_user.id})
        else:
            return "Ошибка при загрузке файла"


@app.route('/blog/new', methods=['GET', 'POST'])
@login_required
def add_news():
    form = NewsForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        news = News()
        news.title = form.title.data
        news.content = form.content.data
        news.is_private = form.is_private.data
        news.tag = form.tag.data
        current_user.news.append(news)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect('/blog')
    return render_template('news.html', title='Добавление новости',
                           form=form)

@app.route('/blog/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_news(id):
    form = NewsForm()
    if request.method == "GET":
        db_sess = db_session.create_session()
        if current_user.rank >= admins:
            news = db_sess.query(News).filter(News.id == id).first()
        else:
            news = db_sess.query(News).filter(News.id == id,
                                              News.user == current_user
                                              ).first()
        if news:
            form.title.data = news.title
            form.content.data = news.content
            form.is_private.data = news.is_private
        else:
            abort(404)
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        if current_user.rank >= admins:
            news = db_sess.query(News).filter(News.id == id).first()
        else:
            news = db_sess.query(News).filter(News.id == id,
                                              News.user == current_user
                                              ).first()
        if news:
            news.title = form.title.data
            news.content = form.content.data
            news.is_private = form.is_private.data
            db_sess.commit()
            return redirect('/blog')
        else:
            abort(404)
    return render_template('news.html',
                           title='Редактирование новости',
                           form=form
                           )


@app.route('/blog_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def news_delete(id):
    db_sess = db_session.create_session()
    if current_user.rank >= admins:
        news = db_sess.query(News).filter(News.id == id).first()
    else:
        news = db_sess.query(News).filter(News.id == id,
                                          News.user == current_user
                                          ).first()
    if news:
        db_sess.delete(news)
        db_sess.commit()
    else:
        abort(404)
    return redirect('/blog')

@app.route('/com_delete/<int:id>', methods=['GET', 'POST'])
@login_required
def com_delete(id):
    db_sess = db_session.create_session()
    if current_user.rank >= admins:
        com = db_sess.query(Com).filter(Com.id == id).first()
    else:
        com = db_sess.query(Com).filter(Com.id == id,
                                          Com.user == current_user
                                          ).first()
    if com:
        db_sess.delete(com)
        db_sess.commit()
    else:
        abort(404)
    return '<script>document.location.href = document.referrer</script>'


@app.route('/blog/<int:id>', methods=['GET', 'POST'])
def news_item(id):
    form = ComForm()
    db_sess = db_session.create_session()
    if form.validate_on_submit():
        com = Com()
        com.content = form.content.data
        com.news_id = id
        current_user.com.append(com)
        db_sess.merge(current_user)
        db_sess.commit()
        return redirect(f'/blog/{id}')
    news = db_sess.query(News).filter(News.id == id).first()
    com = db_sess.query(Com).filter(Com.news_id == id)
    return render_template('blog_i.html', title='Блог',
                           form=form, news=news, com=ComSorter(com, id), status=True, admin=admins, sys=system)


@app.route('/register', methods=['GET', 'POST'])
def reqister():
    form = RegisterForm()
    if form.validate_on_submit():
        if form.password.data != form.password_again.data:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Пароли не совпадают")
        elif len(form.password.data) < 3:
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Ненадежный пароль")
        db_sess = db_session.create_session()
        if db_sess.query(User).filter(User.email == form.email.data).first():
            return render_template('register.html', title='Регистрация',
                                   form=form,
                                   message="Такой пользователь уже есть")
        user = User(
            name=form.name.data,
            email=form.email.data,
            about=form.about.data,
        )
        user.set_password(form.password.data)
        db_sess.add(user)
        db_sess.commit()
        return redirect('/login')
    return render_template('register.html', title='Регистрация', form=form)


@app.route('/profile/<int:owner>')
def view(owner):
    info = downoload_users_datum(owner)
    return render_template('profile.html', user=current_user, status=False, access=info, admin=admins, sys=system)


@app.route('/open_chat/<id>', methods=['GET', 'POST'])
def chat(id):
    res = existing_room(int(current_user.id), int(id))
    if res is None:
        db_sess = db_session.create_session()
        r = Room()
        r.code = room_code = generate_room_code(6)
        r.members = f"{max(int(current_user.id), int(id))}:{min(int(current_user.id), int(id))}"
        db_sess.add(r)
        db_sess.commit()
    else:
        room_code = res[0]
    session['room'] = room_code
    session['rec'] = id
    other_user = downoload_users_datum(id, False)
    m = import_history_of_chat(room_code)
    return render_template('chat_page.html', user=current_user, other=other_user, room=room_code,
                           messages=m, status=True)


@app.route('/rules')  # todo rules of communication
def rule():
    return render_template('rules.html', status=True)


@app.errorhandler(404)
def not_found():
    return make_response(jsonify({'error': 'Not found'}), 404)


@app.errorhandler(400)
def bad_request(_):
    return make_response(jsonify({'error': 'Bad Request'}), 400)


@socketio.on('connect')
def handle_connect():
    room = session.get('room')
    join_room(room)


@socketio.on('message')
def handle_message(payload):
    room = session.get('room')
    rec = session.get('rec')
    message = {
        "sender": current_user.name,
        "message": payload["message"],
        "date": payload['date']
    }
    send(message, to=room)
    msg = Message()
    msg.author = current_user.id
    msg.recipient = rec
    msg.message = payload["message"]
    msg.room_code = room
    db_sess = db_session.create_session()
    db_sess.add(msg)
    db_sess.commit()


@socketio.on('disconnect')
def handle_disconnect():
    room = session.get("room")
    leave_room(room)


def main():
    db_session.global_init("db/blogs.db")
    app.register_blueprint(news_api.blueprint)
    # для списка объектов
    api.add_resource(news_resources.NewsListResource, '/api/v2/news')

    # для одного объекта
    api.add_resource(news_resources.NewsResource, '/api/v2/news/<int:news_id>')
    app.run()


if __name__ == '__main__':
    main()
