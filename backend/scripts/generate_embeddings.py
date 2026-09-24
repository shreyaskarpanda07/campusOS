"""
CLI script to backfill vector embeddings for opportunities and user profiles in CampusOS.

Usage:
    python scripts/generate_embeddings.py [--force] [--batch-size 50]

Options:
    --force         Regenerate embeddings for all records, even if they already have one.
    --batch-size N  Number of records to process per database commit (default: 50).
"""

import argparse
import sys
import time
from pathlib import Path

# Ensure backend root is on sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.db.session import SessionLocal
from app.models.opportunity import Opportunity
from app.models.user import User
from app.services.embedding import embedding_service


def backfill_embeddings(force: bool = False, batch_size: int = 50) -> None:
    db = SessionLocal()
    start_time = time.time()
    try:
        # ── 1. Backfill Opportunities ─────────────────────────────────────
        opp_query = db.query(Opportunity)
        if not force:
            opp_query = opp_query.filter(Opportunity.embedding.is_(None))

        opportunities = opp_query.all()
        total_opps = len(opportunities)
        print(f"[*] Found {total_opps} opportunities to {'regenerate' if force else 'backfill'} embeddings for...")

        opp_updated = 0
        for idx, opp in enumerate(opportunities, start=1):
            embedding = embedding_service.embed_opportunity(opp)
            opp.embedding = embedding
            opp_updated += 1

            if idx % batch_size == 0 or idx == total_opps:
                db.commit()
                print(f"    -> Opportunities progress: {idx}/{total_opps} processed.")

        # ── 2. Backfill Users ─────────────────────────────────────────────
        user_query = db.query(User)
        if not force:
            user_query = user_query.filter(User.embedding.is_(None))

        users = user_query.all()
        total_users = len(users)
        print(f"[*] Found {total_users} user profiles to {'regenerate' if force else 'backfill'} embeddings for...")

        user_updated = 0
        for idx, user in enumerate(users, start=1):
            embedding = embedding_service.embed_user_profile(user)
            user.embedding = embedding
            user_updated += 1

            if idx % batch_size == 0 or idx == total_users:
                db.commit()
                print(f"    -> User profiles progress: {idx}/{total_users} processed.")

        elapsed = time.time() - start_time
        print(f"[+] Successfully generated embeddings: {opp_updated} opportunities and {user_updated} users in {elapsed:.2f}s.")

    except Exception as exc:
        db.rollback()
        print(f"[!] Error generating embeddings: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description="CampusOS Vector Embedding Backfill Utility")
    parser.add_argument("--force", action="store_true", help="Force regeneration of all embeddings")
    parser.add_argument("--batch-size", type=int, default=50, help="Batch commit size (default: 50)")

    args = parser.parse_args()
    backfill_embeddings(force=args.force, batch_size=args.batch_size)


if __name__ == "__main__":
    main()
