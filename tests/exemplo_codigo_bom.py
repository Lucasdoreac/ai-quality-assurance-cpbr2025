"""
Exemplo de código limpo e bem estruturado para teste.
Este código deve receber score alto (80-90+) do sistema.
"""
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime
import logging


@dataclass
class Usuario:
    """Representa um usuário do sistema."""
    id: int
    nome: str
    email: str
    ativo: bool = True
    criado_em: datetime = None
    
    def __post_init__(self):
        if self.criado_em is None:
            self.criado_em = datetime.now()


class GerenciadorUsuarios:
    """Gerencia operações com usuários."""
    
    def __init__(self):
        self.usuarios: Dict[int, Usuario] = {}
        self.logger = logging.getLogger(__name__)
    
    def criar_usuario(self, nome: str, email: str) -> Usuario:
        """
        Cria um novo usuário.
        
        Args:
            nome: Nome do usuário
            email: Email do usuário
            
        Returns:
            Usuario criado
            
        Raises:
            ValueError: Se email já existe
        """
        if self.buscar_por_email(email):
            raise ValueError(f"Email {email} já existe")
        
        user_id = self._gerar_proximo_id()
        usuario = Usuario(id=user_id, nome=nome, email=email)
        
        self.usuarios[user_id] = usuario
        self.logger.info(f"Usuário criado: {usuario.nome}")
        
        return usuario
    
    def buscar_por_email(self, email: str) -> Optional[Usuario]:
        """Busca usuário por email."""
        for usuario in self.usuarios.values():
            if usuario.email == email:
                return usuario
        return None
    
    def listar_ativos(self) -> List[Usuario]:
        """Lista apenas usuários ativos."""
        return [u for u in self.usuarios.values() if u.ativo]
    
    def desativar_usuario(self, user_id: int) -> bool:
        """
        Desativa um usuário.
        
        Args:
            user_id: ID do usuário
            
        Returns:
            True se desativado com sucesso
        """
        if user_id not in self.usuarios:
            return False
        
        self.usuarios[user_id].ativo = False
        self.logger.info(f"Usuário {user_id} desativado")
        return True
    
    def _gerar_proximo_id(self) -> int:
        """Gera próximo ID sequencial."""
        if not self.usuarios:
            return 1
        return max(self.usuarios.keys()) + 1


def validar_email(email: str) -> bool:
    """
    Valida formato básico de email.
    
    Args:
        email: Email para validar
        
    Returns:
        True se email é válido
    """
    if not email or '@' not in email:
        return False
    
    partes = email.split('@')
    if len(partes) != 2:
        return False
    
    usuario, dominio = partes
    return len(usuario) > 0 and len(dominio) > 0 and '.' in dominio


def calcular_estatisticas_usuarios(usuarios: List[Usuario]) -> Dict[str, int]:
    """
    Calcula estatísticas dos usuários.
    
    Args:
        usuarios: Lista de usuários
        
    Returns:
        Dicionário com estatísticas
    """
    total = len(usuarios)
    ativos = sum(1 for u in usuarios if u.ativo)
    inativos = total - ativos
    
    return {
        'total': total,
        'ativos': ativos,
        'inativos': inativos,
        'percentual_ativos': round((ativos / total * 100), 2) if total > 0 else 0
    }


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Criar gerenciador
    gerenciador = GerenciadorUsuarios()
    
    # Criar alguns usuários
    try:
        user1 = gerenciador.criar_usuario("João Silva", "joao@email.com")
        user2 = gerenciador.criar_usuario("Maria Santos", "maria@email.com")
        user3 = gerenciador.criar_usuario("Pedro Costa", "pedro@email.com")
        
        print(f"Criados {len(gerenciador.usuarios)} usuários")
        
        # Listar ativos
        ativos = gerenciador.listar_ativos()
        print(f"Usuários ativos: {len(ativos)}")
        
        # Desativar um usuário
        gerenciador.desativar_usuario(user2.id)
        
        # Calcular estatísticas
        stats = calcular_estatisticas_usuarios(list(gerenciador.usuarios.values()))
        print(f"Estatísticas: {stats}")
        
    except ValueError as e:
        print(f"Erro: {e}")