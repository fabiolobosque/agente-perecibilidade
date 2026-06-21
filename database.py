import sqlite3
import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("pt_BR")
DB_PATH = "estoque.db"

UNIDADES = [
    {"id": 1, "nome": "SESC Unidade Centro"},
    {"id": 2, "nome": "SESC Unidade Norte"},
    {"id": 3, "nome": "SENAC Unidade Sul"},
]

FORNECEDORES = [
    {"id": 1,  "nome": "Distribuidora Norte Alimentos",  "categoria": "Geral"},
    {"id": 2,  "nome": "Frigorífico Sul Ltda",           "categoria": "Proteína"},
    {"id": 3,  "nome": "Laticínios Bela Vista",          "categoria": "Laticínio"},
    {"id": 4,  "nome": "Hortifruti Central",             "categoria": "Hortaliça"},
    {"id": 5,  "nome": "Grãos & Cia",                   "categoria": "Grão"},
    {"id": 6,  "nome": "Padaria Industrial ABC",         "categoria": "Panificação"},
    {"id": 7,  "nome": "Bebidas Express",                "categoria": "Bebida"},
    {"id": 8,  "nome": "Condimentos Brasil",             "categoria": "Condimento"},
    {"id": 9,  "nome": "Limpeza Total Distribuidora",    "categoria": "Limpeza"},
    {"id": 10, "nome": "Descartáveis & Embalagens SA",   "categoria": "Descartável"},
]

