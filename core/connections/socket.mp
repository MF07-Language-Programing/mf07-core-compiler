# Este módulo foi movido para 'core/socket.mp'.
# Mantido apenas por compatibilidade e não expõe nenhuma nova definição.

class TcpClient {
    static intent connect(host: string, port: int, timeout) {
        return TcpConnection.connect(host, port, timeout)
    }
}
