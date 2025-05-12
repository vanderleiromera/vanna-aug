"""
Componentes de visualização para a aplicação Vanna AI Odoo.
"""

import dateutil.parser
import pandas as pd
import plotly.express as px
import streamlit as st


def render_visualizations(results):
    """
    Renderizar visualizações para os resultados da consulta.

    Args:
        results: DataFrame com os resultados da consulta
    """
    st.subheader("📊 Visualizações")

    try:
        # Verificar se temos dados suficientes para visualização
        if len(results) == 0:
            st.info("Não há dados suficientes para visualização")
        elif len(results.columns) < 2:
            st.info("São necessárias pelo menos duas colunas para visualização")
        else:
            # Identificar tipos de colunas
            numeric_cols, date_cols, categorical_cols, measure_cols = (
                identify_column_types(results)
            )

            # Logging para debug
            st.caption(
                f"Colunas detectadas: {len(results.columns)} total, {len(date_cols)} datas, {len(categorical_cols)} categorias, {len(measure_cols)} medidas"
            )

            # Criar abas para diferentes tipos de visualizações
            viz_tabs = st.tabs(
                [
                    "Gráfico Principal",
                    "Gráfico de Barras",
                    "Gráfico de Linha",
                    "Gráfico de Pizza",
                    "Tabela Dinâmica",
                    "Detecção de Anomalias",
                ]
            )

            # Aba 1: Gráfico Principal (automático)
            with viz_tabs[0]:
                render_auto_chart(
                    results, date_cols, categorical_cols, numeric_cols, measure_cols
                )

            # Aba 2: Gráfico de Barras
            with viz_tabs[1]:
                render_bar_chart(results, categorical_cols, numeric_cols, measure_cols)

            # Aba 3: Gráfico de Linha
            with viz_tabs[2]:
                render_line_chart(
                    results, date_cols, categorical_cols, numeric_cols, measure_cols
                )

            # Aba 4: Gráfico de Pizza
            with viz_tabs[3]:
                render_pie_chart(results, categorical_cols, numeric_cols, measure_cols)

            # Aba 5: Tabela Dinâmica
            with viz_tabs[4]:
                render_pivot_table(results, numeric_cols)

            # Aba 6: Detecção de Anomalias
            with viz_tabs[5]:
                render_anomaly_detection(results)

    except Exception as e:
        st.error(f"Erro ao criar visualizações: {e}")
        st.info(
            "Tente selecionar colunas diferentes ou verificar se há valores nulos nos dados."
        )


def identify_column_types(df):
    """
    Identificar os tipos de colunas no DataFrame.

    Args:
        df: DataFrame com os dados

    Returns:
        tuple: (numeric_cols, date_cols, categorical_cols, measure_cols)
    """
    # Identificar colunas numéricas
    numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()

    # Identificar colunas de data
    date_cols = []
    for col in df.columns:
        if is_date_column(df, col):
            date_cols.append(col)

    # Identificar colunas categóricas
    categorical_cols = []
    for col in df.columns:
        if col not in date_cols and is_categorical_column(
            df, col, numeric_cols, date_cols
        ):
            categorical_cols.append(col)

    # Identificar colunas de medida (valores importantes)
    measure_cols = []
    for col in numeric_cols:
        if is_measure_column(df, col, numeric_cols):
            measure_cols.append(col)

    # Se não encontramos medidas, usar todos os numéricos
    if not measure_cols and numeric_cols:
        measure_cols = numeric_cols

    return numeric_cols, date_cols, categorical_cols, measure_cols


def is_date_column(df, col_name):
    """
    Verificar se uma coluna contém datas.

    Args:
        df: DataFrame com os dados
        col_name: Nome da coluna a verificar

    Returns:
        bool: True se a coluna contém datas, False caso contrário
    """
    # Verificar se já é um tipo de data
    if df[col_name].dtype == "datetime64[ns]":
        return True

    # Verificar se o nome da coluna sugere uma data
    date_keywords = [
        "data",
        "date",
        "dt",
        "dia",
        "mes",
        "ano",
        "year",
        "month",
        "day",
    ]
    if any(keyword in col_name.lower() for keyword in date_keywords):
        # Tentar converter para data
        try:
            # Verificar se pelo menos 80% dos valores não-nulos podem ser convertidos para data
            sample = df[col_name].dropna().astype(str).head(100)
            if len(sample) == 0:
                return False

            success_count = 0
            for val in sample:
                try:
                    dateutil.parser.parse(val)
                    success_count += 1
                except:
                    pass

            return success_count / len(sample) >= 0.8
        except:
            return False
    return False


