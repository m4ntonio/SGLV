"""
SGLV — Sistema Gerenciador de Loja de Varejo com Gestão de Estoque de Produtos
===============================================
Disciplina : Computational Thinking with Python

Integrantes: Mario Antonio Oliveira RM : 567713
             Vinicius Augusto Silva RM : 566830
===============================================
Etapa 1: Cadastro de Produtos
Etapa 2: Gestão de Estoque
Integração: Banco de dados SQLite
"""

import os        # Usada para comandos do sistema operacional (ex: limpar tela)
import sqlite3   # Biblioteca para trabalhar com banco de dados SQLite
import logging   # Sistema de logs para registrar eventos do sistema

# --- Configuração do sistema de log ---

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    encoding="utf-8",
    filename="historico.log"
)
logger = logging.getLogger("SGLV")   # Identificador do sistema nos logs

DB_FILE = "produto.db"

# --- Exceção customizada para cancelamento pelo usuário ---
class CancelamentoUsuario(Exception):
    """
    Exceção criada para controlar cancelamentos do usuário.
    Disparada quando o usuário digita 'S' em qualquer campo de entrada,
    sinalizando que deseja cancelar a operação atual e voltar ao menu.
    """
    pass

# --- ETAPA 1: Classe Produto ---
class Produto:
    """
    Classe que representa um produto dentro do sistema.

    Atributos:
        codigo (str)        : Identificador único do produto.
        nome (str)          : Nome do produto.
        categoria (str)     : Categoria do produto (ex: "Grãos e Cereais").
        quantidade (int)    : Quantidade atual em estoque.
        preco (float)       : Preço de venda unitário.
        descricao (str)     : Detalhes adicionais do produto.
        fornecedor (str)    : Nome do fornecedor.
        estoque_minimo (int): Quantidade mínima antes de emitir alerta.
    """

    def __init__(
        self,
        codigo: str,
        nome: str,
        categoria: str,
        quantidade: int,
        preco: float,
        descricao: str,
        fornecedor: str,
        estoque_minimo: int = 0,
    ):
        if quantidade < 0:
            raise ValueError("A quantidade inicial não pode ser negativa.")
        if preco < 0:
            raise ValueError("O preço não pode ser negativo.")

        self.codigo         = codigo
        self.nome           = nome
        self.categoria      = categoria
        self.quantidade     = quantidade
        self.preco          = preco
        self.descricao      = descricao
        self.fornecedor     = fornecedor
        self.estoque_minimo = estoque_minimo

    def exibir_detalhes(self) -> None:
        """Exibe todos os atributos do produto de forma formatada."""
        status = f"⚠︎  ESTOQUE BAIXO: {self.quantidade}" if self.quantidade <= self.estoque_minimo else f"☑︎  ESTOQUE ATUAL: {self.quantidade}"

        # Calcula a largura dinamicamente baseada no conteúdo mais largo
        linhas = [
            f" Código        : {self.codigo}",
            f" Nome          : {self.nome}",
            f" Categoria     : {self.categoria}",
            f" Quantidade    : {self.quantidade} unidades",
            f" Estoque mín.  : {self.estoque_minimo} unidades",
            f" Preço         : R$ {self.preco:.2f}",
            f" Fornecedor    : {self.fornecedor}",
            f" Descrição     : {self.descricao}",
            f" Status        : {status}",
        ]
        sep = "=" * max(len(l) for l in linhas)

        print(f"\n{sep}")
        print(" DETALHES DO PRODUTO")
        print(sep)
        for linha in linhas[:-1]:
            print(linha)
        print(sep)
        print(linhas[-1])
        print(f"{sep}\n")

# ===========================================================================
# ETAPA 3 — Classe ItemVenda e Venda
# ===========================================================================
# Cole após a classe Produto
 
class ItemVenda:
    """
    Representa um item individual dentro de uma venda.
 
    Atributos:
        codigo     : Código do produto vendido.
        nome       : Nome do produto vendido.
        quantidade : Quantidade vendida.
        preco_unit : Preço unitário no momento da venda.
        subtotal   : Valor total do item (quantidade x preco_unit).
    """
 
    def __init__(self, codigo: str, nome: str, quantidade: int, preco_unit: float):
        self.codigo     = codigo
        self.nome       = nome
        self.quantidade = quantidade
        self.preco_unit = preco_unit
        self.subtotal   = quantidade * preco_unit
 
 
class Venda:
    """
    Representa uma venda realizada no SuperMais.
 
    Atributos:
        id_venda   : Código único da venda (ex: VDA-001).
        data_hora  : Data e hora da venda.
        itens      : Lista de ItemVenda da venda.
        desconto   : Percentual de desconto aplicado (0 a 100).
        total      : Valor total sem desconto.
        total_final: Valor total após desconto.
    """
 
    def __init__(self, id_venda: str, data_hora: str, itens: list, desconto: float = 0.0):
        self.id_venda    = id_venda
        self.data_hora   = data_hora
        self.itens       = itens
        self.desconto    = desconto
        self.total       = sum(item.subtotal for item in itens)
        self.total_final = self.total * (1 - desconto / 100)


