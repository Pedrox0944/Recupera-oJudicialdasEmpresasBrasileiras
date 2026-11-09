import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from urllib.error import URLError

from recuperacao.coleta import collect


class Response:
    url = 'https://example.org/fonte.pdf'
    headers = {'Content-Type': 'application/pdf'}

    def __init__(self, content):
        self.content = content

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self, limit):
        return self.content[:limit]


class CollectionTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.path = Path(temp.name)
        self.sources = [{'id': 'S01', 'url': 'https://example.org/fonte.pdf', 'formato': 'pdf'}]

    def test_repeated_collection_preserves_snapshot_and_log(self):
        with patch('recuperacao.coleta.urlopen', return_value=Response(b'%PDF-1.4 example')):
            first = collect(self.sources, self.path, ['S01'])
            second = collect(self.sources, self.path, ['S01'])
        self.assertEqual(first[0]['sha256'], second[0]['sha256'])
        self.assertEqual(len(list(self.path.glob('*.pdf'))), 1)
        self.assertEqual(len((self.path / 'manifesto.jsonl').read_text().splitlines()), 2)

    def test_html_error_does_not_become_pdf(self):
        with patch('recuperacao.coleta.urlopen', return_value=Response(b'<html>Access denied</html>')):
            report = collect(self.sources, self.path, ['S01'])
        self.assertEqual(report[0]['status'], 'falha')
        self.assertEqual(list(self.path.glob('*.pdf')), [])

    def test_network_failure_is_recorded(self):
        with patch('recuperacao.coleta.urlopen', side_effect=URLError('offline')):
            report = collect(self.sources, self.path, ['S01'])
        self.assertEqual(report[0]['status'], 'falha')
        self.assertEqual(json.loads((self.path / 'manifesto.jsonl').read_text())['status'], 'falha')

    def test_unknown_source_is_rejected(self):
        with self.assertRaises(ValueError):
            collect(self.sources, self.path, ['unknown'])
