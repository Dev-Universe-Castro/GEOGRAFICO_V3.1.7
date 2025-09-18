
from app import db
from datetime import datetime
import json
from enum import Enum

class UserRole(Enum):
    ADMIN = "admin"
    USER = "user"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.USER)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = db.Column(db.DateTime)
    
    def __repr__(self):
        return f'<User {self.username}>'
    
    def is_admin(self):
        return self.role == UserRole.ADMIN
    
    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'role': self.role.value,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None
        }

class Revenda(db.Model):
    __tablename__ = 'revendas'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    cnpj = db.Column(db.String(18), nullable=False, unique=True)
    cnae = db.Column(db.String(10), nullable=False)
    endereco = db.Column(db.Text)
    telefone = db.Column(db.String(20))
    email = db.Column(db.String(120))
    responsavel = db.Column(db.String(200))
    municipios = db.Column(db.Text, nullable=False)  # JSON string com lista de códigos de municípios
    cor = db.Column(db.String(7), nullable=False, default='#4CAF50')  # Cor hex para visualização
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref=db.backref('revendas_created', lazy=True))

    def __repr__(self):
        return f'<Revenda {self.nome}>'

    def get_municipios_list(self):
        """Retorna lista de códigos de municípios"""
        try:
            return json.loads(self.municipios) if self.municipios else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_municipios_list(self, municipios_list):
        """Define lista de códigos de municípios"""
        self.municipios = json.dumps(municipios_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'cnpj': self.cnpj,
            'cnae': self.cnae,
            'endereco': self.endereco,
            'telefone': self.telefone,
            'email': self.email,
            'responsavel': self.responsavel,
            'municipios': self.get_municipios_list(),
            'municipios_count': len(self.get_municipios_list()),
            'cor': self.cor,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class Vendedor(db.Model):
    __tablename__ = 'vendedores'
    
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False, unique=True)
    telefone = db.Column(db.String(20), nullable=False)
    cpf = db.Column(db.String(14), nullable=False, unique=True)
    endereco = db.Column(db.Text)
    data_nascimento = db.Column(db.Date)
    municipios = db.Column(db.Text, nullable=False)  # JSON string com lista de códigos de municípios
    cor = db.Column(db.String(7), nullable=False, default='#2196F3')  # Cor hex para visualização
    ativo = db.Column(db.Boolean, nullable=False, default=True)
    created_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    creator = db.relationship('User', backref=db.backref('vendedores_created', lazy=True))

    def __repr__(self):
        return f'<Vendedor {self.nome}>'

    def get_municipios_list(self):
        """Retorna lista de códigos de municípios"""
        try:
            return json.loads(self.municipios) if self.municipios else []
        except (json.JSONDecodeError, TypeError):
            return []

    def set_municipios_list(self, municipios_list):
        """Define lista de códigos de municípios"""
        self.municipios = json.dumps(municipios_list)
    
    def to_dict(self):
        return {
            'id': self.id,
            'nome': self.nome,
            'email': self.email,
            'telefone': self.telefone,
            'cpf': self.cpf,
            'endereco': self.endereco,
            'data_nascimento': self.data_nascimento.isoformat() if self.data_nascimento else None,
            'municipios': self.get_municipios_list(),
            'municipios_count': len(self.get_municipios_list()),
            'cor': self.cor,
            'ativo': self.ativo,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None
        }

class CropData(db.Model):
    __tablename__ = 'crop_data'
    
    id = db.Column(db.Integer, primary_key=True)
    municipality_code = db.Column(db.String(10), nullable=False)
    municipality_name = db.Column(db.String(100), nullable=False)
    state_code = db.Column(db.String(2), nullable=False)
    crop_name = db.Column(db.String(100), nullable=False)
    harvested_area = db.Column(db.Float, nullable=False)
    year = db.Column(db.Integer, nullable=False, default=2023)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<CropData {self.municipality_name} - {self.crop_name}>'

class ProcessingLog(db.Model):
    __tablename__ = 'processing_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(200), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    records_processed = db.Column(db.Integer, default=0)
    error_message = db.Column(db.Text)
    processed_by = db.Column(db.Integer, db.ForeignKey('users.id'))
    processed_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    processor = db.relationship('User', backref=db.backref('processing_logs', lazy=True))

    def __repr__(self):
        return f'<ProcessingLog {self.filename} - {self.status}>'

class UserSession(db.Model):
    __tablename__ = 'user_sessions'
    
    id = db.Column(db.Integer, primary_key=True)
    session_token = db.Column(db.String(255), unique=True, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    ip_address = db.Column(db.String(45))
    user_agent = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    
    # Relationships
    user = db.relationship('User', backref=db.backref('sessions', lazy=True))
    
    def __repr__(self):
        return f'<UserSession {self.user.username}>'
    
    def is_expired(self):
        return datetime.utcnow() > self.expires_at