PRODUTOS = [
    # Proteínas
    {"id": 1,  "nome": "Frango Resfriado",            "unidade": "KG",  "categoria": "Proteína",    "validade_dias": 5,    "fornecedor_ids": [2],    "consumo_base": 15.0},
    {"id": 2,  "nome": "Carne Bovina Moída",          "unidade": "KG",  "categoria": "Proteína",    "validade_dias": 4,    "fornecedor_ids": [2],    "consumo_base": 10.0},
    {"id": 3,  "nome": "Filé de Peixe Congelado",    "unidade": "KG",  "categoria": "Proteína",    "validade_dias": 30,   "fornecedor_ids": [2, 1], "consumo_base": 8.0},
    {"id": 4,  "nome": "Ovo de Galinha",              "unidade": "DZ",  "categoria": "Proteína",    "validade_dias": 30,   "fornecedor_ids": [1, 4], "consumo_base": 20.0},
    {"id": 5,  "nome": "Linguiça Toscana",            "unidade": "KG",  "categoria": "Proteína",    "validade_dias": 10,   "fornecedor_ids": [2],    "consumo_base": 5.0},
    # Laticínios
    {"id": 6,  "nome": "Leite Integral UHT",          "unidade": "CX",  "categoria": "Laticínio",   "validade_dias": 90,   "fornecedor_ids": [3],    "consumo_base": 30.0},
    {"id": 7,  "nome": "Iogurte Natural",             "unidade": "UN",  "categoria": "Laticínio",   "validade_dias": 20,   "fornecedor_ids": [3],    "consumo_base": 25.0},
    {"id": 8,  "nome": "Queijo Muçarela",             "unidade": "KG",  "categoria": "Laticínio",   "validade_dias": 30,   "fornecedor_ids": [3],    "consumo_base": 4.0},
    {"id": 9,  "nome": "Manteiga sem Sal",            "unidade": "UN",  "categoria": "Laticínio",   "validade_dias": 60,   "fornecedor_ids": [3, 1], "consumo_base": 6.0},
    {"id": 10, "nome": "Creme de Leite",              "unidade": "UN",  "categoria": "Laticínio",   "validade_dias": 120,  "fornecedor_ids": [3],    "consumo_base": 10.0},
    {"id": 11, "nome": "Requeijão Cremoso",           "unidade": "UN",  "categoria": "Laticínio",   "validade_dias": 45,   "fornecedor_ids": [3],    "consumo_base": 8.0},
    # Hortaliças
    {"id": 12, "nome": "Alface Americana",            "unidade": "UN",  "categoria": "Hortaliça",   "validade_dias": 4,    "fornecedor_ids": [4],    "consumo_base": 20.0},
    {"id": 13, "nome": "Tomate",                      "unidade": "KG",  "categoria": "Hortaliça",   "validade_dias": 6,    "fornecedor_ids": [4],    "consumo_base": 12.0},
    {"id": 14, "nome": "Cebola",                      "unidade": "KG",  "categoria": "Hortaliça",   "validade_dias": 14,   "fornecedor_ids": [4, 1], "consumo_base": 8.0},
    {"id": 15, "nome": "Batata Inglesa",              "unidade": "KG",  "categoria": "Hortaliça",   "validade_dias": 20,   "fornecedor_ids": [4],    "consumo_base": 20.0},
    {"id": 16, "nome": "Cenoura",                     "unidade": "KG",  "categoria": "Hortaliça",   "validade_dias": 10,   "fornecedor_ids": [4],    "consumo_base": 7.0},
    {"id": 17, "nome": "Brócolis",                    "unidade": "KG",  "categoria": "Hortaliça",   "validade_dias": 5,    "fornecedor_ids": [4],    "consumo_base": 5.0},
    # Frutas
    {"id": 18, "nome": "Maçã Fuji",                  "unidade": "KG",  "categoria": "Fruta",        "validade_dias": 14,   "fornecedor_ids": [4, 1], "consumo_base": 10.0},
    {"id": 19, "nome": "Banana Prata",                "unidade": "KG",  "categoria": "Fruta",        "validade_dias": 5,    "fornecedor_ids": [4],    "consumo_base": 15.0},
    {"id": 20, "nome": "Laranja Pera",                "unidade": "KG",  "categoria": "Fruta",        "validade_dias": 10,   "fornecedor_ids": [4],    "consumo_base": 12.0},
    {"id": 21, "nome": "Melancia",                    "unidade": "UN",  "categoria": "Fruta",        "validade_dias": 7,    "fornecedor_ids": [4],    "consumo_base": 4.0},
    # Panificação
    {"id": 22, "nome": "Pão de Forma Integral",       "unidade": "PCT", "categoria": "Panificação",  "validade_dias": 7,    "fornecedor_ids": [6],    "consumo_base": 10.0},
    {"id": 23, "nome": "Pão Francês",                 "unidade": "KG",  "categoria": "Panificação",  "validade_dias": 2,    "fornecedor_ids": [6],    "consumo_base": 8.0},
    {"id": 24, "nome": "Bolo de Cenoura Fatiado",    "unidade": "UN",  "categoria": "Panificação",  "validade_dias": 5,    "fornecedor_ids": [6],    "consumo_base": 3.0},
    # Bebidas
    {"id": 25, "nome": "Suco de Laranja Natural",    "unidade": "LT",  "categoria": "Bebida",       "validade_dias": 3,    "fornecedor_ids": [7],    "consumo_base": 20.0},
    {"id": 26, "nome": "Água Mineral 500ml",          "unidade": "CX",  "categoria": "Bebida",       "validade_dias": 365,  "fornecedor_ids": [7, 1], "consumo_base": 15.0},
    {"id": 27, "nome": "Refrigerante 2L",             "unidade": "UN",  "categoria": "Bebida",       "validade_dias": 180,  "fornecedor_ids": [7],    "consumo_base": 10.0},
    {"id": 28, "nome": "Chá Gelado Pronto",           "unidade": "LT",  "categoria": "Bebida",       "validade_dias": 30,   "fornecedor_ids": [7],    "consumo_base": 8.0},
    # Grãos e Secos
    {"id": 29, "nome": "Arroz Tipo 1",                "unidade": "KG",  "categoria": "Grão",         "validade_dias": 365,  "fornecedor_ids": [5],    "consumo_base": 40.0},
    {"id": 30, "nome": "Feijão Carioca",              "unidade": "KG",  "categoria": "Grão",         "validade_dias": 365,  "fornecedor_ids": [5],    "consumo_base": 20.0},
    {"id": 31, "nome": "Macarrão Espaguete",          "unidade": "KG",  "categoria": "Grão",         "validade_dias": 365,  "fornecedor_ids": [5, 1], "consumo_base": 15.0},
    {"id": 32, "nome": "Farinha de Trigo",            "unidade": "KG",  "categoria": "Grão",         "validade_dias": 180,  "fornecedor_ids": [5],    "consumo_base": 10.0},
    {"id": 33, "nome": "Açúcar Cristal",              "unidade": "KG",  "categoria": "Grão",         "validade_dias": 730,  "fornecedor_ids": [5, 1], "consumo_base": 12.0},
    # Condimentos
    {"id": 34, "nome": "Óleo de Soja",                "unidade": "LT",  "categoria": "Condimento",   "validade_dias": 180,  "fornecedor_ids": [8],    "consumo_base": 8.0},
    {"id": 35, "nome": "Azeite Extra Virgem",         "unidade": "LT",  "categoria": "Condimento",   "validade_dias": 365,  "fornecedor_ids": [8],    "consumo_base": 2.0},
    {"id": 36, "nome": "Sal Refinado",                "unidade": "KG",  "categoria": "Condimento",   "validade_dias": 1825, "fornecedor_ids": [8, 5], "consumo_base": 3.0},
    {"id": 37, "nome": "Molho de Tomate",             "unidade": "UN",  "categoria": "Condimento",   "validade_dias": 365,  "fornecedor_ids": [8],    "consumo_base": 10.0},
    {"id": 38, "nome": "Maionese",                    "unidade": "KG",  "categoria": "Condimento",   "validade_dias": 90,   "fornecedor_ids": [8],    "consumo_base": 3.0},
    {"id": 39, "nome": "Ketchup",                     "unidade": "KG",  "categoria": "Condimento",   "validade_dias": 180,  "fornecedor_ids": [8],    "consumo_base": 2.0},
    # Frios
    {"id": 40, "nome": "Presunto Fatiado",            "unidade": "KG",  "categoria": "Frios",        "validade_dias": 15,   "fornecedor_ids": [2, 1], "consumo_base": 4.0},
    {"id": 41, "nome": "Salame Milano",               "unidade": "KG",  "categoria": "Frios",        "validade_dias": 30,   "fornecedor_ids": [2],    "consumo_base": 2.0},
    {"id": 42, "nome": "Peito de Peru Defumado",      "unidade": "KG",  "categoria": "Frios",        "validade_dias": 20,   "fornecedor_ids": [2],    "consumo_base": 2.0},
    # Congelados
    {"id": 43, "nome": "Batata Palito Congelada",     "unidade": "KG",  "categoria": "Congelado",    "validade_dias": 180,  "fornecedor_ids": [1, 2], "consumo_base": 10.0},
    {"id": 44, "nome": "Lasanha Congelada",           "unidade": "UN",  "categoria": "Congelado",    "validade_dias": 90,   "fornecedor_ids": [1],    "consumo_base": 5.0},
    {"id": 45, "nome": "Sorvete 2L",                  "unidade": "UN",  "categoria": "Congelado",    "validade_dias": 180,  "fornecedor_ids": [1],    "consumo_base": 4.0},
    # Limpeza
    {"id": 46, "nome": "Detergente Neutro 5L",        "unidade": "UN",  "categoria": "Limpeza",      "validade_dias": 730,  "fornecedor_ids": [9],    "consumo_base": 2.0},
    {"id": 47, "nome": "Água Sanitária 5L",           "unidade": "UN",  "categoria": "Limpeza",      "validade_dias": 365,  "fornecedor_ids": [9],    "consumo_base": 3.0},
    {"id": 48, "nome": "Desinfetante Lavanda 5L",     "unidade": "UN",  "categoria": "Limpeza",      "validade_dias": 730,  "fornecedor_ids": [9],    "consumo_base": 2.0},
    {"id": 49, "nome": "Sabão em Pó 5KG",             "unidade": "UN",  "categoria": "Limpeza",      "validade_dias": 730,  "fornecedor_ids": [9],    "consumo_base": 1.0},
    # Descartáveis
    {"id": 50, "nome": "Copo Descartável 200ml c/100","unidade": "PCT", "categoria": "Descartável",  "validade_dias": 1825, "fornecedor_ids": [10],   "consumo_base": 5.0},
    {"id": 51, "nome": "Luva Descartável M c/100",    "unidade": "CX",  "categoria": "Descartável",  "validade_dias": 1825, "fornecedor_ids": [10],   "consumo_base": 3.0},
    {"id": 52, "nome": "Saco para Lixo 100L c/10",   "unidade": "PCT", "categoria": "Descartável",  "validade_dias": 1825, "fornecedor_ids": [10],   "consumo_base": 4.0},
    {"id": 53, "nome": "Papel Toalha c/2",            "unidade": "PCT", "categoria": "Descartável",  "validade_dias": 1825, "fornecedor_ids": [10],   "consumo_base": 6.0},
]

