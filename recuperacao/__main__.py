import argparse
import json
import sqlite3
import sys
from pathlib import Path

from .pipeline import ROOT, build, cvm_candidates, load, validate


def main(argv=None):
    parser = argparse.ArgumentParser(description='Recuperação em Foco — pesquisa piloto')
    parser.add_argument('--dados', type=Path, default=ROOT / 'data')
    commands = parser.add_subparsers(dest='command', required=True)
    commands.add_parser('validar', help='Conferir integridade do piloto sem alterar arquivos')
    generate = commands.add_parser('gerar', help='Gerar banco, CSVs, relatório e SQL PostgreSQL')
    generate.add_argument('--saida', type=Path, default=ROOT / 'outputs')
    cvm = commands.add_parser('cvm', help='Sugerir correspondências a partir de CSV oficial local')
    cvm.add_argument('arquivo', type=Path)
    cvm.add_argument('--saida', type=Path, default=ROOT / 'outputs')
    args = parser.parse_args(argv)
    try:
        if args.command == 'gerar':
            manifest = build(args.dados, args.saida)
            print(json.dumps(manifest, ensure_ascii=False, indent=2))
            print(f'Arquivos gerados em {args.saida.resolve()}')
        else:
            pilot, sources = load(args.dados)
            errors = validate(pilot, sources)
            if errors:
                raise ValueError('\n'.join(errors))
            if args.command == 'validar':
                print(f"Integridade válida: {len(pilot['registros'])} episódios; {len(sources)} fontes.")
                print('A validação estrutural não confirma fatos, identidade ou elegibilidade.')
            else:
                candidates = cvm_candidates(args.arquivo, pilot, args.saida)
                print(f'{len(candidates)} linhas para revisão em {args.saida / "candidatos_cvm.csv"}')
        return 0
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error) as error:
        print(f'Erro: {error}', file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
