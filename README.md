# SGLV 🛒 Sistema Gerenciador de Loja de Varejo com Gestão de Estoque de Produtos

> Projeto acadêmico desenvolvido para a disciplina **Computational Thinking with Python**

![Checkpoint](https://img.shields.io/badge/Checkpoint-2/3-blueviolet)
![Status](https://img.shields.io/badge/Overfitting-Group-orange.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 👥 Integrantes
```
😐 Mario Antonio Oliveira - RM: 567713
🙂 Vinicius Augusto Silva - RM: 566830
```
## 📋 Sobre o Projeto

O SGLV 🛒 é um Sistema Gerenciador de Loja de Varejo com Gestão de Estoque de Produtos, desenvolvido em Python com foco em **Programação Orientada a Objetos (POO)** e persistência de dados via **SQLite**. O sistema roda no terminal com um menu interativo que limpa a tela a cada operação, proporcionando uma experiência de uso limpa e organizada.

## ✅ Etapas Implementadas

### Etapa 1 - Cadastro de Produtos
Estrutura de dados com as classes `Produto` e `GerenciadorEstoque` para armazenar e cadastrar produtos com os seguintes atributos:

- Nome do Produto
- Código do Produto (identificador único)
- Categoria (ex: "Grãos e Cereais", "Laticínios")
- Quantidade em Estoque
- Preço de Venda
- Descrição
- Fornecedor
- Estoque Mínimo (define o limite para alerta automático)

### Etapa 2 - Gestão de Estoque
Funcionalidades de manipulação do estoque:

- **Adicionar ao Estoque** — aumenta a quantidade de um produto específico
- **Remover do Estoque** — reduz a quantidade, garantindo que não fique negativa
- **Atualização de Estoque** — ajuste manual da quantidade (útil após inventário físico)
- **Alerta de Estoque Baixo** — notificação automática via `logging` quando a quantidade atinge o nível mínimo predefinido

### Etapa 3 — Vendas
Funcionalidades completas de registro e gestão de vendas:

- **Registro de Vendas** — permite adicionar múltiplos produtos em uma única venda
- **Atualização Automática do Estoque** — ao registrar uma venda, o estoque é reduzido automaticamente
- **Emissão de Recibo** — geração de recibo detalhado no terminal com todos os itens, subtotais e total final
- **Descontos e Promoções** — aplicação de desconto percentual antes de confirmar a venda

### Etapa 4 — Relatórios
Relatórios completos para acompanhamento do negócio:

- **Relatório de Vendas** — exibe todas as vendas realizadas com data, produtos, quantidades e valores
- **Relatório de Estoque** — visualização completa do estoque com valor total e produtos em alerta
- **Histórico de Movimentações** — registro completo de todas as entradas, saídas e ajustes de estoque

## 🗄️ Banco de Dados

O sistema utiliza SQLite para persistência local dos dados com 4 tabelas:
```
| Tabela        | Descrição                               |
|---------------|-----------------------------------------|
| produtos      | Cadastro completo de produtos           |
| vendas        | Cabeçalho das vendas realizadas         |
| itens_venda   | Itens de cada venda                     |
| movimentacoes | Histórico de entradas, saídas e ajustes |
```
O arquivo `produto.db` é criado automaticamente na primeira execução.

`produto.db` e `historico.log` estão listados no `.gitignore` e não são versionados no repositório.

## 🖥️ Interface

O sistema conta com um menu interativo no terminal que:

- Limpa a tela a cada operação, mantendo a interface organizada
- Exibe cabeçalho ASCII do SGLV
- Permite cancelar qualquer operação digitando `S` em qualquer campo
- Exibe alertas visuais `⚠️` para produtos com estoque baixo
- Gera recibo detalhado ao finalizar uma venda
- Agrupa os relatórios em um submenu dedicado

## 🛠️ Tecnologias Utilizadas

- Python 3.8+
- SQLite3 (biblioteca padrão)
- Módulo `logging` (alertas e registro de operações)
- Módulo `os` (limpeza de tela multiplataforma)
- Módulo datetime (registro de data e hora das operações)
- Programação Orientada a Objetos (POO)
- Exceção customizada `CancelamentoUsuario`

## 🚀 Como Executar

**Pré-requisito:** Python 3.8 ou superior instalado. Nenhuma instalação adicional necessária.

Clone o repositório:
```bash
git clone https://github.com/m4ntonio/SGLV.git
cd SGLV
```

Execute o sistema:
```bash
python app.py
```

O menu principal será exibido automaticamente.

## 🗂️ Estrutura do Projeto

```
SGLV/
├── app.py              # Sistema completo (classes + interface + banco)
├── requirements.txt         # Dependências do projeto (bibliotecas padrão)
├── .gitignore               # Arquivos ignorados pelo Git
├── LICENSE                  # Licença MIT
├── roadmap.md               # Roteiro de implementação
|── README.md                # Documentação do projeto
├── produto.db *             # Banco de dados SQLite (gerado na primeira execução)
└── historico.log *          # Log de operações (gerado na primeira execução)
```

> Os arquivos `produto.db` e `historico.log` são gerados automaticamente ao rodar o sistema e **não estão inclusos no repositório**.

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────────────┐
│                   Interface (Terminal)                  │
│     menu interativo · exibir_subtitulo · inputs         │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│                  Classes de Serviço (POO)               │
│  GerenciadorEstoque · GerenciadorVendas                 │
│  GerenciadorRelatorios                                  │
└──────────────────────────┬──────────────────────────────┘
                           │
┌──────────────────────────▼──────────────────────────────┐
│               Banco de Dados SQLite                     │
│   produtos · vendas · itens_venda · movimentacoes       │
│                    produto.db                           │
└─────────────────────────────────────────────────────────┘
```

## 🚧 Status do Projeto
```
| Etapa   | Descrição                           | Status    |
|---------|-------------------------------------|-----------|
| Etapa 1 | Cadastro de Produtos                | Concluída |
| Etapa 2 | Gestão de Estoque                   | Concluída |
| Extra   | Integração SQLite + Menu interativo | Concluída |
| Etapa 3 | Vendas + Recibo + Descontos         | Concluída |
| Etapa 4 | Relatórios                          | Concluída |

  Data de conclusão: 27 de abril de 2026
```