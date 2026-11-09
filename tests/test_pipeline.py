import copy
import csv
import json
import sqlite3
import tempfile
import unittest
from contextlib import closing
from pathlib import Path

from recuperacao.__main__ import main
from recuperacao.pipeline import ROOT, build, cvm_candidates, load, validate, load_evidence, validate_evidence


class PipelineTests(unittest.TestCase):
    def setUp(self):
        self.pilot, self.sources = load(ROOT / 'data')
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def test_original_pilot_has_valid_structure(self):
        self.assertEqual(validate(self.pilot, self.sources), [])

    def test_missing_source_blocks_import(self):
        self.pilot['registros'][0]['fontes'] = ['inexistente']
        self.assertTrue(any('fonte inexistente' in e for e in validate(self.pilot, self.sources)))

    def test_duplicate_id_and_company_process_are_rejected(self):
        row = copy.deepcopy(self.pilot['registros'][0])
        self.pilot['registros'].append(row)
        self.assertTrue(any('duplicado' in e for e in validate(self.pilot, self.sources)))
        row['id'], row['episodio'] = 'P99', 99
        self.assertTrue(any('companhia/processo duplicado' in e for e in validate(self.pilot, self.sources)))

    def test_partial_date_is_not_a_full_date(self):
        self.pilot['registros'][2]['pedido'] = '2016'
        self.assertTrue(any('data ISO inválida' in e for e in validate(self.pilot, self.sources)))

    def test_negative_duration_and_future_event_are_rejected(self):
        self.pilot['registros'][0]['encerramento'] = '2015-01-01'
        self.pilot['registros'][1]['deferimento'] = '2027-01-01'
        errors = validate(self.pilot, self.sources)
        self.assertTrue(any('sequência' in e for e in errors))
        self.assertTrue(any('posterior ao corte' in e for e in errors))

    def test_year_and_month_must_match_known_date(self):
        self.pilot['registros'][0].update(ano_pedido=2017, mes_pedido=8)
        errors = validate(self.pilot, self.sources)
        self.assertTrue(any('diverge' in e for e in errors))
        self.assertTrue(any('mes_pedido inconsistente' in e for e in errors))

    def test_partial_date_after_cutoff_is_rejected(self):
        self.pilot['registros'][1].update(pedido=None, ano_pedido=2026, mes_pedido=12)
        self.assertTrue(any('posterior ao corte' in e for e in validate(self.pilot, self.sources)))

    def test_invalid_cnpj_is_rejected(self):
        self.pilot['registros'][0]['cnpj'] = '00000000000000'
        self.assertTrue(any('CNPJ' in e for e in validate(self.pilot, self.sources)))

    def test_date_before_window_is_rejected_without_year_field(self):
        self.pilot['registros'][0].update(pedido='2004-01-01', ano_pedido=None)
        self.assertTrue(any('anterior à janela' in e for e in validate(self.pilot, self.sources)))

    def test_malformed_url_returns_validation_error(self):
        self.sources[0]['url'] = ['https://example.org']
        self.assertTrue(any('URL inválida' in e for e in validate(self.pilot, self.sources)))

    def test_unsupported_audited_status_is_rejected(self):
        self.pilot['registros'][0]['status_no_corte'] = 'em_andamento'
        self.assertTrue(any('status_no_corte' in e for e in validate(self.pilot, self.sources)))

    def test_malformed_structure_returns_errors(self):
        self.pilot['registros'][0]['fontes'] = [{}]
        self.sources.append('invalid')
        self.assertTrue(validate(self.pilot, self.sources))

    def test_build_preserves_unknowns_sources_and_blocks_indicators(self):
        manifest = build(ROOT / 'data', self.root)
        self.assertIsNone(manifest['indicadores_juridicos'])
        self.assertEqual(manifest['contagens']['episodios_pesquisados'], 6)
        with closing(sqlite3.connect(self.root / 'piloto.sqlite3')) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM episodio_fonte').fetchone()[0], sum(len(r['fontes']) for r in self.pilot['registros']))
            self.assertEqual(db.execute("SELECT pedido, encerramento FROM episodio_piloto WHERE id='P03'").fetchone(), ('2016-09-16', None))
            self.assertEqual(db.execute('PRAGMA foreign_key_check').fetchall(), [])
            self.assertEqual(db.execute('SELECT COUNT(*) FROM episodio_piloto WHERE cnpj IS NULL').fetchone()[0], 0)
            self.assertEqual(db.execute('SELECT COUNT(*) FROM evidencia_campo').fetchone()[0], 23)
        with (self.root / 'episodios.csv').open() as file:
            self.assertEqual(len(list(csv.DictReader(file))), 6)
        self.assertIn('sem taxa nacional', (self.root / 'relatorio.md').read_text())

    def test_rebuild_does_not_duplicate_records(self):
        first = build(ROOT / 'data', self.root)
        original = (self.root / 'relatorio.md').read_bytes()
        self.assertEqual(first, build(ROOT / 'data', self.root))
        self.assertEqual(original, (self.root / 'relatorio.md').read_bytes())
        with closing(sqlite3.connect(self.root / 'piloto.sqlite3')) as db:
            self.assertEqual(db.execute('SELECT COUNT(*) FROM episodio_piloto').fetchone()[0], 6)

    def test_invalid_input_does_not_replace_existing_outputs(self):
        build(ROOT / 'data', self.root / 'outputs')
        original = (self.root / 'outputs/resumo.json').read_bytes()
        self.pilot['registros'][0]['fontes'] = ['bad']
        (self.root / 'piloto.json').write_text(json.dumps(self.pilot))
        (self.root / 'fontes.json').write_text(json.dumps(self.sources))
        with self.assertRaises(ValueError):
            build(self.root, self.root / 'outputs')
        self.assertEqual(original, (self.root / 'outputs/resumo.json').read_bytes())

    def test_cvm_candidates_do_not_modify_pilot(self):
        original = copy.deepcopy(self.pilot)
        path = self.root / 'cvm.csv'
        path.write_text('CNPJ_CIA;DENOM_SOCIAL;CD_CVM\n00.000.000/0001-91;OI S.A.;1\n', encoding='latin-1')
        candidates = cvm_candidates(path, self.pilot, self.root / 'out')
        self.assertEqual(self.pilot, original)
        oi = next(r for r in candidates if r['empresa_piloto'] == 'Oi S.A.')
        self.assertEqual(oi['cnpj_candidato'], '00000000000191')
        self.assertEqual(oi['revisao'], 'candidato_nao_confirmado')
        self.assertTrue(any(r['revisao'] == 'sem_correspondencia_exata' for r in candidates))

    def test_postgresql_export_escapes_source_text(self):
        self.sources[0]['titulo'] = "Fonte d'origem"
        (self.root / 'piloto.json').write_text(json.dumps(self.pilot))
        (self.root / 'fontes.json').write_text(json.dumps(self.sources))
        build(self.root, self.root / 'out')
        sql = (self.root / 'out/postgresql.sql').read_text()
        self.assertIn("Fonte d''origem", sql)
        self.assertIn('SET LOCAL search_path TO pesquisa_piloto', sql)
        self.assertNotIn('CREATE VIEW IF NOT EXISTS', sql)

    def test_cli_missing_files_returns_failure(self):
        self.assertEqual(main(['--dados', str(self.root), 'validar']), 1)

    def test_evidence_value_must_match_adopted_data(self):
        evidence = load_evidence(ROOT / 'data')
        evidence[0]['valor'] = '00000000000000'
        self.assertTrue(any('diverge do valor' in e for e in validate_evidence(self.pilot, self.sources, evidence)))

    def test_alternative_evidence_does_not_fill_unknown_date(self):
        evidence = load_evidence(ROOT / 'data')
        self.assertEqual(validate_evidence(self.pilot, self.sources, evidence), [])
        viver = [e for e in evidence if e['episodio_id'] == 'P03' and e['campo'] == 'encerramento']
        self.assertEqual({e['situacao'] for e in viver}, {'alternativa_pendente'})
        self.assertIsNone(self.pilot['registros'][2]['encerramento'])

    def test_evidence_must_reference_obtained_snapshot(self):
        evidence = load_evidence(ROOT / 'data')
        self.assertTrue(any('hash não encontrado' in e for e in validate_evidence(self.pilot, self.sources, evidence, [])))

    def test_cvm_judicial_suffix_is_candidate_only(self):
        path = self.root / 'cvm.csv'
        path.write_text('CNPJ_CIA;DENOM_SOCIAL;CD_CVM\n76.535.764/0001-43;OI S.A. - EM RECUPERAÇÃO JUDICIAL;11312\n')
        rows = cvm_candidates(path, self.pilot, self.root / 'out')
        oi = next(r for r in rows if r['empresa_piloto'] == 'Oi S.A.')
        self.assertEqual(oi['cnpj_candidato'], '76535764000143')
        self.assertEqual(oi['revisao'], 'candidato_nao_confirmado')


if __name__ == '__main__':
    unittest.main()
