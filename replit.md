# FertiCore - Sistema de Visualização Agrícola

## Visão Geral
Sistema de visualização de dados agrícolas com mapas interativos, desenvolvido em Flask com interface web responsiva. O sistema permite visualizar dados de culturas, fertilizantes, agrotóxicos e outros dados agrícolas brasileiros através de mapas e gráficos.

## Estado Atual do Projeto
✅ **Aplicação totalmente funcional no ambiente Replit**

### Arquitetura
- **Backend**: Flask (Python) com SQLAlchemy
- **Frontend**: HTML/CSS/JavaScript com Leaflet para mapas
- **Base de Dados**: SQLite (configurado com caminhos absolutos)
- **Deployment**: Configurado para produção com Gunicorn

### Funcionalidades Implementadas
- Sistema de autenticação de usuários
- Visualização de mapas interativos do Brasil
- APIs RESTful para dados agrícolas (65+ culturas, 8 categorias de fertilizantes)
- Interface responsiva com sidebar mobile
- **Novo Layout**: Cabeçalho branco com logo centralizado e menu hambúrguer

### Modificações Recentes (Solicitação do Usuário)
1. **Cabeçalho Principal**: 
   - Fundo branco com altura de 70px
   - Logo da FertiCore centralizado (texto duplicado removido)
   - Botão menu hambúrguer na esquerda
   
2. **Sidebar Mobile Estilo App**: 
   - **Largura fixa**: 280px (não ocupa tela toda)
   - **Animação**: Desliza da esquerda para direita
   - **Overlay inteligente**: Cobre apenas área não ocupada pelo sidebar
   - **JavaScript null-safe**: Erros de querySelector eliminados
   - Responsivo: persistente em desktop (>992px), retrátil em mobile

3. **Layout Responsivo Otimizado**:
   - Desktop: Sidebar visível por padrão, conteúdo com margem esquerda
   - Mobile/Tablet: Sidebar com largura fixa (280px), acionado pelo botão hambúrguer
   - Mapa ajustado para nova altura do cabeçalho (calc(100vh - 70px))
   - Overlay posicionado: top: 70px, left: 280px, width: calc(100vw - 280px)

## Configuração Técnica

### Dependências Python
- Flask, SQLAlchemy, Flask-Migrate
- Pandas, OpenPyXL para processamento de dados
- Gunicorn para produção
- Werkzeug com ProxyFix para ambiente Replit

### Estrutura de Arquivos
```
/
├── templates/          # Templates HTML
├── static/            # CSS, JS, imagens
├── data/              # Arquivos JSON com dados agrícolas
├── instance/          # Base de dados SQLite
├── app.py            # Configuração Flask
├── routes.py         # Rotas da aplicação  
├── main.py          # Ponto de entrada
└── auth.py          # Sistema de autenticação
```

### Ambiente Replit
- **Workflow**: Flask Application (porta 5000)
- **Host**: 0.0.0.0 para compatibilidade com proxy
- **Deploy**: Configurado para autoscale com Gunicorn

## APIs Disponíveis
- `/api/crops` - Lista de culturas disponíveis
- `/api/crop-data/<cultura>` - Dados por cultura
- `/api/fertilizer-categories` - Categorias de fertilizantes
- `/api/statistics` - Estatísticas gerais
- `/api/brazilian-states` - Estados brasileiros
- `/api/auth/*` - Endpoints de autenticação

## Próximos Passos Sugeridos
- Testes funcionais do novo layout em diferentes dispositivos
- Otimizações de performance para carregamento de dados
- Implementação de cache para APIs
- Melhorias na UX do mapa interativo

---
*Projeto configurado e funcionando no ambiente Replit - Setembro 2025*