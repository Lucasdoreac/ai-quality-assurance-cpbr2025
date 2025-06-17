"""
Exemplo de código com múltiplos problemas para demonstração.
Este código deve receber score baixo e muitos code smells detectados.
"""

# Muitas importações desnecessárias
import os, sys, json, time, datetime, random, math, re, urllib, socket
from typing import *

# Variáveis globais (code smell)
DADOS_GLOBAIS = {}
CONTADOR_GLOBAL = 0
CACHE_GLOBAL = []

# Função com muitos parâmetros (Long Parameter List)
def processar_dados_complexos(dados, tipo, formato, validar, cache, debug, log_level, timeout, retries, callback, metadata, opcoes_extras, configuracao_avancada, parametros_sistema):
    """Função com muitos parâmetros - será detectado como code smell."""
    global CONTADOR_GLOBAL, DADOS_GLOBAIS
    
    # Complexidade ciclomática muito alta
    resultado = []
    for item in dados:
        if tipo == "A":
            if formato == "json":
                if validar:
                    if cache:
                        if debug:
                            if log_level > 0:
                                if timeout > 0:
                                    if retries > 0:
                                        if callback is not None:
                                            if metadata:
                                                if opcoes_extras:
                                                    if configuracao_avancada:
                                                        if parametros_sistema:
                                                            # Aninhamento profundo demais
                                                            resultado.append(item * 2)
                                                        else:
                                                            resultado.append(item)
                                                    else:
                                                        resultado.append(item / 2)
                                                else:
                                                    resultado.append(item + 1)
                                            else:
                                                resultado.append(item - 1)
                                        else:
                                            resultado.append(item * 3)
                                    else:
                                        resultado.append(item / 3)
                                else:
                                    resultado.append(item + 5)
                            else:
                                resultado.append(item - 5)
                        else:
                            resultado.append(item * 10)
                    else:
                        resultado.append(item / 10)
                else:
                    resultado.append(item + 100)
            else:
                resultado.append(item - 100)
        else:
            resultado.append(item)
    
    CONTADOR_GLOBAL += 1
    DADOS_GLOBAIS[str(CONTADOR_GLOBAL)] = resultado
    return resultado


# Classe muito grande (Large Class / God Object)
class ProcessadorUniversal:
    """Classe que faz tudo - será detectada como God Object."""
    
    def __init__(self, config, database, cache, logger, api_client, file_manager, email_service, pdf_generator, xml_parser, json_handler, csv_processor, excel_reader, image_processor, audio_converter, video_encoder):
        # Muitos atributos
        self.config = config
        self.database = database
        self.cache = cache
        self.logger = logger
        self.api_client = api_client
        self.file_manager = file_manager
        self.email_service = email_service
        self.pdf_generator = pdf_generator
        self.xml_parser = xml_parser
        self.json_handler = json_handler
        self.csv_processor = csv_processor
        self.excel_reader = excel_reader
        self.image_processor = image_processor
        self.audio_converter = audio_converter
        self.video_encoder = video_encoder
        self.internal_state = {}
        self.cache_data = {}
        self.temp_files = []
        self.active_connections = []
        self.processing_queue = []
    
    # Muitos métodos (Large Class)
    def processar_arquivos(self): pass
    def validar_dados(self): pass
    def conectar_database(self): pass
    def executar_query(self): pass
    def cachear_resultado(self): pass
    def limpar_cache(self): pass
    def enviar_email(self): pass
    def gerar_pdf(self): pass
    def processar_xml(self): pass
    def processar_json(self): pass
    def processar_csv(self): pass
    def ler_excel(self): pass
    def processar_imagem(self): pass
    def converter_audio(self): pass
    def encodar_video(self): pass
    def fazer_backup(self): pass
    def restaurar_backup(self): pass
    def gerar_relatorio(self): pass
    def exportar_dados(self): pass
    def importar_dados(self): pass
    def sincronizar_dados(self): pass
    def validar_permissoes(self): pass
    def autenticar_usuario(self): pass
    def gerenciar_sessao(self): pass
    def processar_pagamento(self): pass
    def calcular_impostos(self): pass
    def gerar_fatura(self): pass
    def enviar_notificacao(self): pass
    def processar_webhook(self): pass
    def gerenciar_filas(self): pass
    
    # Método muito longo (Long Method)
    def metodo_gigante_que_faz_tudo(self, dados, opcoes):
        """Método muito longo que faz muitas coisas - será detectado."""
        # Mais de 50 linhas de código complexo
        resultado = {}
        
        # Validação inicial
        if not dados:
            return None
        if not opcoes:
            opcoes = {}
        
        # Processamento principal
        for i, item in enumerate(dados):
            if i % 2 == 0:
                if isinstance(item, dict):
                    for chave, valor in item.items():
                        if isinstance(valor, str):
                            if len(valor) > 10:
                                if valor.startswith("http"):
                                    # Processar URL
                                    resultado[f"url_{i}"] = self._processar_url(valor)
                                elif valor.startswith("email"):
                                    # Processar email
                                    resultado[f"email_{i}"] = self._processar_email(valor)
                                else:
                                    # Processar texto normal
                                    resultado[f"texto_{i}"] = valor.upper()
                            else:
                                resultado[f"pequeno_{i}"] = valor.lower()
                        elif isinstance(valor, (int, float)):
                            if valor > 100:
                                resultado[f"grande_{i}"] = valor * 2
                            elif valor > 50:
                                resultado[f"medio_{i}"] = valor * 1.5
                            else:
                                resultado[f"pequeno_{i}"] = valor
                        elif isinstance(valor, list):
                            resultado[f"lista_{i}"] = len(valor)
                        else:
                            resultado[f"outro_{i}"] = str(valor)
                elif isinstance(item, list):
                    for j, subitem in enumerate(item):
                        resultado[f"sub_{i}_{j}"] = subitem
                elif isinstance(item, (int, float)):
                    resultado[f"numero_{i}"] = item ** 2
                else:
                    resultado[f"desconhecido_{i}"] = str(item)
            else:
                # Processamento diferente para índices ímpares
                resultado[f"impar_{i}"] = item
        
        # Pós-processamento
        if "opcao_especial" in opcoes:
            for chave in list(resultado.keys()):
                if chave.startswith("url_"):
                    resultado[chave] = resultado[chave] + "_processado"
        
        # Limpeza
        chaves_para_remover = []
        for chave, valor in resultado.items():
            if valor is None or valor == "":
                chaves_para_remover.append(chave)
        
        for chave in chaves_para_remover:
            del resultado[chave]
        
        # Log detalhado
        self.logger.info(f"Processados {len(dados)} itens")
        self.logger.info(f"Resultado tem {len(resultado)} entradas")
        
        return resultado
    
    def _processar_url(self, url): 
        return url.replace("http://", "https://")
    
    def _processar_email(self, email):
        return email.lower().strip()


