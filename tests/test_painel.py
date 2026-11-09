import json
import tempfile
import threading
import unittest
from functools import partial
from http.server import ThreadingHTTPServer
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import urlopen

from recuperacao.painel import Handler, payload
from recuperacao.pipeline import ROOT


class PanelTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(('127.0.0.1', 0), partial(Handler, data_dir=ROOT / 'data'))
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()
        cls.url = f'http://127.0.0.1:{cls.server.server_port}'

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def test_api_preserves_unknowns_and_conflicting_evidence(self):
        with urlopen(self.url + '/api/dados', timeout=5) as response:
            data = json.load(response)
        self.assertEqual(len(data['registros']), 6)
        viver = next(r for r in data['registros'] if r['id'] == 'P03')
        self.assertIsNone(viver['encerramento'])
        self.assertEqual(sum(e['situacao'] == 'alternativa_pendente' for e in data['evidencias']), 2)
        self.assertTrue(all(r['status_no_corte'] == 'nao_auditado' for r in data['registros']))

    def test_panel_and_assets_are_served(self):
        for path, mime in [('/', 'text/html'), ('/app.js', 'text/javascript'), ('/style.css', 'text/css')]:
            with self.subTest(path=path), urlopen(self.url + path, timeout=5) as response:
                self.assertEqual(response.status, 200)
                self.assertIn(mime, response.headers['Content-Type'])
                self.assertIn("script-src 'self'", response.headers['Content-Security-Policy'])
                self.assertTrue(response.read())

    def test_unlisted_files_and_traversal_are_not_served(self):
        for path in ['/data/piloto.json', '/../README.md', '/.git/config']:
            with self.subTest(path=path), self.assertRaises(HTTPError) as error:
                urlopen(self.url + path, timeout=5)
            self.assertEqual(error.exception.code, 404)

    def test_invalid_data_blocks_panel_payload(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / 'piloto.json').write_text('{"registros": []}')
            (root / 'fontes.json').write_text('[]')
            with self.assertRaises(ValueError):
                payload(root)