# --- ETAPA 2: Classe GerenciadorEstoque com SQLite ---
class GerenciadorEstoque:
    """
    Gerencia o catálogo de produtos e as operações de estoque,
    com persistência em banco de dados SQLite local.

    O banco é criado automaticamente no primeiro uso e salvo no
    arquivo definido pela constante DB_FILE.
    """

    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self._inicializar_banco()

    def _gerar_codigo(self, categoria: str) -> str:
        """
        Gera automaticamente o código do produto baseado na categoria.
        Extrai as 3 primeiras letras da categoria e adiciona um sequencial.
        Exemplo: categoria 'Grãos e Cereais' → 'GRA-001', 'GRA-002'...
        """
        import unicodedata
        # Remove acentos antes de extrair o prefixo
        categoria_sem_acento = unicodedata.normalize('NFKD', categoria).encode('ASCII', 'ignore').decode('ASCII')
        prefixo = ''.join(c for c in categoria_sem_acento.upper() if c.isalpha())[:3]

        with self._conectar() as conn:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM produtos WHERE codigo LIKE ?",
                (f"{prefixo}-%",)
            )
            total = cursor.fetchone()[0]

        return f"{prefixo}-{total + 1:04d}"

    # --- Conexão e inicialização do banco ---

    def _conectar(self) -> sqlite3.Connection:
        """Abre e retorna uma conexão com o banco SQLite."""
        return sqlite3.connect(self.db_file)

    def _inicializar_banco(self) -> None:
        """
        Cria as tabelas 'produtos' e 'movimentacoes' no banco caso não existam.
        Executado automaticamente na inicialização do gerenciador.
        """
        with self._conectar() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS produtos (
                    codigo          TEXT PRIMARY KEY,
                    nome            TEXT NOT NULL,
                    categoria       TEXT NOT NULL,
                    quantidade      INTEGER NOT NULL,
                    preco           REAL NOT NULL,
                    descricao       TEXT,
                    fornecedor      TEXT,
                    estoque_minimo  INTEGER NOT NULL DEFAULT 5
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS movimentacoes (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    data_hora   TEXT NOT NULL,
                    tipo        TEXT NOT NULL,
                    codigo      TEXT NOT NULL,
                    nome        TEXT NOT NULL,
                    quantidade  INTEGER NOT NULL,
                    origem      TEXT NOT NULL
                )
            """)
            conn.commit()

    # --- Conversão de dados do banco ---

    def _linha_para_produto(self, linha: tuple) -> Produto:
        """Converte uma linha do banco (tuple) em um objeto Produto."""
        codigo, nome, categoria, quantidade, preco, descricao, fornecedor, estoque_minimo = linha
        return Produto(codigo, nome, categoria, quantidade, preco, descricao, fornecedor, estoque_minimo)
    
    # --- Verificação de alertas ---

    def _verificar_alerta_estoque(self, produto: Produto) -> None:
        """Emite alerta de estoque baixo via log quando necessário."""
        if produto.quantidade <= produto.estoque_minimo:
            logger.warning(
                f"⚠︎ ALERTA DE ESTOQUE BAIXO | [{produto.codigo}] {produto.nome}: "
                f"{produto.quantidade} unidade(s) (mínimo: {produto.estoque_minimo}). "
                f"Fornecedor: {produto.fornecedor}"
            )

    def _registrar_movimentacao(self, tipo: str, produto: Produto,
                                quantidade: int, origem: str) -> None:
        """
        Registra uma movimentação de estoque no banco de dados.
        Chamado automaticamente pelos métodos de gestão de estoque.

        Args:
            tipo      : Tipo da movimentação (ENTRADA, SAIDA, AJUSTE).
            produto   : Objeto Produto movimentado.
            quantidade: Quantidade movimentada.
            origem    : Origem da movimentação (COMPRA, VENDA, INVENTARIO).
        """
        from datetime import datetime
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        with self._conectar() as conn:
            conn.execute("""
                INSERT INTO movimentacoes
                    (data_hora, tipo, codigo, nome, quantidade, origem)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (data_hora, tipo, produto.codigo, produto.nome, quantidade, origem))
            conn.commit()

    # --- ETAPA 3: Cadastro ---

    def cadastrar_produto(self, produto: Produto) -> None:
        """
        Cadastra um novo produto no banco de dados.

        Raises:
            ValueError: Se já existir um produto com o mesmo código.
        """
        try:
            with self._conectar() as conn:
                conn.execute("""
                    INSERT INTO produtos
                        (codigo, nome, categoria, quantidade, preco, descricao, fornecedor, estoque_minimo)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    produto.codigo, produto.nome, produto.categoria,
                    produto.quantidade, produto.preco, produto.descricao,
                    produto.fornecedor, produto.estoque_minimo
                ))
                conn.commit()
            logger.info(f"☑︎ Produto cadastrado: [{produto.codigo}] {produto.nome}")
            self._verificar_alerta_estoque(produto)
        except sqlite3.IntegrityError:
            raise ValueError(f"Já existe um produto com o código '{produto.codigo}'.")

    def buscar_produto(self, codigo: str) -> Produto:
        """
        Busca e retorna um produto pelo código.

        Raises:
            KeyError: Se o produto não for encontrado.
        """
        with self._conectar() as conn:
            cursor = conn.execute(
                "SELECT * FROM produtos WHERE codigo = ?", (codigo,)
            )
            linha = cursor.fetchone()
        if linha is None:
            raise KeyError(f"Produto com código '{codigo}' não encontrado.")
        return self._linha_para_produto(linha)

    # --- ETAPA 4: Gestão de Estoque ---

    def adicionar_ao_estoque(self, codigo: str, quantidade: int) -> None:
        """
        Aumenta a quantidade em estoque de um produto.

        Args:
            codigo    : Código do produto.
            quantidade: Quantidade a adicionar (deve ser > 0).
        """
        if quantidade <= 0:
            raise ValueError("A quantidade a adicionar deve ser maior que zero.")

        produto = self.buscar_produto(codigo)
        nova_quantidade = produto.quantidade + quantidade

        with self._conectar() as conn:
            conn.execute(
                "UPDATE produtos SET quantidade = ? WHERE codigo = ?",
                (nova_quantidade, codigo)
            )
            conn.commit()
        self._registrar_movimentacao("ENTRADA", produto, quantidade, "COMPRA")

        produto.quantidade = nova_quantidade
        logger.info(
            f"⬆︎ Estoque aumentado | [{codigo}] {produto.nome}: "
            f"+{quantidade} → total {nova_quantidade} unidades"
        )
        self._verificar_alerta_estoque(produto)

    def remover_do_estoque(self, codigo: str, quantidade: int) -> None:
        """
        Reduz a quantidade em estoque de um produto.
        Garante que o estoque nunca fique negativo.

        Args:
            codigo    : Código do produto.
            quantidade: Quantidade a remover (deve ser > 0).
        """
        if quantidade <= 0:
            raise ValueError("A quantidade a remover deve ser maior que zero.")

        produto = self.buscar_produto(codigo)

        if quantidade > produto.quantidade:
            logger.warning(
                f"⚠︎ Remoção parcial | [{codigo}] {produto.nome}: "
                f"solicitado {quantidade}, disponível {produto.quantidade}. "
                f"Estoque será zerado."
            )
            print(f"\n⚠︎  Quantidade solicitada ({quantidade}) maior que o disponível ({produto.quantidade}).")
            print(f"⚠︎  Estoque de '{produto.nome}' será zerado!")
            nova_quantidade = 0
        else:
            nova_quantidade = produto.quantidade - quantidade

        with self._conectar() as conn:
            conn.execute(
                "UPDATE produtos SET quantidade = ? WHERE codigo = ?",
                (nova_quantidade, codigo)
            )
            conn.commit()
        self._registrar_movimentacao("SAIDA", produto, quantidade, "VENDA")

        produto.quantidade = nova_quantidade
        logger.info(
            f"⬇︎ Estoque reduzido | [{codigo}] {produto.nome}: "
            f"total {nova_quantidade} unidades"
        )
        self._verificar_alerta_estoque(produto)

    def atualizar_estoque(self, codigo: str, nova_quantidade: int) -> None:
        """
        Ajusta manualmente a quantidade em estoque (ex: após inventário).

        Args:
            codigo         : Código do produto.
            nova_quantidade: Novo valor absoluto (deve ser >= 0).
        """
        if nova_quantidade < 0:
            raise ValueError("A quantidade em estoque não pode ser negativa.")

        produto = self.buscar_produto(codigo)
        quantidade_anterior = produto.quantidade

        with self._conectar() as conn:
            conn.execute(
                "UPDATE produtos SET quantidade = ? WHERE codigo = ?",
                (nova_quantidade, codigo)
            )
            conn.commit()
        diferenca = abs(nova_quantidade - quantidade_anterior)
        self._registrar_movimentacao("AJUSTE", produto, diferenca, "INVENTARIO")

        produto.quantidade = nova_quantidade
        logger.info(
            f"↪︎ Estoque atualizado | [{codigo}] {produto.nome}: "
            f"{quantidade_anterior} → {nova_quantidade} unidades"
        )
        self._verificar_alerta_estoque(produto)

    def listar_produtos(self) -> None:
        """Exibe uma tabela com todos os produtos cadastrados no banco."""
        with self._conectar() as conn:
            cursor = conn.execute("SELECT * FROM produtos ORDER BY categoria, nome")
            linhas = cursor.fetchall()

        if not linhas:
            print("\nNenhum produto cadastrado ainda.\n")
            return

        print(f"\n{'Código':<9} | {'Nome do produto':<25} | {'Categoria':<18} | {'Qtd Mín.':>5} | {'Preço':>9} | Status")
        print("-" * 110)
        for linha in linhas:
            p = self._linha_para_produto(linha)
            status = f"⚠︎  ESTOQUE BAIXO: {p.quantidade}" if p.quantidade <= p.estoque_minimo else f"☑︎  ESTOQUE ATUAL: {p.quantidade}"
            print(f" {p.codigo:<8} | {p.nome:<25} | {p.categoria:<18} | {p.estoque_minimo:>8} | R${p.preco:>7.2f} | {status}")
        print("-" * 110)
        print(f"Total de produtos: {len(linhas)}\n")

# ===========================================================================
# ETAPA 3 — Classe GerenciadorVendas
# ===========================================================================
# Cole após a classe GerenciadorEstoque
 
class GerenciadorVendas:
    """
    Gerencia o registro de vendas e emissão de recibos,
    com persistência em banco de dados SQLite local.
    """
 
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
        self._inicializar_tabelas()
 
    # -----------------------------------------------------------------------
    # Conexão e inicialização
    # -----------------------------------------------------------------------
 
    def _conectar(self) -> sqlite3.Connection:
        """Abre e retorna uma conexão com o banco SQLite."""
        return sqlite3.connect(self.db_file)
 
    def _inicializar_tabelas(self) -> None:
        """
        Cria as tabelas 'vendas' e 'itens_venda' no banco caso não existam.
        Executado automaticamente na inicialização do gerenciador.
        """
        with self._conectar() as conn:
            # Tabela principal da venda
            conn.execute("""
                CREATE TABLE IF NOT EXISTS vendas (
                    id_venda    TEXT PRIMARY KEY,
                    data_hora   TEXT NOT NULL,
                    total       REAL NOT NULL,
                    desconto    REAL NOT NULL DEFAULT 0,
                    total_final REAL NOT NULL
                )
            """)
            # Tabela dos itens de cada venda
            conn.execute("""
                CREATE TABLE IF NOT EXISTS itens_venda (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    id_venda    TEXT NOT NULL,
                    codigo      TEXT NOT NULL,
                    nome        TEXT NOT NULL,
                    quantidade  INTEGER NOT NULL,
                    preco_unit  REAL NOT NULL,
                    subtotal    REAL NOT NULL,
                    FOREIGN KEY (id_venda) REFERENCES vendas(id_venda)
                )
            """)
            conn.commit()
 
    # -----------------------------------------------------------------------
    # Geração de ID da venda
    # -----------------------------------------------------------------------
 
    def _gerar_id_venda(self) -> str:
        """
        Gera automaticamente o ID da venda no formato VDA-001, VDA-002...
        Consulta o banco para garantir sequencial correto.
        """
        with self._conectar() as conn:
            cursor = conn.execute("SELECT COUNT(*) FROM vendas")
            total = cursor.fetchone()[0]
        return f"VDA-{total + 1:03d}"
 
    # -----------------------------------------------------------------------
    # Registro de venda
    # -----------------------------------------------------------------------
 
    def registrar_venda(self, venda: Venda) -> None:
        """
        Salva a venda e seus itens no banco de dados.
 
        Args:
            venda: Objeto Venda com todos os itens e valores calculados.
        """
        with self._conectar() as conn:
            # Salva o cabeçalho da venda
            conn.execute("""
                INSERT INTO vendas (id_venda, data_hora, total, desconto, total_final)
                VALUES (?, ?, ?, ?, ?)
            """, (venda.id_venda, venda.data_hora, venda.total,
                  venda.desconto, venda.total_final))
 
            # Salva cada item da venda
            for item in venda.itens:
                conn.execute("""
                    INSERT INTO itens_venda
                        (id_venda, codigo, nome, quantidade, preco_unit, subtotal)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (venda.id_venda, item.codigo, item.nome,
                      item.quantidade, item.preco_unit, item.subtotal))
            conn.commit()
 
        logger.info(f"🛒 Venda registrada: [{venda.id_venda}] "
                    f"Total: R$ {venda.total_final:.2f} | "
                    f"Desconto: {venda.desconto}%")
 
    # -----------------------------------------------------------------------
    # Emissão de recibo
    # -----------------------------------------------------------------------
 
    def emitir_recibo(self, venda: Venda) -> None:
        """
        Exibe o recibo da venda formatado no terminal.
        Mostra todos os itens, subtotais, desconto e total final.
        """
        print("\n")
        print("=" * 50)
        print("        🛒  SUPERMERCADO SUPERMAIS")
        print("         Sistema de Gestão — SGLV")
        print("=" * 50)
        print(f"  Venda     : {venda.id_venda}")
        print(f"  Data/Hora : {venda.data_hora}")
        print("-" * 50)
        print(f"  {'Produto':<22} {'Qtd':>4} {'Unit':>8} {'Total':>10}")
        print("-" * 50)
        for item in venda.itens:
            print(f"  {item.nome:<22} {item.quantidade:>4} "
                  f"R${item.preco_unit:>6.2f} R${item.subtotal:>8.2f}")
        print("-" * 50)
        print(f"  {'Subtotal':<35} R${venda.total:>8.2f}")
        if venda.desconto > 0:
            print(f"  {'Desconto (' + str(venda.desconto) + '%)':<35} R${venda.total - venda.total_final:>8.2f}")
        print("=" * 50)
        print(f"  {'TOTAL FINAL':<35} R${venda.total_final:>8.2f}")
        print("=" * 50)
        print("       Obrigado pela preferência!")
        print("=" * 50)

