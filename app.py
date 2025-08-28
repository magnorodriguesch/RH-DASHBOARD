# app.py - Dashboard de RH (Versão 6.3 - Correção de Formato dos KPIs)
#
# Este script cria um dashboard de RH interativo e visualmente atraente.
# Correção do erro KeyError 'Area', melhorias no tratamento de dados e
# ajuste do tamanho da fonte para que os valores de KPI não sejam cortados.
#
# Para rodar:
# 1) Instale as dependências: `pip install streamlit pandas numpy plotly openpyxl python-date-util xlsxwriter`
# 2) Rode o aplicativo: `streamlit run app.py`
#
# Autor: Gemini (Versão final aprimorada)
# Data: 28/08/2025

import os
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import date
from io import BytesIO

# --------------------- 1. PÁGINA DE CONFIGURAÇÃO ---------------------
st.set_page_config(
    page_title="People Analytics | Painel de Colaboradores",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------- 2. FUNÇÕES ÚTEIS ---------------------
@st.cache_data
def load_and_prepare_data(file_path):
    """
    Carrega dados de um arquivo Excel e realiza o pré-processamento.
    Retorna o DataFrame preparado e um booleano de sucesso.
    """
    if not os.path.exists(file_path):
        st.error(f"❌ Arquivo não encontrado: **{file_path}**")
        st.info("Por favor, certifique-se de que o arquivo 'BaseFuncionarios.xlsx' esteja na mesma pasta do 'app.py'.")
        return pd.DataFrame(), False

    try:
        df = pd.read_excel(file_path, engine="openpyxl")
        
        # Normaliza os nomes das colunas, removendo acentos, espaços e caracteres especiais
        df.columns = df.columns.str.normalize('NFKD').str.encode('ascii', 'ignore').str.decode('utf-8').str.replace(' ', '_').str.replace('[^a-zA-Z0-9_]', '', regex=True)

        # Trata colunas de data
        date_cols = ["Data_de_Nascimento", "Data_de_Contratacao", "Data_de_Demissao"]
        for col in date_cols:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col], errors="coerce")
        
        # Cria colunas de dados derivados
        today = pd.Timestamp(date.today())
        if "Data_de_Nascimento" in df.columns:
            df["Idade"] = ((today - df["Data_de_Nascimento"]).dt.days / 365.25).astype(int)
        
        if "Data_de_Demissao" in df.columns:
            df["Status"] = np.where(df["Data_de_Demissao"].notna(), "Desligado", "Ativo")
        else:
            df["Status"] = "Ativo"
        
        if "Sexo" in df.columns:
            df["Sexo"] = df["Sexo"].astype(str).str.upper().str.strip()
            # Garante que os valores sejam 'M' ou 'F'
            df["Sexo"] = df["Sexo"].apply(lambda x: 'M' if x == 'M' else 'F' if x == 'F' else np.nan)

        return df, True

    except Exception as e:
        st.error(f"❌ Erro ao processar o arquivo Excel: {e}")
        return pd.DataFrame(), False

def brl(x: float) -> str:
    """
    Formata um número para o padrão de moeda Real (R$), garantindo 2 casas decimais.
    """
    try:
        # Usa um formato f-string com separador de milhares e vírgula decimal
        return f"R$ {x:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
    except (ValueError, TypeError):
        return "R$ 0,00"
        
def format_kpi_value(value):
    """
    Formata o valor do KPI para que caiba no card.
    Usa um tamanho de fonte menor para valores maiores.
    """
    if isinstance(value, (int, float)):
        # Converte para string com formatação de moeda ou inteiro
        if value > 999999:
            val_str = brl(value) if value >= 1 else f"{int(value):,.0f}".replace(",", ".")
        else:
            val_str = brl(value) if value >= 1 else f"{int(value):,.0f}".replace(",", ".")
    else:
        val_str = str(value)
        
    font_size = "0.9rem" # Tamanho padrão
    if len(val_str) > 10:
        font_size = "0.8rem"
    if len(val_str) > 14:
        font_size = "0.6rem"
        
    return f"""<div style="font-size:{font_size}; color:{colors['main']}; font-weight:500;">{val_str}</div>"""

