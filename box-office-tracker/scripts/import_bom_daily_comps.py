#!/usr/bin/env python3
"""Backfill historical comp opening Fri/Sat/Sun grosses from Box Office Mojo.

This script is intentionally narrow: it reads data/historical-comps.csv,
keeps post-COVID rows only, resolves each movie to its Box Office Mojo domestic
release page, and writes opening Friday/Saturday/Sunday daily grosses.
"""

from __future__ import annotations

import csv
import html
import re
import time
import unicodedata
import urllib.parse
import urllib.request
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parents[1]
COMPS_CSV = BASE_DIR / "data" / "historical-comps.csv"
BOM = "https://www.boxofficemojo.com"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36"


TITLE_OVERRIDES = {
    "Guardians of the Galaxy Vol 3": "Guardians of the Galaxy Vol. 3",
    "Venom: Let There be Carnage": "Venom: Let There Be Carnage",
    "Demon Slayer -Kimetsu no Yaiba- The Movie: Infinity Castle": (
        "Demon Slayer: Kimetsu no Yaiba Infinity Castle"
    ),
}


SUPPLEMENTAL_COMPS = [
    {
        "movie": "Cruella",
        "release_year": "2021",
        "genre": "comedy",
        "audience_type": "female_skewing",
        "franchise_type": "remake",
        "rating": "PG-13",
        "preview_date": "2021/05/27",
        "notes": "Post-COVID supplemental female-skewing Disney remake comp.",
    },
    {
        "movie": "The Boss Baby: Family Business",
        "release_year": "2021",
        "genre": "animation",
        "audience_type": "broad_family",
        "franchise_type": "franchise",
        "rating": "PG",
        "preview_date": "2021/07/01",
        "notes": "Post-COVID supplemental family animation sequel comp.",
    },
    {
        "movie": "The Forever Purge",
        "release_year": "2021",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "franchise",
        "rating": "R",
        "preview_date": "2021/07/01",
        "notes": "Post-COVID supplemental horror franchise comp.",
    },
    {
        "movie": "Escape Room: Tournament of Champions",
        "release_year": "2021",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "franchise",
        "rating": "PG-13",
        "preview_date": "2021/07/15",
        "notes": "Post-COVID supplemental horror/thriller sequel comp.",
    },
    {
        "movie": "Old",
        "release_year": "2021",
        "genre": "horror",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "PG-13",
        "preview_date": "2021/07/22",
        "notes": "Post-COVID supplemental adult-skewing horror/thriller comp.",
    },
    {
        "movie": "Jungle Cruise",
        "release_year": "2021",
        "genre": "adventure",
        "audience_type": "broad_family",
        "franchise_type": "brand_adaptation",
        "rating": "PG-13",
        "preview_date": "2021/07/29",
        "notes": "Post-COVID supplemental family adventure brand comp.",
    },
    {
        "movie": "Free Guy",
        "release_year": "2021",
        "genre": "comedy",
        "audience_type": "broad_family",
        "franchise_type": "original",
        "rating": "PG-13",
        "preview_date": "2021/08/12",
        "notes": "Post-COVID supplemental original comedy/adventure breakout comp.",
    },
    {
        "movie": "Don't Breathe 2",
        "release_year": "2021",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "franchise",
        "rating": "R",
        "preview_date": "2021/08/12",
        "notes": "Post-COVID supplemental horror sequel comp.",
    },
    {
        "movie": "Candyman",
        "release_year": "2021",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "legacy_sequel",
        "rating": "R",
        "preview_date": "2021/08/26",
        "notes": "Post-COVID supplemental horror legacy sequel comp.",
    },
    {
        "movie": "West Side Story",
        "release_year": "2021",
        "genre": "musical",
        "audience_type": "broad_adult",
        "franchise_type": "remake",
        "rating": "PG-13",
        "preview_date": "2021/12/09",
        "notes": "Post-COVID supplemental adult musical remake comp.",
    },
    {
        "movie": "Dog",
        "release_year": "2022",
        "genre": "comedy",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "PG-13",
        "preview_date": "2022/02/17",
        "notes": "Post-COVID supplemental adult comedy/drama comp.",
    },
    {
        "movie": "Jackass Forever",
        "release_year": "2022",
        "genre": "comedy",
        "audience_type": "fan_driven",
        "franchise_type": "franchise",
        "rating": "R",
        "preview_date": "2022/02/03",
        "notes": "Post-COVID supplemental fan-driven comedy franchise comp.",
    },
    {
        "movie": "The Northman",
        "release_year": "2022",
        "genre": "action",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2022/04/21",
        "notes": "Post-COVID supplemental adult action original comp.",
    },
    {
        "movie": "The Bad Guys",
        "release_year": "2022",
        "genre": "animation",
        "audience_type": "broad_family",
        "franchise_type": "original",
        "rating": "PG",
        "preview_date": "2022/04/21",
        "notes": "Post-COVID supplemental family animation original comp.",
    },
    {
        "movie": "Downton Abbey: A New Era",
        "release_year": "2022",
        "genre": "drama",
        "audience_type": "broad_legacy",
        "franchise_type": "legacy_sequel",
        "rating": "PG",
        "preview_date": "2022/05/19",
        "notes": "Post-COVID supplemental adult legacy sequel comp.",
    },
    {
        "movie": "The Bob's Burgers Movie",
        "release_year": "2022",
        "genre": "animation",
        "audience_type": "fan_driven",
        "franchise_type": "brand_adaptation",
        "rating": "PG-13",
        "preview_date": "2022/05/26",
        "notes": "Post-COVID supplemental fan-driven animated brand comp.",
    },
    {
        "movie": "Where the Crawdads Sing",
        "release_year": "2022",
        "genre": "drama",
        "audience_type": "female_skewing",
        "franchise_type": "book_adaptation",
        "rating": "PG-13",
        "preview_date": "2022/07/14",
        "notes": "Post-COVID supplemental female-skewing book adaptation comp.",
    },
    {
        "movie": "DC League of Super-Pets",
        "release_year": "2022",
        "genre": "animation",
        "audience_type": "broad_family",
        "franchise_type": "franchise",
        "rating": "PG",
        "preview_date": "2022/07/28",
        "notes": "Post-COVID supplemental family animation franchise comp.",
    },
    {
        "movie": "Dragon Ball Super: Super Hero",
        "release_year": "2022",
        "genre": "animation",
        "audience_type": "fan_driven",
        "franchise_type": "franchise",
        "rating": "PG-13",
        "preview_date": "2022/08/18",
        "notes": "Post-COVID supplemental anime fan-driven franchise comp.",
    },
    {
        "movie": "Barbarian",
        "release_year": "2022",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2022/09/08",
        "notes": "Post-COVID supplemental original horror comp.",
    },
    {
        "movie": "The Menu",
        "release_year": "2022",
        "genre": "thriller",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2022/11/17",
        "notes": "Post-COVID supplemental adult thriller comp.",
    },
    {
        "movie": "Plane",
        "release_year": "2023",
        "genre": "action",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2023/01/12",
        "notes": "Post-COVID supplemental adult action original comp.",
    },
    {
        "movie": "Cocaine Bear",
        "release_year": "2023",
        "genre": "comedy",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2023/02/23",
        "notes": "Post-COVID supplemental adult comedy/thriller comp.",
    },
    {
        "movie": "65",
        "release_year": "2023",
        "genre": "sci_fi",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "PG-13",
        "preview_date": "2023/03/09",
        "notes": "Post-COVID supplemental adult sci-fi original comp.",
    },
    {
        "movie": "Elemental",
        "release_year": "2023",
        "genre": "animation",
        "audience_type": "broad_family",
        "franchise_type": "original",
        "rating": "PG",
        "preview_date": "2023/06/15",
        "notes": "Post-COVID supplemental family animation original comp.",
    },
    {
        "movie": "Talk to Me",
        "release_year": "2023",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2023/07/27",
        "notes": "Post-COVID supplemental original horror comp.",
    },
    {
        "movie": "The Creator",
        "release_year": "2023",
        "genre": "sci_fi",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "PG-13",
        "preview_date": "2023/09/28",
        "notes": "Post-COVID supplemental original sci-fi comp.",
    },
    {
        "movie": "Trolls Band Together",
        "release_year": "2023",
        "genre": "animation",
        "audience_type": "broad_family",
        "franchise_type": "franchise",
        "rating": "PG",
        "preview_date": "2023/11/16",
        "notes": "Post-COVID supplemental family animation franchise comp.",
    },
    {
        "movie": "Thanksgiving",
        "release_year": "2023",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2023/11/16",
        "notes": "Post-COVID supplemental original horror comp.",
    },
    {
        "movie": "Godzilla Minus One",
        "release_year": "2023",
        "genre": "sci_fi",
        "audience_type": "fan_driven",
        "franchise_type": "franchise",
        "rating": "PG-13",
        "preview_date": "2023/11/30",
        "notes": "Post-COVID supplemental fan-driven sci-fi franchise comp.",
    },
    {
        "movie": "Renaissance: A Film by Beyonce",
        "release_year": "2023",
        "genre": "concert_event",
        "audience_type": "fan_driven",
        "franchise_type": "event",
        "rating": "NR",
        "preview_date": "2023/11/30",
        "notes": "Post-COVID supplemental fan-driven concert-event comp.",
    },
    {
        "movie": "Migration",
        "release_year": "2023",
        "genre": "animation",
        "audience_type": "broad_family",
        "franchise_type": "original",
        "rating": "PG",
        "preview_date": "2023/12/21",
        "notes": "Post-COVID supplemental family animation original comp.",
    },
    {
        "movie": "Anyone But You",
        "release_year": "2023",
        "genre": "comedy",
        "audience_type": "female_skewing",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2023/12/21",
        "notes": "Post-COVID supplemental female-skewing romantic comedy comp.",
    },
    {
        "movie": "The First Omen",
        "release_year": "2024",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "franchise",
        "rating": "R",
        "preview_date": "2024/04/04",
        "notes": "Post-COVID supplemental horror franchise comp.",
    },
    {
        "movie": "The Ministry of Ungentlemanly Warfare",
        "release_year": "2024",
        "genre": "action",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2024/04/18",
        "notes": "Post-COVID supplemental adult action comp.",
    },
    {
        "movie": "Unsung Hero",
        "release_year": "2024",
        "genre": "drama",
        "audience_type": "broad_family",
        "franchise_type": "original",
        "rating": "PG",
        "preview_date": "2024/04/25",
        "notes": "Post-COVID supplemental faith-family drama comp.",
    },
    {
        "movie": "Tarot",
        "release_year": "2024",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "original",
        "rating": "PG-13",
        "preview_date": "2024/05/02",
        "notes": "Post-COVID supplemental original horror comp.",
    },
    {
        "movie": "The Watchers",
        "release_year": "2024",
        "genre": "horror",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "PG-13",
        "preview_date": "2024/06/06",
        "notes": "Post-COVID supplemental adult horror/thriller comp.",
    },
    {
        "movie": "Fly Me to the Moon",
        "release_year": "2024",
        "genre": "comedy",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "PG-13",
        "preview_date": "2024/07/11",
        "notes": "Post-COVID supplemental adult romantic comedy/drama comp.",
    },
    {
        "movie": "Harold and the Purple Crayon",
        "release_year": "2024",
        "genre": "comedy",
        "audience_type": "broad_family",
        "franchise_type": "book_adaptation",
        "rating": "PG",
        "preview_date": "2024/08/01",
        "notes": "Post-COVID supplemental family book-adaptation comp.",
    },
    {
        "movie": "Heretic",
        "release_year": "2024",
        "genre": "horror",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2024/11/07",
        "notes": "Post-COVID supplemental adult horror comp.",
    },
    {
        "movie": "The Best Christmas Pageant Ever",
        "release_year": "2024",
        "genre": "comedy",
        "audience_type": "broad_family",
        "franchise_type": "book_adaptation",
        "rating": "PG",
        "preview_date": "2024/11/07",
        "notes": "Post-COVID supplemental family holiday book-adaptation comp.",
    },
    {
        "movie": "Kraven the Hunter",
        "release_year": "2024",
        "genre": "superhero",
        "audience_type": "young_male",
        "franchise_type": "franchise",
        "rating": "R",
        "preview_date": "2024/12/12",
        "notes": "Post-COVID supplemental young-male superhero underperformance comp.",
    },
]


