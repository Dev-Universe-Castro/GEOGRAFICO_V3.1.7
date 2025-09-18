
"""
Script para inicializar o banco de dados PostgreSQL
"""
from app import app, db
from models import User, UserRole
from auth import auth_manager
import os

def init_database():
    """Inicializa o banco de dados e cria usuário admin"""
    with app.app_context():
        try:
            # Criar todas as tabelas
            db.create_all()
            print("✅ Tabelas criadas com sucesso!")
            
            # Verificar se já existe usuário admin
            admin_user = User.query.filter_by(role=UserRole.ADMIN).first()
            
            if not admin_user:
                # Criar usuário administrador padrão
                admin_username = os.environ.get('ADMIN_USERNAME', 'admin')
                admin_email = os.environ.get('ADMIN_EMAIL', 'admin@ferticore.com')
                admin_password = os.environ.get('ADMIN_PASSWORD', 'admin123456')
                admin_full_name = os.environ.get('ADMIN_FULL_NAME', 'Administrador do Sistema')
                
                result = auth_manager.create_admin_user(
                    username=admin_username,
                    email=admin_email,
                    password=admin_password,
                    full_name=admin_full_name
                )
                
                if result['success']:
                    print(f"✅ Usuário administrador criado: {admin_username}")
                    print(f"   Email: {admin_email}")
                    print(f"   Senha: {admin_password}")
                    print("   ⚠️  IMPORTANTE: Altere a senha padrão após o primeiro login!")
                else:
                    print(f"❌ Erro ao criar usuário admin: {result['error']}")
            else:
                print(f"✅ Usuário administrador já existe: {admin_user.username}")
            
            print("\n🎉 Banco de dados inicializado com sucesso!")
            
        except Exception as e:
            print(f"❌ Erro ao inicializar banco de dados: {e}")
            raise e

if __name__ == "__main__":
    init_database()
