"""
runtime_adapter.py

Stub de adaptador para integrar um serviço de IA ao interpretador CorpLang.
Este arquivo fornece uma classe `ModelAdapter` com implementações de exemplo (simuladas)
e uma função `inject_model` que demonstra como injetar bindings no environment do interpretador.

OBS: Ajuste a forma de injeção conforme a API real do seu interpretador (por exemplo, se precisar expor
atributos de objeto ou se o parser suporta chamadas do tipo `model.request(...)`).
"""

import asyncio
from typing import Any, Dict, Optional

class ModelAdapter:
    """Adaptador de exemplo para um backend de IA."""

    def __init__(self):
        self.registered = {}
        self.connections = set()

    async def request(self, prompt: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Simula envio de prompt a um modelo.

        Em uma implementação real essa função faria uma chamada HTTP/SDK ao provedor de IA.
        """
        await asyncio.sleep(0.05)  # Simula latência
        return {
            "id": "sim-msg-1",
            "type": "text",
            "content": f"[SIMULATED RESPONSE] Para: {prompt}",
            "metadata": metadata or {}
        }

    async def response(self, message: Dict[str, Any]) -> Dict[str, Any]:
        """Simula envio de uma resposta final para um sistema receptor.
        Retorna um resultado com status.
        """
        await asyncio.sleep(0.01)
        return {"status": "ok", "code": 200, "payload": message}

    def initFunction(self, fn_ref: Any, client_ids: list, dataset_id: str) -> Dict[str, Any]:
        """Registra uma função/script para ser acionado pelo runtime IA.

        Nota: `fn_ref` pode ser um nome (string) ou uma referência de função dependendo de como o host
        exposer o script. Neste stub, armazenamos o registro para demonstração.
        """
        reg_id = f"reg-{len(self.registered)+1}"
        self.registered[reg_id] = {"fn_ref": fn_ref, "clients": client_ids, "dataset": dataset_id}
        return {"ok": True, "id": reg_id}

    def addConnection(self, client_id: str) -> bool:
        self.connections.add(client_id)
        return True

    # Auxiliares sync wrappers (para ambientes que chamam funções de forma síncrona)
    def sync_request(self, prompt: Any, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(self.request(prompt, metadata))

    def sync_response(self, message: Dict[str, Any]) -> Dict[str, Any]:
        return asyncio.get_event_loop().run_until_complete(self.response(message))


# Função de utilidade para injetar o adaptador em um interpretador CorpLang.
# Adapte o accesso ao environment conforme sua API (CorpLang vs Interpreter).

def inject_model(target, adapter: ModelAdapter):
    """Injeta bindings no environment do interpretador.

    `target` pode ser uma instância de `module.CorpLang` (que possui `interpreter`) ou
    diretamente uma instância de `Interpreter`.

    Este exemplo registra nomes utilitários que os scripts podem chamar:
      - "model.request" (callable síncrono wrapper)
      - "model.response"
      - "model.initFunction"
      - "addConnection"

    Observação: dependendo do parser da linguagem, chamadas como `model.request(...)` podem
    não ser suportadas diretamente; nesse caso exponha funções sem ponto, ex.: `model_request`.
    """
    # Resolva o environment adequado
    if hasattr(target, 'interpreter'):
        env = target.interpreter.globals
    else:
        env = getattr(target, 'globals', target)

    # Defina nomes que os scripts podem chamar
    try:
        env.define('model.request', adapter.sync_request)
        env.define('model.response', adapter.sync_response)
        env.define('model.initFunction', adapter.initFunction)
        env.define('addConnection', adapter.addConnection)

        # Também exponha variantes sem ponto (útil se parser não aceitar tokens com ponto)
        env.define('model_request', adapter.sync_request)
        env.define('model_response', adapter.sync_response)
        env.define('model_initFunction', adapter.initFunction)
    except Exception as e:
        # Em alguns ambientes `env` pode ter API diferente; imprimir instrução de fallback
        print('Falha ao injetar bindings no environment:', e)
        print('Considere chamar env.define(nome, callable) manualmente conforme a API do Environment.')


# Modo de uso (exemplo)
if __name__ == '__main__':
    # Exemplo rápido de uso quando executado isoladamente
    adapter = ModelAdapter()

    # Simulação de uso assíncrono
    async def demo():
        msg = await adapter.request('Qual seria a melhorar de analisar essa bosta?')
        print('Received:', msg)
        res = await adapter.response(msg)
        print('Result:', res)

    asyncio.run(demo())
