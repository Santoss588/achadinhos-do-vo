# Achadinhos do Vô — automação R$0

Base gratuita para buscar ofertas do Mercado Livre e publicar no Telegram usando GitHub Actions.

## O que esta versão faz

- Busca produtos pela API pública do Mercado Livre.
- Pesquisa vários termos.
- Filtra por desconto e preço.
- Evita repetir produtos usando `data/sent.json`.
- Monta a mensagem padrão do Achadinhos do Vô.
- Envia para um chat/canal do Telegram.
- Roda automaticamente pelo GitHub Actions.

## Importante sobre afiliados

Esta versão **não inventa link de afiliado**. O Mercado Livre orienta que o link seja gerado pelo Gerador de Links/Barra de Afiliados. Por isso, existe `data/affiliate_links.json`: coloque ali os links de afiliado reais que você gerou.

Exemplo:

```json
{
  "MLB123456789": "COLE_AQUI_O_LINK_DE_AFILIADO_GERADO_NO_MERCADO_LIVRE"
}
```

Se um produto não tiver link de afiliado cadastrado, o robô não publica esse produto.

## Configuração rápida

1. Crie um repositório no GitHub, por exemplo `achadinhos-do-vo`.
2. Suba todos os arquivos mantendo a estrutura.
3. Em `Settings → Secrets and variables → Actions`, crie:
   - `TELEGRAM_BOT_TOKEN`
   - `TELEGRAM_CHAT_ID`
4. Dê ao bot permissão para enviar mensagens no canal/grupo.
5. Cadastre links de afiliado reais em `data/affiliate_links.json`.
6. Vá em `Actions → Achadinhos do Vô → Run workflow`.

## Filtros

No arquivo `.github/workflows/automacao.yml`:

- `MIN_DISCOUNT`: desconto mínimo.
- `MAX_PRICE`: preço máximo.
- `MAX_POSTS`: máximo de posts por execução.
- `SEARCH_TERMS`: termos pesquisados.

O workflow está configurado para executar aproximadamente a cada hora.
