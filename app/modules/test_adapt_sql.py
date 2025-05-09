"""
Script para testar a função adapt_sql_from_similar_question.
"""

import re

def adapt_sql_from_similar_question(question, similar_question):
    """
    Adapta a consulta SQL de uma pergunta similar para a pergunta atual
    """
    try:
        # Obter a consulta SQL da pergunta similar
        sql = similar_question["sql"]
        print(f"SQL original:\n{sql}")
        
        # Extrair o número de dias da pergunta atual
        days_match = re.search(r"(\d+)\s+dias", question.lower())
        if days_match:
            days = int(days_match.group(1))
            print(f"Detectado {days} dias na pergunta atual")
            
            # Verificar se é a pergunta específica sobre produtos sem estoque
            if "produtos foram vendidos nos últimos" in question.lower() and "não têm estoque" in question.lower():
                print(f"Detectada pergunta específica sobre produtos sem estoque")
                
                # Verificar se o SQL original contém o padrão de 30 dias
                if "INTERVAL '30 days'" in sql:
                    # Substituir diretamente o padrão de 30 dias pelo número de dias da pergunta atual
                    sql = sql.replace("INTERVAL '30 days'", f"INTERVAL '{days} days'")
                    print(f"Substituído INTERVAL '30 days' por INTERVAL '{days} days'")
                else:
                    # Procurar outros padrões de intervalo de tempo
                    patterns = [
                        (r"INTERVAL\s+'30\s+days'", f"INTERVAL '{days} days'"),
                        (r"NOW\(\)\s*-\s*INTERVAL\s+'30\s+days'", f"NOW() - INTERVAL '{days} days'"),
                        (r"CURRENT_DATE\s*-\s*INTERVAL\s+'30\s+days'", f"CURRENT_DATE - INTERVAL '{days} days'")
                    ]
                    
                    for pattern, replacement in patterns:
                        sql = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)
            
            # Para qualquer pergunta com dias, não apenas a específica sobre produtos sem estoque
            else:
                # Substituir todos os padrões conhecidos de intervalo de tempo
                patterns = [
                    (r"INTERVAL\s+'(\d+)\s+days'", f"INTERVAL '{days} days'"),
                    (r"NOW\(\)\s*-\s*INTERVAL\s+'(\d+)\s+days'", f"NOW() - INTERVAL '{days} days'"),
                    (r"CURRENT_DATE\s*-\s*INTERVAL\s+'(\d+)\s+days'", f"CURRENT_DATE - INTERVAL '{days} days'"),
                    (r"date_order\s*>=\s*NOW\(\)\s*-\s*INTERVAL\s+'(\d+)\s+days'", f"date_order >= NOW() - INTERVAL '{days} days'"),
                    (r"date_order\s*>=\s*CURRENT_DATE\s*-\s*INTERVAL\s+'(\d+)\s+days'", f"date_order >= CURRENT_DATE - INTERVAL '{days} days'")
                ]
                
                original_sql = sql
                for pattern, replacement in patterns:
                    sql = re.sub(pattern, replacement, sql, flags=re.IGNORECASE)
                
                # Verificar se houve alteração
                if sql != original_sql:
                    print(f"Substituído intervalo de dias no SQL para {days} dias")
                else:
                    print(f"Não foi possível substituir o intervalo de dias no SQL")
                    
                    # Tentativa adicional com substituição direta
                    replacements = [
                        ("NOW() - INTERVAL '30 days'", f"NOW() - INTERVAL '{days} days'"),
                        ("CURRENT_DATE - INTERVAL '30 days'", f"CURRENT_DATE - INTERVAL '{days} days'"),
                        ("INTERVAL '30 days'", f"INTERVAL '{days} days'"),
                        ("'30 days'", f"'{days} days'"),
                        ("INTERVAL '7 days'", f"INTERVAL '{days} days'"),
                        ("'7 days'", f"'{days} days'"),
                        ("INTERVAL '60 days'", f"INTERVAL '{days} days'"),
                        ("'60 days'", f"'{days} days'"),
                        ("INTERVAL '90 days'", f"INTERVAL '{days} days'"),
                        ("'90 days'", f"'{days} days'")
                    ]
                    
                    for old_pattern, new_pattern in replacements:
                        if old_pattern in sql:
                            print(f"Substituindo '{old_pattern}' por '{new_pattern}'")
                            sql = sql.replace(old_pattern, new_pattern)
        
        print(f"SQL adaptado:\n{sql}")
        return sql
    except Exception as e:
        print(f"Erro ao adaptar SQL: {e}")
        import traceback
        traceback.print_exc()
        return similar_question["sql"]  # Retornar o SQL original em caso de erro

if __name__ == "__main__":
    # Exemplo de pergunta e SQL
    question = "Quais produtos foram vendidos nos últimos 60 dias, mas não têm estoque em mãos?"
    similar_question = {
        "question": "Quais produtos foram vendidos nos últimos 30 dias, mas não têm estoque em mãos?",
        "sql": """
    SELECT
        pt.name AS produto,
        SUM(sol.product_uom_qty) AS total_vendido,
        COALESCE(SUM(sq.quantity), 0) AS estoque
    FROM
        sale_order_line sol
    JOIN
        product_product pp ON sol.product_id = pp.id
    JOIN
        product_template pt ON pp.product_tmpl_id = pt.id
    LEFT JOIN
        stock_quant sq ON pp.id = sq.product_id AND sq.location_id = (SELECT id FROM stock_location WHERE name = 'Stock' LIMIT 1)
    JOIN
        sale_order so ON sol.order_id = so.id
    WHERE
        so.date_order >= NOW() - INTERVAL '30 days'  -- Filtrando para os últimos 30 dias
    GROUP BY
        pt.id, pt.name, pt.default_code
    HAVING SUM
        (sol.product_uom_qty) > 0 AND COALESCE(SUM(sq.quantity), 0) = 0;
    """
    }

    # Testar a função
    adapted_sql = adapt_sql_from_similar_question(question, similar_question)
    print("\nResultado final:")
    print(adapted_sql)
