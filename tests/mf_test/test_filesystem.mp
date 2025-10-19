# Testa biblioteca de arquivos e diretórios

intent test_filesystem_module() {
    print("=== TESTE: FileSystem & Path ===")

    var root = Path.join(Path.cwd(), "tests", "tmp_fs", null, null)
    var workdir = new Directory(root)
    print("Diretório temporário:", root)

    if (not workdir.exists()) {
        var created = workdir.ensure()
        print("Criado diretório temporário:", created)
    }

    var filePath = Path.join(root, "amostra.txt", null, null, null)
    var file = new File(filePath)
    print("Arquivo alvo:", filePath)

    var wrote = file.writeText("Linha inicial", null)
    print("Escreveu texto inicial:", wrote)

    var appended = file.appendText("\nSegunda linha", null)
    print("Append realizado:", appended)

    var content = file.readText(null)
    print("Conteúdo atual:\n" + content)

    var info = file.info()
    if (info != null) {
        print("Tamanho do arquivo:", info.size)
        print("É arquivo?", info.isFile())
        print("Última modificação:", info.modified)
    }

    var copyPath = Path.join(root, "copia.txt", null, null, null)
    var copied = file.copyTo(copyPath, true)
    print("Cópia criada:", copied)

    var movedPath = Path.join(root, "movido.txt", null, null, null)
    var moved = file.moveTo(movedPath, true)
    print("Movido com sucesso:", moved)

    var listing = workdir.list(false)
    print("Itens no diretório:", listing.size())

    var i = 0
    while (i < listing.size()) {
        var entry = listing.get(i)
        print(" - ", entry.name, " (", entry.type, ")")
        i = i + 1
    }

    var globbed = FileSystem.glob(root, "*.txt")
    print("Resultado glob:", globbed.size())

    var walked = FileSystem.walk(root)
    print("Frames do walk:", walked.size())
    waitSeconds(5)  # Espera para garantir que o walk seja concluído

    var copyRemoved = FileSystem.remove(copyPath, false)
    print("Cópia removida:", copyRemoved)

    var movedRemoved = FileSystem.remove(movedPath, false)
    print("Arquivo movido removido:", movedRemoved)

    var cleaned = workdir.remove(true)
    print("Diretório temporário limpo:", cleaned)

    print("=== FIM DO TESTE FileSystem ===")
}

test_filesystem_module()
