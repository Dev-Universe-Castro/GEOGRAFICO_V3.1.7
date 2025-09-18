
# Configuração do Banco Supabase

## Visão Geral

O sistema FertiCore utiliza uma arquitetura híbrida:

- **Banco de Dados Supabase**: Armazena apenas dados dinâmicos (usuários, revendas, vendedores)
- **Arquivos JSON Locais**: Contém dados estáticos (culturas, fertilizantes, agrotóxicos, etc.)
- **Arquivos GeoJSON Locais**: Contém dados geográficos dos municípios e estados

Esta abordagem garante performance otimizada e facilita atualizações dos dados estáticos.

## Passo 1: Executar SQL no Supabase

1. Acesse o painel do Supabase: https://supabase.com/dashboard/project/lfixewuzliyvhortepkr/sql

2. Execute o seguinte SQL para criar as tabelas:

```sql
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

-- Comentários para documentação
COMMENT ON TABLE users IS 'Usuários do sistema que podem cadastrar revendas e vendedores';
COMMENT ON TABLE revendas IS 'Revendas cadastradas pelos usuários com seus municípios de atuação';
COMMENT ON TABLE vendedores IS 'Vendedores cadastrados pelos usuários com seus municípios de atuação';
COMMENT ON COLUMN revendas.municipios_codigos IS 'Array JSON com códigos IBGE dos municípios onde a revenda atua';
COMMENT ON COLUMN vendedores.municipios_codigos IS 'Array JSON com códigos IBGE dos municípios onde o vendedor atua';
```

## Passo 2: Executar o aplicativo

Após criar as tabelas no Supabase, execute o workflow "Run" novamente.

## Estrutura do Sistema

### Banco de Dados Supabase (Dados Dinâmicos)
- **users**: Usuários do sistema (admin e usuários comuns)
- **revendas**: Revendas cadastradas pelos usuários com municípios de atuação
- **vendedores**: Vendedores cadastrados pelos usuários com municípios de atuação
- **vendedor_revendas**: Relacionamento entre vendedores e revendas

### Arquivos Locais (Dados Estáticos)
- **data/crop_data_static.json**: Dados de culturas agrícolas por município
- **data/fertilizer_data_static_corrigido.json**: Dados de fertilizantes por município
- **data/agrotoxico_data_static.json**: Dados de agrotóxicos por município
- **data/consultoria_tecnica_data_static.json**: Dados de consultoria técnica
- **data/corretivos_data_static.json**: Dados de corretivos agrícolas
- **data/despesa_data_static.json**: Dados de despesas agrícolas
- **data/escolaridade_data_static.json**: Dados de escolaridade rural
- **data/receita_data_static.json**: Dados de receitas agrícolas

### Arquivos GeoJSON (Dados Geográficos)
- **static/data/brazil_states.geojson**: Limites dos estados brasileiros
- **static/data/brazil_municipalities.geojson**: Limites dos municípios brasileiros
- **static/data/[UF].geojson**: Arquivos específicos por estado

## Funcionalidades Principais

### 1. Gerenciamento de Usuários
- Registro e autenticação de usuários
- Controle de acesso (admin/usuário comum)
- Gerenciamento de perfis

### 2. Cadastro de Revendas
- Informações comerciais da revenda
- Seleção de municípios de atuação via códigos IBGE
- Visualização territorial no mapa
- Análise de potencial comercial baseada nos dados estáticos

### 3. Cadastro de Vendedores
- Informações pessoais e profissionais
- Seleção de municípios de atuação via códigos IBGE
- Visualização territorial no mapa
- Análise de potencial comercial baseada nos dados estáticos

### 4. Análises Territoriais
- Cruzamento dos municípios cadastrados com dados estáticos
- Análise de potencial de culturas por região
- Análise de mercado de fertilizantes e insumos
- Relatórios em Excel exportáveis

## Configurações

### Variáveis de Ambiente (.env)
```env
# Configurações do Supabase
SUPABASE_URL=https://lfixewuzliyvhortepkr.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

# Configurações do Usuário Administrador
ADMIN_USERNAME=admin
ADMIN_EMAIL=admin@ferticore.com
ADMIN_PASSWORD=admin123456
ADMIN_FULL_NAME=Administrador do Sistema

# Configurações da Aplicação Flask
SECRET_KEY=sua_chave_secreta_aqui
FLASK_ENV=development
```

## Vantagens da Arquitetura Híbrida

1. **Performance**: Dados estáticos carregados uma vez na memória
2. **Escalabilidade**: Banco focado apenas em dados dinâmicos
3. **Flexibilidade**: Fácil atualização dos dados estáticos
4. **Custo**: Menor uso do banco de dados Supabase
5. **Offline**: Dados estáticos funcionam mesmo sem conexão com o banco

## Fluxo de Trabalho

1. **Login**: Usuário faz login no sistema
2. **Cadastro**: Usuário cadastra revendas/vendedores com seus municípios
3. **Análise**: Sistema cruza municípios cadastrados com dados estáticos
4. **Visualização**: Mapa mostra territórios e dados relevantes
5. **Relatórios**: Exportação de análises em Excel

## Manutenção

### Atualização de Dados Estáticos
1. Substituir arquivos JSON na pasta `data/`
2. Reiniciar aplicação para recarregar dados
3. Não requer alterações no banco de dados

### Backup do Banco
- Fazer backup apenas das tabelas de usuários, revendas e vendedores
- Dados estáticos são versionados junto com o código

## Troubleshooting

### Problema: Tabelas não criadas
**Solução**: Execute o SQL manualmente no Supabase SQL Editor

### Problema: Erro de conexão com Supabase
**Solução**: Verifique as variáveis SUPABASE_URL e SUPABASE_KEY

### Problema: Dados estáticos não carregam
**Solução**: Verifique se os arquivos JSON estão na pasta `data/`

### Problema: Mapas não aparecem
**Solução**: Verifique se os arquivos GeoJSON estão na pasta `static/data/`
