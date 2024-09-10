import secrets, time, datetime
from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for, abort, session, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler
from icmplib import ping
from waitress import serve

#Initialize the Flask app
flaskApp = Flask(__name__)

scheduler = APScheduler()
scheduler.init_app(flaskApp)
scheduler.start()

@scheduler.task('interval', id='monitor_servers', seconds=60)  # Initial interval
def monitor_servers_task():
    with flaskApp.app_context():
        config = AppConfig.query.first()
        if not config:  # Handle case where config doesn't exist yet
            config = AppConfig(monitoring_interval=60)
            db.session.add(config)
            db.session.commit()

        scheduler.modify_job('monitor_servers', trigger='interval', seconds=config.monitoring_interval)
        monitor_servers() 


def monitor_servers():
    servers = Hosts.query.all()
    for server in servers:
        host = ping(server.ip, count=1, timeout=2)
        if host.is_alive:
            server.state = True
            server.trip_time = host.avg_rtt
            server.last_active = datetime.datetime.now()
        else:
            server.state = False
            server.trip_time = None
        log_entry = ServerStatusLog(server_id=server.id, is_online=server.state, trip_time=server.trip_time)
        db.session.add(log_entry)
        db.session.commit()

login_manager = LoginManager()
login_manager.init_app(flaskApp)
login_manager.login_view = 'login'

flaskApp.config['SECRET_KEY'] = secrets.token_hex(32)
flaskApp.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # Using SQLite as the database
db = SQLAlchemy(flaskApp)
bcrypt = Bcrypt(flaskApp)

class AppConfig(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    monitoring_interval = db.Column(db.Integer, default=60)


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True)
    password_hash = db.Column(db.String(128))
    is_admin = db.Column(db.Boolean, default=False)
    last_active = db.Column(db.DateTime)

    def is_active(self):
        return True

class Hosts(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64))
    ip = db.Column(db.String(64))
    trip_time = db.Column(db.Float)
    state = db.Column(db.Boolean, default=None)
    last_active = db.Column(db.DateTime)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'ip': self.ip,
            'state': self.state if self.state != None else 'None',
            'trip_time': round(self.trip_time, 1) if self.trip_time is not None else 'Unknown',
            'last_active': self.last_active.strftime('%Y-%m-%d %H:%M:%S') if self.last_active else 'Unknown'
        }

class ServerStatusLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('hosts.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.datetime.now())
    is_online = db.Column(db.Boolean)
    trip_time = db.Column(db.Float)

    server = db.relationship('Hosts', backref=db.backref('status_logs', lazy=True))

def __repr__(self):
  return f'<User {self.username}>'

@flaskApp.before_request
def update_last_active():
    if current_user.is_authenticated:
        current_user.last_active = datetime.datetime.now()
        db.session.commit()

@login_manager.user_loader
def load_user(user_id):
  return db.session.get(User, user_id)

@flaskApp.route('/')
def index():
    return redirect(url_for('display_servers'))

@flaskApp.route('/servers')
def display_servers():
    servers = Hosts.query.all()
    config = AppConfig.query.first()
    return render_template('servers.html', servers=servers, config=config)

@flaskApp.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    return redirect('/')

@flaskApp.route('/login', methods=['GET', 'POST'])
def login():
    if 'user_id' in session:
        # User is already logged in
        return redirect('/')  # Redirect to admin dashboard
    elif request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password_hash, password):
            session['user_id'] = user.id
            login_user(user)
            return redirect('/')
        else:
            error = 'Invalid username or password'
            return render_template('admin/login.html', error=error)
    else:
        return render_template('admin/login.html')

@flaskApp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        confirmPassword = request.form['confirm_password']

        if password != confirmPassword:
            return render_template('admin/registeration.html', error='Passwords do not match')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username,password_hash=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()  # Rollback the session to prevent inconsistencies
            return render_template('admin/registeration.html', error='Username already taken')
        return redirect('/')
    return render_template('admin/registeration.html')

@flaskApp.route('/server_updates')
def server_updates():
    servers = Hosts.query.all()
    return jsonify(servers=[server.to_dict() for server in servers])

@flaskApp.route('/add_host', methods=['GET', 'POST'])
def add_host():
    if request.method == 'POST':
        ip = request.form.get('ip')
        name = request.form.get('name')
        if name:  # Basic validation: check if the name is provided
            new_host = Hosts(name=name, ip=ip)
            db.session.add(new_host)
            db.session.commit()
            return redirect(url_for('display_servers'))
    return render_template('add_host.html')

@flaskApp.route('/change_interval', methods=['POST'])
def change_interval():
    new_interval = int(request.form.get('interval'))
    config = AppConfig.query.first()
    config.monitoring_interval = new_interval
    db.session.commit()
    return redirect(url_for('display_servers'))

@flaskApp.route('/delete/server/<int:id>')
def delete_server(id):
    host = Hosts.query.get_or_404(id)
    ServerStatusLog.query.filter_by(server_id=host.id).delete()
    db.session.delete(host)
    db.session.commit()
    return redirect(url_for('display_servers'))

if __name__ == '__main__':
    try:
        with flaskApp.app_context():
            db.create_all()
    except Exception as e:
        print(f'Failed to create local databse: {e}')
    try:
        serve(flaskApp, host="0.0.0.0", port=8080, threads=2)
    except Exception as e:
        print(f"Flask failed to be served: {e}")