import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
from database import popular_dados, buscar_lotes_criticos, resumo_estoque, buscar_historico_movimentacoes, get_unidades
from agent import analisar_lotes, chat_com_agente, gerar_relatorio_executivo

st.set_page_config(
    page_title="Agente de Perecibilidade | ERP",
    page_icon="🥗",
    layout="wide",
    initial_sidebar_state="expanded"
)

popular_dados()

# CSS customizado
st.markdown("""
<style>
    .metric-card {
        background: #1e1e2e;
        border-radius: 12px;
        padding: 20px;
        border-left: 4px solid;
    }
    .critico { border-color: #ff4b4b; }
    .atencao { border-color: #ffa500; }
    .monitorar { border-color: #00cc88; }
    .header-badge {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 15px 25px;
        border-radius: 10px;
        margin-bottom: 20px;
    }
</style>
""", unsafe_allow_html=True)

# Header
col_logo, col_title = st.columns([1, 5])
with col_title:
    st.markdown("## 🥗 Agente de Perecibilidade — Controle FEFO")
    st.caption(f"Refeitório Institucional • {datetime.today().strftime('%d/%m/%Y %H:%M')}")

st.divider()

# Sidebar
with st.sidebar:
    st.markdown("### ⚙️ Configurações")
    dias_alerta = st.slider("Janela de alerta (dias)", 3, 30, 7)

    unidades = get_unidades()
    nomes_unidade = ["Todas as Unidades"] + [u["nome"] for u in unidades]
    ids_unidade   = [None] + [u["id"] for u in unidades]
    idx_unidade = st.selectbox("Filtrar por Unidade", range(len(nomes_unidade)),
                               format_func=lambda i: nomes_unidade[i], key="sel_unidade_v2")
    unidade_id = ids_unidade[idx_unidade]
    st.divider()
    st.markdown("### 📌 Navegação")
    pagina = st.radio("", [
        "📊 Dashboard",
        "🔴 Alertas de Vencimento",
        "🤖 Chat com Agente",
        "📋 Relatório Executivo",
        "📦 Movimentações"
    ], label_visibility="collapsed")

