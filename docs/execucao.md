# Execução local — versão 0.2

Requisito: Python 3.10 ou superior com o módulo sqlite3. Esta primeira etapa usa a biblioteca padrão: não exige instalar pacotes, PostgreSQL ou Docker. A adoção de pandas fica para os tratamentos de bases maiores; PostgreSQL e Metabase continuam sendo o destino planejado.

No terminal do VS Code, na raiz do projeto:

```sh
python3 -m recuperacao validar
python3 -m recuperacao gerar
python3 -m unittest discover -s tests -v
```

O comando `validar` verifica a estrutura, não a veracidade das fontes. Erros impedem a geração. CNPJ ausente, processo desconhecido e datas parciais são lacunas de pesquisa: aparecem nas pendências e não recebem valores fictícios.

## Arquivos gerados

Todos ficam em `outputs/`, fora do controle de versão:

| Arquivo | Uso |
|---|---|
| relatorio.md | Cobertura e pendências legíveis no VS Code |
| resumo.json | Contagens, limitações e SHA-256 das entradas |
| piloto.sqlite3 | Banco local com episódios, fontes e vínculos |
| episodios.csv | Episódios sem preencher datas ou identidades desconhecidas |
| fontes.csv | Catálogo original de fontes |
| episodio_fonte.csv | Relações entre episódios e fontes |
| pendencias.csv | Fila de revisão por episódio |
| postgresql.sql | Script transacional para importar o piloto no PostgreSQL |

Para outro destino: `python3 -m recuperacao gerar --saida /tmp/recuperacao-saida`.
Para outras entradas: `python3 -m recuperacao --dados caminho/da/base validar`.

Executar novamente reconstrói os artefatos derivados nesse destino. Os JSONs originais não são modificados. O catálogo pode conter fontes ainda não utilizadas. As datas de consulta dos documentos são preservadas; a execução do programa não equivale a nova consulta documental.

## Cadastro CVM

Baixe o CSV do [cadastro oficial de companhias abertas](https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/) e preserve-o em `data/raw/`, com a data de obtenção. Depois execute:

```sh
python3 -m recuperacao cvm data/raw/cad_cia_aberta.csv
```

O leitor aceita CSV separado por ponto e vírgula, em UTF-8 ou Latin-1. Usa `CNPJ_CIA`, `DENOM_SOCIAL` e `CD_CVM`. Gera `candidatos_cvm.csv` e `cvm_origem.json`, com hash do arquivo. Compara nomes após remover acentos, espaços e pontuação; não faz correspondência aproximada nem resolve nomes históricos. Sem correspondência exata, registra a pendência. CNPJs numéricos candidatos têm os dígitos verificadores conferidos; outros formatos exigem revisão fora deste validador do piloto histórico.

O cadastro atual não demonstra listagem na data do pedido. Nenhum candidato é gravado automaticamente no piloto. Conferir razão social histórica, identidade, processo e listagem antes de atualizar os dados. A integração auditada terá esquema e regras próprios; esta camada aceita apenas `pendente_validacao` e `nao_auditado`.

## PostgreSQL e Metabase

Com um PostgreSQL instalado e um banco escolhido, use a conexão configurada em `PGHOST`, `PGDATABASE`, `PGUSER` e demais variáveis usuais do cliente:

```sh
psql -v ON_ERROR_STOP=1 -f outputs/postgresql.sql
```

O script cria o esquema `pesquisa_piloto` e substitui **somente o conteúdo das três tabelas do piloto nesse esquema**: `fonte`, `episodio_piloto` e `episodio_fonte`. Não usar essas tabelas para inserir pesquisa manual: elas são derivadas dos JSONs. Não executar em um esquema compartilhado com dados que precisem ser preservados. A execução é transacional e repetível.

No Metabase, quando instalado, conectar um usuário com acesso de leitura e criar cartões a partir de `pesquisa_piloto.vw_cobertura_piloto` e uma tabela a partir de `pesquisa_piloto.vw_pendencias_piloto`. O usuário de leitura deve ser provisionado pelo administrador do banco; este projeto não cria contas nem armazena senhas.

As visões apresentam pesquisa e qualidade, sem proporção de sucesso ou duração jurídica. O modelo normalizado descrito em `modelo-de-dados.md` permanece como desenho da futura base auditada. A tabela piloto não é uma implementação completa daquele modelo.

## Limites de validação

O validador confere IDs, relações com fontes, CNPJ numérico quando informado, formato do número CNJ, datas ISO, ordem temporal, ano/mês e corte. Não verifica dígitos do processo CNJ, autenticidade documental, listagem histórica ou situação jurídica. As evidências atuais estão vinculadas ao episódio, ainda não a cada campo.

Referências técnicas: [sqlite3 do Python](https://docs.python.org/3/library/sqlite3.html) e [visões do PostgreSQL](https://www.postgresql.org/docs/current/sql-createview.html).