# ===========================================================================
# ETAPA 4 — Classe GerenciadorRelatorios
# ===========================================================================
# Cole após a classe GerenciadorVendas
 
class GerenciadorRelatorios:
    """
    Gera relatórios de vendas, estoque e histórico de movimentações
    a partir dos dados persistidos no banco de dados SQLite.
    """
 
    def __init__(self, db_file: str = DB_FILE):
        self.db_file = db_file
 
    def _conectar(self) -> sqlite3.Connection:
        """Abre e retorna uma conexão com o banco SQLite."""
        return sqlite3.connect(self.db_file)
 
    # -----------------------------------------------------------------------
    # Relatório 1 — Vendas
    # -----------------------------------------------------------------------
 
    def relatorio_vendas(self) -> None:
        """
        Exibe relatório detalhado de todas as vendas realizadas.
        Mostra data, ID, produtos vendidos, quantidade e valor total.
        """
        with self._conectar() as conn:
            cursor = conn.execute(
                "SELECT * FROM vendas ORDER BY data_hora DESC"
            )
            vendas = cursor.fetchall()
 
        if not vendas:
            print("\nNenhuma venda registrada ainda.\n")
            return
 
        total_geral = 0.0
        sep = "=" * 70
 
        print(f"\n{sep}")
        print("  RELATÓRIO DE VENDAS")
        print(sep)
 
        for venda in vendas:
            id_venda, data_hora, total, desconto, total_final = venda
 
            # Busca os itens da venda
            with self._conectar() as conn:
                cursor = conn.execute(
                    "SELECT * FROM itens_venda WHERE id_venda = ?", (id_venda,)
                )
                itens = cursor.fetchall()
 
            print(f"\n  Venda     : {id_venda}  |  Data: {data_hora}")
            print(f"  {'Produto':<25} {'Qtd':>5} {'Unit':>9} {'Subtotal':>10}")
            print("  " + "-" * 55)
            for item in itens:
                _, _, codigo, nome, quantidade, preco_unit, subtotal = item
                print(f"  {nome:<25} {quantidade:>5} "
                      f"R${preco_unit:>7.2f} R${subtotal:>8.2f}")
            print("  " + "-" * 55)
            print(f"  Subtotal: R$ {total:>8.2f}  |  "
                  f"Desconto: {desconto}%  |  "
                  f"Total Final: R$ {total_final:>8.2f}")
            print(f"  {'-' * 55}")
            total_geral += total_final
 
        print(f"\n{sep}")
        print(f"  Total de vendas  : {len(vendas)}")
        print(f"  Receita total    : R$ {total_geral:.2f}")
        print(f"{sep}\n")
 
    # -----------------------------------------------------------------------
    # Relatório 2 — Estoque
    # -----------------------------------------------------------------------
 
    def relatorio_estoque(self) -> None:
        """
        Exibe relatório completo do estoque atual.
        Inclui valor total em estoque e produtos em alerta.
        """
        with self._conectar() as conn:
            cursor = conn.execute(
                "SELECT * FROM produtos ORDER BY categoria, nome"
            )
            linhas = cursor.fetchall()
 
        if not linhas:
            print("\nNenhum produto cadastrado ainda.\n")
            return
 
        valor_total    = 0.0
        total_alertas  = 0
        sep = "=" * 70
 
        print(f"\n{sep}")
        print("  RELATÓRIO DE ESTOQUE")
        print(sep)
        print(f"  {'Código':<12} {'Nome':<25} {'Categoria':<18} "
              f"{'Qtd':>5} {'Preço':>9} {'Total':>10}")
        print("  " + "-" * 65)
 
        for linha in linhas:
            codigo, nome, categoria, quantidade, preco, descricao, fornecedor, estoque_minimo = linha
            subtotal = quantidade * preco
            valor_total += subtotal
            alerta = " ⚠︎" if quantidade <= estoque_minimo else ""
            print(f"  {codigo:<12} {nome:<25} {categoria:<18} "
                  f"{quantidade:>5} R${preco:>7.2f} R${subtotal:>8.2f}{alerta}")
            if quantidade <= estoque_minimo:
                total_alertas += 1
 
        print(f"\n{sep}")
        print(f"  Total de produtos    : {len(linhas)}")
        print(f"  Produtos em alerta   : {total_alertas}")
        print(f"  Valor total em estoque: R$ {valor_total:.2f}")
        print(f"{sep}\n")
 
    # -----------------------------------------------------------------------
    # Relatório 3 — Histórico de Movimentações
    # -----------------------------------------------------------------------
 
    def historico_movimentacoes(self) -> None:
        """
        Exibe o histórico completo de movimentações de estoque.
        Inclui entradas, saídas e ajustes com data e origem.
        """
        with self._conectar() as conn:
            cursor = conn.execute(
                "SELECT * FROM movimentacoes ORDER BY data_hora DESC"
            )
            movimentacoes = cursor.fetchall()
 
        if not movimentacoes:
            print("\nNenhuma movimentação registrada ainda.\n")
            return
 
        sep = "=" * 75
 
        print(f"\n{sep}")
        print("  HISTÓRICO DE MOVIMENTAÇÕES")
        print(sep)
        print(f"  {'Data/Hora':<20} {'Tipo':<10} {'Origem':<12} "
              f"{'Código':<10} {'Produto':<20} {'Qtd':>6}")
        print("  " + "-" * 70)
 
        for mov in movimentacoes:
            id_, data_hora, tipo, codigo, nome, quantidade, origem = mov
            print(f"  {data_hora:<20} {tipo:<10} {origem:<12} "
                  f"{codigo:<10} {nome:<20} {quantidade:>6}")
 
        print(f"\n{sep}")
        print(f"  Total de movimentações: {len(movimentacoes)}")
        print(f"{sep}\n")

