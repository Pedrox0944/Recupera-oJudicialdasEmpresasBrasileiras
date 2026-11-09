# Recuperação em Foco

**Portfólio de análise de dados, pesquisa de negócios e visualização interativa.**

> Recuperação judicial na bolsa brasileira: quantas empresas conseguiram sair da crise?

Projeto de portfólio que acompanha o ciclo de trabalho entre coleta, tratamento, validação, armazenamento e visualização de dados públicos. A pesquisa investiga episódios de recuperação judicial de companhias brasileiras com ações listadas em bolsa na data do pedido, desde 2005. O objetivo é documentar os desfechos jurídicos e acompanhar a trajetória posterior dessas companhias com evidências rastreáveis.

**Estado atual:** pesquisa exploratória com cinco companhias e seis episódios candidatos. Ferramentas na versão **0.3.0**, base piloto com corte proposto em **09/11/2026**, ainda não auditada. O piloto não representa o universo nacional e não permite calcular uma taxa de sucesso.

## Por onde começar

**Para ver os gráficos no navegador**, execute na raiz do projeto:

```sh
python3 -m recuperacao painel
```

Abra **[http://127.0.0.1:8501](http://127.0.0.1:8501)** e mantenha o terminal em execução. No Windows, use `py -3 -m recuperacao painel`. Para encerrar, pressione `Ctrl+C`. Se a porta estiver ocupada, use `python3 -m recuperacao painel --porta 8502` e abra o endereço com a nova porta.

O painel oferece filtros por companhia e ano, gráficos de pedidos e cobertura dos campos, marcos históricos, tabela de processos, fontes, pendências e download do recorte em CSV. Usa apenas Python e o navegador; funciona sem internet para consultar a base local. Os links para documentos externos precisam de conexão. O botão **Atualizar dados** relê os JSONs locais e valida as evidências; não faz coleta externa.

- **Quero executar e ver os resultados:** siga [Execução rápida](#execução-rápida).
- **Quero conhecer a pesquisa:** leia [Objetivo e critérios](#objetivo-e-critérios) e a [metodologia](docs/metodologia.md).
- **Quero desenvolver ou contribuir:** consulte o [roteiro do projeto](#roteiro-do-projeto) e [Como contribuir](#como-contribuir).
- **Quero compartilhar o projeto:** veja [Acesso para outras pessoas](#acesso-para-outras-pessoas).

## O projeto como portfólio

### Desafio de negócio

Investigar recuperação judicial exige conciliar documentos de épocas diferentes, nomes históricos de companhias e decisões que podem ter recursos posteriores. O desafio é transformar essas informações em uma base consultável, preservando as evidências e deixando as lacunas visíveis.

### Solução desenvolvida

Um fluxo reproduzível em Python coleta fontes públicas, valida a estrutura dos registros, documenta evidências por campo e gera um banco SQLite, exportações e relatórios. Um painel local permite explorar os casos no navegador, filtrar o recorte e acessar os documentos que sustentam os dados.

```text
Fontes públicas → Coleta e versões → Conferência documental → Base piloto
                                                           ↓
                                  Validação → Painel local e exportações
                                                           ↓
                                           SQLite e SQL para PostgreSQL
```

A conferência documental é uma etapa de pesquisa: baixar um arquivo não confirma automaticamente um fato.

### Competências demonstradas

| Área | Aplicação no projeto |
|---|---|
| Análise de negócios | Pergunta de pesquisa, escopo, critérios de inclusão e limites dos indicadores |
| Pesquisa e coleta | Consulta à CVM, documentos corporativos, administradores judiciais e TJSP |
| Qualidade de dados | Validação de datas, referências, identificadores e preservação de desconhecidos |
| Rastreabilidade | Evidências por campo, hashes SHA-256, histórico de alterações e divergências |
| Python e SQL | CLI, processamento, SQLite e geração de script para PostgreSQL |
| Visualização | Painel em HTML, CSS, JavaScript e SVG, com filtros e exportação CSV |
| Testes e documentação | Testes automatizados do processamento, coleta e servidor; guias de reprodução |

### Entregas verificáveis

- Painel local com gráficos, tabela de processos, filtros, fontes e pendências.
- Seis episódios candidatos de cinco companhias, com CNPJ, processo e data completa do pedido preenchidos.
- Onze fontes externas coletadas e 23 evidências por campo, incluindo duas alternativas pendentes.
- Banco SQLite, CSVs, relatório de cobertura e script de carga PostgreSQL.
- **30 testes automatizados aprovados na última execução de 09/11/2026.**

O resultado atual demonstra construção de uma pesquisa reproduzível e controle de qualidade. A resposta à pergunta de negócio ainda depende da auditoria da elegibilidade histórica e dos desfechos; a base piloto não sustenta uma taxa nacional de sucesso.

## Objetivo e critérios

A pergunta central é: das companhias elegíveis que pediram recuperação judicial, quantas tiveram encerramento por cumprimento das obrigações e qual foi sua trajetória posterior?

Para responder, o projeto precisa:

1. Identificar as companhias por CNPJ e confirmar a listagem histórica na data do pedido.
2. Distinguir empresas, processos e episódios, inclusive pedidos recorrentes.
3. Registrar decisões, datas, fontes, precisão temporal e situação na data de corte.
4. Produzir indicadores com denominadores explícitos, incluindo casos não apurados.
5. Acompanhar novos pedidos e continuidade operacional em horizontes definidos.

Encerramento jurídico, continuidade operacional e retorno do acionista são resultados distintos. Ausência de data de encerramento não significa processo em andamento. Campos desconhecidos permanecem nulos. As regras completas estão na [metodologia](docs/metodologia.md).

## O que funciona hoje

| Componente | Situação |
|---|---|
| Piloto de Oi, Viver, Lupatech, Eternit e Renova | Seis episódios candidatos; Oi tem dois |
| Validação estrutural em Python | Implementada |
| Banco local SQLite | Gerado pelo comando `gerar` |
| Relatório de cobertura e pendências | Gerado em Markdown |
| Exportações CSV e manifesto JSON | Implementados |
| Sugestões de identidade por cadastro CVM | Implementadas; exigem revisão manual |
| Script de carga PostgreSQL | Gerado; ainda não executado em PostgreSQL |
| Coleta pública com versões e hashes | Implementada; onze fontes coletadas |
| Evidência por campo e histórico de alterações | Implementados; divergência da Viver preservada |
| Testes automatizados | Validação, coleta e servidor local; execute os testes para conferir |
| Modelo normalizado da base auditada | Planejado |
| Painel local com gráficos no navegador | Implementado; comando `painel` |
| Dashboard Metabase e acesso público pela web | Planejados |
| Indicadores de desfecho, duração e recorrência | Aguardam auditoria da base |

Na versão 0.3, os seis episódios têm CNPJ, processo e data completa do pedido, com os novos campos vinculados às fontes consultadas. Foram preservadas onze coletas externas e registradas 23 evidências por campo. Todos os status no corte e a elegibilidade histórica permanecem pendentes. Veja [dados externos e pendências](docs/importacao.md) e o [registro de andamento](docs/andamento.md).

## Execução rápida

### 1. Obter o projeto

Baixe o ZIP do projeto ou receba uma cópia da pasta completa e extraia os arquivos. A pasta precisa conter `README.md`, `recuperacao/`, `data/` e `sql/`.

Abra essa pasta no VS Code e use **Terminal → Novo Terminal**. Também é possível usar o terminal do sistema. Execute os comandos na raiz, onde está este README.

Repositório: [Recuperação Judicial das Empresas Brasileiras](https://github.com/Pedrox0944/Recupera-oJudicialdasEmpresasBrasileiras). Para obter uma cópia com Git:

```sh
git clone https://github.com/Pedrox0944/Recupera-oJudicialdasEmpresasBrasileiras.git
cd Recupera-oJudicialdasEmpresasBrasileiras
```

### 2. Conferir o Python

Requisito: **Python 3.10 ou superior**, com o módulo `sqlite3`.

Linux ou macOS:

```sh
python3 --version
python3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

Windows, com o inicializador Python instalado:

```powershell
py -3 --version
py -3 -c "import sqlite3; print(sqlite3.sqlite_version)"
```

Esta etapa usa apenas a biblioteca padrão do Python. Não exige `pip install`, PostgreSQL, Docker ou Metabase.

### 3. Abrir o painel com gráficos

Linux ou macOS:

```sh
python3 -m recuperacao painel
```

Windows:

```powershell
py -3 -m recuperacao painel
```

Abra **http://127.0.0.1:8501** no navegador. A mensagem `Painel disponível em...` confirma que o servidor iniciou. Mantenha o terminal aberto enquanto usa o painel; encerre com **Ctrl+C**.

Não é necessário executar `gerar` antes: o painel lê e valida os JSONs incluídos no projeto. A interface permite:

- Filtrar por companhia e ano do pedido.
- Visualizar pedidos por ano e cobertura de preenchimento dos campos.
- Consultar os marcos históricos de pedido e encerramento reportado.
- Explorar processos, pendências e documentos de origem.
- Baixar o recorte selecionado em CSV.

**Atualizar dados** relê a base local; para buscar documentos externos, use o comando `coletar` descrito adiante.

Se a porta estiver ocupada, execute `python3 -m recuperacao painel --porta 8502` e abra `http://127.0.0.1:8502`. No Windows, substitua `python3` por `py -3`.

### 4. Validar e gerar banco e relatórios

Linux ou macOS:

```sh
python3 -m recuperacao validar
python3 -m recuperacao gerar
```

Windows:

```powershell
py -3 -m recuperacao validar
py -3 -m recuperacao gerar
```

A validação deve informar **6 episódios e 20 fontes** no piloto atual. O segundo comando cria a pasta `outputs/` com o banco e os relatórios. Rodar novamente reconstrói esses artefatos, preservando os JSONs de origem.

A validação verifica integridade e consistência. Ela não confirma a veracidade dos fatos nem substitui a auditoria documental.

### 5. Consultar os arquivos gerados

Depois da geração, abra [outputs/relatorio.md](outputs/relatorio.md). No VS Code, use **Abrir Visualização** no editor Markdown para ler o relatório formatado.

| Arquivo em `outputs/` | Como consultar |
|---|---|
| `relatorio.md` | Cobertura, limitações e pendências por episódio |
| `evidencias.csv` | Campos conferidos, localização no documento e hash da cópia usada |
| `resumo.json` | Contagens e hashes SHA-256 das entradas |
| `episodios.csv` | Episódios em um editor ou planilha |
| `fontes.csv` | Catálogo de evidências |
| `episodio_fonte.csv` | Vínculos entre episódios e fontes |
| `pendencias.csv` | Fila de revisão documental |
| `piloto.sqlite3` | Banco para consultas SQL locais |
| `postgresql.sql` | Script para a etapa opcional com PostgreSQL |

Os arquivos de `outputs/` são derivados e não são versionados. Por isso, os links para resultados locais só funcionam depois de executar `gerar`. A execução básica funciona sem internet, a partir dos dados incluídos em `data/`.

### 6. Executar os testes

Linux ou macOS:

```sh
python3 -m unittest discover -s tests -v
```

Windows:

```powershell
py -3 -m unittest discover -s tests -v
```

O resultado esperado é `OK`. Um teste de arquivo inexistente imprime uma mensagem `Erro:` de propósito; ele passa quando essa falha é tratada corretamente.

## Etapas opcionais

### Comparar nomes com o cadastro CVM

Baixe o CSV do [cadastro oficial da CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/) e salve como `data/raw/cad_cia_aberta.csv`. Crie as pastas se necessário. Preserve também a URL e a data de obtenção da cópia.

```sh
python3 -m recuperacao cvm data/raw/cad_cia_aberta.csv
```

No Windows, substitua `python3` por `py -3`.

O comando gera `outputs/candidatos_cvm.csv` e `outputs/cvm_origem.json`. As sugestões comparam nomes normalizados, removem o sufixo “- EM RECUPERAÇÃO JUDICIAL” e não alteram o piloto automaticamente. O cadastro atual não prova listagem histórica. Na primeira coleta, a Oi ficou sem correspondência exata. Na versão 0.3, a denominação com sufixo foi revisada e seu CNPJ conferido também em documento da companhia; os detalhes estão em [dados externos](docs/importacao.md).

A pasta `data/raw/` não é versionada. Outra pessoa precisa obter sua própria cópia para executar esta etapa; ela não é necessária para a execução básica.

### Trazer dados externos

Para baixar novamente as onze fontes catalogadas:

```sh
python3 -m recuperacao coletar S10 S11 S12 S13 S14 S15 S16 S17 S18 S19 S20
```

O comando exige internet, preserva cópias por hash e registra falhas. A coleta não altera os fatos automaticamente: cada campo precisa de conferência documental. Consulte [o guia de importação e resolução de pendências](docs/importacao.md).

### Carregar no PostgreSQL

Esta etapa exige um servidor PostgreSQL disponível, o cliente `psql` e um banco de destino configurado. O comando `gerar` prepara o script, mas não instala nem inicia o servidor.

Configure a conexão pelo cliente PostgreSQL ou pelas variáveis `PGHOST`, `PGPORT`, `PGDATABASE` e `PGUSER`. Depois execute:

```sh
psql -v ON_ERROR_STOP=1 -f outputs/postgresql.sql
```

O script cria o esquema `pesquisa_piloto` e substitui o conteúdo das quatro tabelas derivadas do piloto nesse esquema. Use um banco de desenvolvimento e mantenha as entradas de pesquisa nos JSONs de origem.

As visões disponíveis são `pesquisa_piloto.vw_cobertura_piloto` e `pesquisa_piloto.vw_pendencias_piloto`. A integração ainda precisa ser testada em um servidor PostgreSQL real. Veja [instruções técnicas](docs/execucao.md).

### Consultar pelo Metabase

A especificação está em [docs/dashboard.md](docs/dashboard.md). A etapa depende da carga PostgreSQL, da instalação do Metabase e de uma conexão com usuário de leitura. O primeiro painel deverá apresentar cobertura e qualidade da pesquisa.

## Acesso para outras pessoas

Hoje o acesso é **local**, pelo painel no navegador, por uma cópia do projeto ou pelos arquivos gerados. O servidor escuta apenas em `127.0.0.1`: o endereço funciona no computador em que o comando foi iniciado. Não há endereço público ou dashboard hospedado.

Há duas formas de compartilhar a entrega atual:

1. **Para reproduzir a análise:** compartilhe a pasta do projeto ou publique o código em um repositório. Inclua `recuperacao/` (com `web/`), `sql/`, os JSONs versionados de `data/` — incluindo `piloto.json`, `fontes.json`, `evidencias.json` e `coletas.json` —, `tests/` e a documentação. O destinatário segue a execução rápida deste README.
2. **Para apenas consultar:** compartilhe os arquivos gerados de relatório, resumo, episódios, fontes, vínculos, evidências e pendências. Envie o conjunto com a data de corte e as limitações, para que os dados sejam interpretados no contexto da pesquisa piloto.

O painel já oferece consulta pelo navegador no próprio computador. Para acesso público pela internet, ainda será necessário escolher a hospedagem, configurar a aplicação e as permissões e divulgar um endereço. A alternativa PostgreSQL/Metabase permanece no roteiro de evolução.

## Roteiro do projeto

| Etapa | Entrega e critério de conclusão | Estado |
|---|---|---|
| 1. Pesquisa piloto | Casos preliminares, fontes e metodologia documentados | Disponível, não auditada |
| 2. Execução reproduzível | Validação, banco local, exportações e testes | Implementada |
| 3. Identidade e elegibilidade | CNPJ revisado e listagem comprovada na data do pedido | Pendente |
| 4. Evidência jurídica | Processos, decisões, recursos, datas e status no corte auditados | Pendente |
| 5. Base analítica | Modelo normalizado, deduplicação e evidência por campo | Planejada |
| 6. Indicadores | Denominadores reproduzíveis, desfechos, duração e acompanhamento | Planejada |
| 7. Dashboard | PostgreSQL/Metabase executados e consultas conferidas | Planejada |
| 8. Publicação | Repositório, forma de acesso, permissões e limitações documentados | Planejada |

**Próxima prioridade:** confirmar listagem histórica e status no corte de uma companhia, conciliar os marcos de encerramento da Viver e conferir os campos herdados que ainda não têm evidência específica. As identidades cadastrais do piloto já foram revisadas; isso não encerra a elegibilidade histórica. A sequência detalhada está em [próximos passos](docs/proximos-passos.md).

A versão analítica estará pronta quando identidades e elegibilidade estiverem auditadas, cada resultado tiver evidência, os indicadores tiverem denominadores reproduzíveis e o painel corresponder às consultas. O avanço técnico atual não encerra a pesquisa.

## Estrutura do projeto

```text
RecuperacaoJudicial/
├── README.md                 # Guia principal
├── recuperacao/              # CLI, processamento e servidor do painel
│   └── web/                  # Interface: HTML, CSS e JavaScript
├── data/
│   ├── piloto.json           # Episódios preliminares
│   ├── fontes.json           # Catálogo de fontes
│   ├── evidencias.json       # Evidências por campo e alternativas pendentes
│   ├── coletas.json          # Registro das cópias usadas na pesquisa
│   └── raw/                  # Coletas locais; fora do versionamento
├── sql/piloto.sql            # Tabelas e visões da camada piloto
├── tests/                    # Testes automatizados
├── docs/                     # Metodologia, execução e planejamento
└── outputs/                  # Resultados gerados; fora do versionamento
```

Python e SQLite sustentam a execução atual. pandas está previsto para tratamentos de bases maiores; PostgreSQL e Metabase são o destino planejado para a camada analítica e o painel.

## Como contribuir

1. Leia a [metodologia](docs/metodologia.md) e o [modelo de dados](docs/modelo-de-dados.md).
2. Escolha uma pendência e confira o documento original, registrando URL, localização, consulta e precisão das datas.
3. Preserve desconhecidos como nulos; não preencha dias ou meses fictícios.
4. Atualize as entradas pertinentes e execute validação, geração e testes.
5. Descreva a evidência e o impacto da mudança para revisão.

A camada atual aceita apenas `pendente_validacao`, `nao_auditado` e `piloto_nao_inferencial`. A promoção de registros auditados depende da implementação da camada própria; mudar esses rótulos no piloto faz a validação falhar.

## Problemas comuns

| Sintoma | Como resolver |
|---|---|
| `python3` ou `py` não encontrado | Instale Python 3.10+ e confira o comando disponível no sistema |
| `No module named recuperacao` | Execute na pasta que contém este README e `recuperacao/` |
| Módulo `sqlite3` ausente | Use uma distribuição Python que inclua suporte a SQLite |
| Página do painel não abre | Confira se `painel` está rodando no terminal e use a porta indicada na mensagem de início |
| Porta 8501 ocupada | Execute `painel --porta 8502` e abra `http://127.0.0.1:8502` |
| `outputs/` não existe | Execute o comando `gerar` |
| Falha de integridade | Corrija os campos indicados nas entradas antes de gerar novamente |
| CSV da CVM não encontrado | Obtenha a cópia oficial; esta etapa é opcional |
| `psql` não encontrado ou conexão recusada | Instale/configure o cliente e o servidor PostgreSQL para a etapa opcional |

## Documentação de referência

- [Dados externos e resolução de pendências](docs/importacao.md)
- [Metodologia e interpretação](docs/metodologia.md)
- [Modelo de dados](docs/modelo-de-dados.md)
- [Execução e detalhes técnicos](docs/execucao.md)
- [Especificação do dashboard](docs/dashboard.md)
- [Andamento e primeira coleta](docs/andamento.md)
- [Próximos passos e critérios de conclusão](docs/proximos-passos.md)
