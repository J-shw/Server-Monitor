import secrets, requests
from datetime import date, datetime, timedelta
from requests.exceptions import Timeout
from flask import Flask, render_template, jsonify, request, send_file, redirect, url_for, abort, session, Response
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import IntegrityError
from flask_login import UserMixin, LoginManager, login_user, logout_user, login_required, current_user
from flask_bcrypt import Bcrypt
from flask_apscheduler import APScheduler
from apscheduler.schedulers.background import BackgroundScheduler
from icmplib import ping
from waitress import serve

#Initialize the Flask app
flaskApp = Flask(__name__)

scheduler = APScheduler()
scheduler.init_app(flaskApp)
scheduler.start()

background_scheduler = BackgroundScheduler()

def delete_old_logs():
    with db.engine.begin() as connection:  # Ensure proper transaction handling
        thirty_days_ago = datetime.now() - timedelta(days=30)
        connection.execute(
            ServerStatusLog.__table__.delete().where(ServerStatusLog.timestamp < thirty_days_ago)
        )

def monitor_servers_task():
    with flaskApp.app_context():
        config = AppConfig.query.first()
        background_scheduler.reschedule_job('monitor_servers', trigger='interval', seconds=config.monitoring_interval)
        
        servers = Hosts.query.all()
        for server in servers:
            try:
                if server.check_type == 'ping':
                    host = ping(server.address, count=1, timeout=2)
                    if host.is_alive:
                        server.state = True
                        server.trip_time = host.avg_rtt
                        server.last_active = datetime.now()
                    else:
                        server.state = False
                        server.trip_time = None
                    log_entry = ServerStatusLog(server_id=server.id, state=server.state, trip_time=server.trip_time)
                elif server.check_type == 'fetch':
                    response_code = 0
                    try:
                        response = requests.get(f'{server.scheme}{server.address}', timeout=2)

                        response_code = response.status_code
                        if  response_code == 200:
                            server.state = True
                            server.last_active = datetime.now()
                        else:
                            server.state = False
                    except Timeout:
                        response_code = 408
                        server.state = False

                    server.response_code = response_code
                    log_entry = ServerStatusLog(server_id=server.id, state=server.state, response_code=server.response_code)

                db.session.add(log_entry)
                db.session.commit()
            except Exception as e:
                print(f'failed to check {server.address} - {e}')

background_scheduler.add_job(delete_old_logs, 'cron', id='logs_cleanup', hour=0, minute=0)  # Run daily at midnight
background_scheduler.add_job(monitor_servers_task, 'interval', id='monitor_servers', seconds=0)  # Initial interval
background_scheduler.start()
    
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
    address = db.Column(db.String(64))
    trip_time = db.Column(db.Float)
    response_code = db.Column(db.Integer)
    state = db.Column(db.Boolean, default=None)
    last_active = db.Column(db.DateTime)
    check_type = db.Column(db.String(64)) # Can be 'ping' or 'fetch'
    scheme = db.Column(db.String(64)) # https:// | http:// etc..

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'address': self.address,
            'state': self.state if self.state != None else 'None',
            'trip_time': round(self.trip_time, 1) if self.trip_time is not None else 'Unknown',
            'response_code':self.response_code if self.response_code is not None else 'Unknown',
            'last_active': self.last_active.strftime('%Y-%m-%d %H:%M:%S') if self.last_active else 'Unknown',
            'check_type': self.check_type.capitalize(),
            'scheme': self.scheme
        }

