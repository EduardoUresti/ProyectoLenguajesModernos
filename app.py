from flask import Flask, render_template, request, redirect, url_for, session
import mysql.connector
from flask_bcrypt import Bcrypt

app = Flask(__name__)
app.secret_key = 'supersecretkey'
bcrypt = Bcrypt(app)

# Conexión a la base de datos
conexion = mysql.connector.connect(
    host="localhost",
    user="root",
    password="password",
    database="tienda"
)

cursor = conexion.cursor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        contraseña = request.form['contraseña']
        
        cursor.execute("SELECT * FROM usuarios WHERE nombre_usuario = %s", (nombre_usuario,))
        usuario = cursor.fetchone()
        
        if usuario and bcrypt.check_password_hash(usuario[2], contraseña):
            session['usuario'] = nombre_usuario
            return redirect(url_for('inventario'))
        else:
            return "Nombre de usuario o contraseña incorrectos"
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        nombre_usuario = request.form['nombre_usuario']
        contraseña = bcrypt.generate_password_hash(request.form['contraseña']).decode('utf-8')
        
        cursor.execute("INSERT INTO usuarios (nombre_usuario, contraseña) VALUES (%s, %s)", (nombre_usuario, contraseña))
        conexion.commit()
        
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/inventario')
def inventario():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    cursor.execute("SELECT * FROM inventario")
    productos = cursor.fetchall()
    
    return render_template('inventario.html', productos=productos)

@app.route('/agregar', methods=['GET', 'POST'])
def agregar():
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        nombre_producto = request.form['nombre_producto']
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        
        cursor.execute("INSERT INTO inventario (nombre_producto, cantidad, precio) VALUES (%s, %s, %s)",
                       (nombre_producto, cantidad, precio))
        conexion.commit()
        
        return redirect(url_for('inventario'))
    
    return render_template('agregar.html')

@app.route('/actualizar/<int:id>', methods=['GET', 'POST'])
def actualizar(id):
    if 'usuario' not in session:
        return redirect(url_for('login'))
    
    cursor.execute("SELECT * FROM inventario WHERE id = %s", (id,))
    producto = cursor.fetchone()
    
    if request.method == 'POST':
        cantidad = int(request.form['cantidad'])
        precio = float(request.form['precio'])
        
        cursor.execute("UPDATE inventario SET cantidad = %s, precio = %s WHERE id = %s", (cantidad, precio, id))
        conexion.commit()
        
        return redirect(url_for('inventario'))
    
    return render_template('actualizar.html', producto=producto)

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)