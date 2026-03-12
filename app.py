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
    level=logging.INFO,   # Nível mínimo de log exibido (INFO, WARNING, ERROR)
    format="%(asctime)s [%(levelname)s] %(message)s",   # Formato da mensagem
    datefmt="%Y-%m-%d %H:%M:%S",   # Formato da data e hora
    encoding="utf-8",   # Suporte a caracteres especiais
    filename="historico.log"   # Grava o histórico de operações em arquivo local
)
logger = logging.getLogger("SGLV")   # Identificador do sistema nos logs

DB_FILE = "produto.db" # Arquivo do banco SQLite

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
        """Lista todos os atributos do produto de forma formatada."""
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

    # --- Conexão e inicialização do banco ---

    def _conectar(self) -> sqlite3.Connection:
        """Abre e retorna uma conexão com o banco SQLite."""
        return sqlite3.connect(self.db_file)

    def _inicializar_banco(self) -> None:
        """
        Cria a tabela 'produtos' no banco caso ela ainda não exista.
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
            nova_quantidade = 0
        else:
            nova_quantidade = produto.quantidade - quantidade

        with self._conectar() as conn:
            conn.execute(
                "UPDATE produtos SET quantidade = ? WHERE codigo = ?",
                (nova_quantidade, codigo)
            )
            conn.commit()

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
    print("7. Sair\n")

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
    Lê um inteiro positivo do terminal, repetindo até receber um valor válido.
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
    Lê um float positivo do terminal, repetindo até receber um valor válido.
    Dispara CancelamentoUsuario se o usuário digitar 'S'.
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
    Lê uma string não vazia do terminal.
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
    Lê uma string não vazia respeitando o limite de caracteres.
    Dispara CancelamentoUsuario se o usuário digitar 'S'.
    """
    while True:
        valor = input(mensagem).strip()
        if valor.upper() == "S":
            raise CancelamentoUsuario()
        if not valor:
            print(f"Este campo não pode ficar vazio (ou S para cancelar).")
            continue
        if len(valor) > limite:
            print(f"Máximo de {limite} caracteres. Você digitou {len(valor)}.")
            continue
        return valor

# --- Funções de cada opção do menu ---

def cadastrar_produto(gerenciador: GerenciadorEstoque):
    """Fluxo interativo para cadastrar um novo produto."""
    exibir_subtitulo("Cadastro de novo produto")
    print("(Digite 'S' em qualquer campo para cancelar)\n")
    while True:
        try:
            # Verifica o código antes de continuar o fluxo
            while True:
                codigo = _input_nao_vazio("Digite o código do produto       : ").upper()
                try:
                    gerenciador.buscar_produto(codigo)
                    print(f"Código '{codigo}' já existe. Digite outro código.\n")
                except KeyError:
                    break  # código disponível, pode continuar

            nome        = _input_limit    ("Digite o nome do produto         : ", 25)
            categoria   = _input_nao_vazio("Digite a categoria do produto    : ")
            quantidade  = _input_int      ("Digite a quantidade inicial      : ")
            preco       = _input_float    ("Digite o preço de venda (R$)     : ")
            descricao   = _input_limit    ("Digite a descrição do produto    : ", 10)
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
            print("\nCadastro cancelado.")
            break
        except (ValueError, KeyError) as e:
            print(f"\nErro: {e}")

    voltar_ao_menu_principal()

def listar_produtos(gerenciador: GerenciadorEstoque):
    """Exibe todos os produtos cadastrados no estoque."""
    exibir_subtitulo("Listagem de produtos")
    gerenciador.listar_produtos()
    voltar_ao_menu_principal()

def adicionar_ao_estoque(gerenciador: GerenciadorEstoque):
    """Fluxo interativo para entrada de mercadoria no estoque."""
    exibir_subtitulo("Adicionar ao estoque")
    print("(Digite 'S' em qualquer campo para cancelar)\n")
    while True:
        try:
            codigo     = _input_nao_vazio("Digite o código do produto       : ").upper()
            quantidade = _input_int      ("Digite a quantidade a adicionar  : ")
            gerenciador.adicionar_ao_estoque(codigo, quantidade)
            print("\nEstoque atualizado com sucesso!")
            # continua no loop para nova operação
        except CancelamentoUsuario:
            print("\nOperação cancelada.")
            break
        except (ValueError, KeyError) as e:
            print(f"\nErro: {e}. Tente novamente ou digite 'S' para cancelar.\n")

    voltar_ao_menu_principal()

def remover_do_estoque(gerenciador: GerenciadorEstoque):
    """Fluxo interativo para saída de mercadoria do estoque."""
    exibir_subtitulo("Remover do estoque")
    print("(Digite 'S' em qualquer campo para cancelar)\n")
    while True:
        try:
            codigo     = _input_nao_vazio("Digite o código do produto       : ").upper()
            quantidade = _input_int      ("Digite a quantidade a remover    : ")
            gerenciador.remover_do_estoque(codigo, quantidade)
            print("\nEstoque atualizado com sucesso!")
            # continua no loop para nova operação
        except CancelamentoUsuario:
            print("\nOperação cancelada.")
            break
        except (ValueError, KeyError) as e:
            print(f"\nErro: {e}. Tente novamente ou digite 'S' para cancelar.\n")

    voltar_ao_menu_principal()

def atualizar_estoque(gerenciador: GerenciadorEstoque):
    """Fluxo interativo para ajuste manual do estoque."""
    exibir_subtitulo("Atualizar estoque manualmente")
    print("(Digite 'S' em qualquer campo para cancelar)\n")
    while True:
        try:
            codigo          = _input_nao_vazio("Digite o código do produto       : ").upper()
            nova_quantidade = _input_int      ("Digite a nova quantidade total   : ")
            gerenciador.atualizar_estoque(codigo, nova_quantidade)
            print("\nEstoque atualizado com sucesso!")
            # continua no loop para nova operação
        except CancelamentoUsuario:
            print("\nOperação cancelada.")
            break
        except (ValueError, KeyError) as e:
            print(f"\nErro: {e}. Tente novamente ou digite 'S' para cancelar.\n")

    voltar_ao_menu_principal()

def buscar_produto(gerenciador: GerenciadorEstoque):
    """Fluxo interativo para buscar e exibir detalhes de um produto."""
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

def finalizar_app():
    """Encerra o sistema."""
    exibir_subtitulo("Encerrando o sistema")
    print("Obrigado por usar o SGLV 🛒 Sistema Gerenciador de Loja de Varejo. Até logo!\n")

# --- Escolha de opção e main ---

def escolher_opcao(gerenciador: GerenciadorEstoque):
    """Lê a opção digitada e chama a função correspondente."""
    try:
        opcao = int(input("Escolha uma opção: "))

        if   opcao == 1: cadastrar_produto(gerenciador)
        elif opcao == 2: listar_produtos(gerenciador)
        elif opcao == 3: adicionar_ao_estoque(gerenciador)
        elif opcao == 4: remover_do_estoque(gerenciador)
        elif opcao == 5: atualizar_estoque(gerenciador)
        elif opcao == 6: buscar_produto(gerenciador)
        elif opcao == 7: finalizar_app()
        else:            opcao_invalida()
    except:
        opcao_invalida()

def main():
    """Inicializa o sistema e exibe o menu."""
    os.system("cls" if os.name == "nt" else "clear")
    gerenciador = GerenciadorEstoque()
    exibir_logo()
    exibir_opcoes()
    escolher_opcao(gerenciador)

# --- Entrada do programa ---

if __name__ == "__main__":
    main()
