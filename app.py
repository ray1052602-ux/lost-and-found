from flask import Flask, render_template, request, redirect, url_for, send_from_directory, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
import os
from werkzeug.utils import secure_filename
from sqlalchemy import or_

basedir = os.path.abspath(os.path.dirname(__file__))

UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)

app.config['SECRET_KEY'] = 'a-very-secret-key-that-you-should-change'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'site.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)

login_manager.login_view = 'login'
login_manager.login_message = '請先登入以訪問此頁面。'
login_manager.login_message_category = 'info'


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(60), nullable=False)
    items = db.relationship('Item', backref='author', lazy=True)

    def set_password(self, password):
        self.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Item(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    item_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    location = db.Column(db.String(200), nullable=False)
    image_filename = db.Column(db.String(200), nullable=True)
    author_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        return f'<Item {self.item_name}>'


@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


def allowed_file(filename):
    return '.' in filename and \
        filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/', methods=['GET', 'POST'])
@login_required
def submit_item():
    if request.method == 'POST':
        item_name = request.form.get('item_name')
        description = request.form.get('description')
        location = request.form.get('location')
        image_filename = None

        if 'item_image' in request.files:
            file = request.files['item_image']
            if file and file.filename != '' and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                image_filename = filename

        new_item = Item(
            item_name=item_name,
            description=description,
            location=location,
            image_filename=image_filename,
            author_id=current_user.id
        )

        db.session.add(new_item)
        db.session.commit()

        flash(f'物品「{item_name}」已成功登錄！', 'success')
        return redirect(url_for('list_items'))

    return render_template('submit.html')


# --- 🔽🔽🔽 這是「主要修改」的地方 🔽🔽🔽 ---
@app.route('/list')
def list_items():
    search_query = request.args.get('query')

    # 1. 預設清單為「空」
    all_items = []

    # 2. 只有在 search_query 存在 (使用者有輸入) 時，才去搜尋
    if search_query:
        search_term = f"%{search_query}%"
        all_items = Item.query.filter(
            or_(
                Item.item_name.ilike(search_term),
                Item.description.ilike(search_term),
                Item.location.ilike(search_term)
            )
        ).order_by(Item.id.desc()).all()

    # 3. 如果 search_query 是 None 或空字串，all_items 會是 []
    return render_template('list.html', items=all_items, search_query=search_query)


# --- 🔼🔼🔼 修改結束 🔼🔼🔼 ---


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('list_items'))

    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')

        user_exists = User.query.filter_by(email=email).first()
        if user_exists:
            flash('這個 Email 已經被註冊過了。', 'danger')
            return redirect(url_for('register'))

        user_exists = User.query.filter_by(username=username).first()
        if user_exists:
            flash('這個使用者名稱已經被註冊過了。', 'danger')
            return redirect(url_for('register'))

        new_user = User(username=username, email=email)
        new_user.set_password(password)

        db.session.add(new_user)
        db.session.commit()

        flash(f'帳號 {username} 註冊成功！請登入。', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('list_items'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first()

        if user and user.check_password(password):
            login_user(user, remember=True)
            flash('登入成功！', 'success')

            next_page = request.args.get('next')
            return redirect(next_page or url_for('list_items'))
        else:
            flash('登入失敗。請檢查 Email 和密碼。', 'danger')
            return redirect(url_for('login'))

    return render_template('login.html')


@app.route('/logout')
def logout():
    logout_user()
    flash('你已經成功登出。', 'info')
    return redirect(url_for('login'))


@app.route('/uploads/<filename>')
def serve_upload(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)