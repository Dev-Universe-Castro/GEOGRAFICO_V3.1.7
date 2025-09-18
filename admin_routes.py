from flask import request, jsonify, render_template
from app import app, db
from models import User, UserRole
from auth_supabase import supabase_auth_manager as auth_manager, login_required, admin_required
from datetime import datetime

@app.route('/admin')
@admin_required
def admin_dashboard():
    """Dashboard administrativo"""
    user = auth_manager.get_current_user()
    return render_template('admin/dashboard.html', user=user)

@app.route('/admin/usuarios')
@admin_required
def admin_usuarios():
    """Página de gerenciamento de usuários"""
    user = auth_manager.get_current_user()
    return render_template('admin/usuarios.html', user=user)

@app.route('/api/admin/users', methods=['GET'])
@admin_required
def get_users():
    """Lista todos os usuários (apenas admin)"""
    try:
        users = User.query.all()
        users_data = [user.to_dict() for user in users]

        return jsonify({
            'success': True,
            'users': users_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users', methods=['POST'])
@admin_required
def create_user():
    """Cria novo usuário (apenas admin)"""
    try:
        data = request.get_json()

        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        role_str = data.get('role', 'user')

        # Validar role
        try:
            role = UserRole.ADMIN if role_str == 'admin' else UserRole.USER
        except:
            role = UserRole.USER

        result = auth_manager.register_user(username, email, password, full_name, role)
        return jsonify(result)

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['PUT'])
@admin_required
def update_user(user_id):
    """Atualiza usuário (apenas admin)"""
    try:
        data = request.get_json()
        user = User.query.get_or_404(user_id)

        # Atualizar campos
        if 'full_name' in data:
            user.full_name = data['full_name']
        if 'email' in data:
            # Verificar se email já existe
            existing_user = User.query.filter_by(email=data['email']).first()
            if existing_user and existing_user.id != user_id:
                return jsonify({'success': False, 'error': 'Email já está em uso'}), 400
            user.email = data['email']
        if 'role' in data:
            role_str = data['role']
            user.role = UserRole.ADMIN if role_str == 'admin' else UserRole.USER
        if 'is_active' in data:
            user.is_active = data['is_active']

        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Usuário atualizado com sucesso'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>', methods=['DELETE'])
@admin_required
def delete_user(user_id):
    """Desativa usuário (apenas admin)"""
    try:
        user = User.query.get_or_404(user_id)

        # Não permitir deletar o próprio usuário
        current_user_data = auth_manager.get_current_user()
        if current_user_data['id'] == user_id:
            return jsonify({'success': False, 'error': 'Não é possível desativar seu próprio usuário'}), 400

        # Desativar ao invés de deletar
        user.is_active = False
        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Usuário desativado com sucesso'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/users/<int:user_id>/reset-password', methods=['POST'])
@admin_required
def reset_user_password(user_id):
    """Redefine senha do usuário (apenas admin)"""
    try:
        data = request.get_json()
        new_password = data.get('new_password', '')

        if len(new_password) < 6:
            return jsonify({'success': False, 'error': 'Nova senha deve ter pelo menos 6 caracteres'}), 400

        user = User.query.get_or_404(user_id)
        user.password_hash = auth_manager.hash_password(new_password)
        user.updated_at = datetime.utcnow()
        db.session.commit()

        return jsonify({
            'success': True,
            'message': 'Senha redefinida com sucesso'
        })

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/admin/stats')
@admin_required
def get_admin_stats():
    """Estatísticas do sistema (apenas admin)"""
    try:
        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        admin_users = User.query.filter_by(role=UserRole.ADMIN, is_active=True).count()

        from models import Revenda, Vendedor
        total_revendas = Revenda.query.filter_by(ativo=True).count()
        total_vendedores = Vendedor.query.filter_by(ativo=True).count()

        return jsonify({
            'success': True,
            'stats': {
                'total_users': total_users,
                'active_users': active_users,
                'admin_users': admin_users,
                'total_revendas': total_revendas,
                'total_vendedores': total_vendedores
            }
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500