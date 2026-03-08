from dataclasses import dataclass

import pandas as pd

from src.domains.processing.parsers.categoriser import categorise_transactions


@dataclass
class Rule:
    pattern: str
    category: str
    priority: int = 0


def main() -> None:
    df = pd.DataFrame(
        [
            {"merchant": "LIDL NARAMOWICKA", "transaction_description": "Lokalizacja: Adres: LIDL NARAMOWICKA"},
            {"merchant": "APPLE.COM/BILL", "transaction_description": "Lokalizacja: Adres: APPLE.COM/BILL"},
            {"merchant": "UBER *EATS", "transaction_description": "Lokalizacja: Adres: UBER *EATS"},
        ]
    )

    rules = [
        Rule(pattern=r"LIDL|BIEDRONKA|NETTO", category="groceries", priority=10),
        Rule(pattern=r"APPLE\.COM|YOUTUBE", category="subscriptions", priority=5),
        Rule(pattern=r"UBER", category="transport", priority=1),
    ]

    df = categorise_transactions(df, rules)
    print(df[["merchant", "category"]])


if __name__ == "__main__":
    main()
