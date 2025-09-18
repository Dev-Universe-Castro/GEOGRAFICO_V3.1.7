
"""
Modelos de dados para integração com Supabase
Apenas usuários, revendas e vendedores são armazenados no banco.
Os dados estáticos (JSON/GeoJSON) permanecem como arquivos locais.
"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, List
import json

@dataclass
class SupabaseUser:
    id: Optional[int] = None
    username: str = ""
    email: str = ""
    password_hash: str = ""
    full_name: str = ""
    role: str = "user"  # 'user' or 'admin'
    active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

@dataclass
class SupabaseRevenda:
    id: Optional[int] = None
    nome: str = ""
    cnpj: str = ""
    endereco: str = ""
    cidade: str = ""
    estado: str = ""
    cep: str = ""
    telefone: str = ""
    email: str = ""
    responsavel: str = ""
    municipios_codigos: List[str] = None  # Lista de códigos IBGE
    cor: str = "#4CAF50"  # Cor para visualização
    active: bool = True
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.municipios_codigos is None:
            self.municipios_codigos = []

@dataclass
class SupabaseVendedor:
    id: Optional[int] = None
    nome: str = ""
    cpf: str = ""
    email: str = ""
    telefone: str = ""
    endereco: str = ""
    cidade: str = ""
    estado: str = ""
    cep: str = ""
    data_nascimento: Optional[date] = None
    data_admissao: Optional[date] = None
    salario_base: Optional[float] = None
    comissao_percentual: float = 0.0
    meta_mensal: Optional[float] = None
    municipios_codigos: List[str] = None  # Lista de códigos IBGE
    cor: str = "#2196F3"  # Cor para visualização
    active: bool = True
    created_by: Optional[int] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    def __post_init__(self):
        if self.municipios_codigos is None:
            self.municipios_codigos = []

class SupabaseManager:
    """Gerenciador para operações com Supabase - apenas usuários, revendas e vendedores"""
    
    def __init__(self):
        from supabase_config import get_supabase_client
        self.supabase = get_supabase_client()
    
    # Operações com Usuários
    def create_user(self, user: SupabaseUser) -> dict:
        """Cria um novo usuário"""
        try:
            user_data = {
                'username': user.username,
                'email': user.email,
                'password_hash': user.password_hash,
                'full_name': user.full_name,
                'role': user.role,
                'active': user.active
            }
            result = self.supabase.table('users').insert(user_data).execute()
            return {'success': True, 'data': result.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_users(self) -> List[SupabaseUser]:
        """Recupera todos os usuários"""
        try:
            result = self.supabase.table('users').select('*').execute()
            users = []
            for user_data in result.data:
                user = SupabaseUser(**user_data)
                users.append(user)
            return users
        except Exception as e:
            print(f"Erro ao recuperar usuários: {e}")
            return []
    
    def get_user_by_username_or_email(self, identifier: str) -> dict:
        """Busca usuário por username ou email"""
        try:
            result = self.supabase.table('users').select('*').or_(f'username.eq.{identifier},email.eq.{identifier}').execute()
            if result.data:
                return {'success': True, 'data': result.data[0]}
            return {'success': False, 'error': 'Usuário não encontrado'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def update_user(self, user_id: int, updates: dict) -> dict:
        """Atualiza um usuário"""
        try:
            result = self.supabase.table('users').update(updates).eq('id', user_id).execute()
            return {'success': True, 'data': result.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Operações com Revendas
    def create_revenda(self, revenda: SupabaseRevenda) -> dict:
        """Cria uma nova revenda"""
        try:
            revenda_data = {
                'nome': revenda.nome,
                'cnpj': revenda.cnpj,
                'endereco': revenda.endereco,
                'cidade': revenda.cidade,
                'estado': revenda.estado,
                'cep': revenda.cep,
                'telefone': revenda.telefone,
                'email': revenda.email,
                'responsavel': revenda.responsavel,
                'municipios_codigos': revenda.municipios_codigos,
                'cor': revenda.cor,
                'active': revenda.active,
                'created_by': revenda.created_by
            }
            print(f"DEBUG models_supabase: Inserindo revenda com dados: {revenda_data}")
            result = self.supabase.table('revendas').insert(revenda_data).execute()
            print(f"DEBUG models_supabase: Resultado da inserção: {result.data}")
            return {'success': True, 'data': result.data}
        except Exception as e:
            print(f"Erro ao criar revenda no Supabase: {e}")
            import traceback
            traceback.print_exc()
            return {'success': False, 'error': str(e)}
    
    def get_revendas(self, active_only: bool = True) -> List[SupabaseRevenda]:
        """Recupera todas as revendas"""
        try:
            query = self.supabase.table('revendas').select('*')
            if active_only:
                query = query.eq('active', True)
            
            result = query.execute()
            revendas = []
            for revenda_data in result.data:
                print(f"DEBUG models_supabase: Dados da revenda: {revenda_data}")
                
                # Garantir que municipios_codigos seja uma lista
                municipios_codigos = revenda_data.get('municipios_codigos', [])
                if not isinstance(municipios_codigos, list):
                    if municipios_codigos is None:
                        municipios_codigos = []
                    else:
                        # Tentar converter para lista se for string JSON
                        try:
                            import json
                            if isinstance(municipios_codigos, str):
                                municipios_codigos = json.loads(municipios_codigos)
                            else:
                                municipios_codigos = []
                        except Exception as json_error:
                            print(f"Erro ao converter municipios_codigos: {json_error}")
                            municipios_codigos = []
                
                revenda_data['municipios_codigos'] = municipios_codigos
                print(f"DEBUG models_supabase: Municípios processados: {municipios_codigos}")
                
                # Converter campos de data se forem strings
                for date_field in ['created_at', 'updated_at']:
                    if revenda_data.get(date_field) and isinstance(revenda_data[date_field], str):
                        try:
                            from datetime import datetime
                            revenda_data[date_field] = datetime.fromisoformat(revenda_data[date_field].replace('Z', '+00:00'))
                        except:
                            revenda_data[date_field] = None
                
                revenda = SupabaseRevenda(**revenda_data)
                revendas.append(revenda)
            return revendas
        except Exception as e:
            print(f"Erro ao recuperar revendas: {e}")
            import traceback
            traceback.print_exc()
            return []
    
    def update_revenda(self, revenda_id: int, updates: dict) -> dict:
        """Atualiza uma revenda"""
        try:
            # Garantir que updated_at seja atualizado
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = self.supabase.table('revendas').update(updates).eq('id', revenda_id).execute()
            return {'success': True, 'data': result.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_revenda_by_id(self, revenda_id: int) -> dict:
        """Busca revenda por ID"""
        try:
            result = self.supabase.table('revendas').select('*').eq('id', revenda_id).execute()
            if result.data:
                revenda_data = result.data[0]
                # Garantir que municipios_codigos seja uma lista
                if not isinstance(revenda_data.get('municipios_codigos'), list):
                    revenda_data['municipios_codigos'] = []
                return {'success': True, 'data': revenda_data}
            return {'success': False, 'error': 'Revenda não encontrada'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    # Operações com Vendedores
    def create_vendedor(self, vendedor: SupabaseVendedor) -> dict:
        """Cria um novo vendedor"""
        try:
            vendedor_data = {
                'nome': vendedor.nome,
                'cpf': vendedor.cpf,
                'email': vendedor.email,
                'telefone': vendedor.telefone,
                'endereco': vendedor.endereco,
                'cidade': vendedor.cidade,
                'estado': vendedor.estado,
                'cep': vendedor.cep,
                'data_nascimento': vendedor.data_nascimento.isoformat() if vendedor.data_nascimento else None,
                'data_admissao': vendedor.data_admissao.isoformat() if vendedor.data_admissao else None,
                'salario_base': vendedor.salario_base,
                'comissao_percentual': vendedor.comissao_percentual,
                'meta_mensal': vendedor.meta_mensal,
                'municipios_codigos': vendedor.municipios_codigos,
                'cor': vendedor.cor,
                'active': vendedor.active,
                'created_by': vendedor.created_by
            }
            result = self.supabase.table('vendedores').insert(vendedor_data).execute()
            return {'success': True, 'data': result.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_vendedores(self, active_only: bool = True) -> List[SupabaseVendedor]:
        """Recupera todos os vendedores"""
        try:
            query = self.supabase.table('vendedores').select('*')
            if active_only:
                query = query.eq('active', True)
            
            result = query.execute()
            vendedores = []
            for vendedor_data in result.data:
                # Garantir que municipios_codigos seja uma lista
                if not isinstance(vendedor_data.get('municipios_codigos'), list):
                    vendedor_data['municipios_codigos'] = []
                
                # Converte datas string para objetos date se necessário
                if vendedor_data.get('data_nascimento'):
                    try:
                        vendedor_data['data_nascimento'] = datetime.fromisoformat(vendedor_data['data_nascimento']).date()
                    except:
                        vendedor_data['data_nascimento'] = None
                        
                if vendedor_data.get('data_admissao'):
                    try:
                        vendedor_data['data_admissao'] = datetime.fromisoformat(vendedor_data['data_admissao']).date()
                    except:
                        vendedor_data['data_admissao'] = None
                
                vendedor = SupabaseVendedor(**vendedor_data)
                vendedores.append(vendedor)
            return vendedores
        except Exception as e:
            print(f"Erro ao recuperar vendedores: {e}")
            return []
    
    def update_vendedor(self, vendedor_id: int, updates: dict) -> dict:
        """Atualiza um vendedor"""
        try:
            # Garantir que updated_at seja atualizado
            updates['updated_at'] = datetime.utcnow().isoformat()
            result = self.supabase.table('vendedores').update(updates).eq('id', vendedor_id).execute()
            return {'success': True, 'data': result.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def get_vendedor_by_id(self, vendedor_id: int) -> dict:
        """Busca vendedor por ID"""
        try:
            result = self.supabase.table('vendedores').select('*').eq('id', vendedor_id).execute()
            if result.data:
                vendedor_data = result.data[0]
                # Garantir que municipios_codigos seja uma lista
                if not isinstance(vendedor_data.get('municipios_codigos'), list):
                    vendedor_data['municipios_codigos'] = []
                
                # Converte datas se necessário
                if vendedor_data.get('data_nascimento'):
                    try:
                        vendedor_data['data_nascimento'] = datetime.fromisoformat(vendedor_data['data_nascimento']).date()
                    except:
                        vendedor_data['data_nascimento'] = None
                        
                if vendedor_data.get('data_admissao'):
                    try:
                        vendedor_data['data_admissao'] = datetime.fromisoformat(vendedor_data['data_admissao']).date()
                    except:
                        vendedor_data['data_admissao'] = None
                
                return {'success': True, 'data': vendedor_data}
            return {'success': False, 'error': 'Vendedor não encontrado'}
        except Exception as e:
            return {'success': False, 'error': str(e)}
    
    def associate_vendedor_revenda(self, vendedor_id: int, revenda_id: int) -> dict:
        """Associa vendedor a uma revenda"""
        try:
            association_data = {
                'vendedor_id': vendedor_id,
                'revenda_id': revenda_id,
                'active': True
            }
            result = self.supabase.table('vendedor_revendas').insert(association_data).execute()
            return {'success': True, 'data': result.data}
        except Exception as e:
            return {'success': False, 'error': str(e)}
