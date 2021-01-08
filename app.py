from flask import Flask, g, request, jsonify
from database import get_db
from functools import wraps

app = Flask(__name__)

api_username = 'admin'
api_password = '123'


def authentication(route):
    @wraps(route)
    def wrapper(*args, **kwargs):
        if request.authorization.username == api_username and request.authorization.password == api_password:
            return route(*args, **kwargs)
        return jsonify({'message': 'Authentication failed'}, 403)

    return wrapper


@app.teardown_appcontext
def close_db(error):
    if hasattr(g, 'sqlite3'):
        g.sqlite3.close()


@app.route('/member', methods=['GET'])
def get_members():
    db = get_db()
    cur = db.cursor()
    cur.execute("""SELECT * FROM members""")
    members = cur.fetchall()

    return jsonify(
        {
            'members': [{'id': x['id'],
                         'name': x['name'],
                         'email': x['email'],
                         'level': x['level']}
                        for x in members]
        })


@app.route('/member/<int:member_id>', methods=['GET'])
@authentication
def get_member(member_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("""SELECT id, name, email, level
                    FROM members
                    WHERE id=? """, (member_id, ))
    member = cur.fetchone()

    return jsonify(
        {
            'member':
            {
                'id': member['id'],
                'name': member['name'],
                'email': member['email'],
                'level': member['level']
            }
        }
    )


@app.route('/member', methods=['POST'])
@authentication
def add_member():
    new_member_data = request.get_json()
    name = new_member_data['name']
    email = new_member_data['email']
    level = new_member_data['level']
    db = get_db()
    cur = db.cursor()
    cur.execute("""INSERT INTO members 
                    (name, email, level) 
                    VALUES (?, ?, ?)""",
                (name, email, level))
    db.commit()

    cur.execute("""SELECT id, name, email, level 
                    FROM members
                    WHERE name = ? """,
                (name, ))
    added_member_data = cur.fetchone()

    return jsonify(
        {
            'added_member':
            {
                'id': added_member_data['id'],
                'name': added_member_data['name'],
                'email': added_member_data['email'],
                'level': added_member_data['level']
            }
        }
    )


@app.route('/member/<int:member_id>', methods=['PUT', 'PATCH'])
@authentication
def edit_member(member_id):
    member_data = request.get_json()
    member_name = member_data['name']
    member_email = member_data['email']
    member_level = member_data['level']

    db = get_db()
    cur = db.cursor()
    cur.execute("""UPDATE members
                    SET name = ?, email = ?, level = ? 
                    WHERE id = ?""",
                (member_name, member_email, member_level, member_id))
    db.commit()
    cur.execute("""SELECT * FROM members WHERE id = ?""", (member_id, ))
    updated_member_data = cur.fetchone()
    return jsonify(
        {
            'updated_member':
                {
                    'id': updated_member_data['id'],
                    'name': updated_member_data['name'],
                    'email': updated_member_data['email'],
                    'level': updated_member_data['level']
                }
        }
    )


@app.route('/member/<int:member_id>', methods=['DELETE'])
@authentication
def delete_member(member_id):
    db = get_db()
    cur = db.cursor()
    cur.execute("""SELECT id, name, email, level 
                    FROM members 
                    WHERE id = ?""",
                (member_id, ))
    member_data = cur.fetchone()

    cur.execute("""DELETE FROM members WHERE id = ?""", (member_id, ))
    db.commit()

    return jsonify(
        {
            'deleted_member':
                {
                    'id': member_data['id'],
                    'name': member_data['name'],
                    'email': member_data['email'],
                    'level': member_data['level']
                }
        }
    )


if __name__ == '__main__':
    app.run()