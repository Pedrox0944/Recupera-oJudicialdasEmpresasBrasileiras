"""Validação e exportação do piloto, sem inferência sobre desfechos."""

import csv
import hashlib
import io
import json
import re
import sqlite3
from datetime import date
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
COLUMNS = (
    'id', 'empresa', 'episodio', 'cnpj', 'processo', 'pedido', 'deferimento',
    'encerramento', 'ano_pedido', 'mes_pedido', 'ano_encerramento', 'evento',
    'status_no_corte', 'elegibilidade', 'uso', 'observacao', 'data_corte',
)
WARNING = 'Pesquisa exploratória — sem taxa nacional'


def load(data_dir):
    data_dir = Path(data_dir)
    return (
        json.loads((data_dir / 'piloto.json').read_text(encoding='utf-8')),
        json.loads((data_dir / 'fontes.json').read_text(encoding='utf-8')),
    )


def valid_cnpj(value):
    """Valida os CNPJs numéricos históricos deste piloto."""
    if not isinstance(value, str) or not re.fullmatch(r'[0-9]{14}', value):
        return False
    if len(set(value)) == 1:
        return False
    digits = [int(c) for c in value]
    for size, weights in ((12, (5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2)),
                          (13, (6, 5, 4, 3, 2, 9, 8, 7, 6, 5, 4, 3, 2))):
        remainder = sum(d * w for d, w in zip(digits[:size], weights)) % 11
        if digits[size] != (0 if remainder < 2 else 11 - remainder):
            return False
    return True


