"""
Exemplo realista de código empresarial para teste.
Simula código real que poderia existir em uma empresa.
"""
import logging
import json
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import hashlib
import re


class StatusPedido(Enum):
    """Status possíveis de um pedido."""
    PENDENTE = "pendente"
    PROCESSANDO = "processando"
    ENVIADO = "enviado"
    ENTREGUE = "entregue"
    CANCELADO = "cancelado"


class TipoPagamento(Enum):
    """Tipos de pagamento aceitos."""
    CARTAO_CREDITO = "cartao_credito"
    CARTAO_DEBITO = "cartao_debito"
    PIX = "pix"
    BOLETO = "boleto"
    TRANSFERENCIA = "transferencia"


@dataclass
class Cliente:
    """Representa um cliente da empresa."""
    id: int
    nome: str
    email: str
    cpf: str
    telefone: str
    endereco: Dict[str, str]
    data_cadastro: datetime = field(default_factory=datetime.now)
    ativo: bool = True
    
    def __post_init__(self):
        """Validações pós-inicialização."""
        if not self._validar_email():
            raise ValueError(f"Email inválido: {self.email}")
        if not self._validar_cpf():
            raise ValueError(f"CPF inválido: {self.cpf}")
    
    def _validar_email(self) -> bool:
        """Valida formato do email."""
        padrao = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao, self.email) is not None
    
    def _validar_cpf(self) -> bool:
        """Validação básica de CPF."""
        cpf_numeros = re.sub(r'[^0-9]', '', self.cpf)
        return len(cpf_numeros) == 11 and not cpf_numeros == cpf_numeros[0] * 11


@dataclass
class Produto:
    """Representa um produto do catálogo."""
    id: int
    nome: str
    preco: float
    categoria: str
    estoque: int
    descricao: str = ""
    ativo: bool = True
    peso_kg: float = 0.0
    dimensoes_cm: Tuple[float, float, float] = (0, 0, 0)
    
    def calcular_frete(self, cep_destino: str) -> float:
        """Calcula frete baseado no peso e dimensões."""
        # Lógica simplificada de frete
        peso_fator = self.peso_kg * 2.5
        volume = self.dimensoes_cm[0] * self.dimensoes_cm[1] * self.dimensoes_cm[2] / 1000
        volume_fator = volume * 0.3
        
        # Simular diferentes regiões
        if cep_destino.startswith(('01', '02', '03', '04', '05')):
            # São Paulo - mais barato
            frete_base = 15.0
        elif cep_destino.startswith(('20', '21', '22', '23', '24')):
            # Rio de Janeiro
            frete_base = 20.0
        else:
            # Outras regiões
            frete_base = 25.0
        
        return round(frete_base + peso_fator + volume_fator, 2)


@dataclass
class ItemPedido:
    """Item individual de um pedido."""
    produto_id: int
    quantidade: int
    preco_unitario: float
    desconto_percentual: float = 0.0
    
    def calcular_subtotal(self) -> float:
        """Calcula subtotal do item."""
        valor_bruto = self.quantidade * self.preco_unitario
        desconto = valor_bruto * (self.desconto_percentual / 100)
        return round(valor_bruto - desconto, 2)


@dataclass
class Pedido:
    """Representa um pedido de compra."""
    id: int
    cliente_id: int
    itens: List[ItemPedido]
    status: StatusPedido
    tipo_pagamento: TipoPagamento
    data_criacao: datetime = field(default_factory=datetime.now)
    data_entrega_estimada: Optional[datetime] = None
    observacoes: str = ""
    codigo_rastreamento: Optional[str] = None
    
    def calcular_total_produtos(self) -> float:
        """Calcula total dos produtos."""
        return sum(item.calcular_subtotal() for item in self.itens)
    
    def calcular_frete_total(self, produtos: Dict[int, Produto], cep_destino: str) -> float:
        """Calcula frete total do pedido."""
        frete_total = 0.0
        for item in self.itens:
            if item.produto_id in produtos:
                produto = produtos[item.produto_id]
                frete_item = produto.calcular_frete(cep_destino) * item.quantidade
                frete_total += frete_item
        return round(frete_total, 2)
    
    def calcular_total_final(self, produtos: Dict[int, Produto], cep_destino: str) -> float:
        """Calcula valor total final do pedido."""
        total_produtos = self.calcular_total_produtos()
        frete = self.calcular_frete_total(produtos, cep_destino)
        return round(total_produtos + frete, 2)
    
    def gerar_codigo_rastreamento(self) -> str:
        """Gera código de rastreamento único."""
        data_str = self.data_criacao.strftime("%Y%m%d")
        hash_input = f"{self.id}{self.cliente_id}{data_str}"
        hash_object = hashlib.md5(hash_input.encode())
        return f"BR{hash_object.hexdigest()[:10].upper()}"


