import re

from pandas import DataFrame

from src.domains.etl.models import CategoryRule


def categorise_transactions(df: DataFrame, rules: list[CategoryRule]) -> DataFrame:
    if "category" not in df.columns:
        df["category"] = None

    if "merchant" not in df.columns:
        df["merchant"] = ""

    rules_sorted = sorted(rules, key=lambda rule: rule.priority, reverse=True)

    for rule in rules_sorted:
        try:
            compiled = re.compile(rule.pattern, flags=re.IGNORECASE)
        except re.error:
            continue

        merchant_series = df["merchant"].fillna("")
        description_series = df["transaction_description"].fillna("")
        matches = (
            merchant_series.str.contains(compiled, na=False)
            | description_series.str.contains(compiled, na=False)
        )
        uncategorised_mask = df["category"].isna() & matches
        df.loc[uncategorised_mask, "category"] = rule.category

    return df

