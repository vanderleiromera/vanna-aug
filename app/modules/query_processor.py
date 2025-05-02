"""
Módulo para processamento e ajuste de consultas SQL geradas pelo Vanna.ai
"""

import re
from typing import Tuple, List, Dict, Any, Optional

def extract_numeric_values(question: str) -> Dict[str, Any]:
    """
    Extrai valores numéricos de uma pergunta.
    
    Args:
        question (str): A pergunta do usuário
        
    Returns:
        Dict[str, Any]: Dicionário com os valores numéricos encontrados e seus contextos
    """
    # Padrões para encontrar valores numéricos com contexto
    patterns = [
        # Padrão para "X dias/meses/anos"
        (r'(\d+)\s+(dia|dias|day|days)', 'days'),
        (r'(\d+)\s+(mês|meses|mes|meses|month|months)', 'months'),
        (r'(\d+)\s+(ano|anos|year|years)', 'years'),
        
        # Padrão para valores monetários
        (r'(\d+[.,]?\d*)\s*(reais|R\$|BRL)', 'amount_brl'),
        (r'(\d+[.,]?\d*)\s*(dólares|USD|\$)', 'amount_usd'),
        (r'(\d+[.,]?\d*)\s*(euros|EUR|€)', 'amount_eur'),
        
        # Padrão para quantidades
        (r'(\d+[.,]?\d*)\s*(unidades|itens|peças|produtos)', 'quantity'),
        
        # Padrão para porcentagens
        (r'(\d+[.,]?\d*)\s*(%|por\s+cento|percent)', 'percentage'),
        
        # Padrão para top N
        (r'(top|primeiros|melhores)\s+(\d+)', 'top_n'),
        
        # Padrão para limites
        (r'limite\s+de\s+(\d+)', 'limit'),
        (r'limitar\s+(?:a|para|em)?\s+(\d+)', 'limit'),
        (r'limit\s+(\d+)', 'limit'),
    ]
    
    values = {}
    
    # Procurar por cada padrão na pergunta
    for pattern, key in patterns:
        matches = re.findall(pattern, question.lower())
        if matches:
            if key == 'top_n':
                # Para padrões como "top 10", o número está no segundo grupo
                for match in matches:
                    values[key] = int(match[1])
            else:
                # Para outros padrões, o número está no primeiro grupo
                for match in matches:
                    if isinstance(match, tuple):
                        value = match[0]
                    else:
                        value = match
                    
                    # Converter para o tipo apropriado
                    try:
                        if ',' in value or '.' in value:
                            # Substituir vírgula por ponto para conversão correta
                            value = value.replace(',', '.')
                            values[key] = float(value)
                        else:
                            values[key] = int(value)
                    except ValueError:
                        values[key] = value
    
    return values

