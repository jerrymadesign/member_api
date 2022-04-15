import json
from flask import Flask, g, request, jsonify
from dbHelper import get_db
from functools import wraps

app = Flask(__name__)

API_USERNAME = "admin"
API_PASSWORD = "password"

@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'postgre_db_cur'):
        g.postgres_db_cur.close()

    if hasattr(g, 'postgres_db_conn'):
        g.postgres_db_conn.close()

def protected(f):
    @wraps(f)
    def wrapper(*args, **kwargs):
        auth = request.authorization
        if auth and auth.username == API_USERNAME and auth.password == API_PASSWORD:
            return f(*args, **kwargs)
        else:
            return jsonify({'message': "authentication failed."}), 403
    return wrapper

@app.route('/members', methods=['GET'])
@protected
def get_members():
    db = get_db()
    member_cur = db.execute('select id, name, email, level from members')
    members = member_cur.fetchall()

    json_member_list = []
    for member in members:
        dic = {}
        dic['id'] = member['id']
        dic['name'] = member['name']
        dic['email'] = member['email']
        dic['level'] = member['level']

        json_member_list.append(dic)
        
    return jsonify({'members': json_member_list})

@app.route('/member/<int:member_id>', methods=['GET'])
@protected
def get_member(member_id):
    db = get_db()
    member_cur = db.execute('select id, name, email, level from members where id = ?', [member_id])
    member = member_cur.fetchone()

    return jsonify({'member': {'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']}})

@app.route('/member', methods=['POST'])
@protected
def add_member():
    name = request.json['name']
    email = request.json['email']
    level = request.json['level']

    db = get_db()
    db.execute('insert into members (name, email, level) values (?, ?, ?)', [name, email, level])
    db.commit()

    member_cur = db.execute('select id, name, email, level from members where name = ?', [name])
    new_member = member_cur.fetchone()

    return jsonify({'member': {'id': new_member['id'], 'name': new_member['name'], 'email': new_member['email'], 'level': new_member['level']}})

@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
@protected
def edit_member(member_id):
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']

    db = get_db()

    db.execute('update members set name = ?, email = ?, level = ? where id = ?', [name, email, level, member_id])
    db.commit()

    cur = db.execute('select id, name, email, level from members where id = ?', [member_id])
    member = cur.fetchone()

    return jsonify({'member': {'id': member['id'], 'name': member['name'], 'email': member['email'], 'level': member['level']}})

@app.route('/member/<int:member_id>', methods=['DELETE'])
@protected
def delete_member(member_id):
    db = get_db()
    db.execute('delete from members where id = ?', [member_id])
    db.commit()

    return jsonify({'message': "The member has been deleted."})

if __name__ == '__main__':
    app.run(debug=True)