# --------------------- 3. PALETAS DE CORES ---------------------
# Define as paletas de cores para os gráficos
color_palettes = {
    "Azul": {
        "main": "#005a9c",
        "secondary": "#a9c4db",
        "neutral": "#C0C0C0",
        "sequential": px.colors.sequential.Blues,
        "choropleth": "Blues",
        "pie_gender": ["#005a9c", "#a9c4db"]
    },
    "Vermelho": {
        "main": "#8B0000",
        "secondary": "#E59866",
        "neutral": "#C0C0C0",
        "sequential": px.colors.sequential.Reds,
        "choropleth": "Reds",
        "pie_gender": ["#8B0000", "#E59866"]
    }
}

# --------------------- 4. LAYOUT PRINCIPAL E CARREGAMENTO DE DADOS ---------------------
st.title("People Analytics | Quadro de Colaboradores")
st.markdown("Uma visão completa e interativa sobre a força de trabalho.")

# Carrega os dados
df, success = load_and_prepare_data("BaseFuncionarios.xlsx")
if not success or df.empty:
    st.stop()
    
# Define a variável `today` para ser usada nos KPIs
today = pd.Timestamp(date.today())

# --------------------- 5. BARRA LATERAL (FILTROS) ---------------------
st.sidebar.header("⚙️ Opções de Filtro")

# Seletor de tema de cores
selected_theme = st.sidebar.radio("🎨 Tema de Cores", ("Azul", "Vermelho"))
colors = color_palettes[selected_theme]

# Filtros de dados
st.sidebar.markdown("---")
st.sidebar.subheader("Filtros Específicos")

df_filtered = df.copy()

# Filtro de Área
if "Area" in df.columns:
    areas = ["Todos"] + df["Area"].unique().tolist()
    selected_area = st.sidebar.selectbox("Área", areas)
    if selected_area != "Todos":
        df_filtered = df_filtered[df_filtered["Area"] == selected_area]

# Filtro de Nível
if "Nivel" in df_filtered.columns:
    niveis = ["Todos"] + df_filtered["Nivel"].unique().tolist()
    selected_nivel = st.sidebar.selectbox("Nível", niveis)
    if selected_nivel != "Todos":
        df_filtered = df_filtered[df_filtered["Nivel"] == selected_nivel]

# Filtro de Cargo
if "Cargo" in df_filtered.columns:
    cargos = ["Todos"] + df_filtered["Cargo"].unique().tolist()
    selected_cargo = st.sidebar.selectbox("Cargo", cargos)
    if selected_cargo != "Todos":
        df_filtered = df_filtered[df_filtered["Cargo"] == selected_cargo]

# Filtro de Salário
if "Salario_Base" in df_filtered.columns and not df_filtered["Salario_Base"].dropna().empty:
    min_sal = int(df_filtered["Salario_Base"].min())
    max_sal = int(df_filtered["Salario_Base"].max())
    sal_range = st.sidebar.slider("Faixa Salarial (R$)", min_sal, max_sal, (min_sal, max_sal))
    df_filtered = df_filtered[(df_filtered["Salario_Base"] >= sal_range[0]) & (df_filtered["Salario_Base"] <= sal_range[1])]

# Filtro de Status
if "Status" in df_filtered.columns:
    status_options = ["Todos"] + df_filtered["Status"].unique().tolist()
    selected_status = st.sidebar.selectbox("Status do Funcionário", status_options)
    if selected_status != "Todos":
        df_filtered = df_filtered[df_filtered["Status"] == selected_status]

# Adiciona um filtro geral para "Nome Completo"
st.sidebar.markdown("---")
search_query = st.sidebar.text_input("🔎 Pesquisar por Nome", help="Busque por um nome específico.")
if search_query:
    df_filtered = df_filtered[df_filtered["Nome_Completo"].str.contains(search_query, case=False, na=False)]

