"""SILVER: tipa, valida e deduplica as séries."""
import os

from pyspark.sql import SparkSession, functions as F

from utils import BASE_PATH


def transform(df):
    return (
        df.withColumn("data", F.to_date("data", "dd/MM/yyyy"))
        .withColumn("valor", F.col("valor").cast("double"))
        .filter(F.col("data").isNotNull() & F.col("valor").isNotNull())
        .dropDuplicates(["serie", "data"])
        .withColumn("ano", F.year("data"))
        .select("serie", "data", "valor", "ano", "ingested_at")
    )


def main() -> None:
    spark = SparkSession.builder.appName("silver_bcb").getOrCreate()
    raw = spark.read.option("multiLine", True).json(os.path.join(BASE_PATH, "bronze", "*.json"))
    silver = transform(raw)
    (
        silver.write.mode("overwrite")
        .partitionBy("ano")
        .parquet(os.path.join(BASE_PATH, "silver", "series"))
    )
    print(f"[silver] {silver.count()} registros")
    spark.stop()


if __name__ == "__main__":
    main()
