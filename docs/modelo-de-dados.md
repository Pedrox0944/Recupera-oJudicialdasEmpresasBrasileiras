# Modelo de dados proposto

| Entidade | Chave | Conteúdo |
|---|---|---|
| empresa | empresa_id; CNPJ único | Razão social, nomes históricos e setor com fonte |
| listagem | listagem_id | Empresa, bolsa, início e fim de cada intervalo |
| processo | processo_id; número CNJ | Tribunal, vara, tipo e grupo econômico |
| participacao | participacao_id | Empresa e processo; vínculo único para deduplicação |
| evento | evento_id | Participação, tipo, data, precisão e eficácia da decisão |
| fonte | fonte_id | URL, título, localização, consulta e eventual cópia autorizada |
| evidencia | evidencia_id | Campo ou evento, fonte, resumo e nível de revisão |
| observacao_posterior | observacao_id | Horizonte, continuidade operacional e eventos posteriores |

Não usar ticker como chave. Manter CNPJ como texto com 14 dígitos. Mudanças de razão social preservam identidade quando o CNPJ é o mesmo. CNPJs sucessores exigem análise documentada.

## Dicionário do piloto
- id: identificador provisório do registro, não chave jurídica.
- empresa: nome da companhia; normalização cadastral pendente.
- episodio: ordem provisória dos episódios identificados, sujeita a revisão histórica.
- pedido/deferimento/encerramento: data completa ISO ou nulo.
- ano_pedido/ano_encerramento: ano quando sustentado por evidência; não preencher dia ou mês fictícios.
- mes_pedido: mês conhecido sem dia, quando disponível.
- processo: número CNJ quando transcrito da fonte, caso contrário nulo.
- evento: fato histórico localizado; não representa status atual.
- fontes: referências ao catálogo fontes.json.
- cnpj: nulo até normalização cadastral.
- status_no_corte: não auditado nesta versão.
- elegibilidade: pendente de confirmação histórica nesta versão.
- observacao: limites e pendências específicas.
- uso: piloto não inferencial; impedir publicação como resultado geral.

## Verificações da futura base
Chaves únicas; fontes existentes; CNPJ válido; datas consistentes com o evento; listagem cobrindo o pedido; datas posteriores ao corte excluídas do retrato; duração nunca negativa; recursos sem perda de histórico. Precisão anual não entra no cálculo em dias.

## Camada piloto implementada — versão 0.3

`fonte`, `episodio_piloto`, `episodio_fonte` e `evidencia_campo` sustentam a execução local e a exportação PostgreSQL. A tabela de evidências preserva campo, valor, localização, consulta, precisão, situação e SHA-256 da cópia usada. Alternativas pendentes não substituem o valor do piloto. O esquema normalizado proposto acima continua planejado.
