"""GOLD: tabela mensal com IPCA, Selic, dólar médio, IPCA 12m e juro real."""
import os

from pyspark.sql import SparkSession, Window, functions as F

from utils import BASE_PATH


def build_gold(silver):
    monthly = (
        silver.withColumn("mes", F.trunc("data", "month"))
        .groupBy("mes")
        .pivot("serie", ["ipca", "selic", "usd"])
        .agg(F.avg("valor"))
        .withColumnRenamed("ipca", "ipca_mensal")
        .withColumnRenamed("selic", "selic_mensal")
        .withColumnRenamed("usd", "usd_medio")
        .dropna(subset=["ipca_mensal", "selic_mensal"])
    )

    w12 = Window.orderBy("mes").rowsBetween(-11, 0)
    return (
        monthly.withColumn("n_meses", F.count("*").over(w12))
        .withColumn(
            "ipca_12m",
            F.when(
                F.col("n_meses") == 12,
                (F.exp(F.sum(F.log1p(F.col("ipca_mensal") / 100)).over(w12)) - 1) * 100,
            ),
        )
        .withColumn(
            "juro_real_mensal",
            ((1 + F.col("selic_mensal") / 100) / (1 + F.col("ipca_mensal") / 100) - 1) * 100,
        )
        .drop("n_meses")
        .orderBy("mes")
    )


def main() -> None:
    spark = SparkSession.builder.appName("gold_bcb").getOrCreate()
    silver = spark.read.parquet(os.path.join(BASE_PATH, "silver", "series"))
    gold = build_gold(silver)
    gold.write.mode("overwrite").parquet(os.path.join(BASE_PATH, "gold", "indicadores_mensais"))
    gold.show(12, truncate=False)
    spark.stop()


if __name__ == "__main__":
    main()