SUPPLEMENTAL_COMPS.extend([
    {
        "movie": "Sinners",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/04/17",
        "notes": "Post-COVID supplemental adult original horror breakout comp.",
    },
    {
        "movie": "Mission: Impossible - The Final Reckoning",
        "release_year": "2025",
        "genre": "action",
        "audience_type": "broad_adult",
        "franchise_type": "franchise",
        "rating": "PG-13",
        "preview_date": "2025/05/22",
        "notes": "Post-COVID supplemental adult action franchise comp.",
    },
    {
        "movie": "F1: The Movie",
        "release_year": "2025",
        "genre": "action",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "PG-13",
        "preview_date": "2025/06/26",
        "notes": "Post-COVID supplemental adult sports-action original comp.",
    },
    {
        "movie": "The Conjuring: Last Rites",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "franchise",
        "rating": "R",
        "preview_date": "2025/09/04",
        "notes": "Post-COVID supplemental horror franchise comp.",
    },
    {
        "movie": "Weapons",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/08/07",
        "notes": "Post-COVID supplemental adult original horror breakout comp.",
    },
    {
        "movie": "Final Destination: Bloodlines",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "franchise",
        "rating": "R",
        "preview_date": "2025/05/15",
        "notes": "Post-COVID supplemental horror franchise comp.",
    },
    {
        "movie": "Dog Man",
        "release_year": "2025",
        "genre": "animation",
        "audience_type": "broad_family",
        "franchise_type": "book_adaptation",
        "rating": "PG",
        "preview_date": "2025/01/30",
        "notes": "Post-COVID supplemental family animation book-adaptation comp.",
    },
    {
        "movie": "Freakier Friday",
        "release_year": "2025",
        "genre": "comedy",
        "audience_type": "broad_legacy",
        "franchise_type": "legacy_sequel",
        "rating": "PG",
        "preview_date": "2025/08/07",
        "notes": "Post-COVID supplemental legacy comedy sequel comp.",
    },
    {
        "movie": "Predator: Badlands",
        "release_year": "2025",
        "genre": "sci_fi",
        "audience_type": "young_male",
        "franchise_type": "franchise",
        "rating": "PG-13",
        "preview_date": "2025/11/06",
        "notes": "Post-COVID supplemental young-male sci-fi franchise comp.",
    },
    {
        "movie": "The Bad Guys 2",
        "release_year": "2025",
        "genre": "animation",
        "audience_type": "broad_family",
        "franchise_type": "franchise",
        "rating": "PG",
        "preview_date": "2025/07/31",
        "notes": "Post-COVID supplemental family animation franchise comp.",
    },
    {
        "movie": "Black Phone 2",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "franchise",
        "rating": "R",
        "preview_date": "2025/10/16",
        "notes": "Post-COVID supplemental horror franchise comp.",
    },
    {
        "movie": "Tron: Ares",
        "release_year": "2025",
        "genre": "sci_fi",
        "audience_type": "fan_driven",
        "franchise_type": "franchise",
        "rating": "PG-13",
        "preview_date": "2025/10/09",
        "notes": "Post-COVID supplemental fan-driven sci-fi franchise comp.",
    },
    {
        "movie": "Elio",
        "release_year": "2025",
        "genre": "animation",
        "audience_type": "broad_family",
        "franchise_type": "original",
        "rating": "PG",
        "preview_date": "2025/06/19",
        "notes": "Post-COVID supplemental family animation original comp.",
    },
    {
        "movie": "One Battle After Another",
        "release_year": "2025",
        "genre": "action",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/09/25",
        "notes": "Post-COVID supplemental adult action original comp.",
    },
    {
        "movie": "28 Years Later",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "broad_adult",
        "franchise_type": "franchise",
        "rating": "R",
        "preview_date": "2025/06/19",
        "notes": "Post-COVID supplemental adult horror franchise comp.",
    },
    {
        "movie": "The Accountant 2",
        "release_year": "2025",
        "genre": "action",
        "audience_type": "broad_adult",
        "franchise_type": "franchise",
        "rating": "R",
        "preview_date": "2025/04/24",
        "notes": "Post-COVID supplemental adult action sequel comp.",
    },
    {
        "movie": "Now You See Me: Now You Don't",
        "release_year": "2025",
        "genre": "thriller",
        "audience_type": "broad_adult",
        "franchise_type": "franchise",
        "rating": "PG-13",
        "preview_date": "2025/11/13",
        "notes": "Post-COVID supplemental adult thriller franchise comp.",
    },
    {
        "movie": "Karate Kid: Legends",
        "release_year": "2025",
        "genre": "action",
        "audience_type": "broad_family",
        "franchise_type": "legacy_sequel",
        "rating": "PG-13",
        "preview_date": "2025/05/29",
        "notes": "Post-COVID supplemental family legacy action sequel comp.",
    },
    {
        "movie": "One of Them Days",
        "release_year": "2025",
        "genre": "comedy",
        "audience_type": "female_skewing",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/01/16",
        "notes": "Post-COVID supplemental female-skewing comedy comp.",
    },
    {
        "movie": "Mickey 17",
        "release_year": "2025",
        "genre": "sci_fi",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/03/06",
        "notes": "Post-COVID supplemental adult sci-fi original comp.",
    },
    {
        "movie": "Paddington in Peru",
        "release_year": "2025",
        "genre": "comedy",
        "audience_type": "broad_family",
        "franchise_type": "franchise",
        "rating": "PG",
        "preview_date": "2025/02/13",
        "notes": "Post-COVID supplemental family comedy franchise comp.",
    },
    {
        "movie": "Downton Abbey: The Grand Finale",
        "release_year": "2025",
        "genre": "drama",
        "audience_type": "broad_legacy",
        "franchise_type": "legacy_sequel",
        "rating": "PG",
        "preview_date": "2025/09/11",
        "notes": "Post-COVID supplemental adult legacy sequel comp.",
    },
    {
        "movie": "The Amateur",
        "release_year": "2025",
        "genre": "action",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "PG-13",
        "preview_date": "2025/04/10",
        "notes": "Post-COVID supplemental adult action original comp.",
    },
    {
        "movie": "The Monkey",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/02/20",
        "notes": "Post-COVID supplemental original horror comp.",
    },
    {
        "movie": "A Working Man",
        "release_year": "2025",
        "genre": "action",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/03/27",
        "notes": "Post-COVID supplemental adult action original comp.",
    },
    {
        "movie": "Materialists",
        "release_year": "2025",
        "genre": "comedy",
        "audience_type": "female_skewing",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/06/12",
        "notes": "Post-COVID supplemental female-skewing romantic comedy/drama comp.",
    },
    {
        "movie": "The Long Walk",
        "release_year": "2025",
        "genre": "thriller",
        "audience_type": "broad_adult",
        "franchise_type": "book_adaptation",
        "rating": "R",
        "preview_date": "2025/09/11",
        "notes": "Post-COVID supplemental adult thriller book-adaptation comp.",
    },
    {
        "movie": "I Know What You Did Last Summer",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "legacy_sequel",
        "rating": "R",
        "preview_date": "2025/07/17",
        "notes": "Post-COVID supplemental horror legacy sequel comp.",
    },
    {
        "movie": "Heart Eyes",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/02/06",
        "notes": "Post-COVID supplemental adult horror/comedy comp.",
    },
    {
        "movie": "Flight Risk",
        "release_year": "2025",
        "genre": "thriller",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/01/23",
        "notes": "Post-COVID supplemental adult thriller comp.",
    },
    {
        "movie": "Warfare",
        "release_year": "2025",
        "genre": "action",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/04/10",
        "notes": "Post-COVID supplemental adult war/action comp.",
    },
    {
        "movie": "Him",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/09/18",
        "notes": "Post-COVID supplemental adult horror comp.",
    },
    {
        "movie": "M3GAN 2.0",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "franchise",
        "rating": "PG-13",
        "preview_date": "2025/06/26",
        "notes": "Post-COVID supplemental horror franchise comp.",
    },
    {
        "movie": "The Woman in the Yard",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "original",
        "rating": "PG-13",
        "preview_date": "2025/03/27",
        "notes": "Post-COVID supplemental original horror comp.",
    },
    {
        "movie": "Nobody 2",
        "release_year": "2025",
        "genre": "action",
        "audience_type": "broad_adult",
        "franchise_type": "franchise",
        "rating": "R",
        "preview_date": "2025/08/14",
        "notes": "Post-COVID supplemental adult action franchise comp.",
    },
    {
        "movie": "Black Bag",
        "release_year": "2025",
        "genre": "thriller",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/03/13",
        "notes": "Post-COVID supplemental adult thriller comp.",
    },
    {
        "movie": "Death of a Unicorn",
        "release_year": "2025",
        "genre": "comedy",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/03/27",
        "notes": "Post-COVID supplemental adult comedy/horror comp.",
    },
    {
        "movie": "Last Breath",
        "release_year": "2025",
        "genre": "thriller",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "PG-13",
        "preview_date": "2025/02/27",
        "notes": "Post-COVID supplemental adult survival thriller comp.",
    },
    {
        "movie": "Companion",
        "release_year": "2025",
        "genre": "thriller",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/01/30",
        "notes": "Post-COVID supplemental adult thriller comp.",
    },
    {
        "movie": "Wolf Man",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "remake",
        "rating": "R",
        "preview_date": "2025/01/16",
        "notes": "Post-COVID supplemental horror remake comp.",
    },
    {
        "movie": "Until Dawn",
        "release_year": "2025",
        "genre": "horror",
        "audience_type": "horror_fan",
        "franchise_type": "video_game",
        "rating": "R",
        "preview_date": "2025/04/24",
        "notes": "Post-COVID supplemental video-game horror comp.",
    },
    {
        "movie": "Novocaine",
        "release_year": "2025",
        "genre": "action",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "R",
        "preview_date": "2025/03/13",
        "notes": "Post-COVID supplemental adult action/comedy comp.",
    },
    {
        "movie": "Drop",
        "release_year": "2025",
        "genre": "thriller",
        "audience_type": "broad_adult",
        "franchise_type": "original",
        "rating": "PG-13",
        "preview_date": "2025/04/10",
        "notes": "Post-COVID supplemental adult thriller comp.",
    },
    {
        "movie": "The Naked Gun",
        "release_year": "2025",
        "genre": "comedy",
        "audience_type": "broad_legacy",
        "franchise_type": "legacy_sequel",
        "rating": "PG-13",
        "preview_date": "2025/07/31",
        "notes": "Post-COVID supplemental legacy comedy sequel comp.",
    },
    {
        "movie": "The King of Kings",
        "release_year": "2025",
        "genre": "animation",
        "audience_type": "broad_family",
        "franchise_type": "brand_adaptation",
        "rating": "PG",
        "preview_date": "2025/04/10",
        "notes": "Post-COVID supplemental faith-family animation comp.",
    },
])


