"""
Módulo para avaliação da qualidade de consultas SQL
"""

import re
from typing import Dict, List, Tuple, Any, Optional


def evaluate_sql_quality(sql: str) -> Dict[str, Any]:
    """
    Avalia a qualidade de uma consulta SQL.

    Args:
        sql (str): A consulta SQL a ser avaliada

    Returns:
        Dict[str, Any]: Dicionário com os resultados da avaliação
    """
    # Inicializar resultados
    results = {
        "score": 0,
        "max_score": 100,
        "issues": [],
        "warnings": [],
        "suggestions": [],
        "is_valid": True,
    }

    # Verificar se o SQL está vazio
    if not sql or not sql.strip():
        results["is_valid"] = False
        results["issues"].append("A consulta SQL está vazia")
        results["score"] = 0
        return results

    # Verificar sintaxe básica
    basic_syntax_score, syntax_issues = check_basic_syntax(sql)
    results["score"] += basic_syntax_score
    results["issues"].extend(syntax_issues)

    # Verificar práticas recomendadas
    best_practices_score, best_practices_issues, warnings, suggestions = (
        check_best_practices(sql)
    )
    results["score"] += best_practices_score
    results["issues"].extend(best_practices_issues)
    results["warnings"].extend(warnings)
    results["suggestions"].extend(suggestions)

    # Verificar problemas de desempenho
    (
        performance_score,
        performance_issues,
        performance_warnings,
        performance_suggestions,
    ) = check_performance(sql)
    results["score"] += performance_score
    results["issues"].extend(performance_issues)
    results["warnings"].extend(performance_warnings)
    results["suggestions"].extend(performance_suggestions)

    # Verificar problemas de segurança
    security_score, security_issues, security_warnings = check_security(sql)
    results["score"] += security_score
    results["issues"].extend(security_issues)
    results["warnings"].extend(security_warnings)

    # Ajustar pontuação final
    if results["issues"]:
        results["is_valid"] = False

    # Limitar pontuação a 100
    results["score"] = min(results["score"], 100)

    return results


def check_basic_syntax(sql: str) -> Tuple[int, List[str]]:
    """
    Verifica a sintaxe básica da consulta SQL.

    Args:
        sql (str): A consulta SQL a ser verificada

    Returns:
        Tuple[int, List[str]]: Pontuação e lista de problemas encontrados
    """
    score = 30  # Pontuação máxima para sintaxe básica
    issues = []

    # Verificar se a consulta começa com SELECT, INSERT, UPDATE ou DELETE
    if not re.match(r"^\s*(SELECT|INSERT|UPDATE|DELETE|WITH)", sql.strip().upper()):
        score -= 15
        issues.append(
            "A consulta não começa com uma palavra-chave SQL válida (SELECT, INSERT, UPDATE, DELETE, WITH)"
        )

    # Verificar se há parênteses não fechados
    if sql.count("(") != sql.count(")"):
        score -= 10
        issues.append("A consulta contém parênteses não fechados")

    # Verificar se há aspas não fechadas
    single_quotes = len(re.findall(r"(?<!\\)'", sql)) % 2
    double_quotes = len(re.findall(r'(?<!\\)"', sql)) % 2
    if single_quotes != 0 or double_quotes != 0:
        score -= 10
        issues.append("A consulta contém aspas não fechadas")

    # Verificar se há ponto e vírgula no final
    if not sql.strip().endswith(";"):
        score -= 5
        issues.append("A consulta não termina com ponto e vírgula")

    # Verificar se há cláusulas FROM em consultas SELECT
    if sql.strip().upper().startswith("SELECT") and "FROM" not in sql.upper():
        score -= 10
        issues.append("A consulta SELECT não contém cláusula FROM")

    # Garantir que a pontuação não seja negativa
    score = max(0, score)

    return score, issues