def is_categorical_column(df, col_name, numeric_cols, date_cols):
    """
    Verificar se uma coluna é categórica.

    Args:
        df: DataFrame com os dados
        col_name: Nome da coluna a verificar
        numeric_cols: Lista de colunas numéricas
        date_cols: Lista de colunas de data

    Returns:
        bool: True se a coluna é categórica, False caso contrário
    """
    # Se não é numérica nem data
    if col_name in numeric_cols or col_name in date_cols:
        return False

    # Verificar número de valores únicos
    n_unique = df[col_name].nunique()
    n_total = len(df)

    # Se tem poucos valores únicos em relação ao total, é categórica
    if n_unique <= 20 or (n_unique / n_total) < 0.2:
        return True

    # Verificar se o nome da coluna sugere uma categoria
    cat_keywords = [
        "categoria",
        "category",
        "tipo",
        "type",
        "status",
        "estado",
        "state",
        "grupo",
        "group",
    ]
    if any(keyword in col_name.lower() for keyword in cat_keywords):
        return True

    return False


def is_measure_column(df, col_name, numeric_cols):
    """
    Verificar se uma coluna é uma medida (valor numérico significativo).

    Args:
        df: DataFrame com os dados
        col_name: Nome da coluna a verificar
        numeric_cols: Lista de colunas numéricas

    Returns:
        bool: True se a coluna é uma medida, False caso contrário
    """
    # Deve ser numérica
    if col_name not in numeric_cols:
        return False

    # Verificar se o nome da coluna sugere uma medida
    measure_keywords = [
        "valor",
        "value",
        "total",
        "amount",
        "price",
        "preco",
        "quantidade",
        "quantity",
        "count",
        "sum",
        "media",
        "average",
        "avg",
        "min",
        "max",
    ]
    if any(keyword in col_name.lower() for keyword in measure_keywords):
        return True

    # Verificar variância - medidas tendem a ter maior variância
    try:
        variance = df[col_name].var()
        mean = df[col_name].mean()
        # Coeficiente de variação
        if mean != 0 and not pd.isna(mean) and not pd.isna(variance):
            cv = abs(variance / mean)
            if cv > 0.1:  # Variação significativa
                return True
    except:
        pass

    return False


def determine_best_chart_type(
    df, date_cols, categorical_cols, numeric_cols, measure_cols
):
    """
    Determina o melhor tipo de gráfico com base nas características dos dados.

    Args:
        df: DataFrame com os dados
        date_cols: Lista de colunas de data
        categorical_cols: Lista de colunas categóricas
        numeric_cols: Lista de colunas numéricas
        measure_cols: Lista de colunas de medida

    Returns:
        str: Tipo de gráfico recomendado
    """
    # Verificar se temos dados suficientes
    if len(df) == 0:
        return "no_data"

    # Verificar se temos colunas numéricas
    if not numeric_cols and not measure_cols:
        return "no_numeric"

    # Prioridade 1: Série temporal (se temos datas e medidas)
    if date_cols and (measure_cols or numeric_cols):
        # Verificar se há uma tendência temporal clara
        # Ordenar por data e verificar se há pelo menos 3 pontos
        if len(df) >= 3:
            return "time_series"

    # Prioridade 2: Distribuição de categorias (se temos categorias e medidas)
    if categorical_cols and (measure_cols or numeric_cols):
        cat_col = categorical_cols[0]
        n_categories = df[cat_col].nunique()

        # Se temos muitas categorias, um treemap pode ser melhor
        if n_categories > 10:
            return "treemap"
        # Se temos poucas categorias, um gráfico de barras é bom
        else:
            return "bar_chart"

    # Prioridade 3: Correlação entre variáveis numéricas
    if len(numeric_cols) >= 2:
        # Verificar correlação
        try:
            x_col = numeric_cols[0]
            y_col = numeric_cols[1]
            correlation = df[[x_col, y_col]].corr().iloc[0, 1]

            # Se há correlação significativa, um gráfico de dispersão é bom
            if abs(correlation) > 0.3:
                return "scatter_plot"
        except:
            pass

    # Prioridade 4: Distribuição de uma variável numérica
    if numeric_cols:
        # Verificar se parece uma distribuição
        num_col = numeric_cols[0]
        try:
            # Verificar assimetria
            skew = df[num_col].skew()
            if abs(skew) > 1:
                return "histogram"
        except:
            pass

    # Caso padrão: gráfico de barras simples
    return "bar_chart"


