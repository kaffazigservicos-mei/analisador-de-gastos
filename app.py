import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
from ofxparse import OfxParser

# --- 1. CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Analisador de Gastos", layout="centered")

# --- 2. CSS PARA DESIGN HARMONIOSO ---
st.markdown("""
    <style>
    .stApp { background-color: #020617 !important; color: #f8fafc !important; }
    .block-container { max-width: 850px !important; padding-top: 2rem !important; }

    [data-testid="stTable"], .stDataEditor {
        background-color: #0f172a !important;
        border-radius: 12px !important;
        border: 1px solid #1e293b !important;
    }

    .custom-title {
        color: #f8fafc !important;
        font-size: 22px !important;
        font-weight: 700 !important;
        margin: 40px 0 20px 0 !important;
        text-transform: uppercase;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 3. FUNÇÃO DE FORMATAÇÃO BRASILEIRA ---
def formatar_br(valor):
    try:
        v = "{:,.2f}".format(float(valor))
        v = v.replace(",", "X").replace(".", ",").replace("X", ".")
        return f"R$ {v}"
    except:
        return "R$ 0,00"

# --- 4. BANCO DE DADOS ---
conn = sqlite3.connect('financeiro.db', check_same_thread=False)
c = conn.cursor()
c.execute('CREATE TABLE IF NOT EXISTS transacoes (data TEXT, valor REAL, descricao TEXT, tipo TEXT, categoria TEXT)')
conn.commit()

# --- 5. LOGICA DE NOTIFICAÇÃO (SÓ DISPARA APÓS O RERUN) ---
if "sucesso_extrato" in st.session_state:
    st.toast(st.session_state["sucesso_extrato"], icon="✅")
    del st.session_state["sucesso_extrato"]

if "sucesso_salvar" in st.session_state:
    st.toast(st.session_state["sucesso_salvar"], icon="💾")
    del st.session_state["sucesso_salvar"]

# --- 6. SIDEBAR ---
st.sidebar.header("⚙️ Configurações")
p_inv = st.sidebar.number_input("Investimento (%)", 0, 100, 10)
p_manut = st.sidebar.number_input("Manutenção (%)", 0, 100, 70)
p_livre = st.sidebar.number_input("Gastos Livres (%)", 0, 100, 5)
p_doa = st.sidebar.number_input("Doação (%)", 0, 100, 5)

st.title("📊 Gestão Financeira")

# --- 7. UPLOAD E PROCESSAMENTO ---
with st.expander("📁 Importar Extrato", expanded=False):
    file = st.file_uploader("Suba seu arquivo OFX", type=['ofx'])
    if file:
        if st.button("🔄 Processar Novo Arquivo"):
            ofx = OfxParser.parse(file)
            novos = 0
            for acc in ofx.accounts:
                for tx in acc.statement.transactions:
                    c.execute("SELECT * FROM transacoes WHERE data=? AND valor=? AND descricao=?",
                              (str(tx.date), float(tx.amount), tx.memo))
                    if not c.fetchone():
                        c.execute("INSERT INTO transacoes VALUES (?,?,?,?,?)",
                                 (str(tx.date), float(tx.amount), tx.memo,
                                  "Receita" if tx.amount > 0 else "Despesa", "Outros"))
                        novos += 1
            conn.commit()
            # Salva a mensagem para ser exibida após o rerun
            st.session_state["sucesso_extrato"] = f"Processado: {novos} novos lançamentos."
            st.rerun()

# --- 8. LOGICA DE EXIBIÇÃO ---
df_db = pd.read_sql_query("SELECT * FROM transacoes", conn)

if not df_db.empty:
    rec = df_db[df_db["tipo"] == "Receita"]["valor"].sum()
    desp = abs(df_db[df_db["tipo"] == "Despesa"]["valor"].sum())
    saldo = rec - desp

    # --- CARDS (FONTES 20PX) ---
    st.markdown("<br>", unsafe_allow_html=True)
    col1, col2, col3 = st.columns(3)
    card_html = """
    <div style="background-color: #0f172a; border: 1px solid #1e293b; border-top: 4px solid {cor};
                padding: 1.2rem; border-radius: 12px; text-align: center;">
        <p style="color: #f8fafc; font-size: 20px; margin: 0; font-weight: 700;">{label}</p>
        <h2 style="color: {cor}; font-size: 20px; margin: 10px 0 0 0; font-weight: 700;">{valor}</h2>
    </div>
    """
    col1.markdown(card_html.format(label="RECEITAS", cor="#10b981", valor=formatar_br(rec)), unsafe_allow_html=True)
    col2.markdown(card_html.format(label="DESPESAS", cor="#ef4444", valor=formatar_br(desp)), unsafe_allow_html=True)
    col3.markdown(card_html.format(label="SALDO LÍQUIDO", cor="#3b82f6", valor=formatar_br(saldo)), unsafe_allow_html=True)

    # --- TOP 5 ---
    st.markdown('<p class="custom-title">TOP 5</p>', unsafe_allow_html=True)
    df_desp_calc = df_db[df_db["tipo"] == "Despesa"]
    if not df_desp_calc.empty:
        ranking = df_desp_calc.groupby("categoria")["valor"].sum().abs().reset_index()
        ranking = ranking.nlargest(5, 'valor').sort_values(by="valor", ascending=True)
        ranking['rotulo'] = ranking['valor'].apply(formatar_br)

        fig_rank = px.bar(
            ranking, x="valor", y="categoria", orientation='h',
            text="rotulo", color="categoria",
            color_discrete_sequence=px.colors.qualitative.Safe
        )
        fig_rank.update_layout(
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            xaxis=dict(showticklabels=False, title="", showgrid=False),
            yaxis=dict(title="", tickfont=dict(size=14, color="#f8fafc")),
            height=300, showlegend=False,
            margin=dict(l=0, r=120, t=10, b=10), bargap=0.4
        )
        fig_rank.update_traces(textposition='outside', textfont=dict(color="#f8fafc", size=13), width=0.5, cliponaxis=False)
        st.plotly_chart(fig_rank, use_container_width=True, config={'displayModeBar': False})

    # --- DETALHAMENTO ---
    st.markdown('<p class="custom-title">DETALHAMENTO</p>', unsafe_allow_html=True)
    categorias_lista = ["Saúde", "Transporte", "Alimentação", "Moradia", "Lazer", "Pessoal", "Doação", "Salário", "Investimento", "Outros"]
    df_exibicao = df_db.copy()
    df_exibicao["data"] = pd.to_datetime(df_exibicao["data"]).dt.strftime('%d/%m/%Y')

    df_editado = st.data_editor(
        df_exibicao,
        column_config={
            "data": st.column_config.Column("Data", width="small"),
            "categoria": st.column_config.SelectboxColumn("Categoria", options=categorias_lista),
            "valor": st.column_config.NumberColumn("Valor", format="R$ %.2f")
        },
        hide_index=True, use_container_width=True
    )

    if st.button("💾 Salvar Alterações"):
        for i, row in df_editado.iterrows():
            c.execute("UPDATE transacoes SET categoria=? WHERE descricao=? AND data=?",
                      (row['categoria'], row['descricao'], df_db.iloc[i]['data']))
        conn.commit()
        st.session_state["sucesso_salvar"] = "Alterações salvas com sucesso!"
        st.rerun()

    # --- SUGESTÃO ---
    if saldo > 0:
        st.markdown('<p class="custom-title">SUGESTÃO DE DISTRIBUIÇÃO</p>', unsafe_allow_html=True)
        sugestao_df = pd.DataFrame({
            "Destinação": ["Investimento", "Manutenção", "Gastos Livres", "Doação"],
            "Valor": [formatar_br(saldo * (p/100)) for p in [p_inv, p_manut, p_livre, p_doa]]
        })
        st.table(sugestao_df)
else:
    st.info("Aguardando upload de arquivo OFX para iniciar a análise.")
