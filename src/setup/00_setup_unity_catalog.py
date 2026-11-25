# Databricks notebook source
# MAGIC %md
# MAGIC # 00 - Setup da Fundação no Unity Catalog (Comex Lakehouse)
# MAGIC
# MAGIC Este notebook provisiona de forma **idempotente** toda a fundação de governança
# MAGIC no **Unity Catalog** para o projeto **Comex Lakehouse (MDIC / Comex Stat)**:
# MAGIC
# MAGIC - Namespace de 3 níveis: `<catalog>.<schema>.<object>`
# MAGIC - Schemas da Arquitetura Medallion:
# MAGIC   - `<prefix>_raw`: aterrissagem de arquivos brutos (Unity Catalog Volumes)
# MAGIC   - `<prefix>_bronze`: tabelas Delta brutas com metadados de ingestão
# MAGIC   - `<prefix>_silver`: dados limpos, tipados, deduplicados e enriquecidos
# MAGIC   - `<prefix>_gold`: tabelas analíticas e Star Schema prontas para BI
# MAGIC - Managed Volume `/Volumes/<catalog>/<prefix>_raw/<volume_name>` com subpastas
# MAGIC   para `exportacoes/`, `importacoes/` e `dimensoes/`.

# COMMAND ----------

import re

IDENTIFIER_PATTERN = re.compile(r"^[a-zA-Z_][a-zA-Z0-9_]{0,63}$")


def validate_identifier(value: str, field_name: str) -> str:
    """Valida identificadores SQL do Unity Catalog contra uma allow-list estrita."""
    cleaned = value.strip()
    if not IDENTIFIER_PATTERN.match(cleaned):
        raise ValueError(
            f"Parâmetro inválido para '{field_name}': use apenas letras, números e '_' "
            f"(iniciando por letra ou '_', até 64 caracteres)."
        )
    return cleaned


dbutils.widgets.text("catalog_name", "workspace", "Catálogo (Unity Catalog)")
dbutils.widgets.text("schema_prefix", "comex_dev", "Prefixo dos Schemas")
dbutils.widgets.text("volume_name", "mdic_landing", "Nome do Volume Raw")

CATALOG_NAME = validate_identifier(dbutils.widgets.get("catalog_name"), "catalog_name")
SCHEMA_PREFIX = validate_identifier(dbutils.widgets.get("schema_prefix"), "schema_prefix")
VOLUME_NAME = validate_identifier(dbutils.widgets.get("volume_name"), "volume_name")

print(f"Catálogo alvo : {CATALOG_NAME}")
print(f"Prefixo schema: {SCHEMA_PREFIX}")
print(f"Volume landing: {VOLUME_NAME}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 1. Criação dos Schemas Medallion (Idempotente)

# COMMAND ----------

MEDALLION_SCHEMAS = {
    "raw": "Camada Raw / Landing: armazena arquivos brutos do MDIC (Comex Stat) em Volumes governados.",
    "bronze": "Camada Bronze: tabelas Delta brutas ingeridas incrementalmente com auditoria (_metadata).",
    "silver": "Camada Silver: dados padronizados, deduplicados, validados e enriquecidos com dimensões.",
    "gold": "Camada Gold: tabelas analíticas agregadas e modelagem dimensional para Databricks SQL e BI.",
}

spark.sql("USE CATALOG IDENTIFIER(:catalog)", args={"catalog": CATALOG_NAME})

for layer, description in MEDALLION_SCHEMAS.items():
    schema_name = validate_identifier(f"{SCHEMA_PREFIX}_{layer}", f"schema_{layer}")
    full_schema = f"{CATALOG_NAME}.{schema_name}"
    spark.sql(
        "CREATE SCHEMA IF NOT EXISTS IDENTIFIER(:full_schema) COMMENT :comment",
        args={"full_schema": full_schema, "comment": description},
    )
    print(f"[OK] Schema garantido: {full_schema}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 2. Criação do Managed Volume para Landing dos CSVs do MDIC

# COMMAND ----------

RAW_SCHEMA = f"{SCHEMA_PREFIX}_raw"
FULL_VOLUME = f"{CATALOG_NAME}.{RAW_SCHEMA}.{VOLUME_NAME}"

spark.sql(
    "CREATE VOLUME IF NOT EXISTS IDENTIFIER(:full_volume) COMMENT :comment",
    args={
        "full_volume": FULL_VOLUME,
        "comment": "Managed Volume para pouso dos arquivos CSV brutos do MDIC (EXP, IMP e Dimensões).",
    },
)
print(f"[OK] Managed Volume garantido: {FULL_VOLUME}")

BASE_VOLUME_PATH = f"/Volumes/{CATALOG_NAME}/{RAW_SCHEMA}/{VOLUME_NAME}"
LANDING_FOLDERS = ("exportacoes", "importacoes", "dimensoes", "_checkpoints")

for folder in LANDING_FOLDERS:
    target_path = f"{BASE_VOLUME_PATH}/{folder}"
    dbutils.fs.mkdirs(target_path)
    print(f"[OK] Diretório de landing pronto: {target_path}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## 3. Validação da Fundação Provisionada

# COMMAND ----------

display(
    spark.sql(
        "SHOW SCHEMAS IN IDENTIFIER(:catalog) LIKE :pattern",
        args={"catalog": CATALOG_NAME, "pattern": f"{SCHEMA_PREFIX}_*"},
    )
)

display(
    spark.sql(
        "SHOW VOLUMES IN IDENTIFIER(:raw_schema)",
        args={"raw_schema": f"{CATALOG_NAME}.{RAW_SCHEMA}"},
    )
)