def render_auto_chart(results, date_cols, categorical_cols, numeric_cols, measure_cols):
    """
    Renderizar o gráfico automático com base nas características dos dados.

    Args:
        results: DataFrame com os resultados
        date_cols: Lista de colunas de data
        categorical_cols: Lista de colunas categóricas
        numeric_cols: Lista de colunas numéricas
        measure_cols: Lista de colunas de medida
    """
    import plotly.express as px
    import streamlit as st

    st.subheader("Gráfico Automático")

    # Determinar o melhor tipo de gráfico
    chart_type = determine_best_chart_type(
        results, date_cols, categorical_cols, numeric_cols, measure_cols
    )

    # Criar o gráfico apropriado
    if chart_type == "no_data":
        st.info("Não há dados suficientes para visualização")

    elif chart_type == "no_numeric":
        st.info("Não há colunas numéricas para visualização")

    elif chart_type == "time_series":
        # Série temporal
        x_col = date_cols[0]
        y_col = measure_cols[0] if measure_cols else numeric_cols[0]

        # Verificar se temos uma coluna categórica para agrupar
        color_col = None
        if categorical_cols and len(results[categorical_cols[0]].unique()) <= 7:
            color_col = categorical_cols[0]

        # Ordenar por data
        results_sorted = results.sort_values(by=x_col)

        # Criar gráfico de linha
        if color_col:
            fig = px.line(
                results_sorted,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"Evolução de {y_col} ao longo do tempo",
                labels={
                    x_col: "Data",
                    y_col: y_col.replace("_", " ").title(),
                    color_col: color_col.replace("_", " ").title(),
                },
            )
        else:
            fig = px.line(
                results_sorted,
                x=x_col,
                y=y_col,
                title=f"Evolução de {y_col} ao longo do tempo",
                labels={
                    x_col: "Data",
                    y_col: y_col.replace("_", " ").title(),
                },
            )

        # Melhorar formatação do eixo X para datas
        fig.update_xaxes(tickformat="%d/%m/%Y", tickangle=-45)

        st.plotly_chart(fig, use_container_width=True, key="auto_time_series")

        # Adicionar estatísticas de tendência
        try:
            first_value = results_sorted[y_col].iloc[0]
            last_value = results_sorted[y_col].iloc[-1]
            change = last_value - first_value
            pct_change = (
                (change / first_value) * 100 if first_value != 0 else float("inf")
            )

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Valor inicial", f"{first_value:.2f}")
            with col2:
                st.metric("Valor final", f"{last_value:.2f}")
            with col3:
                st.metric(
                    "Variação",
                    f"{change:.2f} ({pct_change:.1f}%)",
                    delta=change,
                    delta_color="normal",
                )
        except:
            pass

    elif chart_type == "treemap":
        # Treemap para muitas categorias
        cat_col = categorical_cols[0]
        value_col = measure_cols[0] if measure_cols else numeric_cols[0]

        # Verificar se temos uma segunda coluna categórica para agrupar
        parents = None
        if len(categorical_cols) >= 2:
            parents = categorical_cols[1]

        # Agrupar por categoria
        if parents:
            agg_data = (
                results.groupby([cat_col, parents])[value_col].sum().reset_index()
            )
            fig = px.treemap(
                agg_data,
                path=[parents, cat_col],
                values=value_col,
                title=f"Distribuição de {value_col} por {cat_col} e {parents}",
                color=value_col,
                color_continuous_scale="RdBu",
            )
        else:
            agg_data = results.groupby(cat_col)[value_col].sum().reset_index()
            fig = px.treemap(
                agg_data,
                path=[cat_col],
                values=value_col,
                title=f"Distribuição de {value_col} por {cat_col}",
                color=value_col,
                color_continuous_scale="RdBu",
            )

        st.plotly_chart(fig, use_container_width=True, key="auto_treemap")

    elif chart_type == "scatter_plot":
        # Gráfico de dispersão para duas variáveis numéricas
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]

        # Verificar se temos uma coluna categórica para agrupar
        color_col = None
        if categorical_cols and len(results[categorical_cols[0]].unique()) <= 7:
            color_col = categorical_cols[0]

        # Criar gráfico de dispersão
        if color_col:
            fig = px.scatter(
                results,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"Relação entre {x_col} e {y_col}",
                labels={
                    x_col: x_col.replace("_", " ").title(),
                    y_col: y_col.replace("_", " ").title(),
                    color_col: color_col.replace("_", " ").title(),
                },
                trendline="ols",  # Adicionar linha de tendência
            )
        else:
            fig = px.scatter(
                results,
                x=x_col,
                y=y_col,
                title=f"Relação entre {x_col} e {y_col}",
                labels={
                    x_col: x_col.replace("_", " ").title(),
                    y_col: y_col.replace("_", " ").title(),
                },
                trendline="ols",  # Adicionar linha de tendência
            )

        st.plotly_chart(fig, use_container_width=True, key="auto_scatter")

        # Adicionar estatísticas de correlação
        try:
            correlation = results[[x_col, y_col]].corr().iloc[0, 1]
            st.metric(
                "Correlação",
                f"{correlation:.2f}",
                delta=(
                    "Forte"
                    if abs(correlation) > 0.7
                    else ("Moderada" if abs(correlation) > 0.3 else "Fraca")
                ),
            )
        except:
            pass

    elif chart_type == "histogram":
        # Histograma para distribuição de uma variável numérica
        num_col = numeric_cols[0]

        # Verificar se temos uma coluna categórica para agrupar
        color_col = None
        if categorical_cols and len(results[categorical_cols[0]].unique()) <= 5:
            color_col = categorical_cols[0]

        # Criar histograma
        if color_col:
            fig = px.histogram(
                results,
                x=num_col,
                color=color_col,
                title=f"Distribuição de {num_col}",
                labels={num_col: num_col.replace("_", " ").title()},
                marginal="box",  # Adicionar boxplot na margem
            )
        else:
            fig = px.histogram(
                results,
                x=num_col,
                title=f"Distribuição de {num_col}",
                labels={num_col: num_col.replace("_", " ").title()},
                marginal="box",  # Adicionar boxplot na margem
            )

        st.plotly_chart(fig, use_container_width=True, key="auto_histogram")

        # Adicionar estatísticas descritivas
        try:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Média", f"{results[num_col].mean():.2f}")
            with col2:
                st.metric("Mediana", f"{results[num_col].median():.2f}")
            with col3:
                st.metric("Desvio Padrão", f"{results[num_col].std():.2f}")
            with col4:
                st.metric("Assimetria", f"{results[num_col].skew():.2f}")
        except:
            pass

    elif chart_type == "bar_chart":
        # Gráfico de barras para categorias
        if categorical_cols:
            x_col = categorical_cols[0]
        else:
            # Usar a primeira coluna como categoria
            x_col = results.columns[0]

        y_col = measure_cols[0] if measure_cols else numeric_cols[0]

        # Verificar se temos uma segunda coluna categórica para agrupar
        color_col = None
        if (
            len(categorical_cols) >= 2
            and len(results[categorical_cols[1]].unique()) <= 7
        ):
            color_col = categorical_cols[1]

        # Agrupar por categoria
        if (
            len(results) > 15 or results[x_col].nunique() > 15
        ):  # Se muitos dados, agregar
            if color_col:
                # Agrupar por duas categorias
                agg_data = (
                    results.groupby([x_col, color_col])[y_col].sum().reset_index()
                )
            else:
                # Agrupar por uma categoria
                agg_data = results.groupby(x_col)[y_col].sum().reset_index()
                # Ordenar por valor
                agg_data = agg_data.sort_values(by=y_col, ascending=False)
                # Limitar a 15 categorias
                if len(agg_data) > 15:
                    agg_data = agg_data.head(15)

            # Criar gráfico de barras
            if color_col:
                fig = px.bar(
                    agg_data,
                    x=x_col,
                    y=y_col,
                    color=color_col,
                    title=f"{y_col} por {x_col}",
                    labels={
                        x_col: x_col.replace("_", " ").title(),
                        y_col: y_col.replace("_", " ").title(),
                        color_col: color_col.replace("_", " ").title(),
                    },
                )
            else:
                fig = px.bar(
                    agg_data,
                    x=x_col,
                    y=y_col,
                    title=f"{y_col} por {x_col}",
                    labels={
                        x_col: x_col.replace("_", " ").title(),
                        y_col: y_col.replace("_", " ").title(),
                    },
                )
        else:
            # Usar dados originais
            if color_col:
                fig = px.bar(
                    results,
                    x=x_col,
                    y=y_col,
                    color=color_col,
                    title=f"{y_col} por {x_col}",
                    labels={
                        x_col: x_col.replace("_", " ").title(),
                        y_col: y_col.replace("_", " ").title(),
                        color_col: color_col.replace("_", " ").title(),
                    },
                )
            else:
                fig = px.bar(
                    results,
                    x=x_col,
                    y=y_col,
                    title=f"{y_col} por {x_col}",
                    labels={
                        x_col: x_col.replace("_", " ").title(),
                        y_col: y_col.replace("_", " ").title(),
                    },
                )

        # Melhorar formatação
        if results[x_col].nunique() > 8:
            fig.update_xaxes(tickangle=-45)

        st.plotly_chart(fig, use_container_width=True, key="auto_bar_chart")

        # Adicionar estatísticas
        try:
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total", f"{results[y_col].sum():.2f}")
            with col2:
                st.metric("Média", f"{results[y_col].mean():.2f}")
            with col3:
                st.metric("Máximo", f"{results[y_col].max():.2f}")
        except:
            pass

    else:
        # Caso padrão: gráfico de barras simples como fallback
        st.info(
            f"Tipo de gráfico '{chart_type}' não implementado. Usando gráfico de barras simples."
        )

        # Usar a primeira coluna como categoria e a primeira coluna numérica como valor
        x_col = results.columns[0]
        y_col = (
            measure_cols[0]
            if measure_cols
            else (numeric_cols[0] if numeric_cols else results.columns[1])
        )

        # Verificar se temos pelo menos duas colunas
        if len(results.columns) >= 2:
            fig = px.bar(
                results,
                x=x_col,
                y=y_col,
                title=f"{y_col} por {x_col}",
                labels={
                    x_col: x_col.replace("_", " ").title(),
                    y_col: y_col.replace("_", " ").title(),
                },
            )

            st.plotly_chart(fig, use_container_width=True, key="auto_bar_simple")
        else:
            st.warning("Não há colunas suficientes para criar um gráfico")


