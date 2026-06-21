import os
import json
from datetime import datetime
import google.generativeai as genai
from dotenv import load_dotenv
from database import buscar_lotes_criticos, buscar_historico_movimentacoes, resumo_estoque

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

SYSTEM_PROMPT = """Você é o Agente de Perecibilidade do sistema ERP — especialista em controle de validade e FEFO (First Expired, First Out) para refeitórios institucionais como SESC e SENAC.

Seu papel:
- Analisar lotes próximos do vencimento e calcular risco de perda
- Sugerir ações concretas: uso prioritário, promoção, doação, descarte
- Usar linguagem clara e direta, adequada para gestores de almoxarifado
- Sempre indicar o número do lote, produto, quantidade e dias restantes nas suas respostas
- Classificar riscos como: 🔴 CRÍTICO (≤2 dias), 🟡 ATENÇÃO (3-5 dias), 🟢 MONITORAR (6-7 dias)

Formato de resposta: objetivo, com bullets quando listar itens, e sempre fechar com uma recomendação de ação imediata."""

def analisar_lotes(dias_limite: int = 7) -> str:
    lotes = buscar_lotes_criticos(dias_limite)
    if not lotes:
        return "Nenhum lote com vencimento nos próximos dias. Estoque dentro do controle."

    dados_str = json.dumps(lotes, ensure_ascii=False, indent=2, default=str)
    hoje = datetime.today().strftime("%d/%m/%Y")

    prompt = f"""Data de hoje: {hoje}

Lotes com vencimento nos próximos {dias_limite} dias:

{dados_str}

Analise cada lote e:
1. Classifique o nível de risco (CRÍTICO/ATENÇÃO/MONITORAR)
2. Calcule a quantidade estimada que será perdida se nada for feito
3. Sugira a ação mais adequada para cada caso
4. Destaque a ação mais urgente no início da resposta"""

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    response = model.generate_content(prompt)
    return response.text

def chat_com_agente(pergunta: str, historico: list) -> str:
    lotes = buscar_lotes_criticos(30)
    resumo = resumo_estoque()

    contexto = f"""Contexto atual do estoque (data: {datetime.today().strftime('%d/%m/%Y')}):

LOTES COM ATENÇÃO (próximos 30 dias):
{json.dumps(lotes[:10], ensure_ascii=False, indent=2, default=str)}

RESUMO GERAL DO ESTOQUE:
{json.dumps(resumo[:10], ensure_ascii=False, indent=2, default=str)}

Pergunta do operador: {pergunta}"""

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )

    chat = model.start_chat(history=historico)
    response = chat.send_message(contexto)
    return response.text

def gerar_relatorio_executivo() -> str:
    lotes_criticos = buscar_lotes_criticos(7)
    resumo = resumo_estoque()

    hoje = datetime.today().strftime("%d/%m/%Y")

    # Resumo compacto dos lotes críticos
    lotes_resumo = [
        {"produto": l["produto"], "lote": l["numero_lote"], "dias": l["dias_restantes"],
         "saldo": l["saldo"], "unidade": l["unidade_nome"]}
        for l in lotes_criticos[:10]
    ]

    prompt = f"""Data: {hoje}

Relatório executivo CURTO (máx 300 palavras) com:
1. Situação atual (2 linhas)
2. Top alertas críticos (liste até 5)
3. Impacto estimado se sem ação (1 linha)
4. Plano de ação (3 bullets)
5. Valor do agente IA vs manual (1 linha)

LOTES CRÍTICOS: {json.dumps(lotes_resumo, ensure_ascii=False, default=str)}
TOTAL EM ALERTA: {len(lotes_criticos)} lotes
PRODUTOS MONITORADOS: {len(resumo)}"""

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    response = model.generate_content(prompt)
    return response.text