def norm(value: str) -> str:
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    return re.sub(r"[^a-z0-9]+", "", ascii_value.lower())


def money_to_m(value: str) -> float:
    return int(value.replace("$", "").replace(",", "")) / 1_000_000


def fetch(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=25) as resp:
        return resp.read().decode("utf-8", errors="replace")


def numbers_preview_gross_m(movie: str, preview_date: str) -> float:
    page = fetch(f"https://www.the-numbers.com/box-office-chart/daily/{preview_date}")
    target = norm(movie)
    for row in re.findall(r"<td colspan=2>Previews</td>.*?</tr>", page, flags=re.S):
        name_match = re.search(r'<a href="[^"]+">([^<]+)</a>', row)
        gross_match = re.search(r'<td class="data[^"]*">(\$[\d,]+)</td>', row)
        if not name_match or not gross_match:
            continue
        if norm(html.unescape(name_match.group(1))) == target:
            return money_to_m(gross_match.group(1))
    raise ValueError(f"Could not find The Numbers preview gross for {movie} on {preview_date}")


def add_supplemental_rows(rows: list[dict[str, str]], fields: list[str]) -> list[dict[str, str]]:
    existing_names = {norm(row.get("movie", "")) for row in rows}
    merged = list(rows)
    for comp in SUPPLEMENTAL_COMPS:
        if norm(comp["movie"]) in existing_names:
            continue
        preview_m = numbers_preview_gross_m(comp["movie"], comp["preview_date"])
        row = {field: "" for field in fields}
        for key, value in comp.items():
            if key != "preview_date":
                row[key] = value
        row["thursday_preview_m"] = fmt(preview_m)
        row["source_url"] = f"https://www.the-numbers.com/box-office-chart/daily/{comp['preview_date']}"
        merged.append(row)
        existing_names.add(norm(comp["movie"]))
    return merged


