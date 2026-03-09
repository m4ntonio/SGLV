# SGLV 🛒 Sistema Gerenciador de Loja de Varejo com Gestão de Estoque de Produtos

> Projeto acadêmico desenvolvido para a disciplina **Computational Thinking with Python**

![Checkpoint](https://img.shields.io/badge/Checkpoint-1/3-blueviolet)
![Status](https://img.shields.io/badge/Overfitting-Group-orange.svg)
![Python](https://img.shields.io/badge/Python-3.11-blue.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

## 👥 Integrantes

😐 Mario Antonio Oliveira  
🙂 Vinicius Augusto Silva

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

## 🗄️ Banco de Dados

O sistema utiliza **SQLite** para persistência local dos dados. Na primeira execução, o arquivo `sglv.db` é criado automaticamente na mesma pasta do script. Todos os dados cadastrados são preservados entre execuções.

> `sglv.db` está listado no `.gitignore` e **não é versionado** no repositório — cada usuário gera o seu localmente ao rodar o sistema.

## 🖥️ Interface

O sistema conta com um menu interativo no terminal que:

- Limpa a tela a cada operação, mantendo a interface organizada
- Exibe cabeçalho ASCII do SuperMais
- Permite cancelar qualquer operação digitando `S` em qualquer campo
- Exibe alertas visuais `⚠️` para produtos com estoque baixo na listagem

## 🛠️ Tecnologias Utilizadas

- Python 3.8+
- SQLite3 (biblioteca padrão)
- Módulo `logging` (alertas e registro de operações)
- Módulo `os` (limpeza de tela multiplataforma)
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
python sglv_app.py
```

O menu principal será exibido automaticamente.

## 🗂️ Estrutura do Projeto

```
gerenciador-loja-varejo/
├── sglv_app.py              # Sistema completo (classes + interface + banco)
├── requirements.txt         # Dependências do projeto (bibliotecas padrão)
├── .gitignore               # Arquivos ignorados pelo Git
├── LICENSE                  #
├── SGLV.md                  #
└── README.md                # Documentação do projeto
```

> O arquivo `sglv.db` é gerado automaticamente ao rodar o sistema e **não está incluso no repositório**.

## 🏗️ Arquitetura do Sistema

```
┌─────────────────────────────────────────────────┐
│              Interface (Terminal)               │
│   menu interativo · exibir_subtitulo · inputs   │
└────────────────────────┬────────────────────────┘
                         │
┌────────────────────────▼────────────────────────┐
│           GerenciadorEstoque (POO)              │
│  cadastrar · adicionar · remover · atualizar    │
└────────────────────────┬────────────────────────┘
                         │
┌────────────────────────▼────────────────────────┐
│             Banco de Dados SQLite               │
│                     sglv.db                     │
└─────────────────────────────────────────────────┘
```

## 🚧 Status do Projeto
```
| Etapa   | Descrição                           | Status    |
|---------|-------------------------------------|-----------|
| Etapa 1 | Cadastro de Produtos                | Concluída |
| Etapa 2 | Gestão de Estoque                   | Concluída |
| Extra   | Integração SQLite + Menu interativo | Concluída |

  Data de conclusão: 9 de março de 2026
```