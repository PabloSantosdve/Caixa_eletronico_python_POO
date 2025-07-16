from abc import ABC, abstractmethod
from datetime import datetime
import functools

# ===================== Decorador de Log =====================
def log_transacao(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        tipo = func.__name__.capitalize()
        data_hora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        print(f"[LOG] {data_hora} - Transação: {tipo}")
        return func(*args, **kwargs)
    return wrapper

# ===================== Cliente =====================
class Cliente:
    def __init__(self, nome, cpf, nascimento, endereco):
        self.nome = nome
        self.cpf = cpf
        self.nascimento = nascimento
        self.endereco = endereco
        self.contas = []

    @log_transacao
    def abrir_conta(self, conta):
        self.contas.append(conta)

# ===================== Historico =====================
class Historico:
    def __init__(self):
        self.transacoes = []

    def registrar(self, tipo, valor):
        self.transacoes.append({
            "tipo": tipo,
            "valor": valor,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })

    def gerar_relatorio(self, tipo=None):
        for t in self.transacoes:
            if tipo is None or t['tipo'].lower() == tipo.lower():
                yield True

# ===================== ContaBancaria =====================
class ContaBancaria(ABC):
    def __init__(self, numero, cliente):
        self.numero = numero
        self.cliente = cliente
        self.agencia = "0001"
        self.saldo = 0
        self.historico = Historico()

    @abstractmethod
    def sacar(self, valor): pass

    @log_transacao
    def depositar(self, valor):
        if valor <= 0:
            print("Depósito inválido.")
            return False
        self.saldo += valor
        self.historico.registrar("Depósito", valor)
        print("Depósito realizado com sucesso!")
        return True

    def extrato(self):
        print(f"\n=== Extrato da conta {self.numero} ===")
        for t in self.historico.transacoes:
            print(f"{t['data']} - {t['tipo']}: R${t['valor']:.2f}")
        print(f"Saldo atual: R${self.saldo:.2f}\n")

# ===================== ContaCorrente =====================
class ContaCorrente(ContaBancaria):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
        self.saques_realizados = 0

    @log_transacao
    def sacar(self, valor):
        if valor <= 0:
            print("Saque inválido.")
            return False

        if valor > self.limite:
            print("Valor excede o limite de saque.")
            return False

        if self.saques_realizados >= self.limite_saques:
            print("Limite de saques diários atingido.")
            return False

        if valor > self.saldo:
            print("Saldo insuficiente.")
            return False

        self.saldo -= valor
        self.saques_realizados += 1
        self.historico.registrar("Saque", valor)
        print("Saque realizado com sucesso!")
        return True

# ===================== Transacoes =====================
class Transacao(ABC):
    @abstractmethod
    def executar(self, conta): pass

class OperacaoSaque(Transacao):
    def __init__(self, valor):
        self.valor = valor

    @log_transacao
    def executar(self, conta):
        conta.sacar(self.valor)

class OperacaoDeposito(Transacao):
    def __init__(self, valor):
        self.valor = valor

    @log_transacao
    def executar(self, conta):
        conta.depositar(self.valor)

# ===================== Iterador de Contas =====================
class ContaIterador:
    def __init__(self, contas):
        self._contas = contas
        self._index = 0

    def __iter__(self):
        return self

    def __next__(self):
        if self._index >= len(self._contas):
            raise StopIteration
        conta = self._contas[self._index]
        self._index += 1
        return {
            "numero": conta.numero,
            "saldo": conta.saldo,
            "cliente": conta.cliente.nome
        }

# ===================== Teste =====================
if __name__ == "__main__":
    # Cria cliente e conta
    pablo = Cliente("Pablo", "12345678900", "01/01/2000", "Av. Dev Z, 404")
    conta1 = ContaCorrente("000123", pablo)
    pablo.abrir_conta(conta1)

    # Transações
    OperacaoDeposito(1000).executar(conta1)
    OperacaoSaque(200).executar(conta1)
    conta1.extrato()

    # Gerador de relatório filtrado
    print("\n--- Relatório de Depósitos ---")
    for transacao in conta1.historico.gerar_relatorio(tipo="Depósito"):
        print(transacao)

    # Iterando sobre contas
    print("\n--- Todas as contas ---")
    for dados in ContaIterador(pablo.contas):
        print(dados)