def render_bar_chart(results, categorical_cols, numeric_cols, measure_cols):
    """
    Renderizar um gráfico de barras.

    Args:
        results: DataFrame com os resultados
        categorical_cols: Lista de colunas categóricas
        numeric_cols: Lista de colunas numéricas
        measure_cols: Lista de colunas de medida
    """
    import plotly.express as px
    import streamlit as st

    st.subheader("Gráfico de Barras")

    # Selecionar colunas para o gráfico
    if categorical_cols:
        x_options = categorical_cols
    else:
        x_options = results.columns.tolist()

    if measure_cols:
        y_options = measure_cols
    else:
        y_options = numeric_cols if numeric_cols else results.columns.tolist()

    # Selecionar colunas para o gráfico
    col1, col2, col3 = st.columns(3)
    with col1:
        x_col = st.selectbox("Eixo X (Categorias):", x_options, key="bar_x")
    with col2:
        y_col = st.selectbox("Eixo Y (Valores):", y_options, key="bar_y")
    with col3:
        color_options = ["Nenhum"] + categorical_cols
        color_col = st.selectbox("Cor (Opcional):", color_options, key="bar_color")
        if color_col == "Nenhum":
            color_col = None

    # Opções de agregação
    agg_func = st.selectbox(
        "Função de Agregação:",
        ["Soma", "Média", "Contagem", "Mínimo", "Máximo"],
        key="bar_agg",
    )

    # Mapear função de agregação
    agg_map = {
        "Soma": "sum",
        "Média": "mean",
        "Contagem": "count",
        "Mínimo": "min",
        "Máximo": "max",
    }

    # Criar gráfico de barras
    try:
        # Agrupar dados se necessário
        if color_col:
            agg_data = (
                results.groupby([x_col, color_col])[y_col]
                .agg(agg_map[agg_func])
                .reset_index()
            )
            fig = px.bar(
                agg_data,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"{agg_func} de {y_col} por {x_col}",
                labels={
                    x_col: x_col.replace("_", " ").title(),
                    y_col: y_col.replace("_", " ").title(),
                    color_col: color_col.replace("_", " ").title(),
                },
            )
        else:
            agg_data = (
                results.groupby(x_col)[y_col].agg(agg_map[agg_func]).reset_index()
            )
            # Ordenar por valor
            agg_data = agg_data.sort_values(by=y_col, ascending=False)
            # Limitar a 15 categorias
            if len(agg_data) > 15:
                agg_data = agg_data.head(15)
                st.info("Mostrando apenas as 15 principais categorias.")

            fig = px.bar(
                agg_data,
                x=x_col,
                y=y_col,
                title=f"{agg_func} de {y_col} por {x_col}",
                labels={
                    x_col: x_col.replace("_", " ").title(),
                    y_col: y_col.replace("_", " ").title(),
                },
            )

        # Melhorar formatação
        if agg_data[x_col].nunique() > 8:
            fig.update_xaxes(tickangle=-45)

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao criar gráfico de barras: {e}")
        st.info("Tente selecionar colunas diferentes.")