# --- Interface ---

def exibir_logo():
    """Exibe o cabeçalho ASCII do sistema."""
    print("""
░██████╗░██████╗░██╗░░░░░██╗░░░██╗
██╔════╝██╔════╝░██║░░░░░██║░░░██║
╚█████╗░██║░░██╗░██║░░░░░╚██╗░██╔╝
░╚═══██╗██║░░╚██╗██║░░░░░░╚████╔╝░
██████╔╝╚██████╔╝███████╗░░╚██╔╝░░
╚═════╝░░╚═════╝░╚══════╝░░░╚═╝░░░

 SGLV 🛒 Sistema Gerenciador de Loja de Varejo
""")

def exibir_opcoes():
    """Exibe o menu principal de opções."""
    print("1. Cadastrar produto")
    print("2. Listar produtos")
    print("3. Adicionar ao estoque")
    print("4. Remover do estoque")
    print("5. Atualizar estoque manualmente")
    print("6. Buscar produto por código")
    print("7. Registrar venda")
    print("8. Relatórios")
    print("9. Sair\n")

def exibir_subtitulo(texto: str):
    """Limpa a tela e exibe um subtítulo formatado."""
    os.system("cls" if os.name == "nt" else "clear")
    linha = "=" * len(texto)
    print(linha)
    print(texto)
    print(linha)
    print()