def adjust_sql_with_values(sql: str, values: Dict[str, Any]) -> str:
    """
    Ajusta a consulta SQL com os valores extraídos da pergunta.
    
    Args:
        sql (str): A consulta SQL gerada
        values (Dict[str, Any]): Dicionário com os valores extraídos
        
    Returns:
        str: Consulta SQL ajustada
    """
    adjusted_sql = sql
    
    # Substituir valores de dias
    if 'days' in values:
        days_value = values['days']
        # Procurar por padrões como "INTERVAL '120 days'" e substituir o número
        adjusted_sql = re.sub(
            r"INTERVAL\s+'(\d+)\s+days'", 
            f"INTERVAL '{days_value} days'", 
            adjusted_sql
        )
        # Procurar por padrões como "CURRENT_DATE - 120" e substituir o número
        adjusted_sql = re.sub(
            r"CURRENT_DATE\s*-\s*(\d+)", 
            f"CURRENT_DATE - {days_value}", 
            adjusted_sql
        )
        # Procurar por padrões como "date >= (NOW() - INTERVAL '120 DAY')"
        adjusted_sql = re.sub(
            r"NOW\(\)\s*-\s*INTERVAL\s+'(\d+)\s+DAY'", 
            f"NOW() - INTERVAL '{days_value} DAY'", 
            adjusted_sql
        )
        # Procurar por padrões como "date >= (CURRENT_DATE - INTERVAL '120 days')"
        adjusted_sql = re.sub(
            r"CURRENT_DATE\s*-\s*INTERVAL\s+'(\d+)\s+days'", 
            f"CURRENT_DATE - INTERVAL '{days_value} days'", 
            adjusted_sql
        )
    
    # Substituir valores de limite
    if 'limit' in values or 'top_n' in values:
        limit_value = values.get('limit', values.get('top_n'))
        # Procurar por padrões como "LIMIT 10" e substituir o número
        adjusted_sql = re.sub(
            r"LIMIT\s+\d+", 
            f"LIMIT {limit_value}", 
            adjusted_sql
        )
        # Se não houver LIMIT, adicionar ao final se a consulta não tiver ORDER BY
        if "LIMIT" not in adjusted_sql.upper():
            if "ORDER BY" in adjusted_sql.upper():
                # Adicionar após ORDER BY
                parts = adjusted_sql.split("ORDER BY", 1)
                if "LIMIT" not in parts[1].upper():
                    # Verificar se já tem ponto e vírgula no final
                    if parts[1].strip().endswith(';'):
                        adjusted_sql = f"{parts[0]}ORDER BY{parts[1][:-1]} LIMIT {limit_value};"
                    else:
                        adjusted_sql = f"{parts[0]}ORDER BY{parts[1]} LIMIT {limit_value}"
            else:
                # Adicionar ao final da consulta
                if adjusted_sql.strip().endswith(';'):
                    adjusted_sql = f"{adjusted_sql[:-1]} LIMIT {limit_value};"
                else:
                    adjusted_sql = f"{adjusted_sql} LIMIT {limit_value}"
    
    # Substituir valores de quantidade
    if 'quantity' in values:
        quantity_value = values['quantity']
        # Procurar por padrões como "quantity > 10" e substituir o número
        adjusted_sql = re.sub(
            r"quantity\s*>\s*\d+", 
            f"quantity > {quantity_value}", 
            adjusted_sql
        )
        adjusted_sql = re.sub(
            r"quantity\s*<\s*\d+", 
            f"quantity < {quantity_value}", 
            adjusted_sql
        )
        adjusted_sql = re.sub(
            r"quantity\s*=\s*\d+", 
            f"quantity = {quantity_value}", 
            adjusted_sql
        )
    
    # Substituir valores de porcentagem
    if 'percentage' in values:
        percentage_value = values['percentage']
        # Procurar por padrões como "discount > 10" e substituir o número
        adjusted_sql = re.sub(
            r"discount\s*>\s*\d+(\.\d+)?", 
            f"discount > {percentage_value}", 
            adjusted_sql
        )
        adjusted_sql = re.sub(
            r"discount\s*<\s*\d+(\.\d+)?", 
            f"discount < {percentage_value}", 
            adjusted_sql
        )
        adjusted_sql = re.sub(
            r"discount\s*=\s*\d+(\.\d+)?", 
            f"discount = {percentage_value}", 
            adjusted_sql
        )
    
    return adjusted_sql

def process_query(question: str, sql: str) -> str:
    """
    Processa a pergunta e a consulta SQL para garantir que os valores numéricos
    da pergunta sejam corretamente refletidos na consulta.
    
    Args:
        question (str): A pergunta do usuário
        sql (str): A consulta SQL gerada
        
    Returns:
        str: Consulta SQL ajustada
    """
    # Extrair valores numéricos da pergunta
    values = extract_numeric_values(question)
    
    # Se encontrou valores, ajustar a consulta SQL
    if values:
        return adjust_sql_with_values(sql, values)
    
    # Se não encontrou valores, retornar a consulta original
    return sql
