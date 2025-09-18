
import hashlib
import secrets
from datetime import datetime, timedelta
from functools import wraps
from flask import session, request, jsonify, redirect, url_for
from models import User, UserSession, UserRole
from app import db

class AuthManager:
    def __init__(self):
        pass
    
    def hash_password(self, password):
        """Hash da senha com salt"""
        salt = secrets.token_hex(16)
        password_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
        return f"{salt}:{password_hash.hex()}"
    
    def verify_password(self, password, hashed_password):
        """Verifica se a senha está correta"""
        try:
            salt, password_hash = hashed_password.split(':')
            new_hash = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt.encode('utf-8'), 100000)
            return password_hash == new_hash.hex()
        except:
            return False
    
    def register_user(self, username, email, password, full_name=None, role=UserRole.USER):
        """Registra um novo usuário"""
        try:
            # Validações
            if not username or len(username) < 3:
                return {'success': False, 'error': 'Nome de usuário deve ter pelo menos 3 caracteres'}
            
            if not email or '@' not in email:
                return {'success': False, 'error': 'Email inválido'}
            
            if not password or len(password) < 6:
                return {'success': False, 'error': 'Senha deve ter pelo menos 6 caracteres'}
            
            # Verifica se usuário já existe
            if User.query.filter_by(username=username).first():
                return {'success': False, 'error': 'Nome de usuário já existe'}
            
            if User.query.filter_by(email=email).first():
                return {'success': False, 'error': 'Email já está em uso'}
            
            # Cria novo usuário
            user = User(
                username=username,
                email=email,
                password_hash=self.hash_password(password),
                full_name=full_name or username,
                role=role
            )
            
            db.session.add(user)
            db.session.commit()
            
            return {'success': True, 'message': 'Usuário registrado com sucesso'}
        
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Erro interno: {str(e)}'}
    
    def login_user(self, username, password):
        """Autentica um usuário"""
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user:
                return {'success': False, 'error': 'Usuário não encontrado'}
            
            if not user.is_active:
                return {'success': False, 'error': 'Conta desativada'}
            
            if not self.verify_password(password, user.password_hash):
                return {'success': False, 'error': 'Senha incorreta'}
            
            # Cria sessão
            session_token = secrets.token_urlsafe(32)
            expires_at = datetime.utcnow() + timedelta(days=7)  # Sessão válida por 7 dias
            
            user_session = UserSession(
                session_token=session_token,
                user_id=user.id,
                ip_address=request.environ.get('HTTP_X_FORWARDED_FOR', request.environ.get('REMOTE_ADDR')),
                user_agent=request.environ.get('HTTP_USER_AGENT', ''),
                expires_at=expires_at
            )
            
            db.session.add(user_session)
            
            # Atualiza último login
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            # Define sessão no Flask
            session['session_token'] = session_token
            session['user_id'] = user.id
            session['logged_in'] = True
            
            return {
                'success': True,
                'message': 'Login realizado com sucesso',
                'user': user.to_dict()
            }
        
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Erro interno: {str(e)}'}
    
    def logout_user(self):
        """Faz logout do usuário"""
        try:
            session_token = session.get('session_token')
            
            if session_token:
                user_session = UserSession.query.filter_by(session_token=session_token).first()
                if user_session:
                    user_session.is_active = False
                    db.session.commit()
            
            session.clear()
            return {'success': True, 'message': 'Logout realizado com sucesso'}
        
        except Exception as e:
            return {'success': False, 'error': f'Erro interno: {str(e)}'}
    
    def get_current_user(self):
        """Retorna dados do usuário atual"""
        try:
            if not session.get('logged_in'):
                return None
            
            session_token = session.get('session_token')
            user_id = session.get('user_id')
            
            if not session_token or not user_id:
                return None
            
            # Verifica se sessão ainda é válida
            user_session = UserSession.query.filter_by(
                session_token=session_token,
                is_active=True
            ).first()
            
            if not user_session or user_session.is_expired():
                session.clear()
                return None
            
            # Busca dados do usuário
            user = User.query.get(user_id)
            if not user or not user.is_active:
                session.clear()
                return None
            
            return user.to_dict()
        
        except Exception as e:
            print(f"Error getting current user: {e}")
            return None
    
    def is_authenticated(self):
        """Verifica se usuário está autenticado"""
        return self.get_current_user() is not None
    
    def is_admin(self):
        """Verifica se usuário atual é administrador"""
        user_data = self.get_current_user()
        return user_data and user_data.get('role') == 'admin'
    
    def change_password(self, username, old_password, new_password):
        """Altera senha do usuário"""
        try:
            user = User.query.filter_by(username=username).first()
            
            if not user:
                return {'success': False, 'error': 'Usuário não encontrado'}
            
            if not self.verify_password(old_password, user.password_hash):
                return {'success': False, 'error': 'Senha atual incorreta'}
            
            if len(new_password) < 6:
                return {'success': False, 'error': 'Nova senha deve ter pelo menos 6 caracteres'}
            
            user.password_hash = self.hash_password(new_password)
            user.updated_at = datetime.utcnow()
            db.session.commit()
            
            return {'success': True, 'message': 'Senha alterada com sucesso'}
        
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'error': f'Erro interno: {str(e)}'}
    
    def create_admin_user(self, username, email, password, full_name):
        """Cria usuário administrador"""
        return self.register_user(username, email, password, full_name, UserRole.ADMIN)

# Instância global do gerenciador de autenticação
auth_manager = AuthManager()

def login_required(f):
    """Decorator que exige autenticação"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_manager.is_authenticated():
            if request.is_json:
                return jsonify({'success': False, 'error': 'Autenticação necessária'}), 401
            return redirect(url_for('login_page'))
        return f(*args, **kwargs)
    return decorated_function

def admin_required(f):
    """Decorator que exige permissões de administrador"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not auth_manager.is_authenticated():
            if request.is_json:
                return jsonify({'success': False, 'error': 'Autenticação necessária'}), 401
            return redirect(url_for('login_page'))
        
        if not auth_manager.is_admin():
            if request.is_json:
                return jsonify({'success': False, 'error': 'Permissões de administrador necessárias'}), 403
            return jsonify({'success': False, 'error': 'Acesso negado'}), 403
        
        return f(*args, **kwargs)
    return decorated_function