def voltar_ao_menu_principal():
    """Pausa e retorna ao menu principal."""
    input("\nDigite uma tecla para voltar ao menu ")
    main()

def opcao_invalida():
    """Avisa sobre opção inválida e retorna ao menu."""
    print("Opção inválida!\n")
    voltar_ao_menu_principal()

# --- Helpers de entrada do usuário ---

def _input_int(mensagem: str) -> int:
    """
    Lê um número inteiro do terminal.
    Rejeita valores negativos, textos e campos vazios.
    Repete a solicitação até receber um valor válido.
    Dispara CancelamentoUsuario se o usuário digitar 'S'.
    """
    while True:
        try:
            valor = input(mensagem).strip()
            if valor.upper() == "S":
                raise CancelamentoUsuario()
            numero = int(valor)
            if numero < 0:
                print("Digite um número positivo (ou 'S' para cancelar).")
                continue
            return numero
        except ValueError:
            print("Digite um número inteiro válido (ou 'S' para cancelar).")

def _input_float(mensagem: str) -> float:
    """
    Lê um número decimal do terminal.
    Rejeita valores negativos, textos e campos vazios.
    Aceita vírgula ou ponto como separador decimal (ex: 9,99 ou 9.99).
    Repete a solicitação até receber um valor válido.
    """
    while True:
        try:
            valor = input(mensagem).strip().replace(",", ".")
            if valor.upper() == "S":
                raise CancelamentoUsuario()
            numero = float(valor)
            if numero < 0:
                print("Digite um valor positivo (ex: 9.99 | ou 'S' para cancelar).")
                continue
            return numero
        except ValueError:
            print("Digite um valor numérico válido (ex: 9.99 | ou 'S' para cancelar).")

