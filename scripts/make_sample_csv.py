"""Generate a fake hotel Sample CSV with Faker. No real data is involved.

Usage: uv run python scripts/make_sample_csv.py [output.csv] [rows]
"""

import random
import sys
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
from faker import Faker


def make_sample(rows: int = 500, seed: int = 42) -> pd.DataFrame:
    fake = Faker()
    Faker.seed(seed)
    rng = random.Random(seed)
    countries = [fake.country() for _ in range(8)]
    room_types = ["single", "double", "suite", "family"]
    # Mostly shared labels, plus one-off corporate names (Rare categories).
    accounts = ["walk-in", "online", "agency"]
    one_offs = [fake.company() for _ in range(max(3, rows // 50))]
    records = []
    for i in range(rows):
        room = rng.choices(room_types, weights=[4, 8, 2, 3])[0]
        nights = rng.randint(1, 14)
        base = {"single": 80, "double": 120, "suite": 260, "family": 170}[room]
        check_in = date(2024, 1, 1) + timedelta(days=rng.randint(0, 600))
        price = round(base * nights * rng.uniform(0.85, 1.2), 2)
        records.append(
            {
                "booking_id": f"BK-{100000 + i}",
                "guest_name": fake.name(),
                "email": fake.email(),
                "phone": fake.numerify("+49 ### #######"),
                "address": fake.street_address(),
                "card_number": fake.credit_card_number("visa16"),
                "check_in": check_in.isoformat(),
                "check_out": (check_in + timedelta(days=nights)).isoformat(),
                "nights": nights,
                "adults": rng.randint(1, 4),
                "account": rng.choice(accounts),
                "room_type": room,
                "country": rng.choice(countries),
                "total_price": price,
                "rating": rng.choice([None, round(rng.uniform(1, 5), 1)]),
                "guest_notes": f"{fake.sentence(nb_words=10)} {fake.sentence(nb_words=6)}",
                "breakfast_included": rng.choice(["yes", "no"]),
            }
        )
    df = pd.DataFrame(records)
    for i, name in enumerate(one_offs):
        df.loc[i * 7 % rows, "account"] = name
    return df


if __name__ == "__main__":
    out = Path(sys.argv[1] if len(sys.argv) > 1 else "hotel_sample.csv")
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 500
    sample = make_sample(n)
    sample.to_csv(out, index=False)
    # Same rows as a European Excel export: `;`, decimal comma, cp1252.
    messy = out.with_name(f"{out.stem}_messy{out.suffix}")
    european = sample.copy()
    for col in ("check_in", "check_out"):
        european[col] = pd.to_datetime(european[col]).dt.strftime("%d.%m.%Y")
    european.to_csv(messy, index=False, sep=";", decimal=",", encoding="cp1252", errors="replace")
    print(f"Wrote {n} fake rows to {out} and {messy}")
