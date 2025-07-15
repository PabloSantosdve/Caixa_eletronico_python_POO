from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, nome, cpf, nascimento, endereco):
        self.nome = nome
        self.cpf = cpf
        self.nascimento = nascimento
        self.endereco = endereco
        self.contas = []

    def abrir_conta(self, conta):
        self.contas.append(conta)


class Historico:
    def __init__(self):
        self.transacoes = []

    def registrar(self, tipo, valor):
        self.transacoes.append({
            "tipo": tipo,
            "valor": valor,
            "data": datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        })


class ContaBancaria(ABC):
    def __init__(self, numero, cliente):
        self.numero = numero
        self.cliente = cliente
        self.agencia = "0001"
        self.saldo = 0
        self.historico = Historico()

    @abstractmethod
    def sacar(self, valor): pass

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


class ContaCorrente(ContaBancaria):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques
        self.saques_realizados = 0

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


class Transacao(ABC):
    @abstractmethod
    def executar(self, conta): pass


class OperacaoSaque(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def executar(self, conta):
        conta.sacar(self.valor)


class OperacaoDeposito(Transacao):
    def __init__(self, valor):
        self.valor = valor

    def executar(self, conta):
        conta.depositar(self.valor)
