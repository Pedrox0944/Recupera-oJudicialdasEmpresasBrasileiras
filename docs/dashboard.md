# Painel no Metabase

## Painel local disponível

Execute `python3 -m recuperacao painel` e abra `http://127.0.0.1:8501`. O terminal deve continuar aberto. Para encerrar, use `Ctrl+C`; para outra porta, acrescente `--porta 8502`. No Windows, use `py -3` no lugar de `python3`.

O painel local usa Python e SVG no navegador, sem bibliotecas externas ou servidor de banco. Inclui pedidos por ano, preenchimento dos dados, linha de marcos históricos, filtros por companhia/ano, tabela, download CSV, pendências e evidências. Gráficos e cartões acompanham o recorte dos filtros. Datas não definidas permanecem desconhecidas. O status no corte e os indicadores de sucesso continuam sem auditoria.

O botão Atualizar dados relê as entradas locais, conferindo integridade e evidências. Não coleta documentos da internet. A página usa somente os arquivos do painel e a API local; não serve os diretórios do projeto. O servidor é restrito ao computador local.

A especificação abaixo continua sendo o plano para o futuro painel no Metabase.

## Implementação disponível — versão 0.2

`python3 -m recuperacao gerar` produz `outputs/relatorio.md`, CSVs, SQLite e SQL PostgreSQL. As visões `vw_cobertura_piloto` e `vw_pendencias_piloto` implementam o recorte inicial de qualidade. Metabase ainda não foi instalado nem conectado. Passos de carga e limitações em `execucao.md`.

## Visão geral
Título: Recuperação judicial na bolsa brasileira.
Subtítulo obrigatório: período, corte, cobertura e versão da base. Enquanto piloto, exibir “Pesquisa exploratória — sem taxa nacional”.

Cartões: companhias elegíveis; episódios; encerramentos por cumprimento; falências; em andamento; não apurados. Antes da auditoria, apresentar apenas quantidade de casos pesquisados e pendências.

## Visuais
- Barras de estados por ano do pedido, preservando a categoria não apurado.
- Duração por setor: mediana, número de casos e intervalo, somente com datas completas.
- Recorrência em 24 meses: exibir numerador, denominador e excluídos por acompanhamento insuficiente.
- Tabela de companhias com episódios, status no corte e acesso à evidência.
- Aba de qualidade: CNPJs faltantes, listagens pendentes, desfechos sem sentença e datas incompletas.

Filtros: ano do pedido, setor, desfecho e companhia. Não oferecer taxa setorial sem mostrar tamanho da amostra.

## Conexão prevista
Metabase conectado ao PostgreSQL com usuário de leitura nas tabelas analíticas. Credenciais ficam fora do repositório. O painel consulta visões validadas; os dados brutos não são editados pelo dashboard. Instalação e conexão ainda não executadas.
