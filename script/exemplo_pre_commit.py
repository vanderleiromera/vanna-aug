"""Exemplo de arquivo para demonstrar o pre-commit.

Este arquivo contém exemplos de problemas que o pre-commit pode detectar e corrigir.
"""

# Removidas importações não utilizadas


def funcao_sem_docstring():
    """Função de exemplo para demonstrar o pre-commit.

    Returns:
        str: Uma string de resultado.
    """
    # Removida variável não utilizada
    return "Resultado"


def funcao_com_docstring_incorreto():
    """Esta função faz algo.

    Returns:
        str: Uma string de resultado.
    """
    return "Resultado"


def funcao_com_tipo_incorreto() -> str:
    """Função com tipo correto.

    Returns:
        str: Uma string de resultado.
    """
    return "Resultado"


def funcao_com_espacos():
    """Esta função tem espaços em branco no final das linhas.

    Returns:
        str: Uma string de resultado.
    """
    return "Resultado"


def funcao_com_formatacao_incorreta(param1, param2):
    """Função com formatação correta.

    Args:
        param1: Primeiro parâmetro.
        param2: Segundo parâmetro.

    Returns:
        int: A soma dos parâmetros.
    """
    return param1 + param2


class ClasseSemDocstring:
    """Classe de exemplo para demonstrar o pre-commit."""

    def __init__(self):
        """Inicializa a classe com um valor padrão."""
        self.valor = 10


# Variável global com nome correto
VARIAVEL_GLOBAL = 100

# Linha dividida para não ultrapassar o limite de caracteres
string_longa = (
    "Esta é uma string muito longa que foi dividida para não ultrapassar "
    "o limite de caracteres recomendado pelo PEP 8."
)

if __name__ == "__main__":
    print(funcao_sem_docstring())
    print(funcao_com_docstring_incorreto())
    print(funcao_com_tipo_incorreto())
    print(funcao_com_espacos())
    print(funcao_com_formatacao_incorreta(1, 2))
    print(ClasseSemDocstring().valor)
    print(VARIAVEL_GLOBAL)