def _input_nao_vazio(mensagem: str) -> str:
    """
    Lê um texto do terminal.
    Rejeita campos vazios e espaços em branco.
    Repete a solicitação até receber um valor válido.
    Dispara CancelamentoUsuario se o usuário digitar 'S'.
    """
    while True:
        valor = input(mensagem).strip()
        if valor.upper() == "S":
            raise CancelamentoUsuario()
        if valor:
            return valor
        print("Este campo não pode ficar vazio (ou 'S' para cancelar).")

def _input_limit(mensagem: str, limite: int) -> str:
    """
    Lê um texto do terminal respeitando o limite máximo de caracteres.
    Rejeita campos vazios, espaços em branco e textos acima do limite.
    Repete a solicitação até receber um valor válido.
    Dispara CancelamentoUsuario se o usuário digitar 'S'.
    """
    while True:
        valor = input(mensagem).strip()
        if valor.upper() == "S":
            raise CancelamentoUsuario()
        if not valor:
            print(f"Este campo não pode ficar vazio (ou 'S' para cancelar).")
            continue
        if len(valor) > limite:
            print(f"Máximo de {limite} caracteres. Você digitou {len(valor)}.")
            continue
        return valor

# --- Funções de cada opção do menu ---

def cadastrar_produto(gerenciador: GerenciadorEstoque):  # Opção 1
    """Solicita e valida todos os campos necessários para cadastrar um novo produto."""
    exibir_subtitulo("Cadastrar novo produto")
    print("(Digite 'S' em qualquer campo para cancelar)\n")
    while True:
        try:
            nome        = _input_limit    ("Digite o nome do produto         : ", 25)
            categoria   = _input_nao_vazio("Digite a categoria do produto    : ")
            codigo      = gerenciador._gerar_codigo(categoria)
            print(f"Código gerado automaticamente    : {codigo}")
            quantidade  = _input_int      ("Digite a quantidade inicial      : ")
            preco       = _input_float    ("Digite o preço de venda (R$)     : ")
            descricao   = _input_limit    ("Digite a descrição do produto    : ", 25)
            fornecedor  = _input_nao_vazio("Digite o nome do fornecedor      : ")
            estoque_min = _input_int      ("Digite o estoque mínimo          : ")

            produto = Produto(codigo, nome, categoria, quantidade, preco,
                              descricao, fornecedor, estoque_min)
            gerenciador.cadastrar_produto(produto)
            print(f"\nO produto '{nome}' foi cadastrado com sucesso!")
            print("─" * 40)

            continuar = input("\nDeseja cadastrar outro produto? ('S' para sair / 'Enter' para continuar): ").strip().upper()
            print()
            if continuar == "S":
                break

        except CancelamentoUsuario:
            print("\n✖︎ CADASTRO CANCELADO.")
            break
        except (ValueError, KeyError) as e:
            print(f"\nErro: {e}")

    voltar_ao_menu_principal()

def listar_produtos(gerenciador: GerenciadorEstoque):  # Opção 2
    """Exibe todos os produtos cadastrados no estoque."""
    exibir_subtitulo("Listagem de produtos")
    gerenciador.listar_produtos()
    voltar_ao_menu_principal()

def adicionar_ao_estoque(gerenciador: GerenciadorEstoque):  # Opção 3
    """
    Solicita o código do produto e a quantidade a ser adicionada.
    Atualiza o estoque no banco de dados.
    Permanece em loop permitindo adicionar vários produtos seguidos.
    Encerra quando o usuário digitar 'S'.
    """
    exibir_subtitulo("Adicionar ao estoque")
    print("(Digite 'S' em qualquer campo para cancelar)\n")
    while True:
        try:
            codigo     = _input_nao_vazio("Digite o código do produto       : ").upper()
            quantidade = _input_int      ("Digite a quantidade a adicionar  : ")
            gerenciador.adicionar_ao_estoque(codigo, quantidade)
            produto = gerenciador.buscar_produto(codigo)
            print(f"\n☑︎ Estoque atualizado com sucesso!")
            print("─" * 35)
            print(f"  Produto    : {produto.nome}")
            print(f"  Adicionado : +{quantidade} unidades")
            print(f"  Total      : {produto.quantidade} unidades")
            print("─" * 35 + "\n")

            continuar = input("Deseja adicionar outro produto? ('S' para sair / 'Enter' para continuar): ").strip().upper()
            print()
            if continuar == "S":
                break

        except CancelamentoUsuario:
            print("\nOperação cancelada.")
            main()
            return
        except (ValueError, KeyError) as e:
            print(f"\nErro: {e}. Tente novamente ou digite 'S' para cancelar.\n")
    main()

