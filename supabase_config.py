"""
Configuração e inicialização do banco de dados Supabase
"""
import os
from supabase import create_client, Client
from dotenv import load_dotenv
import json
from werkzeug.security import generate_password_hash

# Carrega variáveis de ambiente
load_dotenv()

# Configurações do Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL", "https://lfixewuzliyvhortepkr.supabase.co")
SUPABASE_KEY = os.getenv("SUPABASE_KEY", "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImxmaXhld3V6bGl5dmhvcnRlcGtyIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NTgxMTYyMDAsImV4cCI6MjA3MzY5MjIwMH0._DBv6xaCgZeY3_TeVnhsD19Hyb79POUAJs9W5LyDjp0")

def get_supabase_client() -> Client:
    """Cria e retorna cliente do Supabase"""
    return create_client(SUPABASE_URL, SUPABASE_KEY)

def init_supabase_tables():
    """Inicializa as tabelas no Supabase"""
    supabase = get_supabase_client()

    print("🔄 Verificando estrutura do banco Supabase...")

    # Verifica se as tabelas já existem tentando fazer select
    tables_to_check = ['users', 'revendas', 'vendedores', 'vendedor_revendas']
    existing_tables = []

    for table_name in tables_to_check:
        try:
            result = supabase.table(table_name).select('*').limit(1).execute()
            existing_tables.append(table_name)
            print(f"✅ Tabela {table_name} já existe")
        except Exception as e:
            print(f"⚠️  Tabela {table_name} não encontrada: {str(e)[:100]}")

    if len(existing_tables) == len(tables_to_check):
        print("✅ Todas as tabelas já existem no Supabase!")
    else:
        print("⚠️  Algumas tabelas precisam ser criadas manualmente no Supabase SQL Editor")
        print("📋 Execute o seguinte SQL no Supabase SQL Editor:")
        print_sql_schema()

    # Cria usuário administrador se não existir
    create_admin_user(supabase)

    print("🎉 Verificação do Supabase concluída!")
    print("📝 IMPORTANTE: Os dados estáticos (JSON/GeoJSON) permanecem como arquivos locais")

def print_sql_schema():
    """Imprime o schema SQL para ser executado manualmente"""
    sql_schema = """
-- Tabela de usuários do sistema
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(200),
    role VARCHAR(20) DEFAULT 'user',
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de revendas cadastradas pelos usuários
CREATE TABLE IF NOT EXISTS revendas (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    cnpj VARCHAR(20) UNIQUE,
    endereco TEXT,
    cidade VARCHAR(100),
    estado VARCHAR(2),
    cep VARCHAR(10),
    telefone VARCHAR(20),
    email VARCHAR(120),
    responsavel VARCHAR(200),
    municipios_codigos JSONB DEFAULT '[]', -- Array com códigos IBGE dos municípios
    cor VARCHAR(7) DEFAULT '#4CAF50', -- Cor para visualização no mapa
    active BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de vendedores cadastrados pelos usuários
CREATE TABLE IF NOT EXISTS vendedores (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(200) NOT NULL,
    cpf VARCHAR(15) UNIQUE,
    email VARCHAR(120) UNIQUE,
    telefone VARCHAR(20),
    endereco TEXT,
    cidade VARCHAR(100),
    estado VARCHAR(2),
    cep VARCHAR(10),
    data_nascimento DATE,
    data_admissao DATE,
    salario_base DECIMAL(10,2),
    comissao_percentual DECIMAL(5,2) DEFAULT 0.00,
    meta_mensal DECIMAL(10,2),
    municipios_codigos JSONB DEFAULT '[]', -- Array com códigos IBGE dos municípios
    cor VARCHAR(7) DEFAULT '#2196F3', -- Cor para visualização no mapa
    active BOOLEAN DEFAULT true,
    created_by INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Tabela de relacionamento vendedor-revenda (opcional)
CREATE TABLE IF NOT EXISTS vendedor_revendas (
    id SERIAL PRIMARY KEY,
    vendedor_id INTEGER REFERENCES vendedores(id) ON DELETE CASCADE,
    revenda_id INTEGER REFERENCES revendas(id) ON DELETE CASCADE,
    data_inicio DATE DEFAULT CURRENT_DATE,
    data_fim DATE,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(vendedor_id, revenda_id)
);

-- Índices para melhor performance
CREATE INDEX IF NOT EXISTS idx_revendas_active ON revendas(active);
CREATE INDEX IF NOT EXISTS idx_revendas_created_by ON revendas(created_by);
CREATE INDEX IF NOT EXISTS idx_vendedores_active ON vendedores(active);
CREATE INDEX IF NOT EXISTS idx_vendedores_created_by ON vendedores(created_by);

-- Habilita RLS (Row Level Security) se necessário
-- ALTER TABLE users ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE revendas ENABLE ROW LEVEL SECURITY;
-- ALTER TABLE vendedores ENABLE ROW LEVEL SECURITY;

-- Comentários para documentação
COMMENT ON TABLE users IS 'Usuários do sistema que podem cadastrar revendas e vendedores';
COMMENT ON TABLE revendas IS 'Revendas cadastradas pelos usuários com seus municípios de atuação';
COMMENT ON TABLE vendedores IS 'Vendedores cadastrados pelos usuários com seus municípios de atuação';
COMMENT ON COLUMN revendas.municipios_codigos IS 'Array JSON com códigos IBGE dos municípios onde a revenda atua';
COMMENT ON COLUMN vendedores.municipios_codigos IS 'Array JSON com códigos IBGE dos municípios onde o vendedor atua';
"""
    print(sql_schema)

def create_admin_user(supabase):
    """Cria usuário administrador se não existir"""
    try:
        # Verifica se já existe um usuário admin
        admin_check = supabase.table('users').select('*').eq('role', 'admin').limit(1).execute()

        if not admin_check.data:
            # Gera hash da senha
            password_hash = generate_password_hash(os.getenv('ADMIN_PASSWORD', 'admin123456'))

            admin_data = {
                'username': os.getenv('ADMIN_USERNAME', 'admin'),
                'email': os.getenv('ADMIN_EMAIL', 'admin@ferticore.com'),
                'password_hash': password_hash,
                'full_name': os.getenv('ADMIN_FULL_NAME', 'Administrador do Sistema'),
                'role': 'admin',
                'active': True
            }

            result = supabase.table('users').insert(admin_data).execute()
            print("✅ Usuário administrador criado no Supabase")
            print(f"   Username: {os.getenv('ADMIN_USERNAME', 'admin')}")
            print(f"   Email: {os.getenv('ADMIN_EMAIL', 'admin@ferticore.com')}")
            print("   ⚠️  IMPORTANTE: Configure a autenticação do Supabase adequadamente!")
        else:
            print("✅ Usuário administrador já existe no Supabase")

    except Exception as e:
        print(f"⚠️  Erro ao criar usuário admin (talvez tabela users não exista ainda): {e}")

if __name__ == "__main__":
    try:
        init_supabase_tables()
        print("\n🎯 Configuração do Supabase concluída!")
        print("\n📋 Se as tabelas não existirem, execute o SQL mostrado acima no Supabase SQL Editor")
        print("🔗 Acesse: https://supabase.com/dashboard/project/lfixewuzliyvhortepkr/sql")
        print("\n📊 Os dados estáticos (culturas, fertilizantes, etc.) permanecem como arquivos JSON locais")
        print("👥 Apenas usuários, revendas e vendedores são armazenados no banco de dados")
    except Exception as e:
        print(f"❌ Erro na configuração do Supabase: {e}")