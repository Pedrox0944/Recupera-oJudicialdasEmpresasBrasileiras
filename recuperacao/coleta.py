"""Coleta pública reproduzível; guarda versões pelo hash e nunca promove fatos."""

import hashlib
import json
import socket
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import URLError
from urllib.parse import urlsplit
from urllib.request import Request, urlopen


def collect(sources, destination, selected):
    destination = Path(destination)
    destination.mkdir(parents=True, exist_ok=True)
    catalog = {s['id']: s for s in sources}
    unknown = set(selected) - catalog.keys()
    if unknown:
        raise ValueError(f'Fontes inexistentes: {sorted(unknown)}')
    report = []
    for sid in dict.fromkeys(selected):
        source = catalog[sid]
        url = source['url']
        if urlsplit(url).scheme != 'https':
            raise ValueError(f'{sid}: a coleta exige HTTPS.')
        entry = {'fonte_id': sid, 'url': url,
                 'obtido_em': datetime.now(timezone.utc).isoformat()}
        try:
            request = Request(url, headers={'User-Agent': 'RecuperacaoEmFoco/0.3 pesquisa-publica'})
            with urlopen(request, timeout=30) as response:
                if urlsplit(response.url).scheme != 'https':
                    raise ValueError('Redirecionamento para protocolo não HTTPS.')
                content = response.read(25_000_001)
                if not content or len(content) > 25_000_000:
                    raise ValueError('Arquivo vazio ou maior que o limite de 25 MB.')
                content_type = response.headers.get('Content-Type', '')
                if source.get('formato') == 'pdf' and not content.startswith(b'%PDF-'):
                    raise ValueError('Resposta não é PDF; possível bloqueio ou página de erro.')
                if source.get('formato') == 'csv' and b'CNPJ_CIA' not in content[:2000]:
                    raise ValueError('Resposta não corresponde ao CSV esperado da CVM.')
                digest = hashlib.sha256(content).hexdigest()
                suffix = {'pdf': 'pdf', 'csv': 'csv'}.get(source.get('formato'), 'html')
                file = destination / f'{sid}-{digest}.{suffix}'
                if not file.exists():
                    file.write_bytes(content)
                entry.update(status='obtida', arquivo=file.name, sha256=digest,
                             bytes=len(content), content_type=content_type, url_final=response.url)
        except (OSError, URLError, ValueError, socket.timeout) as error:
            entry.update(status='falha', erro=str(error))
        report.append(entry)
        # Log cumulativo: falhas e consultas anteriores permanecem registradas.
        with (destination / 'manifesto.jsonl').open('a', encoding='utf-8') as handle:
            handle.write(json.dumps(entry, ensure_ascii=False) + '\n')
    return report
