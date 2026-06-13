"""Extract product names and images from Amazon 2018 metadata for trust-scored products."""

import ast
import gzip
import json
import os
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
META_PATH = os.path.join(ROOT, "data", "raw", "meta_AMAZON_FASHION.json.gz")
TRUST_SCORES_PATH = os.path.join(ROOT, "data", "processed", "product_trust_scores.csv")
OUTPUT_PATH = os.path.join(ROOT, "demo", "product_metadata.csv")
META_URL = (
    "https://mcauleylab.ucsd.edu:8443/public_datasets/data/amazon_v2/metaFiles/"
    "meta_AMAZON_FASHION.json.gz"
)


def open_meta_stream(path: str):
    """Yield parsed metadata records from gzip (single or double-compressed JSONL)."""
    with gzip.open(path, "rb") as handle:
        payload = handle.read()

    try:
        inner = gzip.decompress(payload)
    except OSError:
        inner = payload

    text = inner.decode("utf-8", errors="replace")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            yield json.loads(line)
        except json.JSONDecodeError:
            yield ast.literal_eval(line)


def get_image_url(record: dict) -> str:
    """Pick the best available image URL from metadata fields."""
    image = record.get("image")
    if isinstance(image, list) and image:
        return str(image[0])
    if isinstance(image, str) and image:
        return image

    for key in ("imageURLHighRes", "imageURL"):
        value = record.get(key)
        if isinstance(value, list) and value:
            return str(value[0])
        if isinstance(value, str) and value:
            return value

    im_url = record.get("imUrl")
    if isinstance(im_url, str) and im_url:
        return im_url
    return ""


def get_category(record: dict) -> str:
    if record.get("main_cat"):
        return str(record["main_cat"])
    categories = record.get("category") or record.get("categories")
    if isinstance(categories, list) and categories:
        return str(categories[-1])
    return "Fashion"


def get_price(record: dict) -> str:
    price = record.get("price")
    if price is None:
        return "N/A"
    return str(price)


def get_product_id(record: dict) -> str:
    return str(record.get("parent_asin") or record.get("asin") or "")


def extract_metadata(product_ids: set) -> pd.DataFrame:
    """Stream metadata and collect rows for requested product IDs."""
    rows = []
    found = 0

    for record in open_meta_stream(META_PATH):
        product_id = get_product_id(record)
        if product_id not in product_ids:
            continue

        rows.append(
            {
                "product_id": product_id,
                "product_name": record.get("title", "Unknown Product") or "Unknown Product",
                "category": get_category(record),
                "brand": record.get("brand", "Unknown Brand") or "Unknown Brand",
                "price": get_price(record),
                "image_url": get_image_url(record),
                "description": record.get("description", "") or "",
            }
        )
        found += 1
        if found >= len(product_ids):
            break

    return pd.DataFrame(rows)


def main() -> None:
    os.chdir(ROOT)

    if not os.path.exists(META_PATH):
        print(f"Metadata file not found: {META_PATH}")
        print(f"Download from: {META_URL}")
        sys.exit(1)

    print("Loading product IDs from trust scores...")
    trust_scores = pd.read_csv(TRUST_SCORES_PATH, usecols=["product_id"])
    product_ids = set(trust_scores["product_id"].astype(str))
    print(f"  {len(product_ids):,} products to match")

    print("Extracting metadata (streaming)...")
    metadata = extract_metadata(product_ids)
    metadata = metadata.drop_duplicates(subset="product_id", keep="first")
    print(f"  Matched {len(metadata):,} unique products in metadata file")

    missing_ids = product_ids - set(metadata["product_id"])
    if missing_ids:
        print(f"  {len(missing_ids):,} products missing from metadata (using placeholders)")
        placeholders = pd.DataFrame(
            {
                "product_id": list(missing_ids),
                "product_name": [f"Amazon Fashion Product {pid}" for pid in missing_ids],
                "category": "Fashion",
                "brand": "Unknown Brand",
                "price": "N/A",
                "image_url": "",
                "description": "",
            }
        )
        metadata = pd.concat([metadata, placeholders], ignore_index=True)

    metadata = metadata.sort_values("product_id").reset_index(drop=True)
    os.makedirs(os.path.dirname(OUTPUT_PATH), exist_ok=True)
    metadata.to_csv(OUTPUT_PATH, index=False)

    placeholder_count = metadata["product_name"].str.startswith("Amazon Fashion Product").sum()
    with_image = (metadata["image_url"].astype(str).str.len() > 0).sum()
    print(f"\nSaved {len(metadata):,} rows to {OUTPUT_PATH}")
    print(f"  Real names: {len(metadata) - placeholder_count:,}")
    print(f"  With images: {with_image:,}")


if __name__ == "__main__":
    main()