def render_line_chart(results, date_cols, categorical_cols, numeric_cols, measure_cols):
    """
    Renderizar um gráfico de linha.

    Args:
        results: DataFrame com os resultados
        date_cols: Lista de colunas de data
        categorical_cols: Lista de colunas categóricas
        numeric_cols: Lista de colunas numéricas
        measure_cols: Lista de colunas de medida
    """
    import plotly.express as px
    import streamlit as st

    st.subheader("Gráfico de Linha")

    # Verificar se temos colunas de data
    if not date_cols:
        st.info(
            "Não foram detectadas colunas de data para criar um gráfico de linha temporal."
        )
        st.info("Selecione colunas para criar um gráfico de linha genérico:")
        x_options = results.columns.tolist()
    else:
        st.info("Colunas de data detectadas. Criando gráfico de linha temporal.")
        x_options = date_cols

    if measure_cols:
        y_options = measure_cols
    else:
        y_options = numeric_cols if numeric_cols else results.columns.tolist()

    # Selecionar colunas para o gráfico
    col1, col2, col3 = st.columns(3)
    with col1:
        x_col = st.selectbox("Eixo X (Tempo/Sequência):", x_options, key="line_x")
    with col2:
        y_col = st.selectbox("Eixo Y (Valores):", y_options, key="line_y")
    with col3:
        color_options = ["Nenhum"] + categorical_cols
        color_col = st.selectbox("Cor (Opcional):", color_options, key="line_color")
        if color_col == "Nenhum":
            color_col = None

    # Criar gráfico de linha
    try:
        # Ordenar por eixo X
        results_sorted = results.sort_values(by=x_col)

        # Criar gráfico
        if color_col:
            fig = px.line(
                results_sorted,
                x=x_col,
                y=y_col,
                color=color_col,
                title=f"Evolução de {y_col} por {x_col}",
                labels={
                    x_col: x_col.replace("_", " ").title(),
                    y_col: y_col.replace("_", " ").title(),
                    color_col: color_col.replace("_", " ").title(),
                },
            )
        else:
            fig = px.line(
                results_sorted,
                x=x_col,
                y=y_col,
                title=f"Evolução de {y_col} por {x_col}",
                labels={
                    x_col: x_col.replace("_", " ").title(),
                    y_col: y_col.replace("_", " ").title(),
                },
            )

        # Melhorar formatação para datas
        if x_col in date_cols:
            fig.update_xaxes(tickformat="%d/%m/%Y", tickangle=-45)

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao criar gráfico de linha: {e}")
        st.info("Tente selecionar colunas diferentes.")