def validate(pilot, sources):
    """Erros impedem importação. Lacunas documentais ficam no relatório."""
    errors = []
    if not isinstance(pilot, dict) or not isinstance(sources, list):
        return ['A base deve ser um objeto e o catálogo de fontes uma lista.']

    def parse_date(value, label, required=False):
        if value is None and not required:
            return None
        try:
            if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
                raise ValueError
            return date.fromisoformat(value)
        except (TypeError, ValueError):
            errors.append(f'{label}: data ISO inválida ({value!r}).')
            return None

    cutoff = parse_date(pilot.get('data_corte_proposta'), 'data_corte_proposta', True)
    parse_date(pilot.get('consulta'), 'consulta', True)
    if not isinstance(pilot.get('cobertura'), str) or not pilot['cobertura'].strip():
        errors.append('Cobertura da pesquisa ausente.')
    source_ids = set()
    for source in sources:
        if not isinstance(source, dict):
            errors.append('Fonte deve ser um objeto.')
            continue
        sid = source.get('id')
        if not isinstance(sid, str) or not sid or sid in source_ids:
            errors.append(f'Fonte com ID inválido ou duplicado: {sid!r}.')
            continue
        source_ids.add(sid)
        for field in ('titulo', 'url', 'escopo'):
            if not isinstance(source.get(field), str) or not source[field].strip():
                errors.append(f'{sid}: {field} ausente.')
        try:
            if not isinstance(source.get('url'), str):
                raise ValueError
            url = urlsplit(source['url'])
            if url.scheme not in ('https', 'http') or not url.netloc:
                raise ValueError
        except (ValueError, TypeError):
            errors.append(f'{sid}: URL inválida.')
        parse_date(source.get('consulta'), f'{sid}.consulta', True)

    records = pilot.get('registros')
    if not isinstance(records, list) or not records:
        return errors + ['registros deve ser uma lista não vazia.']
    seen, episodes, processes = set(), set(), set()
    for index, row in enumerate(records):
        if not isinstance(row, dict):
            errors.append(f'Registro {index}: deve ser um objeto.')
            continue
        rid = row.get('id')
        if not isinstance(rid, str) or not rid or rid in seen:
            errors.append(f'ID de episódio inválido ou duplicado: {rid!r}.')
            continue
        seen.add(rid)
        for field in ('empresa', 'evento', 'observacao'):
            if not isinstance(row.get(field), str) or not row[field].strip():
                errors.append(f'{rid}: {field} ausente.')
        company, episode = row.get('empresa'), row.get('episodio')
        if type(episode) is not int or episode < 1:
            errors.append(f'{rid}: episodio deve ser inteiro positivo.')
        elif isinstance(company, str):
            key = (company, episode)
            if key in episodes:
                errors.append(f'{rid}: companhia/episódio duplicado.')
            episodes.add(key)
        for field, expected in (
            ('uso', 'piloto_nao_inferencial'),
            ('status_no_corte', 'nao_auditado'),
            ('elegibilidade', 'pendente_validacao'),
        ):
            if row.get(field) != expected:
                errors.append(f'{rid}: {field} deve permanecer {expected} nesta camada piloto.')
        if row.get('cnpj') is not None and not valid_cnpj(row['cnpj']):
            errors.append(f'{rid}: CNPJ numérico inválido; manter 14 dígitos como texto.')
        process = row.get('processo')
        if process is not None:
            if not isinstance(process, str) or not re.fullmatch(r'\d{7}-\d{2}\.\d{4}\.\d\.\d{2}\.\d{4}', process):
                errors.append(f'{rid}: formato do número CNJ inválido.')
            elif isinstance(company, str):
                key = (company, process)
                if key in processes:
                    errors.append(f'{rid}: mesma companhia/processo duplicado.')
                processes.add(key)
        refs = row.get('fontes')
        if not isinstance(refs, list) or not refs:
            errors.append(f'{rid}: fonte obrigatória.')
        else:
            valid_refs = [r for r in refs if isinstance(r, str)]
            if len(valid_refs) != len(refs) or len(set(valid_refs)) != len(refs):
                errors.append(f'{rid}: referências inválidas ou repetidas.')
            for ref in valid_refs:
                if ref not in source_ids:
                    errors.append(f'{rid}: fonte inexistente {ref}.')
        dates = {}
        for field in ('pedido', 'deferimento', 'encerramento'):
            dates[field] = parse_date(row.get(field), f'{rid}.{field}')
            if dates[field] and cutoff and dates[field] > cutoff:
                errors.append(f'{rid}.{field}: evento posterior ao corte.')
            if dates[field] and dates[field].year < 2005:
                errors.append(f'{rid}.{field}: evento anterior à janela do projeto.')
        for field in ('pedido', 'encerramento'):
            year = row.get('ano_' + field)
            if year is not None:
                if type(year) is not int or not 2005 <= year <= (cutoff.year if cutoff else 9999):
                    errors.append(f'{rid}: ano_{field} fora da janela.')
                elif dates[field] and dates[field].year != year:
                    errors.append(f'{rid}: ano_{field} diverge da data completa.')
        month = row.get('mes_pedido')
        if month is not None:
            if type(month) is not int or not 1 <= month <= 12:
                errors.append(f'{rid}: mes_pedido inválido.')
            elif row.get('ano_pedido') is None or (dates['pedido'] and dates['pedido'].month != month):
                errors.append(f'{rid}: mes_pedido inconsistente com ano/data.')
            elif cutoff and row.get('ano_pedido') == cutoff.year and month > cutoff.month:
                errors.append(f'{rid}: mês do pedido posterior ao corte.')
        ordered = [dates[f] for f in ('pedido', 'deferimento', 'encerramento') if dates[f]]
        if ordered != sorted(ordered):
            errors.append(f'{rid}: sequência de datas inconsistente.')
        start, end = row.get('ano_pedido'), row.get('ano_encerramento')
        if type(start) is int and type(end) is int and end < start:
            errors.append(f'{rid}: ano de encerramento anterior ao pedido.')
    return errors


def quality(pilot):
    result = []
    for row in pilot['registros']:
        missing = []
        for field, label in (
            ('cnpj', 'CNPJ não normalizado'), ('processo', 'processo não identificado'),
            ('pedido', 'pedido sem data completa'),
            ('encerramento', 'encerramento sem data completa; desfecho não presumido'),
        ):
            if row.get(field) is None:
                missing.append(label)
        missing.extend(('listagem histórica pendente', 'status no corte não auditado',
                        'evidência por campo pendente'))
        result.append({'id': row['id'], 'empresa': row['empresa'],
                       'pendencias': '; '.join(missing)})
    return result