FATOR_DIA_SEMANA = {0: 1.2, 1: 1.1, 2: 1.0, 3: 1.1, 4: 1.3, 5: 0.5, 6: 0.2}
FATOR_MES = {1: 0.8, 2: 0.9, 3: 1.0, 4: 1.0, 5: 1.1, 6: 1.0,
             7: 1.2, 8: 1.1, 9: 1.0, 10: 1.0, 11: 1.3, 12: 1.4}

def get_conn():
    return sqlite3.connect(DB_PATH)

def criar_banco():
    conn = get_conn()
    c = conn.cursor()
    c.executescript("""
        CREATE TABLE IF NOT EXISTS unidades (
            id    INTEGER PRIMARY KEY,
            nome  TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS fornecedores (
            id        INTEGER PRIMARY KEY,
            nome      TEXT NOT NULL,
            categoria TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS produtos (
            id            INTEGER PRIMARY KEY,
            nome          TEXT NOT NULL,
            unidade       TEXT NOT NULL,
            categoria     TEXT NOT NULL,
            validade_dias INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS lotes (
            id            INTEGER PRIMARY KEY AUTOINCREMENT,
            produto_id    INTEGER NOT NULL,
            unidade_id    INTEGER NOT NULL,
            numero_lote   TEXT NOT NULL,
            quantidade    REAL NOT NULL,
            data_entrada  DATE NOT NULL,
            data_validade DATE NOT NULL,
            fornecedor_id INTEGER NOT NULL,
            FOREIGN KEY (produto_id)    REFERENCES produtos(id),
            FOREIGN KEY (unidade_id)    REFERENCES unidades(id),
            FOREIGN KEY (fornecedor_id) REFERENCES fornecedores(id)
        );
        CREATE TABLE IF NOT EXISTS movimentacoes (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            lote_id     INTEGER NOT NULL,
            produto_id  INTEGER NOT NULL,
            unidade_id  INTEGER NOT NULL,
            tipo        TEXT NOT NULL CHECK(tipo IN ('ENTRADA','SAIDA','TRANSFERENCIA')),
            quantidade  REAL NOT NULL,
            data_mov    DATE NOT NULL,
            responsavel TEXT NOT NULL,
            observacao  TEXT,
            FOREIGN KEY (lote_id)    REFERENCES lotes(id),
            FOREIGN KEY (unidade_id) REFERENCES unidades(id)
        );
    """)
    conn.commit()
    return conn