class GerenciadorPedidos:
    """Gerencia operações com pedidos."""
    
    def __init__(self):
        self.pedidos: Dict[int, Pedido] = {}
        self.clientes: Dict[int, Cliente] = {}
        self.produtos: Dict[int, Produto] = {}
        self.logger = logging.getLogger(__name__)
        self._proximo_id_pedido = 1
    
    def adicionar_cliente(self, cliente: Cliente) -> None:
        """Adiciona cliente ao sistema."""
        if cliente.id in self.clientes:
            raise ValueError(f"Cliente {cliente.id} já existe")
        
        self.clientes[cliente.id] = cliente
        self.logger.info(f"Cliente adicionado: {cliente.nome}")
    
    def adicionar_produto(self, produto: Produto) -> None:
        """Adiciona produto ao catálogo."""
        if produto.id in self.produtos:
            raise ValueError(f"Produto {produto.id} já existe")
        
        self.produtos[produto.id] = produto
        self.logger.info(f"Produto adicionado: {produto.nome}")
    
    def criar_pedido(self, cliente_id: int, itens: List[ItemPedido], 
                     tipo_pagamento: TipoPagamento, observacoes: str = "") -> Pedido:
        """Cria um novo pedido."""
        if cliente_id not in self.clientes:
            raise ValueError(f"Cliente {cliente_id} não encontrado")
        
        # Validar disponibilidade dos produtos
        for item in itens:
            if item.produto_id not in self.produtos:
                raise ValueError(f"Produto {item.produto_id} não encontrado")
            
            produto = self.produtos[item.produto_id]
            if not produto.ativo:
                raise ValueError(f"Produto {produto.nome} não está ativo")
            
            if produto.estoque < item.quantidade:
                raise ValueError(f"Estoque insuficiente para {produto.nome}")
        
        # Criar pedido
        pedido = Pedido(
            id=self._proximo_id_pedido,
            cliente_id=cliente_id,
            itens=itens,
            status=StatusPedido.PENDENTE,
            tipo_pagamento=tipo_pagamento,
            observacoes=observacoes
        )
        
        # Reservar estoque
        for item in itens:
            self.produtos[item.produto_id].estoque -= item.quantidade
        
        self.pedidos[pedido.id] = pedido
        self._proximo_id_pedido += 1
        
        self.logger.info(f"Pedido criado: {pedido.id} para cliente {cliente_id}")
        return pedido
    
    def processar_pagamento(self, pedido_id: int) -> bool:
        """Simula processamento de pagamento."""
        if pedido_id not in self.pedidos:
            return False
        
        pedido = self.pedidos[pedido_id]
        if pedido.status != StatusPedido.PENDENTE:
            return False
        
        # Simular delay de processamento baseado no tipo
        if pedido.tipo_pagamento == TipoPagamento.BOLETO:
            # Boleto demora mais
            pedido.data_entrega_estimada = datetime.now() + timedelta(days=5)
        elif pedido.tipo_pagamento == TipoPagamento.PIX:
            # PIX é instantâneo
            pedido.data_entrega_estimada = datetime.now() + timedelta(days=2)
        else:
            # Cartão
            pedido.data_entrega_estimada = datetime.now() + timedelta(days=3)
        
        pedido.status = StatusPedido.PROCESSANDO
        pedido.codigo_rastreamento = pedido.gerar_codigo_rastreamento()
        
        self.logger.info(f"Pagamento processado para pedido {pedido_id}")
        return True
    
    def atualizar_status_entrega(self, pedido_id: int, novo_status: StatusPedido) -> bool:
        """Atualiza status de entrega do pedido."""
        if pedido_id not in self.pedidos:
            return False
        
        pedido = self.pedidos[pedido_id]
        status_anterior = pedido.status
        pedido.status = novo_status
        
        self.logger.info(f"Status do pedido {pedido_id} alterado: {status_anterior.value} → {novo_status.value}")
        return True
    
    def gerar_relatorio_vendas(self, data_inicio: datetime, data_fim: datetime) -> Dict:
        """Gera relatório de vendas por período."""
        pedidos_periodo = [
            p for p in self.pedidos.values()
            if data_inicio <= p.data_criacao <= data_fim
        ]
        
        total_vendas = 0.0
        vendas_por_status = {}
        vendas_por_pagamento = {}
        
        for pedido in pedidos_periodo:
            cliente = self.clientes[pedido.cliente_id]
            cep = cliente.endereco.get('cep', '01000-000')
            total = pedido.calcular_total_final(self.produtos, cep)
            
            total_vendas += total
            
            # Agrupar por status
            status = pedido.status.value
            vendas_por_status[status] = vendas_por_status.get(status, 0) + total
            
            # Agrupar por tipo pagamento
            pagamento = pedido.tipo_pagamento.value
            vendas_por_pagamento[pagamento] = vendas_por_pagamento.get(pagamento, 0) + total
        
        return {
            'periodo': f"{data_inicio.strftime('%Y-%m-%d')} a {data_fim.strftime('%Y-%m-%d')}",
            'total_vendas': round(total_vendas, 2),
            'quantidade_pedidos': len(pedidos_periodo),
            'ticket_medio': round(total_vendas / len(pedidos_periodo), 2) if pedidos_periodo else 0,
            'vendas_por_status': vendas_por_status,
            'vendas_por_pagamento': vendas_por_pagamento
        }


