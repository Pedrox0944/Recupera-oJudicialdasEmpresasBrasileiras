# Andamento — 09/11/2026

## Entrega técnica 0.2

- Validação estrutural e carga reproduzível do piloto em SQLite.
- CSVs de episódios, fontes, vínculos e pendências.
- Relatório de cobertura e manifesto com hashes dos dados de origem.
- Exportação transacional para o esquema `pesquisa_piloto` no PostgreSQL.
- Leitura de cadastro CVM local e sugestões de correspondência por nome.
- Testes automatizados de integridade e geração.

O piloto permanece com cinco nomes de companhias e seis episódios candidatos. Existem seis episódios sem CNPJ normalizado, cinco sem processo identificado e três sem data completa do pedido. Todos os status e a elegibilidade continuam não auditados. Nenhuma taxa de sucesso foi produzida.

## Primeira coleta de cadastro

Foi preservado o [CSV oficial da CVM](https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv) em `data/raw/cad_cia_aberta.csv`, com URL, horário de obtenção, tamanho e SHA-256 em `data/raw/cad_cia_aberta.origem.json`.

SHA-256 da cópia obtida:

```text
4364c52c1102d94db8e99ecc67a038350e5936c9aa298802fcebb76349a58121
```

A comparação por nome normalizado gerou candidatos para Eternit, Lupatech, Renova e Viver. A Oi não teve correspondência exata; isso não implica ausência no cadastro. É necessário investigar nomes históricos e sufixos da denominação. Os resultados locais estão em `outputs/candidatos_cvm.csv`. A base original não recebeu CNPJs automaticamente.

O cadastro consultado é atual. Não demonstra que a companhia estava listada na data do pedido nem valida o processo judicial. Os candidatos ainda exigem revisão documental.

## Próxima etapa de pesquisa

1. Revisar cada candidato de identidade; investigar a denominação da Oi no cadastro.
2. Registrar evidência por campo, incluindo localização no documento, precisão da data e responsável pela revisão.
3. Confirmar listagem histórica e números dos processos, começando por uma companhia.
4. Implementar a camada auditada separada da tabela de pesquisa piloto, conforme o modelo proposto.
5. Executar a carga PostgreSQL e conectar o Metabase em ambiente com essas ferramentas disponíveis.

PostgreSQL e Metabase não foram executados neste ambiente. A exportação SQL foi conferida pela geração e por testes de conteúdo, mas ainda precisa ser validada em um servidor PostgreSQL real.
