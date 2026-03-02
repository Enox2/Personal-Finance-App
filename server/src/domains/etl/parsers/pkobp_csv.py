from pathlib import Path

import pandas as pd
from pandas import DataFrame

from src.domains.csv.models import CSVFile


def prepare_dataframe(file_model: CSVFile | None) -> DataFrame:
    if file_model is None:
        raise ValueError("CSV file not found")

    df = pd.read_csv(Path(str(file_model.path)), encoding="cp1250")
    unnamed_cols = [col for col in df.columns if col.startswith("Unnamed")]

    df["Opis transakcji"] = df[["Opis transakcji"] + unnamed_cols].astype(str).agg(
        " ".join, axis=1
    )

    df = df.drop(columns=[*unnamed_cols, "Saldo po transakcji"])

    df.columns = [
        "transaction_date",
        "value_date",
        "transaction_type",
        "amount",
        "currency",
        "transaction_description",
    ]

    examples = (
        df.groupby("transaction_type", as_index=False)
        .first()[["transaction_type", "transaction_description", "amount"]]
    )

    for _, row in examples.iterrows():
        print(
            f"{row['transaction_type']}: {row['amount']}, {row['transaction_description']}\n"
        )

    return df