def remover_do_estoque(gerenciador: GerenciadorEstoque):  # Opção 4
    """
    Solicita o código do produto e a quantidade a ser removida.
    Atualiza o estoque no banco de dados.
    Alerta se a quantidade solicitada for maior que o disponível.
    Permanece em loop permitindo remover vários produtos seguidos.
    Encerra quando o usuário digitar 'S'.
    """
    exibir_subtitulo("Remover do estoque")
    print("(Digite 'S' em qualquer campo para cancelar)\n")
    while True:
        try:
            codigo     = _input_nao_vazio("Digite o código do produto       : ").upper()
            quantidade = _input_int      ("Digite a quantidade a remover    : ")
            gerenciador.remover_do_estoque(codigo, quantidade)
            produto = gerenciador.buscar_produto(codigo)
            print(f"\n☑︎ Estoque atualizado com sucesso!")
            print("─" * 35)
            print(f"  Produto    : {produto.nome}")
            print(f"  Removido   : -{quantidade} unidades")
            print(f"  Total      : {produto.quantidade} unidades")

            # Alerta 1 já tratado dentro do método remover_do_estoque

            # Alerta 2 — estoque zerado
            if produto.quantidade == 0:
                print(f"  ⚠︎  ESTOQUE ZERADO — REPOSIÇÃO URGENTE!")
                print(f"  ⚠︎  Fornecedor: {produto.fornecedor}")

            # Alerta 3 — estoque baixo
            elif produto.quantidade <= produto.estoque_minimo:
                print(f"  ⚠︎  ESTOQUE BAIXO — REPOSIÇÃO NECESSÁRIA!")
                print(f"  ⚠︎  Mínimo     : {produto.estoque_minimo} unidades")
            
            print("─" * 35 + "\n")

            continuar = input("Deseja remover outro produto? ('S' para sair / 'Enter' para continuar): ").strip().upper()
            print()
            if continuar == "S":
                break

        except CancelamentoUsuario:
            print("\nOperação cancelada.")
            main()
            return
        except (ValueError, KeyError) as e:
            print(f"\nErro: {e}. Tente novamente ou digite 'S' para cancelar.\n")
    main()

def atualizar_estoque(gerenciador: GerenciadorEstoque):  # Opção 5
    """
    Solicita o código do produto e a nova quantidade total.
    Sobrescreve a quantidade atual no banco de dados.
    Útil para correções após inventário físico.
    Permanece em loop permitindo atualizar vários produtos seguidos.
    Encerra quando o usuário digitar 'S'.
    """
    exibir_subtitulo("Atualizar estoque manualmente")
    print("(Digite 'S' em qualquer campo para cancelar)\n")
    while True:
        try:
            codigo          = _input_nao_vazio("Digite o código do produto       : ").upper()
            nova_quantidade = _input_int      ("Digite a nova quantidade total   : ")
            produto_antes   = gerenciador.buscar_produto(codigo)
            quantidade_antes = produto_antes.quantidade
            gerenciador.atualizar_estoque(codigo, nova_quantidade)
            produto = gerenciador.buscar_produto(codigo)
            print(f"\n☑︎ Estoque atualizado com sucesso!")
            print("─" * 35)
            print(f"  Produto    : {produto.nome}")
            print(f"  Anterior   : {quantidade_antes} unidades")
            print(f"  Atual      : {produto.quantidade} unidades")
            print("─" * 35 + "\n")

            continuar = input("Deseja atualizar outro produto? ('S' para sair / 'Enter' para continuar): ").strip().upper()
            print()
            if continuar == "S":
                break

        except CancelamentoUsuario:
            print("\nOperação cancelada.")
            main()
            return
        except (ValueError, KeyError) as e:
            print(f"\nErro: {e}. Tente novamente ou digite 'S' para cancelar.\n")
    main()

def buscar_produto(gerenciador: GerenciadorEstoque):  # Opção 6
    """Solicita o código do produto e exibe todos os seus detalhes."""
    exibir_subtitulo("Buscar produto por código")
    while True:
        try:
            codigo  = _input_nao_vazio("Digite o código do produto ou 'S' para cancelar: ").upper()
            produto = gerenciador.buscar_produto(codigo)
            produto.exibir_detalhes()
        except CancelamentoUsuario:
            print("\nOperação cancelada.")
            break   # usuário cancelou, sai do loop
        except KeyError:
            print(f"\nProduto não encontrado. Tente novamente ou digite 'S' para cancelar.\n")

    voltar_ao_menu_principal()

# ===========================================================================
# ETAPA 3 — Funções do menu de vendas
# ===========================================================================
# Cole no bloco de funções do menu existente
 