# --------------------- 6. ESTILOS CSS PERSONALIZADOS ---------------------
st.markdown(f"""
<style>
    .st-emotion-cache-18ni7ap {{
        padding-top: 1rem;
        padding-bottom: 1rem;
    }}
    .main .block-container {{
        padding-top: 1rem;
        padding-bottom: 1rem;
    }}
    .stMetric {{
        background-color: #ffffff;
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        text-align: left;
        transition: transform 0.3s;
    }}
    .stMetric:hover {{
        transform: translateY(-5px);
    }}
    .stMetric label {{
        font-size: 1.2rem;
        color: #4a4a4a;
        font-weight: 500;
    }}
    .stMetric .css-1g6x8j0 {{
        overflow: hidden !important;
    }}
    .metric-container {{
        display: flex;
        justify-content: space-between;
    }}
    .chart-card {{
        background-color: #ffffff;
        padding: 15px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
        height: 100%;
    }}
    h1, h2 {{
        color: #4a4a4a;
        border-bottom: 2px solid #e0e0e0;
        padding-bottom: 5px;
    }}
    .st-emotion-cache-13ln4j7 {{
        background-color: #bdbdbd;
        height: 2px;
        margin: 20px 0;
    }}
</style>
""", unsafe_allow_html=True)

# --------------------- 7. SEÇÃO DE KPIs (BARRA SUPERIOR) ---------------------
st.subheader("Métricas de Visão Geral")

# Cálculo de KPIs
headcount_total = len(df_filtered)
headcount_ativo = len(df_filtered[df_filtered["Status"] == "Ativo"])
novas_contratacoes = len(df_filtered[df_filtered["Data_de_Contratacao"].dt.year == today.year])
total_demissoes = len(df_filtered[df_filtered["Status"] == "Desligado"])
masculino_count = len(df_filtered[df_filtered.get("Sexo") == 'M'])
feminino_count = len(df_filtered[df_filtered.get("Sexo") == 'F'])

# Folha salarial anual
if "Salario_Base" in df_filtered.columns:
    folha_salarial_anual = df_filtered["Salario_Base"].sum() * 12
    folha_salarial_anual_fmt = brl(folha_salarial_anual)
else:
    folha_salarial_anual_fmt = "N/A"

# Salário médio
if "Salario_Base" in df_filtered.columns and headcount_total > 0:
    salario_medio = df_filtered["Salario_Base"].mean()
    salario_medio_fmt = brl(salario_medio)
else:
    salario_medio_fmt = "N/A"

# Idade média
if "Idade" in df_filtered.columns and headcount_total > 0:
    idade_media = df_filtered["Idade"].mean()
    idade_media_fmt = f"{idade_media:.1f} anos"
else:
    idade_media_fmt = "N/A"

# 2 linhas de KPIs: 3 em cima, 2 embaixo
kpi_row1 = st.columns(3)
with kpi_row1[0]:
    st.metric("Total de Funcionários", value=headcount_total)
with kpi_row1[1]:
    st.metric("Funcionários Ativos", value=headcount_ativo)
with kpi_row1[2]:
    st.metric("Novas Contratações (Ano)", value=novas_contratacoes)

kpi_row2 = st.columns(2)
with kpi_row2[0]:
    st.metric("Total de Demissões", value=total_demissoes)
with kpi_row2[1]:
    st.metric("Folha Salarial Anual", value=folha_salarial_anual_fmt)

# Linha extra para salário médio e idade média (opcional, pode remover se não quiser)
kpi_row3 = st.columns(2)
with kpi_row3[0]:
    st.metric("Salário Médio", value=salario_medio_fmt)
with kpi_row3[1]:
    st.metric("Idade Média", value=idade_media_fmt)

st.markdown("---")

# --------------------- 8. SEÇÃO DE GRÁFICOS E ANÁLISES ---------------------
row1_col1, row1_col2 = st.columns(2)
row2_col1, row2_col2 = st.columns(2)
row3_col1, row3_col2 = st.columns(2)

