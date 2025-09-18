
import os
from app import app
from init_database import init_database

if __name__ == "__main__":
    # Inicializar banco de dados
    try:
        init_database()
    except Exception as e:
        print(f"Erro na inicialização do banco: {e}")
        # Continuar mesmo com erro para não quebrar o desenvolvimento
    
    # Importar rotas administrativas
    import admin_routes
    
    # Executar aplicação
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
