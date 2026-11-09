# Dados externos e resolução de pendências — versão 0.3

Em 09/11/2026 foram coletadas onze fontes públicas adicionais: cadastro CVM, documentos das companhias, relatórios de administradores judiciais e consulta do TJSP. As cópias locais ficam em `data/raw/coletas/`; cada versão é identificada pelo SHA-256. O registro de obtenção está em `data/coletas.json` e o log cumulativo local em `data/raw/coletas/manifesto.jsonl`.

## Resultado incorporado

| Pendência por episódio | Antes | Depois |
|---|---:|---:|
| CNPJ ausente | 6 | 0 |
| Número de processo ausente | 5 | 0 |
| Pedido sem data completa | 3 | 0 |
| Status no corte não auditado | 6 | 6 |

Foram registradas 23 evidências por campo: 21 incorporadas e duas alternativas pendentes. O histórico anterior está em `data/historico/piloto_v0_1.json`. As diferenças estão em `data/alteracoes.json`. O preenchimento não confirma listagem histórica, trânsito ou situação atual.

## O que foi conferido

| Episódio | Dados acrescentados e fonte |
|---|---|
| Todos | CNPJs revisados por código CVM e denominação no [cadastro oficial](https://dados.cvm.gov.br/dados/CIA_ABERTA/CAD/DADOS/cad_cia_aberta.csv), fonte S10 |
| Oi, segundo pedido | Pedido em 01/03/2023 no [documento da companhia](https://api.mziq.com/mzfilemanager/v2/d/6aebbd40-9373-4b5a-8461-9839bd41cbbb/489b8f34-44e7-2b13-47b4-f729bc694efe?origin=1), S11; processo após migração no aviso de 18/09/2023 do [administrador judicial](https://recuperacaojudicialoi.com.br/inicio-2/principal-2/), S12 |
| Viver | Pedido em 16/09/2016, deferimento em 29/09/2016 e processo no [relatório da administradora](https://midia.kpmg.com.br/digital-marketing/pdfs/grupo-viver/relatorio-circunstanciado-viver.pdf), fls. 68242, S13 |
| Lupatech | Número da recuperação identificado na [consulta pública TJSP](https://esaj.tjsp.jus.br/cpopg/show.do?processo.codigo=2S000GWQT0000&processo.foro=1), S16; data de distribuição por direcionamento não substitui a data do pedido |
| Eternit | Processo e encerramento em 09/08/2024 na [sentença disponibilizada no RI](https://ri.eternit.com.br/Download.aspx?Arquivo=RMHUj4vQ%2FQny4yFWyx8AVA%3D%3D), S18; conferência adicional no fato relevante S17 |
| Renova | Pedido e deferimento em 16/10/2019 e processo no [cronograma da administradora](https://api.mziq.com/mzfilemanager/v2/d/4208c3ab-ee07-4344-b70f-f03d3fecbcc3/320fc30f-879c-0c90-5065-5aba9ca1fe78?origin=1), fls. 61416, S19; encerramento reportado em 12/02/2025 no [comunicado da companhia](https://api.mziq.com/mzfilemanager/v2/d/4208c3ab-ee07-4344-b70f-f03d3fecbcc3/402188d8-0adf-8ee8-7bef-2bc759b05104?origin=1), S20 |

As localizações, os valores, a precisão temporal e o hash da cópia usada estão em `data/evidencias.json`, exportados também para `outputs/evidencias.csv` e para a tabela `evidencia_campo` no banco. São conferências de campos específicos, sem certificação de auditoria jurídica completa.

## Divergência preservada: Viver

A resposta da Viver de 17/11/2021, fonte S14, reporta sentença em 02/08/2021 e informa que ainda não havia trânsito na ocasião. A apresentação de resultados de 2022, fonte S15, descreve encerramento em 17/12/2021. Podem ser marcos diferentes; isso ainda não foi demonstrado com sentença e certidão. As duas referências permanecem como `alternativa_pendente`. O campo único `encerramento` continua nulo, com precisão anual preservada.

## Repetir a coleta

Na raiz do projeto:

```sh
python3 -m recuperacao coletar S10 S11 S12 S13 S14 S15 S16 S17 S18 S19 S20
python3 -m recuperacao validar
python3 -m recuperacao gerar
python3 -m unittest discover -s tests -v
```

No Windows, use `py -3` em lugar de `python3`. A coleta precisa de internet. Cada arquivo tem limite de 25 MB e timeout de 30 segundos. Falhas são registradas e resultam em código de saída diferente de zero; as demais fontes continuam sendo coletadas. Resposta HTML no lugar de PDF é recusada.

Coletar **não atualiza os fatos automaticamente**. O comando preserva versões novas sem apagar as antigas e acrescenta entradas ao log local. `data/coletas.json` é o registro versionado das cópias efetivamente usadas nas evidências; só deve receber uma versão nova depois da conferência de seu conteúdo. Assim, uma atualização remota não muda retroativamente a origem de um campo já incorporado.

Para uma fonte nova: cadastre ID, título, URL HTTPS, escopo, consulta e formato (`csv`, `pdf` ou `html`) em `data/fontes.json`; execute `coletar ID`; confira o documento; registre a cópia usada em `coletas.json` e a evidência por campo. A consulta identifica quando o documento foi lido; a obtenção identifica quando a cópia foi baixada. Nenhuma delas substitui a data do evento.

## O que ainda falta e como resolver

1. **Listagem histórica:** localizar documentos da B3/CVM ou relatórios da época que demonstrem negociação/listagem na data de cada pedido. Registro CVM atual e ticker em documento posterior não bastam para estabelecer todo o intervalo histórico.
2. **Status no corte:** obter decisões e recursos posteriores, conferindo eficácia e eventual suspensão até 09/11/2026. A sentença antiga não define sozinha a situação no corte.
3. **Marcos da Viver:** obter sentença, eventuais decisões posteriores e certidão para distinguir agosto e dezembro de 2021.
4. **Sentenças originais e recursos:** complementar os encerramentos conhecidos apenas por divulgação corporativa. Uma consulta indicando “extinto” não estabelece automaticamente encerramento por cumprimento.
5. **Campos herdados:** conferir as datas do piloto que ainda não têm evidência específica; o relatório lista esses campos por episódio.
6. **Acompanhamento:** pesquisar eventos posteriores e documentar a janela de 24 meses antes de calcular recorrência ou continuidade.

Enquanto essas verificações não estiverem concluídas, o projeto mantém os indicadores jurídicos bloqueados e os estados da camada piloto como não auditados.
