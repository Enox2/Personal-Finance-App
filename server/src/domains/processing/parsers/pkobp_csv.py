from pathlib import Path
import re

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

    df["transaction_date"] = pd.to_datetime(df["transaction_date"]).dt.date
    df["value_date"] = pd.to_datetime(df["value_date"]).dt.date
    df["merchant"] = df["transaction_description"].apply(extract_merchant)

    return df


def extract_merchant(description: str) -> str:
    match = re.search(r"Lokalizacja:\s*Adres:\s*(.+?)\s*Miasto:", description)
    if match:
        return match.group(1).strip()

    match = re.search(r"Nazwa odbiorcy:\s*(.+?)(?:\s*Adres odbiorcy:|$)", description)
    if match:
        return match.group(1).strip()

    match = re.search(r"Lokalizacja:\s*Adres:\s*(\S+)", description)
    if match:
        return match.group(1).strip()

    return ""

