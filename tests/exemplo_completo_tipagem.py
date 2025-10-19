"""
Exemplo completo com interfaces, tipagem genérica e coleções tipadas.
"""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from src.logging_config import setup_production_logging
from module import CorpLang


def main():
    print("=== Exemplo completo: Interfaces + Tipagem Genérica + Coleções ===")
    setup_production_logging()

    corp_lang = CorpLang()

    test_code = """
    # Definir interfaces
    interface Produto {
        intent getNome(): string
        intent getPreco(): int
        intent getCategoria(): string
    }
    
    interface Vendedor {
        intent getNome(): string
        intent vender(produto: Produto): boolean
    }
    
    # Implementar classes que seguem as interfaces
    class Livro implements Produto {
        private var nome: string
        private var preco: int
        private var autor: string
        
        intent constructor(nome: string, preco: int, autor: string) {
            this.nome = nome
            this.preco = preco
            this.autor = autor
        }
        
        intent getNome(): string {
            return this.nome
        }
        
        intent getPreco(): int {
            return this.preco
        }
        
        intent getCategoria(): string {
            return "Livros"
        }
        
        intent getAutor(): string {
            return this.autor
        }
    }
    
    class Eletronico implements Produto {
        private var nome: string
        private var preco: int
        private var marca: string
        
        intent constructor(nome: string, preco: int, marca: string) {
            this.nome = nome
            this.preco = preco
            this.marca = marca
        }
        
        intent getNome(): string {
            return this.nome
        }
        
        intent getPreco(): int {
            return this.preco
        }
        
        intent getCategoria(): string {
            return "Eletrônicos"
        }
        
        intent getMarca(): string {
            return this.marca
        }
    }
    
    class Funcionario implements Vendedor {
        private var nome: string
        private var vendas: List
        
        intent constructor(nome: string) {
            this.nome = nome
            this.vendas = new List("Produto")
        }
        
        intent getNome(): string {
            return this.nome
        }
        
        intent vender(produto: Produto): boolean {
            this.vendas.append(produto)
            return true
        }
        
        intent getVendas(): List {
            return this.vendas
        }
    }
    
    # Sistema de loja com coleções tipadas
    class Loja {
        private var produtos: HashMap
        private var categorias: Set
        private var vendedores: List
        
        intent constructor() {
            this.produtos = new HashMap("string", "Produto")
            this.categorias = new Set("string")
            this.vendedores = new List("Vendedor")
        }
        
        intent adicionarProduto(id: string, produto: Produto) {
            this.produtos.put(id, produto)
            this.categorias.add(produto.getCategoria())
        }
        
        intent adicionarVendedor(vendedor: Vendedor) {
            this.vendedores.append(vendedor)
        }
        
        intent buscarProduto(id: string): Produto {
            return this.produtos.get(id)
        }
        
        intent listarCategorias() {
            print("Categorias disponíveis:")
            this.categorias.forEach(fn(categoria) {
                print("- " + categoria)
            })
        }
        
        intent listarVendedores() {
            print("Vendedores:")
            this.vendedores.forEach(fn(vendedor) {
                print("- " + vendedor.getNome())
            })
        }
        
        intent relatorioVendas() {
            print("=== Relatório de Vendas ===")
            this.vendedores.forEach(fn(vendedor) {
                print("Vendedor:", vendedor.getNome())
                var vendas = vendedor.getVendas()
                print("Total de vendas:", vendas.length())
                
                vendas.forEach(fn(produto) {
                    print("  - " + produto.getNome() + " (R$ " + produto.getPreco() + ")")
                })
            })
        }
    }
    
    intent exemploCompleto() {
        print("=== Sistema de Loja com Interfaces e Tipagem ===")
        
        # Criar loja
        var loja = new Loja()
        
        # Criar produtos
        var livro1 = new Livro("Clean Code", 85, "Robert Martin")
        var livro2 = new Livro("Design Patterns", 120, "Gang of Four")
        var notebook = new Eletronico("Dell Inspiron", 2500, "Dell")
        var mouse = new Eletronico("Mouse Gamer", 150, "Logitech")
        
        # Adicionar produtos à loja
        loja.adicionarProduto("L001", livro1)
        loja.adicionarProduto("L002", livro2)
        loja.adicionarProduto("E001", notebook)
        loja.adicionarProduto("E002", mouse)
        
        # Criar vendedores
        var vendedor1 = new Funcionario("João Silva")
        var vendedor2 = new Funcionario("Maria Santos")
        
        loja.adicionarVendedor(vendedor1)
        loja.adicionarVendedor(vendedor2)
        
        # Simular vendas
        vendedor1.vender(livro1)
        vendedor1.vender(notebook)
        vendedor2.vender(livro2)
        vendedor2.vender(mouse)
        
        # Relatórios
        loja.listarCategorias()
        print("")
        loja.listarVendedores()
        print("")
        loja.relatorioVendas()
        
        print("")
        print("Exemplo completo executado com sucesso!")
        print("✓ Interfaces implementadas")
        print("✓ Tipagem genérica funcionando")
        print("✓ HashMap<string, Produto>")
        print("✓ Set<string> para categorias")
        print("✓ List<Vendedor> e List<Produto>")
    }
    
    exemploCompleto()
    """

    corp_lang.run(test_code)


if __name__ == "__main__":
    main()