def fator_consumo(data: datetime) -> float:
    fw = FATOR_DIA_SEMANA.get(data.weekday(), 1.0)
    fm = FATOR_MES.get(data.month, 1.0)
    return fw * fm

def popular_dados():
    conn = criar_banco()
    c = conn.cursor()

    c.execute("SELECT COUNT(*) FROM produtos")
    if c.fetchone()[0] > 0:
        conn.close()
        return

    for u in UNIDADES:
        c.execute("INSERT INTO unidades VALUES (?,?)", (u["id"], u["nome"]))
    for f in FORNECEDORES:
        c.execute("INSERT INTO fornecedores VALUES (?,?,?)", (f["id"], f["nome"], f["categoria"]))
    for p in PRODUTOS:
        c.execute("INSERT INTO produtos VALUES (?,?,?,?,?)",
                  (p["id"], p["nome"], p["unidade"], p["categoria"], p["validade_dias"]))

    hoje = datetime.today()
    historico_dias = 90
    lote_seq = 1

    for unidade in UNIDADES:
        for prod in PRODUTOS:
            num_lotes = random.randint(3, 7)
            for i in range(num_lotes):
                fornecedor_id = random.choice(prod["fornecedor_ids"])
                dias_atras = random.randint(0, historico_dias)
                data_entrada = hoje - timedelta(days=dias_atras)

                cenario = random.choices(
                    ["normal", "critico", "parado", "acelerado", "vencido"],
                    weights=[50, 15, 10, 15, 10]
                )[0]

                if cenario == "critico":
                    dias_val = random.randint(1, 4)
                elif cenario == "vencido":
                    dias_val = random.randint(-3, 0)
                elif cenario == "parado":
                    dias_val = random.randint(min(5, prod["validade_dias"]), prod["validade_dias"])
                elif cenario == "acelerado":
                    dias_val = random.randint(3, 8)
                else:
                    dias_val = random.randint(
                        max(1, prod["validade_dias"] // 3),
                        prod["validade_dias"]
                    )

                data_validade = hoje + timedelta(days=dias_val)
                qtd_entrada = round(random.uniform(
                    prod["consumo_base"] * 2,
                    prod["consumo_base"] * 10
                ), 2)
                numero_lote = f"LT{unidade['id']:01d}{prod['id']:03d}{lote_seq:05d}"

                c.execute("""
                    INSERT INTO lotes VALUES (NULL,?,?,?,?,?,?,?)
                """, (prod["id"], unidade["id"], numero_lote, qtd_entrada,
                      data_entrada.date(), data_validade.date(), fornecedor_id))
                lote_id = c.lastrowid

                c.execute("""
                    INSERT INTO movimentacoes VALUES (NULL,?,?,?,?,?,?,?,?)
                """, (lote_id, prod["id"], unidade["id"], "ENTRADA", qtd_entrada,
                      data_entrada.date(), fake.name(), "Recebimento de mercadoria"))

                saldo = qtd_entrada
                consumo_base_dia = prod["consumo_base"] / len(UNIDADES)
                if cenario == "parado":
                    consumo_base_dia *= 0.05
                elif cenario == "acelerado":
                    consumo_base_dia *= 2.5

                for d in range(dias_atras):
                    if saldo <= 0.5:
                        break
                    data_saida = data_entrada + timedelta(days=d + 1)
                    if data_saida.date() > hoje.date():
                        break
                    fator = fator_consumo(data_saida)
                    consumo = round(
                        min(consumo_base_dia * fator * random.uniform(0.7, 1.3), saldo), 2
                    )
                    if consumo <= 0:
                        continue
                    c.execute("""
                        INSERT INTO movimentacoes VALUES (NULL,?,?,?,?,?,?,?,?)
                    """, (lote_id, prod["id"], unidade["id"], "SAIDA", consumo,
                          data_saida.date(), fake.name(), "Consumo refeitório"))
                    saldo -= consumo

                if random.random() < 0.10 and saldo > 5:
                    outras = [u for u in UNIDADES if u["id"] != unidade["id"]]
                    destino = random.choice(outras)
                    qtd_transf = round(saldo * random.uniform(0.2, 0.4), 2)
                    data_transf = data_entrada + timedelta(days=random.randint(1, max(1, dias_atras)))
                    if data_transf.date() <= hoje.date():
                        c.execute("""
                            INSERT INTO movimentacoes VALUES (NULL,?,?,?,?,?,?,?,?)
                        """, (lote_id, prod["id"], unidade["id"], "TRANSFERENCIA", qtd_transf,
                              data_transf.date(), fake.name(),
                              f"Transferência para {destino['nome']}"))

                lote_seq += 1

    conn.commit()
    conn.close()
    print("Banco robusto populado com sucesso.")

def saldo_lote(lote_id: int, conn) -> float:
    c = conn.cursor()
    c.execute("""
        SELECT COALESCE(SUM(CASE WHEN tipo='ENTRADA' THEN quantidade
                               WHEN tipo IN ('SAIDA','TRANSFERENCIA') THEN -quantidade
                               ELSE 0 END), 0)
        FROM movimentacoes WHERE lote_id = ?
    """, (lote_id,))
    return c.fetchone()[0]

def buscar_lotes_criticos(dias_limite: int = 7, unidade_id: int = None):
    conn = get_conn()
    c = conn.cursor()
    hoje = datetime.today().date()
    limite = hoje + timedelta(days=dias_limite)

    query = """
        SELECT l.id, l.numero_lote, p.nome, p.categoria, p.unidade,
               l.data_validade, f.nome, l.data_entrada, u.nome, l.unidade_id
        FROM lotes l
        JOIN produtos     p ON p.id = l.produto_id
        JOIN fornecedores f ON f.id = l.fornecedor_id
        JOIN unidades     u ON u.id = l.unidade_id
        WHERE l.data_validade <= ?
    """
    params = [limite]
    if unidade_id:
        query += " AND l.unidade_id = ?"
        params.append(unidade_id)
    query += " ORDER BY l.data_validade ASC"

    c.execute(query, params)
    resultado = []
    for row in c.fetchall():
        lote_id, numero_lote, nome, categoria, unidade, data_val, fornecedor, data_entrada, unidade_nome, uid = row
        saldo = saldo_lote(lote_id, conn)
        if saldo <= 0:
            continue
        dias_restantes = (datetime.strptime(data_val, "%Y-%m-%d").date() - hoje).days
        c.execute("""
            SELECT COALESCE(AVG(quantidade), 0) FROM movimentacoes
            WHERE lote_id = ? AND tipo = 'SAIDA' AND data_mov >= ?
        """, (lote_id, (hoje - timedelta(days=7)).isoformat()))
        consumo_medio = c.fetchone()[0]
        dias_para_escoar = round(saldo / consumo_medio, 1) if consumo_medio > 0 else 9999
        percentual_risco = min(100, round((dias_para_escoar / max(dias_restantes, 1)) * 100)) if dias_restantes > 0 else 100
        resultado.append({
            "lote_id": lote_id,
            "numero_lote": numero_lote,
            "produto": nome,
            "categoria": categoria,
            "unidade_medida": unidade,
            "data_validade": data_val,
            "dias_restantes": dias_restantes,
            "saldo": round(saldo, 2),
            "consumo_medio_dia": round(consumo_medio, 2),
            "dias_para_escoar": dias_para_escoar,
            "fornecedor": fornecedor,
            "risco_perda_pct": percentual_risco,
            "unidade_nome": unidade_nome,
        })
    conn.close()
    return resultado

def buscar_historico_movimentacoes(unidade_id: int = None, dias: int = 30):
    conn = get_conn()
    c = conn.cursor()
    desde = (datetime.today() - timedelta(days=dias)).date()
    query = """
        SELECT m.data_mov, u.nome, p.nome, m.tipo, m.quantidade,
               p.unidade, m.responsavel, l.numero_lote, l.data_validade
        FROM movimentacoes m
        JOIN lotes    l ON l.id = m.lote_id
        JOIN produtos p ON p.id = m.produto_id
        JOIN unidades u ON u.id = m.unidade_id
        WHERE m.data_mov >= ?
    """
    params = [desde]
    if unidade_id:
        query += " AND m.unidade_id = ?"
        params.append(unidade_id)
    query += " ORDER BY m.data_mov DESC LIMIT 200"
    c.execute(query, params)
    cols = ["Data", "Unidade", "Produto", "Tipo", "Quantidade", "Un.", "Responsável", "Lote", "Validade"]
    rows = [dict(zip(cols, r)) for r in c.fetchall()]
    conn.close()
    return rows

def resumo_estoque(unidade_id: int = None):
    conn = get_conn()
    c = conn.cursor()
    hoje = datetime.today().date()
    query = """
        SELECT p.nome, p.categoria, p.unidade, u.nome,
               COUNT(DISTINCT l.id), MIN(l.data_validade)
        FROM produtos p
        JOIN lotes    l ON l.produto_id = p.id
        JOIN unidades u ON u.id = l.unidade_id
    """
    params = []
    if unidade_id:
        query += " WHERE l.unidade_id = ?"
        params.append(unidade_id)
    query += " GROUP BY p.id, u.id ORDER BY MIN(l.data_validade) ASC"
    c.execute(query, params)
    resultado = []
    for row in c.fetchall():
        nome, cat, unidade, unidade_nome, num_lotes, prox_val = row
        dias = (datetime.strptime(prox_val, "%Y-%m-%d").date() - hoje).days
        resultado.append({
            "Produto": nome, "Categoria": cat, "Unidade": unidade,
            "Filial": unidade_nome, "Lotes Ativos": num_lotes,
            "Próxima Validade": prox_val, "Dias p/ Vencer": dias,
        })
    conn.close()
    return resultado

def get_unidades():
    conn = get_conn()
    c = conn.cursor()
    c.execute("SELECT id, nome FROM unidades")
    rows = [{"id": r[0], "nome": r[1]} for r in c.fetchall()]
    conn.close()
    return rows

if __name__ == "__main__":
    popular_dados()
