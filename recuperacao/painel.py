"""Painel local de consulta, sem dependências externas."""

import json
from functools import partial
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlsplit

from .pipeline import ROOT, WARNING, check_evidence, load, quality, validate

WEB = Path(__file__).resolve().parent / 'web'


def payload(data_dir):
    pilot, sources = load(data_dir)
    errors = validate(pilot, sources)
    evidence = []
    if not errors:
        evidence, evidence_errors = check_evidence(data_dir, pilot, sources)
        errors.extend(evidence_errors)
    if errors:
        raise ValueError('\n'.join(errors))
    return {
        'aviso': WARNING, 'corte': pilot['data_corte_proposta'],
        'cobertura': pilot['cobertura'], 'registros': pilot['registros'],
        'fontes': sources, 'evidencias': evidence, 'pendencias': quality(pilot, evidence),
    }


class Handler(BaseHTTPRequestHandler):
    def __init__(self, *args, data_dir, **kwargs):
        self.data_dir = data_dir
        super().__init__(*args, **kwargs)

    def do_GET(self):
        route = urlsplit(self.path).path
        if route == '/api/dados':
            try:
                body = json.dumps(payload(self.data_dir), ensure_ascii=False).encode('utf-8')
            except (OSError, ValueError, KeyError, TypeError) as error:
                self.respond(422, json.dumps({'erro': str(error)}, ensure_ascii=False).encode('utf-8'), 'application/json')
                return
            self.respond(200, body, 'application/json')
            return
        assets = {'/': ('index.html', 'text/html'), '/app.js': ('app.js', 'text/javascript'),
                  '/style.css': ('style.css', 'text/css')}
        if route not in assets:
            self.respond(404, b'Pagina nao encontrada.', 'text/plain')
            return
        filename, mime = assets[route]
        self.respond(200, (WEB / filename).read_bytes(), mime)

    def respond(self, status, content, mime):
        self.send_response(status)
        self.send_header('Content-Type', mime + '; charset=utf-8')
        self.send_header('Content-Length', str(len(content)))
        self.send_header('Cache-Control', 'no-store')
        self.send_header('X-Content-Type-Options', 'nosniff')
        self.send_header('Content-Security-Policy', "default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'; frame-ancestors 'none'")
        self.end_headers()
        self.wfile.write(content)


def serve(data_dir=ROOT / 'data', port=8501):
    payload(data_dir)  # Falhar antes de iniciar se a base estiver inconsistente.
    with ThreadingHTTPServer(('127.0.0.1', port), partial(Handler, data_dir=data_dir)) as server:
        print(f'Painel disponível em http://127.0.0.1:{server.server_port}', flush=True)
        print('Abra esse endereço no navegador. Para encerrar: Ctrl+C.', flush=True)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nPainel encerrado.', flush=True)