def title_candidates(title: str) -> list[tuple[str, str, int | None]]:
    query = urllib.parse.quote_plus(TITLE_OVERRIDES.get(title, title))
    page = fetch(f"{BOM}/search/?q={query}")
    candidates = []
    for href, name, year in re.findall(
        r'<a class="a-size-medium a-link-normal a-text-bold" href="([^"]+)">([^<]+)</a>'
        r'<span class="a-color-secondary"> \((\d{4})\)</span>',
        page,
    ):
        candidates.append((html.unescape(name), href.split("?")[0], int(year)))
    if candidates:
        return candidates
    for href, name in re.findall(
        r'<a class="a-size-medium a-link-normal a-text-bold" href="([^"]+)">([^<]+)</a>',
        page,
    ):
        candidates.append((html.unescape(name), href.split("?")[0], None))
    return candidates


def choose_title(title: str, year: int, candidates: list[tuple[str, str, int | None]]) -> str | None:
    target = norm(TITLE_OVERRIDES.get(title, title))
    if not candidates:
        return None
    for name, href, candidate_year in candidates:
        if norm(name) == target and candidate_year in (year, year - 1):
            return href

    target_tokens = set(re.findall(r"[a-z0-9]+", TITLE_OVERRIDES.get(title, title).lower()))
    best = None
    best_score = -1
    for name, href, candidate_year in candidates:
        tokens = set(re.findall(r"[a-z0-9]+", name.lower()))
        score = len(target_tokens & tokens) - len(tokens - target_tokens) * 0.25
        if candidate_year == year:
            score += 3
        elif candidate_year == year - 1:
            score += 1.5
        if score > best_score:
            best = href
            best_score = score
    return best