# ── DASHBOARD ──────────────────────────────────────────────────────────────────
if pagina == "📊 Dashboard":
    lotes_criticos = buscar_lotes_criticos(dias_alerta, unidade_id)
    resumo = resumo_estoque(unidade_id)

    criticos = [l for l in lotes_criticos if l["dias_restantes"] <= 2]
    atencao  = [l for l in lotes_criticos if 3 <= l["dias_restantes"] <= 5]
    monitorar = [l for l in lotes_criticos if l["dias_restantes"] > 5]

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("🔴 Críticos", len(criticos), help="Vencimento em até 2 dias")
    c2.metric("🟡 Atenção", len(atencao), help="Vencimento em 3-5 dias")
    c3.metric("🟢 Monitorar", len(monitorar), help="Vencimento em 6+ dias")
    c4.metric("📦 Total em alerta", len(lotes_criticos))

    st.divider()

    col_graf1, col_graf2 = st.columns(2)

    with col_graf1:
        st.markdown("#### Distribuição por Categoria")
        if lotes_criticos:
            df_cat = pd.DataFrame(lotes_criticos)
            fig = px.pie(df_cat, names="categoria", values="saldo",
                        color_discrete_sequence=px.colors.qualitative.Set3,
                        hole=0.4)
            fig.update_layout(margin=dict(t=20, b=20), height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("Nenhum lote em alerta.")

    with col_graf2:
        st.markdown("#### Dias Restantes por Produto")
        if lotes_criticos:
            df_dias = pd.DataFrame(lotes_criticos).nsmallest(10, "dias_restantes")
            cores = ["#ff4b4b" if d <= 2 else "#ffa500" if d <= 5 else "#00cc88"
                     for d in df_dias["dias_restantes"]]
            fig2 = go.Figure(go.Bar(
                x=df_dias["produto"],
                y=df_dias["dias_restantes"],
                marker_color=cores,
                text=df_dias["dias_restantes"],
                textposition="outside"
            ))
            fig2.update_layout(margin=dict(t=20, b=20), height=300,
                               yaxis_title="Dias", xaxis_title="")
            st.plotly_chart(fig2, use_container_width=True)

    st.markdown("#### Resumo do Estoque")
    df_resumo = pd.DataFrame(resumo)
    if not df_resumo.empty:
        def colorir(row):
            d = row["Dias p/ Vencer"]
            if d <= 2:
                return ["background-color: #3d0000"] * len(row)
            elif d <= 5:
                return ["background-color: #3d2600"] * len(row)
            return [""] * len(row)
        st.dataframe(df_resumo.style.apply(colorir, axis=1), use_container_width=True, height=350)

# ── ALERTAS ────────────────────────────────────────────────────────────────────
elif pagina == "🔴 Alertas de Vencimento":
    st.markdown(f"### Lotes vencendo nos próximos **{dias_alerta} dias**")

    lotes = buscar_lotes_criticos(dias_alerta, unidade_id)
    if not lotes:
        st.success("✅ Nenhum lote em situação de alerta no período.")
    else:
        for lote in lotes:
            dias = lote["dias_restantes"]
            icon = "🔴" if dias <= 2 else "🟡" if dias <= 5 else "🟢"
            nivel = "CRÍTICO" if dias <= 2 else "ATENÇÃO" if dias <= 5 else "MONITORAR"

            with st.expander(f"{icon} {lote['produto']} — Lote {lote['numero_lote']} | Vence em **{dias} dia(s)**"):
                c1, c2, c3, c4 = st.columns(4)
                c1.metric("Saldo", f"{lote['saldo']} {lote['unidade']}")
                c2.metric("Dias Restantes", dias)
                c3.metric("Consumo Médio/dia", f"{lote['consumo_medio_dia']} {lote['unidade']}")
                c4.metric("Dias para Escoar", lote["dias_para_escoar"])

                st.markdown(f"""
                - **Fornecedor:** {lote['fornecedor']}
                - **Data de Validade:** {lote['data_validade']}
                - **Nível de Risco:** {icon} {nivel}
                """)

                if dias <= 2:
                    st.error("⚡ Ação imediata necessária: priorize o uso deste lote hoje.")
                elif dias <= 5:
                    st.warning("⚠️ Inclua este item prioritariamente no cardápio dos próximos dias.")
                else:
                    st.info("👁️ Monitorar. Verifique a previsão de consumo.")

    if lotes:
        st.divider()
        if st.button("🤖 Analisar com IA", type="primary", use_container_width=True):
            with st.spinner("Agente analisando os lotes críticos..."):
                analise = analisar_lotes(dias_alerta)
            st.markdown("### Análise do Agente")
            st.markdown(analise)

# ── CHAT ───────────────────────────────────────────────────────────────────────
elif pagina == "🤖 Chat com Agente":
    st.markdown("### 🤖 Converse com o Agente de Perecibilidade")
    st.caption("Pergunte sobre lotes, riscos, ações recomendadas ou qualquer dúvida sobre o estoque.")

    if "historico_chat" not in st.session_state:
        st.session_state.historico_chat = []
    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    for msg in st.session_state.mensagens:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    sugestoes = [
        "Quais lotes estão em situação crítica hoje?",
        "O que fazer com o frango que vence amanhã?",
        "Qual produto tem maior risco de perda esta semana?",
        "Me dê um resumo do estoque perecível",
    ]
    st.markdown("**Sugestões:**")
    cols = st.columns(len(sugestoes))
    for i, sug in enumerate(sugestoes):
        if cols[i].button(sug, key=f"sug_{i}", use_container_width=True):
            st.session_state.pergunta_rapida = sug

    pergunta = st.chat_input("Digite sua pergunta...")
    if not pergunta and "pergunta_rapida" in st.session_state:
        pergunta = st.session_state.pop("pergunta_rapida")

    if pergunta:
        st.session_state.mensagens.append({"role": "user", "content": pergunta})
        with st.chat_message("user"):
            st.markdown(pergunta)

        with st.chat_message("assistant"):
            with st.spinner("Analisando estoque..."):
                resposta = chat_com_agente(pergunta, st.session_state.historico_chat)
            st.markdown(resposta)

        st.session_state.mensagens.append({"role": "assistant", "content": resposta})
        st.session_state.historico_chat.append({"role": "user", "parts": [pergunta]})
        st.session_state.historico_chat.append({"role": "model", "parts": [resposta]})
        st.rerun()

# ── RELATÓRIO EXECUTIVO ────────────────────────────────────────────────────────
elif pagina == "📋 Relatório Executivo":
    st.markdown("### 📋 Relatório Executivo — Gestão de Perecíveis")
    st.caption("Gerado por IA para apresentação à diretoria")

    if st.button("🤖 Gerar Relatório com IA", type="primary", use_container_width=True):
        with st.spinner("Gerando relatório executivo..."):
            relatorio = gerar_relatorio_executivo()
        st.session_state.relatorio = relatorio

    if "relatorio" in st.session_state:
        st.divider()
        st.markdown(st.session_state.relatorio)
        st.divider()
        st.download_button(
            "⬇️ Baixar Relatório (.txt)",
            data=st.session_state.relatorio,
            file_name=f"relatorio_perecibilidade_{datetime.today().strftime('%Y%m%d')}.txt",
            mime="text/plain"
        )

# ── MOVIMENTAÇÕES ──────────────────────────────────────────────────────────────
elif pagina == "📦 Movimentações":
    st.markdown("### 📦 Histórico de Movimentações")

    dias_hist = st.selectbox("Período", [7, 15, 30], index=2, format_func=lambda x: f"Últimos {x} dias")
    movs = buscar_historico_movimentacoes(unidade_id=unidade_id, dias=dias_hist)

    if movs:
        df = pd.DataFrame(movs)
        col_f, col_t = st.columns(2)
        filtro_tipo = col_f.multiselect("Tipo", ["ENTRADA", "SAIDA"], default=["ENTRADA", "SAIDA"])
        df_f = df[df["Tipo"].isin(filtro_tipo)]

        st.dataframe(df_f, use_container_width=True, height=450)
        st.caption(f"{len(df_f)} registros encontrados")
    else:
        st.info("Nenhuma movimentação no período.")
