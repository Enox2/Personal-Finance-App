import argparse
import re
from pathlib import Path

import pandas as pd


CATEGORY_RULES: list[tuple[str, str]] = [
    (r"LIDL|BIEDRONKA|NETTO|ZABKA|ROSSMANN|DM PTAK|ALDI|CARREFOUR|AUCHAN", "groceries"),
    (r"UBER|BOLT|FREE NOW", "transport"),
    (r"APPLE\\.COM|GOOGLE|YOUTUBE|DISNEY|NETFLIX|SPOTIFY|PLAYSTATION|STEAM", "subscriptions"),
    (r"ALLEGRO|AMAZON|EBAY", "shopping"),
    (r"MCDONALDS|PIZZ|KFC|BURGER|CAFE|BISTRO|RESTAUR", "eating_out"),
    (r"ORANGE|T-MOBILE|PLAY|PLUS", "mobile"),
    (r"MENNICA|AUTOMAT|BILET|KOMUNIKACYJNEGO", "public_transport"),
    (r"MUZEUM|TEATR|CINEMA|KINO", "entertainment"),
    (r"ZARA|H&M|RESERVED|CROPP|SINSAY|PULL&BEAR", "clothing"),
    (r"PAYPAL", "payments"),
]


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


def normalize_merchant(value: str) -> str:
    if not value:
        return ""
    if "ZABKA" in value.upper():
        return "ZABKA"

    if "BIEDRONKA" in value.upper():
        return "BIEDRONKA"

    if "LIDL" in value.upper():
        return "LIDL"

    if "NETTO" in value.upper():
        return "NETTO"

    if "MCDONALDS" in value.upper():
        return "MCDONALDS"

    if "BOLT" in value.upper():
        return "BOLT"
    normalized = re.sub(r"\s+", " ", value).strip()
    # normalized = re.sub(r"\s+", " ", value.upper()).strip()
    # normalized = re.sub(r"\s+[Kk]\.\d+", "", normalized)
    # normalized = re.sub(r"\b\d{2,}[/-]\d{2,}\b", "", normalized)
    # normalized = re.sub(r"[\/#-]\s*\d+", "", normalized)
    # normalized = re.sub(r"\b(?:ID|NR|NO|REF|TRX|TX|POS)\s*\d+\b", "", normalized)
    # normalized = re.sub(r"\bZ[0-9A-Z]{3,6}\b", "", normalized)
    # normalized = re.sub(r"\b[A-Z]{1,3}\d{6,}\b", "", normalized)
    # normalized = re.sub(r"\b[A-Z0-9]{8,}\b", "", normalized)
    # normalized = re.sub(r"\b\d{3,}\b", "", normalized)
    # normalized = re.sub(r"\b(SPOTIFY)(?:\s+\1)+\b", r"\1", normalized)
    # normalized = re.sub(r"\s+\d{1,2}$", "", normalized)
    # normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()


def suggest_category(merchant: str, description: str) -> str | None:
    text = f"{merchant} {description}".strip()
    for pattern, category in CATEGORY_RULES:
        if re.search(pattern, text, flags=re.IGNORECASE):
            return category
    return "Uncategorized"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--input",
        default="data/uploads/Zestawienie operacji za 21.02.2025 - 21.02.2026.csv",
    )
    parser.add_argument("--output", default="data/etl_merchant_suggestions_new1.csv")
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parents[1]
    csv_path = Path(args.input)
    if not csv_path.is_absolute():
        csv_path = base_dir / csv_path

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = base_dir / output_path

    df = pd.read_csv(csv_path, encoding="cp1250")
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

    df["merchant_raw"] = df["transaction_description"].apply(extract_merchant)
    df["merchant_key"] = df["merchant_raw"].apply(normalize_merchant)
    df["suggested_category"] = df.apply(
        lambda row: suggest_category(row["merchant_key"], row["transaction_description"]),
        axis=1,
    )

    result = []

    for item in df["transaction_type"]:
        if item not in result:
            result.append(item)

    print(result)

    summary = (
        df[df["merchant_key"] != ""]
        .groupby(["merchant_key", "suggested_category"], as_index=False)
        .size()
        .sort_values("size", ascending=False)
    )

    output_path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_path, index=False)

    if summary.empty:
        debug_path = output_path.with_name("etl_merchant_debug.csv")
        df[["transaction_description", "merchant_raw", "merchant_key"]].head(50).to_csv(
            debug_path, index=False
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
