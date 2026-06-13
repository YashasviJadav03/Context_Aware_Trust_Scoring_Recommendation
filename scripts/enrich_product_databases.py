"""Merge product metadata into SQLite databases used by the app and API."""

import os
import sqlite3
import sys

import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
METADATA_PATH = os.path.join(ROOT, "demo", "product_metadata.csv")
TRUST_SCORES_PATH = os.path.join(ROOT, "data", "processed", "product_trust_scores.csv")
PROCESSED_DB = os.path.join(ROOT, "data", "processed", "reviews.db")
API_DB = os.path.join(ROOT, "database", "reviews.db")


def enrich_processed_db(metadata: pd.DataFrame) -> None:
    """Replace products table in data/processed/reviews.db with scores + metadata."""
    scores = pd.read_csv(TRUST_SCORES_PATH)
    products = scores.merge(metadata, on="product_id", how="left")
    products["product_name"] = products["product_name"].fillna("Unknown Product")
    products["category"] = products["category"].fillna("Fashion")
    products["brand"] = products["brand"].fillna("Unknown Brand")
    products["price"] = products["price"].fillna("N/A")
    products["image_url"] = products["image_url"].fillna("")
    products["description"] = products["description"].fillna("")

    temp_db = PROCESSED_DB + ".new"
    if os.path.exists(temp_db):
        os.remove(temp_db)

    conn = sqlite3.connect(temp_db)
    products.to_sql("products", conn, if_exists="replace", index=False)

    # Copy reviews table from existing DB if present
    if os.path.exists(PROCESSED_DB):
        src = sqlite3.connect(f"file:{PROCESSED_DB}?mode=ro", uri=True)
        try:
            reviews = pd.read_sql("SELECT * FROM reviews", src)
            reviews.to_sql("reviews", conn, if_exists="replace", index=False)
        except Exception:
            pass
        src.close()

    conn.close()
    os.replace(temp_db, PROCESSED_DB)
    print(f"Rebuilt products table in {PROCESSED_DB} ({len(products):,} rows)")


def rebuild_api_db(metadata: pd.DataFrame) -> None:
    sys.path.append(ROOT)
    from database.db_manager import DatabaseManager

    scores = pd.read_csv(TRUST_SCORES_PATH)
    products = scores.merge(metadata, on="product_id", how="left")
    products["product_name"] = products["product_name"].fillna("Unknown Product")
    products["category"] = products["category"].fillna("Fashion")
    products["brand"] = products["brand"].fillna("Unknown Brand")
    products["price"] = products["price"].fillna("N/A")
    products["image_url"] = products["image_url"].fillna("")
    products["description"] = products["description"].fillna("")

    db = DatabaseManager(db_type="sqlite", db_path="database/reviews.db")
    db.initialize_schema(os.path.join(ROOT, "database", "schema.sql"))
    db.conn.execute("DELETE FROM reviews")
    db.conn.execute("DELETE FROM products")
    db.conn.commit()
    db.bulk_insert_products(products)

    reviews_path = os.path.join(ROOT, "data", "processed", "reviews_sample.csv")
    if os.path.exists(reviews_path):
        reviews = pd.read_csv(reviews_path)
        if "predicted_trust_score" not in reviews.columns:
            reviews["predicted_trust_score"] = reviews["trust_score"]
        db.bulk_insert_reviews(reviews)

    db.close()
    print(f"Rebuilt {API_DB} with {len(products):,} products")


def report(conn: sqlite3.Connection, label: str) -> None:
    total = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
    named = conn.execute(
        "SELECT COUNT(*) FROM products WHERE product_name IS NOT NULL "
        "AND product_name != '' AND product_name NOT LIKE 'Amazon Fashion Product %' "
        "AND product_name != 'Unknown Product'"
    ).fetchone()[0]
    imaged = conn.execute(
        "SELECT COUNT(*) FROM products WHERE image_url IS NOT NULL AND image_url != ''"
    ).fetchone()[0]
    print(f"{label}: {total:,} products, {named:,} with names, {imaged:,} with images")


def main() -> None:
    os.chdir(ROOT)

    if not os.path.exists(METADATA_PATH):
        print(f"Missing metadata file: {METADATA_PATH}")
        print("Run: python scripts/extract_product_metadata.py")
        sys.exit(1)

    metadata = pd.read_csv(METADATA_PATH).drop_duplicates(subset="product_id", keep="first")
    print(f"Loaded {len(metadata):,} metadata rows")

    if os.path.exists(PROCESSED_DB):
        try:
            enrich_processed_db(metadata)
            report(sqlite3.connect(PROCESSED_DB), "data/processed/reviews.db")
        except OSError as exc:
            print(f"Skipped {PROCESSED_DB} (in use): {exc}")
            print("App will merge demo/product_metadata.csv at runtime.")

    print("Rebuilding database/reviews.db...")
    rebuild_api_db(metadata)
    report(sqlite3.connect(API_DB), "database/reviews.db")
    print("Done.")


if __name__ == "__main__":
    main()