def check_best_practices(sql: str) -> Tuple[int, List[str], List[str], List[str]]:
    """
    Verifica se a consulta SQL segue as melhores práticas.

    Args:
        sql (str): A consulta SQL a ser verificada

    Returns:
        Tuple[int, List[str], List[str], List[str]]: Pontuação, problemas, avisos e sugestões
    """
    score = 30  # Pontuação máxima para melhores práticas
    issues = []
    warnings = []
    suggestions = []

    # Verificar se está usando SELECT *
    if re.search(r"SELECT\s+\*\s+FROM", sql.upper()):
        score -= 10
        warnings.append("A consulta usa SELECT * em vez de especificar colunas")
        suggestions.append("Especifique as colunas necessárias em vez de usar SELECT *")

    # Verificar se há aliases para tabelas
    if re.search(r"FROM\s+\w+\s+\w+", sql.upper()) or re.search(
        r"JOIN\s+\w+\s+\w+", sql.upper()
    ):
        # Há aliases, o que é bom
        pass
    else:
        # Não há aliases
        if "JOIN" in sql.upper():
            score -= 5
            suggestions.append(
                "Use aliases para tabelas em consultas com JOIN para melhorar a legibilidade"
            )

    # Verificar se há GROUP BY sem agregação
    if "GROUP BY" in sql.upper() and not any(
        x in sql.upper() for x in ["COUNT(", "SUM(", "AVG(", "MAX(", "MIN("]
    ):
        score -= 5
        warnings.append("A consulta usa GROUP BY sem funções de agregação")

    # Verificar se há ORDER BY sem LIMIT em consultas grandes
    if "ORDER BY" in sql.upper() and "LIMIT" not in sql.upper():
        suggestions.append(
            "Considere adicionar LIMIT à consulta com ORDER BY para limitar o número de resultados"
        )

    # Verificar se há JOINs sem condições
    if re.search(r"JOIN\s+\w+(\s+\w+)?\s+ON", sql.upper()):
        # JOIN com ON, o que é bom
        pass
    elif "JOIN" in sql.upper():
        score -= 10
        issues.append("A consulta contém JOIN sem condição ON")

    # Garantir que a pontuação não seja negativa
    score = max(0, score)

    return score, issues, warnings, suggestions


def check_performance(sql: str) -> Tuple[int, List[str], List[str], List[str]]:
    """
    Verifica problemas de desempenho na consulta SQL.

    Args:
        sql (str): A consulta SQL a ser verificada

    Returns:
        Tuple[int, List[str], List[str], List[str]]: Pontuação, problemas, avisos e sugestões
    """
    score = 20  # Pontuação máxima para desempenho
    issues = []
    warnings = []
    suggestions = []

    # Verificar se há subconsultas não otimizadas
    subquery_count = len(re.findall(r"\(\s*SELECT", sql.upper()))
    if subquery_count > 2:
        score -= 5
        warnings.append(
            f"A consulta contém {subquery_count} subconsultas, o que pode afetar o desempenho"
        )
        suggestions.append("Considere usar JOINs em vez de múltiplas subconsultas")

    # Verificar se há funções em cláusulas WHERE
    if re.search(r"WHERE\s+\w+\s*\(\s*\w+\s*\)", sql.upper()):
        score -= 5
        warnings.append(
            "A consulta usa funções em cláusulas WHERE, o que pode impedir o uso de índices"
        )
        suggestions.append("Evite usar funções em colunas na cláusula WHERE")

    # Verificar se há DISTINCT desnecessário
    if "DISTINCT" in sql.upper() and "GROUP BY" in sql.upper():
        score -= 5
        warnings.append(
            "A consulta usa DISTINCT com GROUP BY, o que pode ser redundante"
        )
        suggestions.append("Considere remover DISTINCT quando usar GROUP BY")

    # Verificar se há muitas tabelas em JOIN
    join_count = len(re.findall(r"JOIN", sql.upper()))
    if join_count > 5:
        score -= 5
        warnings.append(
            f"A consulta contém {join_count} JOINs, o que pode afetar o desempenho"
        )
        suggestions.append(
            "Considere simplificar a consulta ou dividir em consultas menores"
        )

    # Garantir que a pontuação não seja negativa
    score = max(0, score)

    return score, issues, warnings, suggestions


def check_security(sql: str) -> Tuple[int, List[str], List[str]]:
    """
    Verifica problemas de segurança na consulta SQL.

    Args:
        sql (str): A consulta SQL a ser verificada

    Returns:
        Tuple[int, List[str], List[str]]: Pontuação, problemas e avisos
    """
    score = 20  # Pontuação máxima para segurança
    issues = []
    warnings = []

    # Verificar se há comentários suspeitos (possível injeção SQL)
    if "--" in sql or "/*" in sql:
        score -= 10
        warnings.append(
            "A consulta contém comentários, o que pode indicar tentativa de injeção SQL"
        )

    # Verificar se há comandos perigosos
    dangerous_commands = [
        "DROP",
        "TRUNCATE",
        "DELETE FROM",
        "UPDATE",
        "ALTER",
        "GRANT",
        "REVOKE",
    ]
    for cmd in dangerous_commands:
        if cmd in sql.upper():
            score -= 10
            issues.append(f"A consulta contém o comando perigoso: {cmd}")

    # Verificar se há UNION (possível injeção SQL)
    if "UNION" in sql.upper():
        score -= 5
        warnings.append(
            "A consulta contém UNION, verifique se não é uma tentativa de injeção SQL"
        )

    # Garantir que a pontuação não seja negativa
    score = max(0, score)

    return score, issues, warnings