class ServerStatusLog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server_id = db.Column(db.Integer, db.ForeignKey('hosts.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=lambda: datetime.now())
    unix_timestamp = db.Column(db.Float, default=lambda: datetime.now().timestamp())
    state = db.Column(db.Boolean)
    trip_time = db.Column(db.Float)
    response_code = db.Column(db.Integer)

    def to_dict(self):
        return {
            'id': self.id,
            'server_id': self.server_id,
            'timestamp': self.timestamp,
            'unix_timestamp': self.unix_timestamp,
            'state': self.state,
            'trip_time': round(self.trip_time, 1) if self.trip_time is not None else 0,
            'response_code':self.response_code
        }

    server = db.relationship('Hosts', backref=db.backref('status_logs', lazy=True))

def __repr__(self):
  return f'<User {self.username}>'

@flaskApp.before_request
def update_last_active():
    if current_user.is_authenticated:
        current_user.last_active = datetime.now()
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
@login_required
def register():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        confirmPassword = request.form['confirm_password']

        if password != confirmPassword:
            return render_template('admin/credentials.html', error='Passwords do not match', action='/register', title='Registration', page_title='Register User')

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        new_user = User(username=username,password_hash=hashed_password)
        try:
            db.session.add(new_user)
            db.session.commit()
        except IntegrityError:
            db.session.rollback()  # Rollback the session to prevent inconsistencies
            return render_template('admin/credentials.html', error='Username already taken', action='/register', title='Registration', page_title='Register User')
        return redirect('/')
    return render_template('admin/credentials.html', action='/register', title='Registration', page_title='Register User')

@flaskApp.route('/server_updates')
def server_updates():
    servers = Hosts.query.all()
    return jsonify(servers=[server.to_dict() for server in servers])

@flaskApp.route('/get_server/<int:id>')
def get_server(id):
    server = Hosts.query.get_or_404(id)
    return jsonify(server=server.to_dict())

@flaskApp.route('/get_logs/<int:id>')
def get_logs(id):
    today_start = datetime.combine(date.today(), datetime.min.time())
    today_end = datetime.combine(date.today(), datetime.max.time())

    logs = ServerStatusLog.query.filter_by(server_id=id) \
                                .filter(ServerStatusLog.timestamp >= today_start) \
                                .filter(ServerStatusLog.timestamp <= today_end) \
                                .all()
    if not logs:
        # Handle the case where no logs are found (e.g., return a 404 or a custom message)
        return jsonify({"data": None, "message": "No server status logs found for the given server_id"}), 404
    
    log_dicts = [log.to_dict() for log in logs]
    return jsonify(data=log_dicts)

@flaskApp.route('/add_host', methods=['GET', 'POST'])
@login_required
def add_host():
    if request.method == 'POST':
        address = request.form.get('address')
        name = request.form.get('name')
        check_type = request.form.get('check_type')
        scheme = request.form.get('scheme')
        if name:  # Basic validation: check if the name is provided
            new_host = Hosts(name=name, address=address, check_type=check_type, scheme=scheme)
            db.session.add(new_host)
            db.session.commit()
            return redirect(url_for('display_servers'))
    return render_template('add_host.html')

@flaskApp.route('/update_host', methods=['POST'])
@login_required
def update_host():
    id = request.form.get('id')
    address = request.form.get('address')
    name = request.form.get('name')
    check_type = request.form.get('check_type')
    scheme = request.form.get('scheme')

    host_to_update = Hosts.query.get(id) 

    if host_to_update:
        host_to_update.address = address
        host_to_update.name = name
        host_to_update.check_type = check_type
        host_to_update.scheme = scheme

        db.session.commit()
        return redirect(url_for('display_servers'))
    return 'failed'

@flaskApp.route('/update_login', methods=['GET','POST'])
@login_required
def update_login():
    if request.method == 'POST':
        username = request.form['username'].lower()
        password = request.form['password']
        confirmPassword = request.form['confirm_password']

        if password != confirmPassword:
            return render_template('admin/credentials.html', error='Passwords do not match', action='/update_login', title='Update Login', page_title='Update User Credentials')

        current_user_id = current_user.id

        # Fetch the existing user record
        user_to_update = User.query.get(current_user_id) 

        if user_to_update:
            user_to_update.username = username
            user_to_update.password_hash = bcrypt.generate_password_hash(password).decode('utf-8')

            try:
                db.session.commit()
            except IntegrityError:
                db.session.rollback()  # Rollback the session to prevent inconsistencies
                return render_template('admin/credentials.html', error='Username already taken', action='/update_login', title='Update Login', page_title='Update User Credentials')
            return redirect('/')
    return render_template('admin/credentials.html', action='/update_login', title='Update Login', page_title='Update User Credentials')

@flaskApp.route('/change_interval', methods=['POST'])
@login_required
def change_interval():
    new_interval = int(request.form.get('interval'))
    config = AppConfig.query.first()
    config.monitoring_interval = new_interval
    db.session.commit()
    return redirect(url_for('display_servers'))

@flaskApp.route('/delete/server/<int:id>')
@login_required
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

            # DataBase initialise
            config = AppConfig.query.first()
            if not config:  # Handle case where config doesn't exist yet
                config = AppConfig(monitoring_interval=60)
                db.session.add(config)
                db.session.commit()
            
            user = User.query.first()
            if not user: # Creates default User admin
                hashed_password = bcrypt.generate_password_hash('admin').decode('utf-8')
                new_user = User(username='admin',password_hash=hashed_password)
                db.session.add(new_user)
                db.session.commit()

    except Exception as e:
        print(f'Failed to create local databse: {e}')
    try:
        serve(flaskApp, host="0.0.0.0", port=8080, threads=2)
    except Exception as e:
        print(f"Flask failed to be served: {e}")