# Funções utilitárias
def formatar_cpf(cpf: str) -> str:
    """Formata CPF com pontos e traço."""
    cpf_numeros = re.sub(r'[^0-9]', '', cpf)
    if len(cpf_numeros) != 11:
        return cpf
    return f"{cpf_numeros[:3]}.{cpf_numeros[3:6]}.{cpf_numeros[6:9]}-{cpf_numeros[9:]}"


def calcular_desconto_cliente_fiel(cliente: Cliente, valor_pedido: float) -> float:
    """Calcula desconto para cliente fiel."""
    dias_cadastro = (datetime.now() - cliente.data_cadastro).days
    
    if dias_cadastro > 365:  # Mais de 1 ano
        return min(valor_pedido * 0.1, 100.0)  # 10% até R$ 100
    elif dias_cadastro > 180:  # Mais de 6 meses
        return min(valor_pedido * 0.05, 50.0)   # 5% até R$ 50
    else:
        return 0.0


# Exemplo de uso do sistema
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    
    # Criar gerenciador
    gerenciador = GerenciadorPedidos()
    
    # Adicionar cliente
    cliente = Cliente(
        id=1,
        nome="João Silva",
        email="joao.silva@email.com",
        cpf="123.456.789-00",
        telefone="(11) 99999-9999",
        endereco={
            "rua": "Rua das Flores, 123",
            "cidade": "São Paulo",
            "estado": "SP",
            "cep": "01234-567"
        }
    )
    gerenciador.adicionar_cliente(cliente)
    
    # Adicionar produtos
    produto1 = Produto(
        id=1,
        nome="Notebook Gamer",
        preco=2500.00,
        categoria="Eletrônicos",
        estoque=10,
        peso_kg=2.5,
        dimensoes_cm=(35, 25, 3)
    )
    
    produto2 = Produto(
        id=2,
        nome="Mouse Wireless",
        preco=150.00,
        categoria="Acessórios",
        estoque=50,
        peso_kg=0.2,
        dimensoes_cm=(12, 8, 4)
    )
    
    gerenciador.adicionar_produto(produto1)
    gerenciador.adicionar_produto(produto2)
    
    # Criar pedido
    itens = [
        ItemPedido(produto_id=1, quantidade=1, preco_unitario=2500.00),
        ItemPedido(produto_id=2, quantidade=2, preco_unitario=150.00, desconto_percentual=10)
    ]
    
    try:
        pedido = gerenciador.criar_pedido(
            cliente_id=1,
            itens=itens,
            tipo_pagamento=TipoPagamento.PIX,
            observacoes="Entrega urgente"
        )
        
        print(f"Pedido criado: {pedido.id}")
        print(f"Total: R$ {pedido.calcular_total_final(gerenciador.produtos, cliente.endereco['cep'])}")
        
        # Processar pagamento
        if gerenciador.processar_pagamento(pedido.id):
            print(f"Pagamento processado. Código rastreamento: {pedido.codigo_rastreamento}")
        
        # Gerar relatório
        relatorio = gerenciador.gerar_relatorio_vendas(
            datetime.now() - timedelta(days=30),
            datetime.now()
        )
        print(f"Relatório mensal: {json.dumps(relatorio, indent=2, ensure_ascii=False)}")
        
    except ValueError as e:
        print(f"Erro ao criar pedido: {e}")