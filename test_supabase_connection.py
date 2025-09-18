
"""
Teste de conexão com Supabase
"""
from supabase_config import get_supabase_client
from dotenv import load_dotenv
import os

# Carrega variáveis de ambiente
load_dotenv()

def test_supabase_connection():
    """Testa a conexão com o Supabase"""
    try:
        # Cria cliente
        supabase = get_supabase_client()
        
        print("🔄 Testando conexão com Supabase...")
        print(f"URL: {os.getenv('SUPABASE_URL')}")
        print(f"Key: {os.getenv('SUPABASE_KEY')[:20]}...")
        
        # Testa uma query simples
        result = supabase.table('users').select('*').limit(1).execute()
        
        print("✅ Conexão com Supabase estabelecida com sucesso!")
        print(f"Dados de teste: {len(result.data)} registros encontrados")
        
        return True
        
    except Exception as e:
        print(f"❌ Erro na conexão com Supabase: {e}")
        return False

if __name__ == "__main__":
    test_supabase_connection()