def render_pie_chart(results, categorical_cols, numeric_cols, measure_cols):
    """
    Renderizar um gráfico de pizza.

    Args:
        results: DataFrame com os resultados
        categorical_cols: Lista de colunas categóricas
        numeric_cols: Lista de colunas numéricas
        measure_cols: Lista de colunas de medida
    """
    import plotly.express as px
    import streamlit as st

    st.subheader("Gráfico de Pizza")

    # Verificar se temos colunas categóricas
    if not categorical_cols:
        st.info(
            "Não foram detectadas colunas categóricas para criar um gráfico de pizza."
        )
        st.info("Selecione uma coluna para usar como categoria:")
        names_options = results.columns.tolist()
    else:
        names_options = categorical_cols

    if measure_cols:
        values_options = measure_cols
    else:
        values_options = numeric_cols if numeric_cols else results.columns.tolist()

    # Selecionar colunas para o gráfico
    col1, col2 = st.columns(2)
    with col1:
        names_col = st.selectbox("Categorias:", names_options, key="pie_names")
    with col2:
        values_col = st.selectbox("Valores:", values_options, key="pie_values")

    # Criar gráfico de pizza
    try:
        # Agrupar dados
        agg_data = results.groupby(names_col)[values_col].sum().reset_index()

        # Ordenar por valor
        agg_data = agg_data.sort_values(by=values_col, ascending=False)

        # Limitar a 10 categorias para melhor visualização
        if len(agg_data) > 10:
            # Separar as 9 principais categorias e agrupar o resto como "Outros"
            top_data = agg_data.head(9)
            others_sum = agg_data.iloc[9:][values_col].sum()
            others_row = pd.DataFrame({names_col: ["Outros"], values_col: [others_sum]})
            agg_data = pd.concat([top_data, others_row], ignore_index=True)
            st.info(
                "Mostrando as 9 principais categorias. O restante foi agrupado como 'Outros'."
            )

        # Criar gráfico
        fig = px.pie(
            agg_data,
            names=names_col,
            values=values_col,
            title=f"Distribuição de {values_col} por {names_col}",
            hole=0.4,  # Donut chart
        )

        # Melhorar formatação
        fig.update_traces(textposition="inside", textinfo="percent+label")

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Erro ao criar gráfico de pizza: {e}")
        st.info("Tente selecionar colunas diferentes.")


