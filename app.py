from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models.base import session_factory  # Usamos session_factory
from models.model import Usuario, CancerData, ContactMessage
from werkzeug.security import generate_password_hash, check_password_hash
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, PasswordField, SubmitField, EmailField, SelectField
from wtforms.validators import DataRequired, Length, Email, EqualTo
import os
import traceback

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev_key_fallback")
app.config['WTF_CSRF_ENABLED'] = True

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Setup de LoginManager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth'

# WTForms for Auth
class AuthForm(FlaskForm):
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=50)])
    password = StringField('Contraseña', validators=[DataRequired(), Length(min=8)])
    login_submit = SubmitField('Iniciar Sesión')

class RegisterForm(FlaskForm):
    full_name = StringField('Nombre Completo', validators=[DataRequired(), Length(min=2, max=100)])
    nationality = SelectField('Nacionalidad', choices=[
        ('', 'Selecciona tu nacionalidad'),
        ('Argentina', 'Argentina'),
        ('Bolivia', 'Bolivia'),
        ('Brasil', 'Brasil'),
        ('Chile', 'Chile'),
        ('Colombia', 'Colombia'),
        ('Ecuador', 'Ecuador'),
        ('Paraguay', 'Paraguay'),
        ('Peru', 'Perú'),
        ('Uruguay', 'Uruguay'),
        ('Venezuela', 'Venezuela'),
        ('Otro', 'Otro')
    ], validators=[DataRequired()])
    email = EmailField('Correo Electrónico', validators=[DataRequired(), Email()])
    username = StringField('Usuario', validators=[DataRequired(), Length(min=4, max=50)])
    password = PasswordField('Contraseña', validators=[DataRequired(), Length(min=8)])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[DataRequired(), EqualTo('password', message='Las contraseñas deben coincidir')])
    register_submit = SubmitField('Registrarse')

@login_manager.user_loader
def load_user(user_id):
    session = session_factory()
    try:
        user = session.query(Usuario).get(int(user_id))
        return user
    finally:
        session.close()

# Teardown to clean up session after each request
@app.teardown_appcontext
def shutdown_session(exception=None):
    session = session_factory()
    if exception:
        session.rollback()
    session.close()

# Rutas del modo lector
@app.route('/')
def home():
    session = session_factory()
    try:
        return render_template('home.html')
    finally:
        session.close()

@app.route('/information')
def information():
    session = session_factory()
    try:
        return render_template('information.html')
    finally:
        session.close()

@app.route('/visualization')
def visualization():
    session = session_factory()
    try:
        return render_template('visualization.html')
    finally:
        session.close()

@app.route('/contact')
def contact():
    session = session_factory()
    try:
        return render_template('contact.html')
    finally:
        session.close()

@app.route('/submit_contact', methods=['POST'])
def submit_contact():
    session = session_factory()
    try:
        # Obtener datos (tanto JSON como form-data)
        if request.is_json:
            data = request.get_json()
        else:
            data = request.form

        # Validación
        if not all(data.get(field) for field in ['fullName', 'phoneNumber', 'email']):
            return jsonify({'success': False, 'message': 'Campos requeridos faltantes'}), 400

        # Crear mensaje
        new_message = ContactMessage(
            full_name=data['fullName'],
            phone_number=data['phoneNumber'],
            email=data['email'],
            message=data.get('message', '')
        )
        
        session.add(new_message)
        session.commit()
        
        return jsonify({'success': True, 'message': 'Mensaje enviado'})
        
    except Exception as e:
        session.rollback()
        # ¡Importante! Devuelve JSON incluso en errores
        return jsonify({
            'success': False,
            'message': f'Error del servidor: {str(e)}'
        }), 500
    finally:
        session.close()
# Rutas del modo administrador
@app.route('/auth', methods=['GET', 'POST'])
def auth():
    session = session_factory()
    try:
        login_form = AuthForm()
        register_form = RegisterForm()

        # Handle Login
        if login_form.login_submit.data and login_form.validate_on_submit():
            username = login_form.username.data
            password = login_form.password.data
            user = session.query(Usuario).filter_by(username=username).first()
            print(f"Checking user: {username}, found: {user is not None}")
            if user and check_password_hash(user.password, password):
                login_user(user)
                flash('Sesión iniciada exitosamente', 'success')
                return redirect(url_for('dashboard'))
            else:
                flash('Usuario o contraseña incorrectos', 'danger')
                return redirect(url_for('auth'))

        # Handle Registration
        if register_form.register_submit.data and register_form.validate_on_submit():
            username = register_form.username.data
            email = register_form.email.data
            if session.query(Usuario).filter_by(username=username).first():
                flash('El usuario ya existe', 'danger')
            elif session.query(Usuario).filter_by(email=email).first():
                flash('El correo ya está registrado', 'danger')
            else:
                new_user = Usuario(
                    username=username,
                    password=generate_password_hash(register_form.password.data),
                    full_name=register_form.full_name.data,
                    nationality=register_form.nationality.data,
                    email=email
                )
                session.add(new_user)
                session.commit()
                flash('Usuario creado exitosamente. Por favor, inicia sesión.', 'success')
                return redirect(url_for('auth'))

        return render_template('auth.html', login_form=login_form, register_form=register_form)
    except Exception as e:
        session.rollback()
        print(f"Error in auth route: {str(e)}")
        print(traceback.format_exc())
        flash(f'Error en la autenticación: {str(e)}', 'danger')
        return redirect(url_for('auth'))
    finally:
        session.close()