# Função com código duplicado
def calcular_preco_produto_a(preco_base, desconto, taxa):
    """Calcula preço do produto A."""
    preco_com_desconto = preco_base * (1 - desconto)
    preco_com_taxa = preco_com_desconto * (1 + taxa)
    preco_final = preco_com_taxa * 1.1  # Margem
    return round(preco_final, 2)


def calcular_preco_produto_b(preco_base, desconto, taxa):
    """Calcula preço do produto B."""
    # Código duplicado - mesma lógica que produto A
    preco_com_desconto = preco_base * (1 - desconto)
    preco_com_taxa = preco_com_desconto * (1 + taxa)
    preco_final = preco_com_taxa * 1.1  # Margem
    return round(preco_final, 2)


def calcular_preco_produto_c(preco_base, desconto, taxa):
    """Calcula preço do produto C."""
    # Mais código duplicado
    preco_com_desconto = preco_base * (1 - desconto)
    preco_com_taxa = preco_com_desconto * (1 + taxa)
    preco_final = preco_com_taxa * 1.1  # Margem
    return round(preco_final, 2)


# Função sem documentação e com lógica confusa
def func_misteriosa(x, y, z):
    if x:
        if y:
            if z:
                return x + y + z
            else:
                return x + y
        else:
            if z:
                return x + z
            else:
                return x
    else:
        if y:
            if z:
                return y + z
            else:
                return y
        else:
            if z:
                return z
            else:
                return 0


# Classe com responsabilidades misturadas (Low Cohesion)
class GerenciadorMisturado:
    """Classe que mistura responsabilidades."""
    
    def __init__(self):
        self.usuarios = []
        self.produtos = []
        self.vendas = []
        self.configuracoes = {}
    
    def adicionar_usuario(self, usuario):
        self.usuarios.append(usuario)
    
    def calcular_estoque(self):
        # Não tem relação com usuários
        return sum(p.get('estoque', 0) for p in self.produtos)
    
    def enviar_email_marketing(self):
        # Responsabilidade diferente
        for usuario in self.usuarios:
            print(f"Enviando email para {usuario}")
    
    def gerar_relatorio_fiscal(self):
        # Outra responsabilidade
        return {"vendas": len(self.vendas), "total": sum(v.get('valor', 0) for v in self.vendas)}
    
    def fazer_backup_database(self):
        # Mais uma responsabilidade
        print("Fazendo backup...")


# Uso com práticas ruins
if __name__ == "__main__":
    # Sem tratamento de erro
    dados = [1, 2, 3, "texto", None, [1, 2], {"a": 1}]
    resultado = processar_dados_complexos(
        dados, "A", "json", True, True, True, 1, 30, 3, 
        None, {}, {}, {}, {}
    )
    
    # Variáveis com nomes ruins
    p = ProcessadorUniversal(None, None, None, None, None, None, None, None, None, None, None, None, None, None, None)
    x = p.metodo_gigante_que_faz_tudo(dados, {"opcao_especial": True})
    
    # Sem validação
    preco = calcular_preco_produto_a(100, 0.1, 0.05)
    
    print("Processamento concluído com muitos problemas!")