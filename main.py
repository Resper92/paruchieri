from flask import Flask, jsonify, request, session
from werkzeug.security import generate_password_hash, check_password_hash
from conectdb import db_session, init_db
import model

app = Flask(__name__)
app.secret_key = 'dasdasdasdadljkfgsdd15486486'

@app.route('/register', methods=['POST'])
def register():
    username = request.form.get('username')
    password = request.form.get('password')
    role = request.form.get('role')

    
    if not username or not password:
        return jsonify({'status': 'error', 'message': 'Username e password obbligatori'}), 400

    hashed_password = generate_password_hash(password)

    # 3. Salva l'utente
    user = model.User(email=username, password_hash=hashed_password, role=role)
    db_session.add(user)
    db_session.commit()
    db_session.close()

    return jsonify({'status': 'success', 'message': 'Registration successful!'}), 200


@app.route('/login', methods=['POST'])
def login():  # Corretto il nome della funzione (era loghin)
    username = request.form.get('username')
    password = request.form.get('password')

    # 1. Cerca l'utente nel DB solo tramite email/username
    user = model.User.query.filter_by(email=username).first()

    # 2. Verifica se l'utente esiste E se la password corrisponde all'hash
    if not user or not check_password_hash(user.password_hash, password):
        return jsonify({'status': 'error', 'message': 'Invalid username or password'}), 401

    # 3. Salva in sessione SOLO dati non sensibili (es. username o id)
    session['username'] = username
    session['role'] = user.role

    return jsonify({'status': 'success', 'message': 'Login successful!'}), 200



if __name__ == '__main__':
    init_db()  # Inizializza il DB all'avvio
    app.run(debug=True)