@app.route('/dashboard')
@login_required
def dashboard():
    session = session_factory()
    try:
        # Query the database with error handling
        cancer_data = session.query(CancerData).all()
        users = session.query(Usuario).all()
        messages = session.query(ContactMessage).all()

        # Debug prints
        print(f"Number of cancer records: {len(cancer_data)}")
        print(f"Number of users: {len(users)}")
        print(f"Number of messages: {len(messages)}")

        # If cancer_data is empty, let's log the first few records (if any)
        if cancer_data:
            print("First cancer record:", {
                "patient_id": cancer_data[0].patient_id,
                "age": cancer_data[0].age,
                "gender": cancer_data[0].gender,
                "region": cancer_data[0].region,
                "year": cancer_data[0].year
            })
        else:
            print("No cancer data retrieved from the database.")

        # Format cancer_data for the frontend
        cancer_data_formatted = []
        for record in cancer_data:
            cancer_data_formatted.append({
                "patient_id": record.patient_id,
                "age": record.age,
                "gender": record.gender,
                "region": record.region,
                "year": record.year,
                "genetic_risk": record.genetic_risk,
                "air_pollution": record.air_pollution,
                "alcohol_consumption": record.alcohol_consumption,
                "smoking": record.smoking,
                "obesity_level": record.obesity_level,
                "cancer_type": record.cancer_type,
                "cancer_stage": record.cancer_stage,
                "treatment_cost": record.treatment_cost,
                "survival_years": record.survival_years,
                "severity_score": record.severity_score
            })

        return render_template('dashboard.html', username=current_user.username, cancer_data=cancer_data_formatted, users=users, messages=messages)
    except Exception as e:
        session.rollback()
        print(f"Error in dashboard route: {str(e)}")
        print(traceback.format_exc())
        flash(f"Error al cargar los datos: {str(e)}", 'danger')
        return render_template('dashboard.html', username=current_user.username, cancer_data=[], users=[], messages=[])
    finally:
        session.close()

@app.route('/logout')
@login_required
def logout():
    session = session_factory()
    try:
        logout_user()
        return redirect(url_for('home'))
    except Exception as e:
        session.rollback()
        flash(f'Error al cerrar sesión: {str(e)}', 'danger')
        return redirect(url_for('home'))
    finally:
        session.close()

from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response

# Endpoints de API
@app.route('/api/cancer_data')
def api_cancer_data():
    session = session_factory()
    try:
        filters = {
            'region': request.args.get('region'),
            'year': request.args.get('year'),
            'cancer_type': request.args.get('cancer_type'),
            'gender': request.args.get('gender')
        }
        
        query = session.query(CancerData)
        
        # Aplicar filtros
        if filters['region']:
            query = query.filter(CancerData.region == filters['region'])
        if filters['year']:
            query = query.filter(CancerData.year == int(filters['year']))
        if filters['cancer_type']:
            query = query.filter(CancerData.cancer_type == filters['cancer_type'])
        if filters['gender']:
            query = query.filter(CancerData.gender == filters['gender'])
        
        cancer_records = query.limit(1000000).all()
        
        records = []
        for record in cancer_records:
            records.append({
                "patient_id": record.patient_id,
                "age": record.age,
                "gender": record.gender,
                "region": record.region,
                "year": record.year,
                "genetic_risk": float(record.genetic_risk) if record.genetic_risk else None,
                "air_pollution": float(record.air_pollution) if record.air_pollution else None,
                "alcohol_consumption": float(record.alcohol_consumption) if record.alcohol_consumption else None,
                "smoking": float(record.smoking) if record.smoking else None,
                "obesity_level": float(record.obesity_level) if record.obesity_level else None,
                "cancer_type": record.cancer_type,
                "cancer_stage": record.cancer_stage,
                "treatment_cost": float(record.treatment_cost) if record.treatment_cost else None,
                "survival_years": float(record.survival_years) if record.survival_years else None,
                "severity_score": float(record.severity_score) if record.severity_score else None
            })
        return jsonify(records)
    except Exception as e:
        session.rollback()
        return jsonify({'error': str(e)}), 500
    finally:
        session.close()

@app.route('/api/filtros')
def obtener_filtros():
    session = session_factory()
    try:
        response_headers = {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': 'http://127.0.0.1:5000',
            'Access-Control-Allow-Methods': 'GET'
        }

        # Consultas optimizadas para obtener valores únicos
        cancer_types = session.query(CancerData.cancer_type).distinct().filter(CancerData.cancer_type.isnot(None)).all()
        years = session.query(CancerData.year).distinct().filter(CancerData.year.isnot(None)).all()
        regions = session.query(CancerData.region).distinct().filter(CancerData.region.isnot(None)).all()
        genders = session.query(CancerData.gender).distinct().filter(CancerData.gender.isnot(None)).all()
        
        response_data = {
            'cancer_types': sorted([item[0] for item in cancer_types]),
            'years': sorted([item[0] for item in years]),
            'regions': sorted([item[0] for item in regions]),
            'genders': sorted([item[0] for item in genders])
        }
        
        response = make_response(jsonify(response_data))
        response.headers = response_headers
        return response
    except Exception as e:
        session.rollback()
        print(f"Error in /api/filtros: {str(e)}")
        print(traceback.format_exc())
        error_response = make_response(jsonify({'error': str(e)}), 500)
        error_response.headers = response_headers
        return error_response
    finally:
        session.close()

if __name__ == '__main__':
    app.run(debug=True)

##app.run(debug=True)
    port = int(os.environ.get("PORT", 5000))  # Render asigna el puerto dinámicamente
    app.run(host='0.0.0.0', port=port)