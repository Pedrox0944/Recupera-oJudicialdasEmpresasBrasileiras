-- Camada de pesquisa piloto; compatível com SQLite e PostgreSQL.
-- Identidades e resultados jurídicos ainda não auditados.
CREATE TABLE IF NOT EXISTS fonte (
    id TEXT PRIMARY KEY,
    titulo TEXT NOT NULL,
    url TEXT NOT NULL,
    escopo TEXT NOT NULL,
    consulta TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS episodio_piloto (
    id TEXT PRIMARY KEY,
    empresa TEXT NOT NULL,
    episodio INTEGER NOT NULL CHECK (episodio > 0),
    cnpj TEXT,
    processo TEXT,
    pedido TEXT,
    deferimento TEXT,
    encerramento TEXT,
    ano_pedido INTEGER,
    mes_pedido INTEGER CHECK (mes_pedido BETWEEN 1 AND 12),
    ano_encerramento INTEGER,
    evento TEXT NOT NULL,
    status_no_corte TEXT NOT NULL CHECK (status_no_corte = 'nao_auditado'),
    elegibilidade TEXT NOT NULL CHECK (elegibilidade = 'pendente_validacao'),
    uso TEXT NOT NULL CHECK (uso = 'piloto_nao_inferencial'),
    observacao TEXT NOT NULL,
    data_corte TEXT NOT NULL,
    UNIQUE (empresa, episodio)
);

CREATE TABLE IF NOT EXISTS episodio_fonte (
    episodio_id TEXT NOT NULL REFERENCES episodio_piloto(id),
    fonte_id TEXT NOT NULL REFERENCES fonte(id),
    PRIMARY KEY (episodio_id, fonte_id)
);

CREATE TABLE IF NOT EXISTS evidencia_campo (
    id TEXT PRIMARY KEY,
    episodio_id TEXT NOT NULL REFERENCES episodio_piloto(id),
    campo TEXT NOT NULL,
    valor TEXT NOT NULL,
    fonte_id TEXT NOT NULL REFERENCES fonte(id),
    localizacao TEXT NOT NULL,
    consulta TEXT NOT NULL,
    precisao TEXT NOT NULL,
    situacao TEXT NOT NULL CHECK (situacao IN ('incorporada', 'alternativa_pendente')),
    observacao TEXT NOT NULL,
    sha256_fonte TEXT NOT NULL
);

CREATE VIEW IF NOT EXISTS vw_cobertura_piloto AS
SELECT COUNT(*) AS episodios_pesquisados,
       COUNT(DISTINCT empresa) AS nomes_de_companhias,
       SUM(CASE WHEN cnpj IS NULL THEN 1 ELSE 0 END) AS episodios_sem_cnpj,
       SUM(CASE WHEN processo IS NULL THEN 1 ELSE 0 END) AS episodios_sem_processo,
       SUM(CASE WHEN pedido IS NULL THEN 1 ELSE 0 END) AS episodios_sem_pedido_completo,
       SUM(CASE WHEN status_no_corte = 'nao_auditado' THEN 1 ELSE 0 END) AS status_pendentes
FROM episodio_piloto;

CREATE VIEW IF NOT EXISTS vw_pendencias_piloto AS
SELECT id, empresa, episodio, cnpj, processo, pedido, ano_pedido,
       encerramento, ano_encerramento, evento, status_no_corte,
       elegibilidade, observacao, data_corte
FROM episodio_piloto;