def domestic_release_path(title_href: str) -> str | None:
    page = fetch(BOM + title_href)
    match = re.search(r'Domestic Opening</span><span><a class="a-link-normal" href="([^"]+)"', page)
    if match:
        return match.group(1).split("?")[0].replace("/weekend", "")

    match = re.search(
        r'<tr><td><a class="a-link-normal" href="([^"]+)">Domestic</a></td>',
        page,
    )
    if match:
        return match.group(1).split("?")[0]
    return None


def first_opening_weekend_daily(release_path: str) -> tuple[float, float, float]:
    page = fetch(f"{BOM}{release_path}?sortDir=asc")
    daily = {}
    found_friday = False
    for row in re.findall(r"<tr[^>]*>(.*?)</tr>", page, flags=re.S):
        cells = re.findall(r"<td[^>]*>(.*?)</td>", row, flags=re.S)
        if len(cells) < 4:
            continue
        clean = [
            re.sub(r"<[^>]+>", "", cell).strip()
            for cell in cells
        ]
        dow = html.unescape(clean[1])
        gross = html.unescape(clean[3])
        if dow == "Friday" and not found_friday:
            found_friday = True
        if not found_friday:
            continue
        if dow in ("Friday", "Saturday", "Sunday") and dow not in daily:
            daily[dow] = money_to_m(gross)
        if all(day in daily for day in ("Friday", "Saturday", "Sunday")):
            return daily["Friday"], daily["Saturday"], daily["Sunday"]
    raise ValueError(f"Could not parse opening Fri/Sat/Sun from {release_path}")