def render_pivot_table(results, numeric_cols):
    """
    Renderizar uma tabela dinâmica.

    Args:
        results: DataFrame com os resultados
        numeric_cols: Lista de colunas numéricas
    """
    import pandas as pd
    import plotly.express as px
    import streamlit as st

    st.subheader("Tabela Dinâmica")

    # Permitir ao usuário selecionar colunas
    cols = list(results.columns)

    col1, col2, col3 = st.columns(3)
    with col1:
        index_col = st.selectbox("Linhas:", cols, key="pivot_index")
    with col2:
        if len(cols) > 1:
            columns_col = st.selectbox(
                "Colunas (opcional):",
                ["Nenhum"] + cols,
                key="pivot_columns",
            )
        else:
            columns_col = "Nenhum"
    with col3:
        available_values = numeric_cols if numeric_cols else cols
        values_col = st.selectbox("Valores:", available_values, key="pivot_values")

    # Selecionar função de agregação
    agg_func = st.selectbox(
        "Função de agregação:",
        ["Soma", "Média", "Contagem", "Mínimo", "Máximo"],
        key="pivot_agg",
    )

    # Mapear função de agregação
    agg_map = {
        "Soma": "sum",
        "Média": "mean",
        "Contagem": "count",
        "Mínimo": "min",
        "Máximo": "max",
    }

    # Criar tabela dinâmica
    try:
        if columns_col != "Nenhum":
            pivot = pd.pivot_table(
                results,
                index=index_col,
                columns=columns_col,
                values=values_col,
                aggfunc=agg_map[agg_func],
            )
        else:
            pivot = pd.pivot_table(
                results,
                index=index_col,
                values=values_col,
                aggfunc=agg_map[agg_func],
            )

        # Exibir tabela dinâmica
        st.dataframe(pivot, use_container_width=True)

        # Criar gráfico de calor
        if columns_col != "Nenhum":
            st.subheader("Mapa de Calor")
            fig = px.imshow(
                pivot,
                labels=dict(x=columns_col, y=index_col, color=values_col),
                title=f"{agg_func} de {values_col} por {index_col} e {columns_col}",
            )
            st.plotly_chart(fig, use_container_width=True)
    except Exception as e:
        st.error(f"Erro ao criar tabela dinâmica: {e}")
        st.info(
            "Tente selecionar colunas diferentes ou verificar se há valores nulos nos dados."
        )


