# Pipeline Medalhão com Dados do Banco Central

Pipeline de dados ponta a ponta que coleta séries econômicas da API pública do Banco Central (SGS),
organiza em camadas **bronze → silver → gold** com PySpark e orquestra com Airflow.
A tabela final responde: *como estão inflação, juros e dólar mês a mês, e qual o juro real?*

## Problema
Séries econômicas vêm em formatos diferentes (datas em `dd/MM/yyyy`, valores como texto, frequências distintas).
Para analisar juro real é preciso padronizar e consolidar tudo em uma única tabela mensal confiável.

## Arquitetura

```
API BCB (SGS)
   │  requests (janelas de 5 anos)
   ▼
BRONZE  → JSON bruto + data de ingestão (nada é alterado)
   │  PySpark: tipagem, datas, dedupe, validações
   ▼
SILVER  → séries limpas, tipadas, particionadas por ano
   │  PySpark: agregação mensal, janelas, IPCA 12m, juro real
   ▼
GOLD    → tabela mensal pronta para BI / análise
```

Orquestração: DAG do Airflow mensal (`dags/bcb_pipeline_dag.py`).

## Séries utilizadas
| Código SGS | Série |
|---|---|
| 433 | IPCA – variação mensal (%) |
| 4390 | Selic acumulada no mês (%) |
| 1 | Dólar (venda) – diário |

## Como rodar localmente
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

python src/bronze_ingest.py      # baixa JSON bruto
python src/silver_transform.py   # limpa e tipa
python src/gold_aggregate.py     # gera tabela mensal
pytest                           # testes
```
Saídas em `data/bronze`, `data/silver` e `data/gold`.

### No Databricks
Importe os 3 scripts como notebooks, troque `BASE_PATH` por `/Volumes/...` (ou DBFS)
e, se quiser, troque `parquet` por `delta` no `write`.

## Decisões técnicas
- **Bronze imutável**: guarda o dado como veio, permitindo reprocessar sem chamar a API de novo.
- **Janelas de 5 anos** na coleta, pois a API limita o período em séries diárias.
- **Dedupe e validações** na silver (datas inválidas, valores nulos).
- **Juro real** calculado como `((1 + selic) / (1 + ipca) - 1)`, não pela subtração simples.

## Resultados
> Adicione aqui um print da tabela gold ou de um gráfico (Power BI, Databricks SQL ou matplotlib).

## Aprendizados e próximos passos
- Trocar parquet por Delta e usar `MERGE` para cargas incrementais
- Adicionar checks de qualidade (Great Expectations)
- Publicar um dashboard em Power BI sobre a camada gold