with row1_col1:
    with st.container(border=True):
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.subheader("Contratações e Demissões (Mensal)")
        if "Data_de_Contratacao" in df_filtered.columns and "Data_de_Demissao" in df_filtered.columns:
            df_admissao = df_filtered[df_filtered['Status'] == 'Ativo'].copy()
            df_demissao = df_filtered[df_filtered['Status'] == 'Desligado'].copy()

            df_admissao["Mes"] = df_admissao["Data_de_Contratacao"].dt.to_period('M').astype(str)
            df_demissao["Mes"] = df_demissao["Data_de_Demissao"].dt.to_period('M').astype(str)

            admissao_counts = df_admissao.groupby("Mes").size().reset_index(name="Admissões")
            demissao_counts = df_demissao.groupby("Mes").size().reset_index(name="Demissões")

            df_line = pd.merge(admissao_counts, demissao_counts, on="Mes", how="outer").fillna(0)
            df_line_long = pd.melt(df_line, id_vars="Mes", var_name="Tipo", value_name="Contagem")
            
            fig_line = px.area(
                df_line_long, 
                x="Mes", 
                y="Contagem", 
                color="Tipo",
                title="Tendência de Contratações vs. Demissões por Mês",
                color_discrete_map={"Admissões": colors["main"], "Demissões": colors["neutral"]}
            )
            fig_line.update_layout(xaxis_title="", yaxis_title="Número de Pessoas")
            st.plotly_chart(fig_line, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with row1_col2:
    with st.container(border=True):
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.subheader("Análise Demográfica")
        col_demog1, col_demog2 = st.columns(2)
        
        with col_demog1:
            if "Sexo" in df_filtered.columns:
                sex_counts = df_filtered.get("Sexo").value_counts().reset_index()
                sex_counts.columns = ["Sexo", "Contagem"]
                fig_sex = px.pie(
                    sex_counts,
                    values="Contagem",
                    names="Sexo",
                    title="Distribuição por Sexo",
                    color_discrete_sequence=colors["pie_gender"]
                )
                fig_sex.update_traces(textposition='inside', textinfo='percent+label')
                st.plotly_chart(fig_sex, use_container_width=True)

        with col_demog2:
            if "Idade" in df_filtered.columns:
                bins = [0, 18, 25, 35, 45, 55, 65, 100]
                labels = ['0-18', '19-25', '26-35', '36-45', '46-55', '56-65', '65+']
                df_filtered["Faixa_Etaria"] = pd.cut(df_filtered["Idade"], bins=bins, labels=labels, right=False)
                age_counts = df_filtered["Faixa_Etaria"].value_counts().reset_index()
                age_counts.columns = ["Faixa_Etaria", "Contagem"]
                fig_age = px.bar(
                    age_counts.sort_values(by="Faixa_Etaria"),
                    x="Faixa_Etaria",
                    y="Contagem",
                    title="Distribuição por Faixa Etária",
                    color="Faixa_Etaria",
                    color_discrete_sequence=colors["sequential"]
                )
                st.plotly_chart(fig_age, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with row2_col1:
    with st.container(border=True):
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.subheader("Nível Hierárquico")
        if "Cargo" in df_filtered.columns:
            cargo_counts = df_filtered["Cargo"].value_counts().reset_index()
            cargo_counts.columns = ["Cargo", "Contagem"]
            fig_cargo = px.bar(
                cargo_counts.sort_values(by="Contagem", ascending=False).head(10),
                x="Cargo",
                y="Contagem",
                title="Top 10 Cargos por Headcount",
                color="Cargo",
                color_discrete_sequence=colors["sequential"]
            )
            fig_cargo.update_layout(xaxis={'categoryorder':'total descending'})
            st.plotly_chart(fig_cargo, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with row2_col2:
    with st.container(border=True):
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.subheader("Salário Médio por Cargo")
        if "Cargo" in df_filtered.columns and "Salario_Base" in df_filtered.columns:
            salary_by_cargo = df_filtered.groupby("Cargo")["Salario_Base"].mean().reset_index()
            fig_sal_cargo = px.bar(
                salary_by_cargo.sort_values(by="Salario_Base", ascending=False).head(10),
                x="Salario_Base",
                y="Cargo",
                orientation='h',
                title="Top 10 Salários Médios por Cargo",
                color="Cargo",
                color_discrete_sequence=colors["sequential"]
            )
            fig_sal_cargo.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_sal_cargo, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with row3_col1:
    with st.container(border=True):
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.subheader("Custo por Nível e Área")
        if "Custo_Total_Mensal" not in df_filtered.columns:
            custo_cols = [c for c in ["Salario_Base", "Impostos", "Beneficios", "VT", "VR"] if c in df_filtered.columns]
            df_filtered["Custo_Total_Mensal"] = df_filtered[custo_cols].sum(axis=1)

        if "Nivel" in df_filtered.columns and "Custo_Total_Mensal" in df_filtered.columns:
            fig_sunburst = px.sunburst(
                df_filtered, 
                path=['Nivel', 'Area'],
                values='Custo_Total_Mensal',
                color_discrete_sequence=colors["sequential"]
            )
            fig_sunburst.update_layout(title_text="Custo por Nível e Área", margin=dict(t=0, b=0, l=0, r=0))
            st.plotly_chart(fig_sunburst, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

with row3_col2:
    with st.container(border=True):
        st.markdown("<div class='chart-card'>", unsafe_allow_html=True)
        st.subheader("Mapa de Contratações por Estado")
        if "Endereço" in df_filtered.columns:
            df_filtered["Estado"] = df_filtered["Endereço"].str.extract(r'-\s(..),?$', expand=False)
            df_filtered["Estado"] = df_filtered["Estado"].fillna("Outro")
            
            estado_counts = df_filtered["Estado"].value_counts().reset_index()
            estado_counts.columns = ["Estado", "Contagem"]

            state_codes = {
                'AC': 'AC', 'AL': 'AL', 'AP': 'AP', 'AM': 'AM', 'BA': 'BA', 'CE': 'CE', 'DF': 'DF', 'ES': 'ES', 
                'GO': 'GO', 'MA': 'MA', 'MT': 'MT', 'MS': 'MS', 'MG': 'MG', 'PA': 'PA', 'PB': 'PB', 'PR': 'PR', 
                'PE': 'PE', 'PI': 'PI', 'RJ': 'RJ', 'RN': 'RN', 'RS': 'RS', 'RO': 'RO', 'RR': 'RR', 'SC': 'SC', 
                'SP': 'SP', 'SE': 'SE', 'TO': 'TO', 'Outro': 'Outro'
            }
            
            estado_counts["iso_code"] = estado_counts["Estado"].map(state_codes)
            
            fig_map = px.choropleth(
                estado_counts,
                geojson="https://raw.githubusercontent.com/codeforamerica/click-that-hood/master/geojson/brazil-states.geojson",
                locations="iso_code",
                featureidkey="properties.sigla",
                color="Contagem",
                hover_name="Estado",
                color_continuous_scale=colors["choropleth"],
                title="Contratações por Estado"
            )
            fig_map.update_geos(fitbounds="locations", visible=False)
            st.plotly_chart(fig_map, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

st.markdown("---")

# --------------------- 9. TABELA DETALHADA E DOWNLOADS ---------------------
st.subheader("Tabela de Dados e Download")
with st.expander("Clique para visualizar a tabela completa de funcionários"):
    if not df_filtered.empty:
        df_display = df_filtered.drop(columns=["Estado", "Faixa_Etaria", "Custo_Total_Mensal"], errors='ignore')
        st.dataframe(df_display, use_container_width=True)
    else:
        st.warning("⚠️ Nenhum dado encontrado com os filtros selecionados.")

col_dl1, col_dl2 = st.columns(2)
if not df_filtered.empty:
    csv_bytes = df_filtered.to_csv(index=False).encode("utf-8")
    col_dl1.download_button(
        label="📥 Baixar CSV Filtrado",
        data=csv_bytes,
        file_name="funcionarios_filtrado.csv",
        mime="text/csv",
        use_container_width=True
    )
    
from io import BytesIO
import xlsxwriter

excel_buffer = BytesIO()
with pd.ExcelWriter(excel_buffer, engine="xlsxwriter") as writer:
    df_filtered.to_excel(writer, index=False, sheet_name="Dados Filtrados")

col_dl2.download_button(
    label="📥 Baixar Excel Filtrado",
    data=excel_buffer.getvalue(),
    file_name="funcionarios_filtrado.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    use_container_width=True
)
