import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from ofxparse import OfxParser
import io

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Analisador de Gastos", layout="wide")

# --- FUNÇÃO DE FORMATAÇÃO PADRÃO BRASIL (COM PONTO NO MILHAR) ---
def formatar_br(valor):
    try:
        v = "{:,.2f}".format(float(valor))
        v = v.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {v}"
    except:
        return "R$ 0,00"

# --- BANCO DE DADOS (SQLite) ---
conn = sqlite3.connect('financeiro.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS transacoes (data TEXT, valor REAL, descricao TEXT, tipo TEXT, categoria TEXT)')
conn.commit()

# --- SIDEBAR: HIERARQUIA COM DIGITAÇÃO (ITEM 5) ---
st.sidebar.header("Configurar Hierarquia (%)")
p_inv = st.sidebar.number_input("Investimento", min_value=0, max_value=100, value=10, step=1)
p_manut = st.sidebar.number_input("Manutenção", min_value=0, max_value=100, value=70, step=1)
p_livre = st.sidebar.number_input("Gastos Livres", min_value=0, max_value=100, value=5, step=1)
p_doa = st.sidebar.number_input("Doação", min_value=0, max_value=100, value=5, step=1)

total_p = p_inv + p_manut + p_livre + p_doa
if total_p != 100:
    st.sidebar.warning(f"A soma das porcentagens é {total_p}%. O ideal é 100%.")

st.title("📊 Analisador de Gastos Profissional")

# --- UPLOAD DO ARQUIVO ---
file = st.file_uploader("Suba seu arquivo OFX", type=['ofx'])

if file:
    ofx = OfxParser.parse(file)
    for acc in ofx.accounts:
        for tx in acc.statement.transactions:
            c.execute("SELECT * FROM transacoes WHERE data=? AND valor=? AND descricao=?",
                      (str(tx.date), float(tx.amount), tx.memo))
            if not c.fetchone():
                c.execute("INSERT INTO transacoes VALUES (?,?,?,?,?)",
                         (str(tx.date), float(tx.amount), tx.memo,
                          "Receita" if tx.amount > 0 else "Despesa", "Outros"))
    conn.commit()

# --- TABELA DE CATEGORIZAÇÃO (ITEM 3) ---
df_db = pd.read_sql_query("SELECT * FROM transacoes", conn)

if not df_db.empty:
    st.subheader("📝 Categorização de Lançamentos")
    # Incluída a categoria "Pessoal" conforme solicitado
    categorias_lista = ["Saúde", "Transporte", "Alimentação", "Moradia", "Lazer", "Pessoal", "Doação", "Salário", "Investimento", "Outros"]

    # Prepara a tabela de exibição (Data DD/MM/AA e Valor formatado)
    df_exibicao = df_db.copy()
    df_exibicao["data"] = pd.to_datetime(df_exibicao["data"]).dt.strftime('%d/%m/%y')
    df_exibicao["valor"] = df_exibicao["valor"].apply(formatar_br)

    df_editado = st.data_editor(
        df_exibicao,
        column_config={
            "data": st.column_config.Column("Data"),
            "categoria": st.column_config.SelectboxColumn("Categoria", options=categorias_lista),
            "valor": st.column_config.Column("Valor (R$)", disabled=True)
        },
        hide_index=True
    )

    if st.button("Salvar Alterações e Gerar Análise"):
        for i, row in df_editado.iterrows():
            c.execute("UPDATE transacoes SET categoria=? WHERE descricao=? AND data=?",
                      (row['categoria'], row['descricao'], df_db.iloc[i]['data']))
        conn.commit()
        st.success("Dados salvos e análise atualizada!")

        # --- CÁLCULOS ---
        rec = df_db[df_db["tipo"] == "Receita"]["valor"].sum()
        desp = abs(df_db[df_db["tipo"] == "Despesa"]["valor"].sum())
        saldo = rec - desp

        # --- MÉTRICAS COM FONTE AUMENTADA (HARMONIA VISUAL) ---
        st.subheader("💰 Resumo Financeiro")
        col1, col2, col3 = st.columns(3)
        estilo = "<p style='font-size:22px; font-weight:bold; margin-bottom:-10px;'>{label}</p><p style='font-size:34px; color:#1f77b4; font-weight:bold;'>{valor}</p>"

        col1.markdown(estilo.format(label="Total Receitas", valor=formatar_br(rec)), unsafe_allow_html=True)
        col2.markdown(estilo.format(label="Total Despesas", valor=formatar_br(desp)), unsafe_allow_html=True)
        col3.markdown(estilo.format(label="Saldo Líquido", valor=formatar_br(saldo)), unsafe_allow_html=True)

        # --- RANKING DE DESPESAS (ITEM 4 - TOP 5) ---
        st.subheader("🔝 Top 5 Categorias de Gastos")
        df_desp_calc = df_db[df_db["tipo"] == "Despesa"]
        if not df_desp_calc.empty:
            ranking = df_desp_calc.groupby("categoria")["valor"].sum().abs().reset_index()
            ranking = ranking.nlargest(5, 'valor').sort_values(by="valor", ascending=True)

            fig_rank = px.bar(ranking, x="valor", y="categoria", orientation='h', color="categoria")

            # Limpeza total dos eixos e títulos
            fig_rank.update_layout(
                separators=',.',
                showlegend=False,
                font=dict(size=16), # Aumentei um pouco a fonte das categorias
                xaxis=dict(showticklabels=False, title="", showgrid=False), # Esconde números e título de baixo
                yaxis=dict(title=""), # Esconde título lateral
                margin=dict(l=20, r=20, t=20, b=20), # Ajusta margens para ganhar espaço
                plot_bgcolor="rgba(0,0,0,0)", # Fundo transparente
            )

            fig_rank.update_traces(
                texttemplate='<b>R$ %{x:,.2f}</b>', # Valor em negrito
                textposition='outside',
                cliponaxis=False # Garante que o texto não seja cortado
            )
            st.plotly_chart(fig_rank, use_container_width=True)

        # --- HIERARQUIA DE SALDO (ITEM 5) ---
        if saldo > 0:
            st.subheader("💡 Sugestão de Distribuição do Saldo")
            sug_dados = {
                "Destinação de Valores": ["Investimento", "Manutenção", "Gastos Livres", "Doação"],
                "Valor Recomendado": [
                    formatar_br(saldo * (p_inv/100)),
                    formatar_br(saldo * (p_manut/100)),
                    formatar_br(saldo * (p_livre/100)),
                    formatar_br(saldo * (p_doa/100))
                ]
            }
            st.table(pd.DataFrame(sug_dados))
else:
    st.info("Aguardando upload de arquivo OFX para iniciar a análise.")