def render_anomaly_detection(results):
    """
    Renderizar a detecção de anomalias.

    Args:
        results: DataFrame com os resultados
    """
    import streamlit as st

    st.subheader("Detecção de Anomalias")

    # Verificar se temos colunas numéricas
    numeric_cols = results.select_dtypes(include=["number"]).columns.tolist()

    if not numeric_cols:
        st.info("Não foram detectadas colunas numéricas para detecção de anomalias.")
        return

    # Permitir ao usuário selecionar colunas para análise
    selected_columns = st.multiselect(
        "Selecione colunas numéricas para análise:",
        numeric_cols,
        default=numeric_cols[: min(3, len(numeric_cols))],
        key="anomaly_columns",
    )

    if not selected_columns:
        st.info("Selecione pelo menos uma coluna para análise.")
        return

    # Selecionar método de detecção
    method = st.selectbox(
        "Método de detecção:",
        ["z-score", "iqr", "isolation_forest", "knn"],
        key="anomaly_method",
        format_func=lambda x: {
            "z-score": "Estatístico (Z-score)",
            "iqr": "Intervalo Interquartil (IQR)",
            "isolation_forest": "Isolation Forest",
            "knn": "K-Nearest Neighbors (KNN)",
        }.get(x, x),
    )

    # Parâmetros específicos do método
    params = {}

    if method == "z-score":
        params["z_threshold"] = st.slider(
            "Limiar Z-score:",
            min_value=1.0,
            max_value=5.0,
            value=3.0,
            step=0.1,
            key="z_threshold",
        )

    elif method == "iqr":
        params["iqr_multiplier"] = st.slider(
            "Multiplicador IQR:",
            min_value=0.5,
            max_value=3.0,
            value=1.5,
            step=0.1,
            key="iqr_multiplier",
        )

    elif method == "isolation_forest" or method == "knn":
        params["contamination"] = st.slider(
            "Contaminação esperada (%):",
            min_value=0.01,
            max_value=0.5,
            value=0.05,
            step=0.01,
            key="contamination",
        )

        if method == "knn":
            params["n_neighbors"] = st.slider(
                "Número de vizinhos:",
                min_value=1,
                max_value=20,
                value=5,
                step=1,
                key="n_neighbors",
            )

    # Botão para executar a detecção
    if st.button("Detectar Anomalias", key="detect_anomalies") and selected_columns:
        try:
            with st.spinner("Detectando anomalias..."):
                # Importar a função de detecção de anomalias
                from modules.anomaly_detection import (
                    create_anomaly_visualization,
                    format_anomaly_summary,
                )

                # Criar visualização com detecção de anomalias
                fig, df_with_outliers, anomaly_summary = create_anomaly_visualization(
                    results,
                    method=method,
                    columns=selected_columns,
                    **params,
                )

                # Exibir o gráfico
                if fig:
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.warning(
                        "Não foi possível criar uma visualização para os dados selecionados"
                    )

                # Exibir resumo das anomalias
                st.markdown(format_anomaly_summary(anomaly_summary))

                # Exibir dados com anomalias destacadas
                if "contains_outliers" in df_with_outliers.columns:
                    st.subheader("Dados com Anomalias Destacadas")

                    # Função para destacar anomalias
                    def highlight_anomalies(row):
                        try:
                            if "contains_outliers" in row and row["contains_outliers"]:
                                return ["background-color: rgba(255, 0, 0, 0.2)"] * len(
                                    row
                                )
                        except Exception as e:
                            st.error(f"Erro ao destacar anomalias: {str(e)}")
                        return [""] * len(row)

                    # Exibir DataFrame estilizado
                    try:
                        # Criar uma cópia do DataFrame para não modificar o original
                        display_df = df_with_outliers.copy()

                        # Remover a coluna 'contains_outliers' se existir
                        if "contains_outliers" in display_df.columns:
                            display_df = display_df.drop(columns=["contains_outliers"])

                        # Aplicar o estilo
                        styled_df = display_df.style.apply(highlight_anomalies, axis=1)
                        st.dataframe(styled_df, use_container_width=True)
                    except Exception as e:
                        st.error(f"Erro ao exibir dados com anomalias: {str(e)}")
                        # Exibir o DataFrame sem estilo como fallback
                        st.dataframe(df_with_outliers, use_container_width=True)

                    # Opção para baixar os dados com anomalias
                    try:
                        # Criar uma cópia do DataFrame para não modificar o original
                        download_df = df_with_outliers.copy()

                        # Adicionar uma coluna 'é_anomalia' para indicar se a linha é uma anomalia
                        if "contains_outliers" in download_df.columns:
                            download_df["é_anomalia"] = download_df["contains_outliers"]
                            download_df = download_df.drop(
                                columns=["contains_outliers"]
                            )

                        # Converter para CSV
                        csv = download_df.to_csv(index=False)

                        # Botão de download
                        st.download_button(
                            "Baixar Dados com Anomalias (CSV)",
                            csv,
                            "anomalias_detectadas.csv",
                            "text/csv",
                            key="download_anomalies",
                        )
                    except Exception as e:
                        st.error(f"Erro ao preparar dados para download: {str(e)}")
        except Exception as e:
            st.error(f"Erro ao detectar anomalias: {str(e)}")
            st.info(
                "Verifique se as colunas selecionadas são adequadas para o método escolhido."
            )
