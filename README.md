# Recuperação em Foco

**Recuperação judicial na bolsa brasileira: quantas empresas conseguiram sair da crise?**

Projeto de portfólio em análise de dados e negócios. Ferramentas versão 0.2 — pesquisa piloto original de 09/11/2026, ainda não auditada.

## Pergunta de negócio
Das empresas brasileiras com ações listadas em bolsa na data do pedido de recuperação judicial desde 2005, quantas tiveram encerramento por cumprimento das obrigações e qual foi sua trajetória posterior?

## Estado real da entrega
- Pesquisa piloto de cinco companhias, com seis episódios candidatos: Oi (dois), Viver, Lupatech, Eternit e Renova.
- Fontes primárias vinculadas aos registros, campos desconhecidos explícitos e regras de cálculo.
- O piloto NÃO é censo, amostra representativa ou cálculo de taxa de sucesso.
- Cadastro CVM, elegibilidade histórica, sentenças e status no corte ainda precisam de auditoria.
- Implementados: CLI Python, validação estrutural, banco SQLite local, exportações CSV, relatório de pendências, sugestões de identidade por CSV da CVM e script de importação PostgreSQL.
- O banco SQLite e os relatórios são gerados localmente. PostgreSQL e Metabase ainda não foram instalados ou executados; não há dashboard publicado.
- Indicadores jurídicos ficam bloqueados enquanto as evidências e a elegibilidade não forem auditadas.

## Executar no VS Code

Na raiz do projeto, com Python 3.10 ou superior, sem dependências externas:

```sh
python3 -m recuperacao validar
python3 -m recuperacao gerar
python3 -m unittest discover -s tests -v
```

Após gerar, abra [o relatório de cobertura](outputs/relatorio.md). Veja [instruções completas de execução](docs/execucao.md), incluindo CSV da CVM e a etapa com PostgreSQL/Metabase.

O [registro de andamento](docs/andamento.md) documenta a primeira coleta do cadastro CVM, os candidatos encontrados e as pendências de pesquisa.

## Ferramentas definidas
Python: validação e processamento implementados com biblioteca padrão. SQLite: execução local sem servidor. pandas: planejado para tratamentos maiores. PostgreSQL: destino analítico planejado, com script de carga do piloto disponível. Metabase: exploração e dashboards planejados. Git/GitHub: histórico e documentação.

## Arquivos
- docs/metodologia.md: escopo e indicadores.
- docs/modelo-de-dados.md: entidades, chaves e dicionário do piloto.
- docs/dashboard.md: especificação do painel.
- docs/proximos-passos.md: sequência de execução e critérios de conclusão.
- data/piloto.json: fatos preliminares por episódio.
- data/fontes.json: catálogo de evidências.
- recuperacao/: implementação e comandos Python.
- sql/piloto.sql: tabelas e visões da camada piloto.
- tests/test_pipeline.py: testes de integridade e geração.
- docs/execucao.md: comandos, artefatos e limitações da implementação.

## Primeiro exercício
Escolher uma companhia do piloto; confirmar CNPJ na CVM, listagem na data do pedido e número do processo. Conferir o evento no documento original, registrar precisão das datas e atualizar a evidência. Só então marcar o episódio como elegível.

## Principal cuidado
Encerramento jurídico, continuidade operacional, nova recuperação e retorno do acionista são resultados diferentes. O projeto não atribui causalidade nem presume quitação integral da dívida após o encerramento.