def sql_literal(value):
    if value is None:
        return 'NULL'
    if type(value) is int:
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


def normalized_rows(pilot):
    return [dict(row, data_corte=pilot['data_corte_proposta']) for row in pilot['registros']]


def write_csv(path, columns, rows):
    with path.open('w', encoding='utf-8', newline='') as handle:
        writer = csv.DictWriter(handle, fieldnames=columns, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rows)


def build(data_dir, output):
    """Reconstrói artefatos derivados; jamais altera dados de origem."""
    pilot, sources = load(data_dir)
    errors = validate(pilot, sources)
    if errors:
        raise ValueError('\n'.join(errors))
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    rows = normalized_rows(pilot)
    schema = (ROOT / 'sql/piloto.sql').read_text(encoding='utf-8')
    # O banco é um artefato inteiramente derivado, reconstruído em memória.
    with sqlite3.connect(':memory:') as database:
        database.execute('PRAGMA foreign_keys = ON')
        database.executescript(schema)
        for source in sources:
            database.execute('INSERT INTO fonte VALUES (?, ?, ?, ?, ?)',
                             tuple(source[k] for k in ('id', 'titulo', 'url', 'escopo', 'consulta')))
        for row in rows:
            placeholders = ', '.join('?' for _ in COLUMNS)
            database.execute(f"INSERT INTO episodio_piloto ({', '.join(COLUMNS)}) VALUES ({placeholders})",
                             tuple(row.get(k) for k in COLUMNS))
            database.executemany('INSERT INTO episodio_fonte VALUES (?, ?)',
                                 [(row['id'], ref) for ref in row['fontes']])
        database.commit()
        with sqlite3.connect(output / 'piloto.sqlite3') as destination:
            database.backup(destination)
        database.row_factory = sqlite3.Row
        coverage = dict(database.execute('SELECT * FROM vw_cobertura_piloto').fetchone())

    write_csv(output / 'episodios.csv', COLUMNS, rows)
    write_csv(output / 'fontes.csv', ('id', 'titulo', 'url', 'escopo', 'consulta'), sources)
    pending = quality(pilot)
    write_csv(output / 'pendencias.csv', ('id', 'empresa', 'pendencias'), pending)
    links = [{'episodio_id': r['id'], 'fonte_id': ref} for r in rows for ref in r['fontes']]
    write_csv(output / 'episodio_fonte.csv', ('episodio_id', 'fonte_id'), links)

    # PostgreSQL exige CREATE VIEW sem IF NOT EXISTS; esquema isolado evita colisões.
    statements = ['BEGIN;', 'SET standard_conforming_strings = on;',
                  'CREATE SCHEMA IF NOT EXISTS pesquisa_piloto;',
                  'SET LOCAL search_path TO pesquisa_piloto;',
                  schema.replace('CREATE VIEW IF NOT EXISTS', 'CREATE OR REPLACE VIEW'),
                  'DELETE FROM episodio_fonte;', 'DELETE FROM episodio_piloto;', 'DELETE FROM fonte;']
    for table, columns, records in (
        ('fonte', ('id', 'titulo', 'url', 'escopo', 'consulta'), sources),
        ('episodio_piloto', COLUMNS, rows),
        ('episodio_fonte', ('episodio_id', 'fonte_id'), links),
    ):
        for row in records:
            values = ', '.join(sql_literal(row.get(k)) for k in columns)
            statements.append(f"INSERT INTO {table} ({', '.join(columns)}) VALUES ({values});")
    statements.append('COMMIT;')
    (output / 'postgresql.sql').write_text('\n'.join(statements) + '\n', encoding='utf-8')

    manifest = {
        'versao': '0.2.0', 'aviso': WARNING, 'data_corte': pilot['data_corte_proposta'],
        'cobertura': pilot['cobertura'], 'contagens': coverage,
        'indicadores_juridicos': None,
        'bloqueio': 'Elegibilidade, identidade e desfechos ainda não auditados.',
        'sha256_entradas': {
            name: hashlib.sha256((Path(data_dir) / name).read_bytes()).hexdigest()
            for name in ('piloto.json', 'fontes.json')
        },
    }
    (output / 'resumo.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# Relatório de cobertura — Recuperação em Foco', '', WARNING, '',
             f"Corte proposto: {pilot['data_corte_proposta']}. Versão da ferramenta: 0.2.0.",
             f"Cobertura: {pilot['cobertura']}.", '',
             f"- Nomes de companhias pesquisadas: {coverage['nomes_de_companhias']} (identidade cadastral pendente).",
             f"- Episódios candidatos: {coverage['episodios_pesquisados']}.",
             f"- Episódios sem CNPJ normalizado: {coverage['episodios_sem_cnpj']}.",
             f"- Episódios sem processo identificado: {coverage['episodios_sem_processo']}.",
             f"- Episódios sem data completa do pedido: {coverage['episodios_sem_pedido_completo']}.",
             f"- Status no corte pendentes de auditoria: {coverage['status_pendentes']}.", '',
             'Taxa de sucesso, duração verificada e recorrência não calculadas: faltam auditoria e denominadores válidos.', '',
             '## Pendências por episódio', '']
    for item in pending:
        lines.extend([f"### {item['id']} — {item['empresa']}", '', item['pendencias'] + '.', ''])
    lines.extend(['## Rastreabilidade', '',
                  'Os vínculos com fontes são herdados do piloto; não constituem revisão dos documentos originais.',
                  'Consulta e corte são metadados de origem; executar a ferramenta não atualiza a auditoria.',
                  'Os hashes das entradas estão em resumo.json. Nulos permanecem desconhecidos.', ''])
    (output / 'relatorio.md').write_text('\n'.join(lines), encoding='utf-8')
    return manifest


