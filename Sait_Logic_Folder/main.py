import flask
import sqlite3
import json
import os
from test_system import Pascal_Code_Checker as PCC

app = flask.Flask(__name__, template_folder='../templates', static_folder='../static')
app.secret_key = '61646d696e7363686f6f6c31353370617363616c746573747361697466726f6d6e61696c'

def Data_Base_Connection():
    current_directory = os.path.dirname(os.path.abspath(__file__))
    Data_Base_path = os.path.abspath(os.path.join(current_directory, '..', 'Data_Folder', 'database.db'))
    connection = sqlite3.connect(Data_Base_path, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection

def tasks_num() -> int:
    Data_Base = Data_Base_Connection()
    count = Data_Base.execute('SELECT COUNT(*) FROM tasks').fetchone()[0]
    Data_Base.close()
    return count

@app.route('/', methods=['GET', 'POST'])
@app.route('/login', methods=['GET', 'POST'])
def login():
    if flask.request.method == 'POST':
        user_login = flask.request.form.get('login')
        user_password = flask.request.form.get('password')

        user_login_r = flask.request.form.get('login-r')
        user_password_r = flask.request.form.get('password-r')
        user_name_r = flask.request.form.get('name-r')
        user_surname_r = flask.request.form.get('surname-r') or ''
        if user_login and user_password:
            Data_Base = Data_Base_Connection()
            user = Data_Base.execute('SELECT * FROM users WHERE login = ? AND password = ?', (user_login, user_password)).fetchone()
            Data_Base.close()
            if user:
                flask.session['login'] = user['login']
                flask.session['password'] = user['password']
                flask.session['name'] = user['name']
                flask.session['surname'] = user['surname']
                flask.session['task-complated'] = user['task_complated']

                return flask.redirect(flask.url_for('dashboard'))
            
            return flask.render_template('login.html', error='Неверный логин или пароль!')
        elif user_login_r and user_password_r and user_name_r:
            try:
                Data_Base = Data_Base_Connection()
                Data_Base.execute('''
                    INSERT INTO users (login, password, name, surname)
                    VALUES (?, ?, ?, ?)
                ''', (user_login_r, user_password_r, user_name_r, user_surname_r))
                Data_Base.commit()
                Data_Base.close()

                flask.session['login'] = user_login_r
                flask.session['password'] = user_password_r
                flask.session['name'] = user_name_r
                flask.session['surname'] = user_surname_r
                flask.session['task-complated'] = 0

                return flask.redirect(flask.url_for('dashboard'))
            
            except sqlite3.IntegrityError:
                return flask.render_template('login.html', error='Данный логин уже занят!')

    return flask.render_template('login.html')


@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'login' not in flask.session: 
        return flask.redirect(flask.url_for('login'))
    
    Data_Base = Data_Base_Connection()
    tasks = Data_Base.execute('''
        SELECT t.id, t.title, COALESCE(ut.task_status, 'f') AS task_status 
        FROM tasks t LEFT JOIN user_tasks ut ON t.id = ut.task_id AND ut.login = ?
    ''', (flask.session['login'],)).fetchall()

    info = Data_Base.execute('''
        SELECT task_complated, name, surname FROM users
        WHERE login = ?
    ''', (flask.session['login'],)).fetchone()

    Data_Base.close()
     
    return flask.render_template('dashboard.html', tasks=tasks, info=info, count=tasks_num(),**flask.session)


@app.route('/get_task/<int:id>', methods=['GET'])
def give_task_to_js(id):
    if 'login' not in flask.session: 
        return flask.jsonify({'status': 401, 'message': 'Сессия истекла!'})
    if id <= 0 or id > tasks_num():
        return flask.jsonify({'status': False, 'message': 'Неверный ID задачи!'}), 404
    else:
        try:
            Data_Base = Data_Base_Connection()
            task = Data_Base.execute('SELECT title, text FROM tasks WHERE id = ?', (id,)).fetchone()
            Data_Base.close()
            if task is None:
                return flask.jsonify({'status': False, 'message': 'Задача не найдена!'}), 404
            return flask.jsonify({'title': task[0], 'text': task[1]})
        except Exception as e:
            print(f'!!! ОШИБКА ПОЛУЧЕНИЯ ЗАДАЧИ: {e} !!!')
            return flask.jsonify({'status': False, 'message': 'Внутренняя ошибка сервера. Попробуйте позже!'}), 500


@app.route('/check_task/<int:id>', methods=['POST'])
def check_code(id):
    if 'login' not in flask.session: 
        return flask.jsonify({'status': 401, 'message': 'Сессия истекла!', 'serverfault': False})
    if id <= 0 or id > tasks_num():
        return flask.jsonify({'status': False, 'message': 'Неверный ID задачи!', 'serverfault': False}), 404
    data = flask.request.get_json()
    if not data or 'code' not in data:
        return flask.jsonify({'status': False, 'message': 'Напишите код перед отправкой!', 'serverfault': False}), 400

    user_code = data['code']
    user_login = flask.session.get('login')
    try:
        Data_Base = Data_Base_Connection()
        task = Data_Base.execute('SELECT inputs, outputs FROM tasks WHERE id = ?', (id,)).fetchone()
        Data_Base.close()
        if not task:
            return flask.jsonify({'status': False, 'message': 'Задача не найдена!', 'serverfault': False}), 404
        inputs, outputs = json.loads(task['inputs']), json.loads(task['outputs'])
        success, message, error = PCC(user_code, inputs, outputs, user_login)
        error = False if error is None else error
        status = 't' if success else 'f'
        Data_Base = Data_Base_Connection()
        Data_Base.execute('''
            INSERT OR REPLACE INTO user_tasks (login, task_id, task_status)
            VALUES (?, ?, ?)
        ''', (user_login, id, status))
        if success:
            complated_tasks = Data_Base.execute('''
            SELECT COUNT(*) FROM user_tasks WHERE login = ? AND task_status = 't'
            ''', (user_login,)).fetchone()[0]
            Data_Base.execute('UPDATE users SET task_complated = ? WHERE login = ? ', (complated_tasks, user_login))
            flask.session['task-complated'] = complated_tasks
        Data_Base.commit()
        Data_Base.close()
        return flask.jsonify({'status': success, 'message': message, 'serverfault': error})
    except Exception as e:
        print(f'!!! ОШИБКА ПРОВЕРКИ КОДА: {e} !!!')
        return flask.jsonify({'status': False, 'message': f'Внутренняя ошибка сервера. Попробуйте позже!', 'serverfault': False})


@app.route('/admin/route/createtask', methods=['GET', 'POST'])
def admin_func():
    if 'login' not in flask.session or flask.session['login'] != 'adminaccount':
        return flask.render_template('login.html', error='Сессия истекла!')

    if flask.request.method == 'POST':
        title = flask.request.form.get('title')
        text = flask.request.form.get('if')
        inputs = flask.request.form.get('inputs')
        outputs = flask.request.form.get('outputs')

        if title and text and inputs and outputs:
            try:
                json_inputs = json.dumps([i.strip() for i in inputs.split('\n') if i.strip()])
                json_outputs = json.dumps([o.strip() for o in outputs.split('\n') if o.strip()])

                Data_Base = Data_Base_Connection()
                Data_Base.execute('''
                    INSERT INTO tasks (title, text, inputs, outputs)
                    VALUES (?, ?, ?, ?)
                ''', (title, text, json_inputs, json_outputs))
                Data_Base.commit()
                Data_Base.close()

                print('ЗАДАЧА ДОБАВЛЕНА')
                return 'удачно'
            except Exception as error:
                print('ОШИБКА:', error)
                return 'ошибка'
    return flask.render_template('admin.html')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)