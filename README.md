# Dashboard Porsche com Agente de IA — Desafio DIO

Projeto completo para tratar a base sanitizada de vendas Porsche, explorar os indicadores em um dashboard interativo e gerar insights executivos com um agente de IA.

## Visão geral

O projeto usa os campos `*Sanitized` da planilha como fonte confiável e mantém os campos originais para auditoria. O dashboard mostra:

- valor total registrado, ticket médio, registros e entregas;
- receita e volume por família de modelo;
- evolução anual e mensal somente com datas válidas;
- distribuição por estado, forma de pagamento e status;
- alertas de qualidade de dados;
- insights automáticos, com uso opcional da API da OpenAI.

> A base possui 100 registros. Há 24 datas marcadas como `INVALID`; elas não entram nas análises temporais. O valor total registrado inclui todos os status, inclusive cancelamentos.

## Estrutura

```text
.
├── app.py                         # Dashboard Streamlit
├── assets/
│   └── dashboard-reference.png   # Referência visual
├── canva/
│   └── presentation-brief.md     # Brief pronto para o Canva/ChatGPT
├── data/
│   └── porsche_sales_sanitized.xlsx
├── outputs/
│   └── .gitkeep
├── src/
│   ├── __init__.py
│   ├── ai_agent.py               # Insights e integração opcional com IA
│   └── data_processor.py          # Validação, limpeza e agregações
├── tests/
│   └── test_data_processor.py
├── .env.example
├── .gitignore
├── LICENSE
└── requirements.txt
```

## Como executar

Requer Python 3.10 ou superior.

```bash
python -m venv .venv
source .venv/bin/activate        # Linux/macOS
# .venv\\Scripts\\activate       # Windows
pip install -r requirements.txt
streamlit run app.py
```

O agente funciona em modo local sem chave de API. Para habilitar uma síntese generativa adicional:

```bash
cp .env.example .env
```

Depois, preencha `OPENAI_API_KEY` no arquivo `.env`. Nunca publique a sua chave.

## Tratamento aplicado

1. Leitura da aba `Sanitized`.
2. Seleção dos campos tratados de data, modelo, ano, preço, quilometragem, pagamento, cidade, estado e status.
3. Conversão de preço, quilometragem e ano para tipos numéricos.
4. Conversão de datas inválidas para valores ausentes, sem inventar datas.
5. Normalização do nome dos vendedores para apresentação.
6. Criação da família do modelo (`911`, `718`, `Taycan`, `Panamera`, `Cayenne` e `Macan`).
7. Criação de métricas e alertas auditáveis.

## Indicadores conferidos

| Indicador | Resultado |
|---|---:|
| Registros | 100 |
| Valor total registrado | USD 12.827.800,50 |
| Ticket médio | USD 128.278,01 |
| Datas válidas | 76 |
| Datas inválidas | 24 |
| Entregues | 41 |
| Cancelados | 7 |
| Família líder em receita | 911 |

## Canva

O arquivo [`canva/presentation-brief.md`](canva/presentation-brief.md) contém a estrutura de seis páginas pronta para gerar o material no Canva para ChatGPT, seguindo o visual escuro da referência.

## Testes

```bash
pytest -q
```

## Tecnologias

Python, Pandas, Streamlit, Plotly, OpenAI API (opcional), Canva e GitHub.

## Autor

Luis Henrique Gonçalves de Sá — projeto desenvolvido para o desafio da DIO.