def cvm_candidates(csv_path, pilot, output):
    """Sugestões por nome exato normalizado; nunca confirmam elegibilidade."""
    import unicodedata

    def normalize(name):
        ascii_name = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode()
        return re.sub(r'[^A-Z0-9]', '', ascii_name.upper())

    raw = Path(csv_path).read_bytes()
    try:
        text = raw.decode('utf-8-sig')
    except UnicodeDecodeError:
        text = raw.decode('latin-1')
    reader = csv.DictReader(io.StringIO(text), delimiter=';')
    required = {'CNPJ_CIA', 'DENOM_SOCIAL', 'CD_CVM'}
    if not required.issubset(reader.fieldnames or []):
        raise ValueError('CSV da CVM sem colunas CNPJ_CIA, DENOM_SOCIAL e CD_CVM.')
    companies = sorted({r['empresa'] for r in pilot['registros']})
    catalog = {}
    for row in reader:
        catalog.setdefault(normalize(row['DENOM_SOCIAL']), []).append(row)
    candidates = []
    for company in companies:
        matches = catalog.get(normalize(company), [])
        for match in matches or [{}]:
            cnpj = re.sub(r'\D', '', match.get('CNPJ_CIA', '')) or None
            candidates.append({
                'empresa_piloto': company, 'denominacao_cvm': match.get('DENOM_SOCIAL'),
                'cnpj_candidato': cnpj, 'codigo_cvm': match.get('CD_CVM'),
                'cnpj_numerico_valido': valid_cnpj(cnpj) if cnpj else None,
                'revisao': 'candidato_nao_confirmado' if match else 'sem_correspondencia_exata',
            })
    output = Path(output)
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / 'candidatos_cvm.csv', tuple(candidates[0]), candidates)
    (output / 'cvm_origem.json').write_text(json.dumps({
        'arquivo': Path(csv_path).name, 'sha256': hashlib.sha256(raw).hexdigest(),
        'metodo': 'Nome exato após normalização; sem confirmação automática de identidade ou listagem.',
    }, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return candidates