def registrar_venda(gerenciador_estoque: GerenciadorEstoque,
                    gerenciador_vendas: GerenciadorVendas):  # Opção 7
    """
    Solicita os produtos e quantidades para registrar uma nova venda.
    Atualiza o estoque automaticamente após confirmação.
    Emite o recibo ao final da venda.
    Permite aplicar desconto antes de confirmar.
    Encerra quando o usuário confirmar ou cancelar a venda.
    """
    from datetime import datetime
 
    exibir_subtitulo("Registrar venda")
    print("(Digite 'S' em qualquer campo para cancelar)\n")
 
    itens = []  # lista de itens da venda
 
    # --- Adição de produtos à venda ---
    gerenciador_estoque.listar_produtos()
 
    while True:
        try:
            print(f"Itens na venda: {len(itens)} | "
                  f"Subtotal: R$ {sum(i.subtotal for i in itens):.2f}")
            print("(Enter sem código para finalizar a venda)\n")
 
            codigo = input("Código do produto (ou Enter para finalizar): ").strip().upper()
 
            # Enter sem código — vai para confirmação
            if codigo == "":
                if not itens:
                    print("\n⚠︎  Nenhum produto adicionado. Adicione pelo menos um produto.\n")
                    continue
                break
 
            # S — cancela a venda
            if codigo == "S":
                raise CancelamentoUsuario()
 
            # Busca o produto
            produto = gerenciador_estoque.buscar_produto(codigo)
 
            # Pede a quantidade
            quantidade = _input_int("Quantidade                         : ")
 
            # Verifica se há estoque suficiente
            if quantidade > produto.quantidade:
                print(f"\n⚠︎  Estoque insuficiente! Disponível: {produto.quantidade} unidades.\n")
                continue
 
            # Adiciona o item à venda
            item = ItemVenda(produto.codigo, produto.nome, quantidade, produto.preco)
            itens.append(item)
            print(f"\n☑︎  {produto.nome} adicionado! Subtotal: R$ {item.subtotal:.2f}\n")
 
        except CancelamentoUsuario:
            print("\nVenda cancelada.")
            voltar_ao_menu_principal()
            return
        except KeyError:
            print(f"\n⚠︎  Produto não encontrado. Tente novamente.\n")
 
    # --- Aplicar desconto ---
    try:
        print("\n" + "-" * 40)
        desconto = 0.0
        aplicar = input("Deseja aplicar desconto? ('S' para sim / Enter para não): ").strip().upper()
        if aplicar == "S":
            desconto = _input_float("Percentual de desconto (ex: 10.5)  : ")
            if desconto >= 100:
                print("⚠︎  Desconto não pode ser 100% ou mais. Desconto zerado.")
                desconto = 0.0
 
        # --- Confirmação da venda ---
        total = sum(i.subtotal for i in itens)
        total_final = total * (1 - desconto / 100)
        print(f"\n  Total    : R$ {total:.2f}")
        if desconto > 0:
            print(f"  Desconto : {desconto}%")
        print(f"  Total final: R$ {total_final:.2f}")
        print("-" * 40)
 
        confirmar = input("\nConfirmar venda? ('S' para confirmar / Enter para cancelar): ").strip().upper()
        if confirmar != "S":
            print("\nVenda cancelada.")
            voltar_ao_menu_principal()
            return
 
        # --- Registra a venda ---
        id_venda  = gerenciador_vendas._gerar_id_venda()
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        venda     = Venda(id_venda, data_hora, itens, desconto)
 
        # Atualiza o estoque automaticamente
        for item in itens:
            gerenciador_estoque.remover_do_estoque(item.codigo, item.quantidade)
 
        # Salva no banco
        gerenciador_vendas.registrar_venda(venda)
 
        # Emite o recibo
        gerenciador_vendas.emitir_recibo(venda)
 
    except CancelamentoUsuario:
        print("\nVenda cancelada.")
 
    voltar_ao_menu_principal()

# ===========================================================================
# ETAPA 4 — Funções do menu de relatórios
# ===========================================================================
# Cole no bloco de funções do menu existente, antes do finalizar_app()
 
def menu_relatorios(gerenciador_relatorios: GerenciadorRelatorios):  # Opção 8
    """
    Exibe o submenu de relatórios e direciona para o relatório escolhido.
    Agrupa os três relatórios em um único submenu organizado.
    Encerra quando o usuário digitar 0.
    """
    while True:
        exibir_subtitulo("Relatórios")
        print("1. Relatório de Vendas")
        print("2. Relatório de Estoque")
        print("3. Histórico de Movimentações")
        print("0. Voltar ao menu principal\n")
 
        opcao = input("Escolha uma opção: ").strip()
 
        if opcao == "1":
            exibir_subtitulo("Relatório de Vendas")
            gerenciador_relatorios.relatorio_vendas()
            input("Digite uma tecla para voltar aos relatórios ")
 
        elif opcao == "2":
            exibir_subtitulo("Relatório de Estoque")
            gerenciador_relatorios.relatorio_estoque()
            input("Digite uma tecla para voltar aos relatórios ")
 
        elif opcao == "3":
            exibir_subtitulo("Histórico de Movimentações")
            gerenciador_relatorios.historico_movimentacoes()
            input("Digite uma tecla para voltar aos relatórios ")
 
        elif opcao == "0":
            main()
            return
 
        else:
            print("\nOpção inválida!\n")

def finalizar_app():  # Opção 9
    """Encerra o sistema."""
    exibir_subtitulo("Encerrando o sistema")
    print("Obrigado por usar o SGLV 🛒 Sistema Gerenciador de Loja de Varejo. Até logo!\n")

# --- Escolha de opção e main ---

def escolher_opcao(gerenciador_estoque: GerenciadorEstoque,
                   gerenciador_vendas: GerenciadorVendas,
                   gerenciador_relatorios: GerenciadorRelatorios):
    """Lê o número digitado pelo usuário e chama a função correspondente."""
    try:
        opcao = int(input("Escolha uma opção: "))

        if   opcao == 1: cadastrar_produto(gerenciador_estoque)
        elif opcao == 2: listar_produtos(gerenciador_estoque)
        elif opcao == 3: adicionar_ao_estoque(gerenciador_estoque)
        elif opcao == 4: remover_do_estoque(gerenciador_estoque)
        elif opcao == 5: atualizar_estoque(gerenciador_estoque)
        elif opcao == 6: buscar_produto(gerenciador_estoque)
        elif opcao == 7: registrar_venda(gerenciador_estoque, gerenciador_vendas)
        elif opcao == 8: menu_relatorios(gerenciador_relatorios)
        elif opcao == 9: finalizar_app()
        else:            opcao_invalida()
    except:
        opcao_invalida()

def main():
    """Inicializa o sistema e exibe o menu."""
    os.system("cls" if os.name == "nt" else "clear")
    gerenciador_estoque = GerenciadorEstoque()
    gerenciador_vendas  = GerenciadorVendas()
    gerenciador_relatorios = GerenciadorRelatorios()
    exibir_logo()
    exibir_opcoes()
    escolher_opcao(gerenciador_estoque, gerenciador_vendas, gerenciador_relatorios)

# --- Entrada do programa ---

if __name__ == "__main__":
    main()
