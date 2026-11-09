# Sequência de execução

## Avanço técnico — versão 0.2

A camada piloto tem importação validada em SQLite, exportações CSV, relatório de qualidade, leitor local de cadastro CVM para sugestões e script PostgreSQL. Os testes automatizados cobrem integridade, datas, fontes, repetição da carga e preservação de desconhecidos. Consulte `execucao.md`. As etapas de auditoria abaixo continuam pendentes; o esquema normalizado e os indicadores jurídicos ainda não foram implementados. PostgreSQL e Metabase não foram executados.

1. Normalizar cinco companhias usando cadastro CVM; preservar arquivos de origem e data da extração.
2. Confirmar listagem na data de cada pedido, incluindo nomes e códigos históricos.
3. Obter números de processo e documentos judiciais dos episódios; conferir decisões e recursos até o corte.
4. Atualizar Viver, Eternit e Renova com datas e desfechos precisos; reconstruir os episódios da Oi sem atribuir status atual por notícia antiga; verificar eventos posteriores da Lupatech.
5. Ampliar busca de forma sistemática em CVM, B3 e documentos históricos. Registrar a estratégia de inclusão e os casos excluídos, evitando selecionar apenas exemplos famosos de saída.
6. Implementar importação e validação com Python/pandas e modelo PostgreSQL; só após confirmar o esquema mínimo com o piloto.
7. Criar consultas de indicadores com denominadores explícitos e amostras manuais de conferência.
8. Instalar Metabase e montar painel, primeiro com indicadores de cobertura.
9. Publicar README, metodologia, dados permitidos e evidências no GitHub. Documentar lacunas e não declarar censo se a cobertura histórica não estiver demonstrada.

## Critério de conclusão da versão analítica
Identidades e elegibilidade auditadas; nenhum resultado sem evidência; denominadores reproduzíveis; nulos explícitos; painel coerente com consultas; limitações visíveis; nenhuma credencial no pacote. A pesquisa 0.1 conclui apenas o piloto e o desenho; as ferramentas 0.2 acrescentam execução local e qualidade, sem concluir a versão analítica.