def fmt(value: float) -> str:
    text = f"{value:.6f}".rstrip("0").rstrip(".")
    return text if text else "0"


def main() -> None:
    with COMPS_CSV.open(newline="") as f:
        rows = list(csv.DictReader(f))
        fields = list(rows[0].keys())
    rows = add_supplemental_rows(rows, fields)

    out = []
    failures = []
    for row in rows:
        year = int(row.get("release_year") or 0)
        if year < 2021:
            continue

        title = row["movie"]
        if all((row.get(key) or "").strip() for key in [
            "thursday_preview_m",
            "opening_weekend_m",
            "friday_m",
            "saturday_m",
            "sunday_m",
            "daily_source_url",
        ]):
            out.append(row)
            continue

        try:
            candidates = title_candidates(title)
            title_href = choose_title(title, year, candidates)
            if not title_href:
                raise ValueError("no title match")
            release_path = domestic_release_path(title_href)
            if not release_path:
                raise ValueError("no domestic release page")
            friday, saturday, sunday = first_opening_weekend_daily(release_path)
            opening = float(row["opening_weekend_m"]) if row.get("opening_weekend_m") else 0.0
            daily_opening = friday + saturday + sunday
            if opening and abs(daily_opening - opening) / opening > 0.08:
                raise ValueError(
                    f"daily sum mismatch {daily_opening:.3f} vs opening {opening:.3f}"
                )
            if not opening:
                row["opening_weekend_m"] = fmt(daily_opening)
            row["friday_m"] = fmt(friday)
            row["saturday_m"] = fmt(saturday)
            row["sunday_m"] = fmt(sunday)
            row["daily_source_url"] = BOM + release_path
            row["daily_notes"] = (
                "Box Office Mojo Domestic Daily opening Friday/Saturday/Sunday; "
                "Friday includes previews under public daily convention."
            )
            out.append(row)
            print(f"ok {title}: {friday:.3f}/{saturday:.3f}/{sunday:.3f}")
        except Exception as exc:
            failures.append(f"{title}: {exc}")
            print(f"FAIL {title}: {exc}")
        time.sleep(0.25)

    if failures:
        raise SystemExit("\n".join(failures))

    with COMPS_CSV.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, lineterminator="\n")
        writer.writeheader()
        writer.writerows(out)


if __name__ == "__main__":
    main()
