"""Vector A — Synthetic Identity & Document Fraud Generator.

Generates realistic, seedable, reproducible batches of synthetic identity profiles
and accompanying document-metadata bundles conforming to the Frankenstein identity
schema specified in generate/identity/schema_spec.md and generate/identity/identity_schema.json.

Key Guarantees:
1. 100% Deterministic & Reproducible (same seed -> identical output).
2. PII Safety Guardrails:
   - US SSNs strictly use SSA-reserved unassigned/non-issuable area blocks (e.g. 900-999 series, 666, 000, group 00, serial 0000).
   - Phone numbers strictly use NANP reserved fictitious exchange (555-0100 to 555-0199).
   - Email addresses strictly use synthetic/test domain TLDs (.test, .example).
3. Rich Demographics & Non-Templated Diversity (500+ names, 60+ real metro clusters, diverse industries).
4. Realistic Frankenstein Divergence Physics (anchor issuance year vs DOB, CMRA addresses, burner VOIPs, forensic EXIF artifacts).
"""

from __future__ import annotations

import argparse
import datetime
import hashlib
import json
import math
import os
import random
import uuid
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple


# =============================================================================
# DEMOGRAPHIC & GEOGRAPHIC CORPUS POOLS
# =============================================================================

FIRST_NAMES_MALE = [
    "James", "John", "Robert", "Michael", "William", "David", "Richard", "Joseph",
    "Thomas", "Charles", "Christopher", "Daniel", "Matthew", "Anthony", "Donald",
    "Mark", "Paul", "Steven", "Andrew", "Kenneth", "Joshua", "Kevin", "Brian",
    "George", "Timothy", "Ronald", "Edward", "Jason", "Jeffrey", "Ryan", "Jacob",
    "Gary", "Nicholas", "Eric", "Jonathan", "Stephen", "Larry", "Justin", "Scott",
    "Brandon", "Benjamin", "Samuel", "Gregory", "Alexander", "Patrick", "Frank",
    "Raymond", "Jack", "Dennis", "Jerry", "Tyler", "Aaron", "Jose", "Henry",
    "Adam", "Douglas", "Nathan", "Peter", "Zachary", "Kyle", "Walter", "Harold",
    "Jeremy", "Ethan", "Carl", "Keith", "Roger", "Gerald", "Christian", "Terry",
    "Sean", "Arthur", "Austin", "Noah", "Lawrence", "Jesse", "Joe", "Bryan",
    "Billy", "Jordan", "Albert", "Dylan", "Bruce", "Willie", "Gabriel", "Alan",
    "Juan", "Logan", "Wayne", "Ralph", "Roy", "Eugene", "Randy", "Vincent",
    "Russell", "Louis", "Philip", "Bobby", "Johnny", "Bradley", "Alejandro", "Mateo",
    "Santiago", "Carlos", "Luis", "Diego", "Javier", "Miguel", "Rafael", "Fernando",
    "Wei", "Hao", "Ming", "Jun", "Chen", "Jian", "Bo", "Lei", "Tao", "Feng",
    "Arjun", "Rohan", "Aarav", "Vikram", "Aditya", "Siddharth", "Karan", "Rahul",
    "Tariq", "Zayd", "Omar", "Kareem", "Yusuf", "Hamza", "Bilal", "Malik",
    "Kwame", "Kofi", "Emeka", "Tunde", "Chidi", "Babajide", "Tendai", "Jabari",
    "Dmitri", "Nikolai", "Ivan", "Mikhail", "Alexei", "Sergei", "Yuri", "Pavel",
    "Kenji", "Hiroshi", "Takashi", "Daisuke", "Kazuki", "Ren", "Yuto", "Sora"
]

FIRST_NAMES_FEMALE = [
    "Mary", "Patricia", "Jennifer", "Linda", "Elizabeth", "Barbara", "Susan",
    "Jessica", "Sarah", "Karen", "Lisa", "Nancy", "Betty", "Margaret", "Sandra",
    "Ashley", "Kimberly", "Emily", "Donna", "Michelle", "Carol", "Amanda", "Dorothy",
    "Melissa", "Deborah", "Stephanie", "Rebecca", "Sharon", "Laura", "Cynthia",
    "Kathleen", "Amy", "Angela", "Shirley", "Anna", "Brenda", "Pamela", "Emma",
    "Nicole", "Helen", "Samantha", "Katherine", "Christine", "Debra", "Rachel",
    "Carolyn", "Janet", "Catherine", "Maria", "Heather", "Diane", "Ruth", "Julie",
    "Olivia", "Joyce", "Virginia", "Victoria", "Kelly", "Lauren", "Christina",
    "Joan", "Evelyn", "Judith", "Megan", "Andrea", "Cheryl", "Hannah", "Jacqueline",
    "Martha", "Gloria", "Teresa", "Ann", "Sara", "Madison", "Frances", "Kathryn",
    "Janice", "Jean", "Abigail", "Alice", "Julia", "Judy", "Sophia", "Grace",
    "Denise", "Amber", "Doris", "Marilyn", "Danielle", "Beverly", "Isabella",
    "Theresa", "Diana", "Natalie", "Brittany", "Charlotte", "Marie", "Kayla",
    "Alexis", "Lori", "Sofia", "Valentina", "Camila", "Lucia", "Elena", "Isabel",
    "Xiu", "Ying", "Mei", "Li", "Fang", "Yan", "Hui", "Jing", "Ting", "Lan",
    "Priya", "Ananya", "Diya", "Isha", "Kavya", "Pooja", "Sunita", "Deepika",
    "Fatima", "Amina", "Zainab", "Layla", "Noor", "Mariam", "Soraya", "Salma",
    "Nia", "Zuri", "Amina", "Aba", "Folami", "Amara", "Chioma", "Adanna",
    "Elena", "Natasha", "Svetlana", "Olga", "Tatiana", "Yulia", "Ksenia", "Irina",
    "Yuki", "Sakura", "Aoi", "Hina", "Yui", "Mei", "Nanami", "Rin"
]

FIRST_NAMES_NEUTRAL = [
    "Alex", "Taylor", "Jordan", "Morgan", "Casey", "Riley", "Avery", "Cameron",
    "Dakota", "Reese", "Quinn", "Skyler", "Rowan", "Kendall", "Peyton", "Finley",
    "Emerson", "River", "Hayden", "Logan", "Sawyer", "Parker", "Kai", "Eden"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson",
    "Thomas", "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson",
    "White", "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker",
    "Young", "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill",
    "Flores", "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell",
    "Mitchell", "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz",
    "Parker", "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales",
    "Murphy", "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson",
    "Bailey", "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Mendoza", "Gray",
    "Castillo", "Hughes", "Price", "Alvarez", "Sanders", "Patel", "Myers", "Long",
    "Ross", "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell", "Sullivan",
    "Bell", "Coleman", "Butler", "Henderson", "Barnes", "Gonzales", "Fisher", "Vasquez",
    "Simmons", "Romero", "Jordan", "Patterson", "Alexander", "Hamilton", "Graham",
    "Reynolds", "Griffin", "Wallace", "Moreno", "West", "Cole", "Hayes", "Bryant",
    "Herrera", "Gibson", "Ellis", "Tran", "Medina", "Aguilar", "Stevens", "Murray",
    "Ford", "Castro", "Marshall", "Owens", "Harrison", "Fernandez", "McDonald", "Woods",
    "Washington", "Kennedy", "Wells", "Vargas", "Henry", "Chen", "Freeman", "Webb",
    "Tucker", "Guzman", "Burns", "Crawford", "Olson", "Simpson", "Porter", "Hunter",
    "Gordon", "Mendez", "Silva", "Shaw", "Snyder", "Mason", "Dixon", "Muñoz",
    "Rios", "Soto", "Lin", "Huang", "Zhang", "Wu", "Wang", "Liu", "Yang", "Zhao",
    "Gupta", "Sharma", "Verma", "Singh", "Reddy", "Nair", "Mehta", "Bose", "Choudhury",
    "Kowalski", "Nowak", "Wiśniewski", "Wójcik", "Kamiński", "Lewandowski", "Zieliński",
    "Ivanov", "Smirnov", "Kuznetsov", "Popov", "Vasiliev", "Petrov", "Sokolov",
    "Takahashi", "Sato", "Suzuki", "Tanaka", "Watanabe", "Ito", "Yamamoto", "Nakamura",
    "Okafor", "Adeyemi", "Mensah", "Diallo", "Traore", "Nwachukwu", "Osei", "Kone"
]

STREET_BASES = [
    "Maple", "Oak", "Washington", "Lincoln", "Highland", "Park", "Sunset", "Beacon",
    "Cedar", "Elm", "Pine", "Willow", "Lexington", "Madison", "Cypress", "Valley",
    "River", "Grand", "Prospect", "Franklin", "Chestnut", "Walnut", "Magnolia",
    "Spring", "Ridge", "Meadow", "Hillside", "Forest", "Lake", "Hickory", "Birch",
    "Fairview", "Church", "Main", "Broad", "Adams", "Jefferson", "Jackson", "Centennial",
    "University", "Industrial", "Mission", "Peachtree", "Biscayne", "Ocean", "Wilshire",
    "Sunset", "Colfax", "Piedmont", "Commonwealth", "Michigan", "Bayshore", "Westheimer"
]

STREET_SUFFIXES = ["St", "Ave", "Blvd", "Dr", "Rd", "Way", "Ln", "Ct", "Cir", "Pkwy", "Terr"]

US_METROS: List[Dict[str, Any]] = [
    {"city": "New York", "state": "NY", "zip_prefix": "100", "area_code": "212", "ssn_state_pool": ["NY", "NJ", "CT"]},
    {"city": "Brooklyn", "state": "NY", "zip_prefix": "112", "area_code": "718", "ssn_state_pool": ["NY", "NJ"]},
    {"city": "Los Angeles", "state": "CA", "zip_prefix": "900", "area_code": "213", "ssn_state_pool": ["CA", "NV", "AZ"]},
    {"city": "San Francisco", "state": "CA", "zip_prefix": "941", "area_code": "415", "ssn_state_pool": ["CA", "OR", "WA"]},
    {"city": "San Jose", "state": "CA", "zip_prefix": "951", "area_code": "408", "ssn_state_pool": ["CA"]},
    {"city": "San Diego", "state": "CA", "zip_prefix": "921", "area_code": "619", "ssn_state_pool": ["CA", "AZ"]},
    {"city": "Chicago", "state": "IL", "zip_prefix": "606", "area_code": "312", "ssn_state_pool": ["IL", "IN", "WI"]},
    {"city": "Houston", "state": "TX", "zip_prefix": "770", "area_code": "713", "ssn_state_pool": ["TX", "LA"]},
    {"city": "Dallas", "state": "TX", "zip_prefix": "752", "area_code": "214", "ssn_state_pool": ["TX", "OK"]},
    {"city": "Austin", "state": "TX", "zip_prefix": "787", "area_code": "512", "ssn_state_pool": ["TX"]},
    {"city": "San Antonio", "state": "TX", "zip_prefix": "782", "area_code": "210", "ssn_state_pool": ["TX"]},
    {"city": "Phoenix", "state": "AZ", "zip_prefix": "850", "area_code": "602", "ssn_state_pool": ["AZ", "CA", "NM"]},
    {"city": "Philadelphia", "state": "PA", "zip_prefix": "191", "area_code": "215", "ssn_state_pool": ["PA", "NJ", "DE"]},
    {"city": "Miami", "state": "FL", "zip_prefix": "331", "area_code": "305", "ssn_state_pool": ["FL", "NY"]},
    {"city": "Orlando", "state": "FL", "zip_prefix": "328", "area_code": "407", "ssn_state_pool": ["FL", "GA"]},
    {"city": "Tampa", "state": "FL", "zip_prefix": "336", "area_code": "813", "ssn_state_pool": ["FL"]},
    {"city": "Atlanta", "state": "GA", "zip_prefix": "303", "area_code": "404", "ssn_state_pool": ["GA", "AL", "SC", "NC"]},
    {"city": "Seattle", "state": "WA", "zip_prefix": "981", "area_code": "206", "ssn_state_pool": ["WA", "OR", "ID"]},
    {"city": "Boston", "state": "MA", "zip_prefix": "021", "area_code": "617", "ssn_state_pool": ["MA", "NH", "RI"]},
    {"city": "Denver", "state": "CO", "zip_prefix": "802", "area_code": "303", "ssn_state_pool": ["CO", "WY", "UT"]},
    {"city": "Las Vegas", "state": "NV", "zip_prefix": "891", "area_code": "702", "ssn_state_pool": ["NV", "CA", "AZ"]},
    {"city": "Detroit", "state": "MI", "zip_prefix": "482", "area_code": "313", "ssn_state_pool": ["MI", "OH"]},
    {"city": "Charlotte", "state": "NC", "zip_prefix": "282", "area_code": "704", "ssn_state_pool": ["NC", "SC", "VA"]},
    {"city": "Raleigh", "state": "NC", "zip_prefix": "276", "area_code": "919", "ssn_state_pool": ["NC", "VA"]},
    {"city": "Minneapolis", "state": "MN", "zip_prefix": "554", "area_code": "612", "ssn_state_pool": ["MN", "WI"]},
    {"city": "Portland", "state": "OR", "zip_prefix": "972", "area_code": "503", "ssn_state_pool": ["OR", "WA"]},
    {"city": "Nashville", "state": "TN", "zip_prefix": "372", "area_code": "615", "ssn_state_pool": ["TN", "KY", "AL"]},
    {"city": "Columbus", "state": "OH", "zip_prefix": "432", "area_code": "614", "ssn_state_pool": ["OH", "PA", "IN"]},
    {"city": "Indianapolis", "state": "IN", "zip_prefix": "462", "area_code": "317", "ssn_state_pool": ["IN", "IL", "OH"]},
    {"city": "Washington", "state": "DC", "zip_prefix": "200", "area_code": "202", "ssn_state_pool": ["DC", "MD", "VA"]},
    {"city": "Baltimore", "state": "MD", "zip_prefix": "212", "area_code": "410", "ssn_state_pool": ["MD", "DC", "PA"]},
    {"city": "Salt Lake City", "state": "UT", "zip_prefix": "841", "area_code": "801", "ssn_state_pool": ["UT", "ID", "NV"]},
    {"city": "Kansas City", "state": "MO", "zip_prefix": "641", "area_code": "816", "ssn_state_pool": ["MO", "KS"]},
    {"city": "St. Louis", "state": "MO", "zip_prefix": "631", "area_code": "314", "ssn_state_pool": ["MO", "IL"]}
]

EMPLOYERS_VERIFIED = [
    {"name": "Apex Global Logistics Inc", "sector": "Logistics", "base_salary": 72000},
    {"name": "Cascade Health Systems", "sector": "Healthcare", "base_salary": 88000},
    {"name": "Vertex Software Technologies LLC", "sector": "Technology", "base_salary": 135000},
    {"name": "Meridian Financial Partners", "sector": "Finance", "base_salary": 110000},
    {"name": "Starlight Hospitality Group", "sector": "Hospitality", "base_salary": 54000},
    {"name": "Pinnacle Engineering & Design", "sector": "Engineering", "base_salary": 102000},
    {"name": "Horizon Media & Communications", "sector": "Media", "base_salary": 78000},
    {"name": "Vanguard Biotech Solutions", "sector": "Biotech", "base_salary": 125000},
    {"name": "NorthStar Retail Enterprises", "sector": "Retail", "base_salary": 58000},
    {"name": "Summit Clean Energy Corp", "sector": "Energy", "base_salary": 96000},
    {"name": "Kensington Advisory Partners", "sector": "Consulting", "base_salary": 140000},
    {"name": "Beacon Medical Technologies", "sector": "Healthcare", "base_salary": 115000},
    {"name": "Atlas Cloud Infrastructure", "sector": "Technology", "base_salary": 145000},
    {"name": "Pacific Standard Insurance Co", "sector": "Insurance", "base_salary": 82000},
    {"name": "Silverline Architectural Group", "sector": "Architecture", "base_salary": 92000}
]

EMPLOYERS_SHELL_SYNTHETIC = [
    {"name": "Nexis Strategic Capital Management LLC", "sector": "Finance", "base_salary": 185000},
    {"name": "Quantum Global Enterprises Group Inc", "sector": "Technology", "base_salary": 220000},
    {"name": "OmniCore Advisory Solutions LLC", "sector": "Consulting", "base_salary": 195000},
    {"name": "Synthetix Digital Innovations Corp", "sector": "Technology", "base_salary": 210000},
    {"name": "PrimeSource Global Holdings LLC", "sector": "Trading", "base_salary": 175000},
    {"name": "Apex Dynamic Logistics & Freight LLC", "sector": "Logistics", "base_salary": 160000},
    {"name": "Vanguard Edge Consulting Partners", "sector": "Consulting", "base_salary": 230000},
    {"name": "BioMatrix Innovations International", "sector": "Biotech", "base_salary": 205000},
    {"name": "Sterling Crest Capital Advisors", "sector": "Finance", "base_salary": 240000},
    {"name": "Aegis Secure Systems Global LLC", "sector": "Security", "base_salary": 190000}
]

JOB_ROLES = [
    {"title": "Software Engineer", "level": "MID", "multiplier": 1.0},
    {"title": "Senior Solutions Architect", "level": "SR", "multiplier": 1.4},
    {"title": "Director of Operations", "level": "DIR", "multiplier": 1.7},
    {"title": "Financial Analyst", "level": "MID", "multiplier": 0.95},
    {"title": "Vice President of Strategic Growth", "level": "EXEC", "multiplier": 2.2},
    {"title": "Clinical Research Coordinator", "level": "MID", "multiplier": 0.85},
    {"title": "Supply Chain Specialist", "level": "MID", "multiplier": 0.80},
    {"title": "Account Executive", "level": "MID", "multiplier": 0.90},
    {"title": "Chief Technology Officer", "level": "EXEC", "multiplier": 2.5},
    {"title": "Marketing Manager", "level": "MID", "multiplier": 0.95},
    {"title": "Project Manager", "level": "MID", "multiplier": 1.05},
    {"title": "Senior Data Scientist", "level": "SR", "multiplier": 1.45},
    {"title": "Compliance Officer", "level": "SR", "multiplier": 1.15},
    {"title": "Customer Operations Lead", "level": "ENTRY", "multiplier": 0.65}
]

CARRIERS_POSTPAID = ["Verizon Wireless", "AT&T Mobility", "T-Mobile USA"]
CARRIERS_PREPAID = ["Metro by T-Mobile", "Cricket Wireless", "Boost Mobile", "Mint Mobile"]
CARRIERS_VOIP = ["Twilio", "Bandwidth.com", "Google Voice", "TextNow", "Vonage Business", "RingCentral"]

DOMAINS_LEGITIMATE = ["gmail.test", "yahoo.test", "outlook.test", "icloud.test", "proton.test"]
DOMAINS_DISPOSABLE = ["temp-mail.test", "mailinator.test", "throwaway-inbox.test", "guerrillamail.test", "sharklasers.test", "fastinbox-relay.test"]
DOMAINS_CUSTOM_SHELL = ["nexis-capital.test", "quantumglobal-group.test", "omnicore-advisory.test", "prime-holdings.test"]

EXIF_HARDWARE = [
    "Apple iOS 17.4 (iPhone 15 Pro)",
    "Apple iOS 16.6 (iPhone 14)",
    "Samsung Camera SM-S918B (Galaxy S23 Ultra)",
    "Google Pixel 8 Pro Camera v9.2",
    "Fujitsu ScanSnap iX1600 v3.1",
    "Canon CanoScan LiDE 400 Twain Driver"
]

EXIF_SYNTHETIC = [
    "ReportLab PDF Library v3.6.12",
    "Canvas 2D Context (Chromium Headless)",
    "PIL/Pillow 10.2.0 Python Engine",
    "Adobe Photoshop 2024 (Windows)",
    "wkhtmltopdf 0.12.6",
    "None/Stripped (Metadata Cleared)"
]


# =============================================================================
# HELPER MATHEMATICS & ENTROPY
# =============================================================================

def calculate_shannon_entropy(s: str) -> float:
    """Compute normalized Shannon character entropy [0.0, 1.0] of a string."""
    if not s:
        return 0.0
    length = len(s)
    freq: Dict[str, int] = {}
    for char in s:
        freq[char] = freq.get(char, 0) + 1
    
    entropy = 0.0
    for count in freq.values():
        p = count / length
        entropy -= p * math.log2(p)
        
    # Normalize by max possible entropy for string length over base36 (alphanumeric)
    max_entropy = math.log2(min(length, 36)) if length > 1 else 1.0
    if max_entropy <= 0:
        return 0.0
    return round(min(1.0, max(0.0, entropy / max_entropy)), 4)


def compute_icao_check_digit(data: str) -> int:
    """Compute ICAO Doc 9303 check digit (weights 7, 3, 1 repeating)."""
    weights = [7, 3, 1]
    total = 0
    for i, char in enumerate(data.upper()):
        if char.isdigit():
            val = int(char)
        elif char.isalpha():
            val = ord(char) - ord('A') + 10
        elif char == '<':
            val = 0
        else:
            val = 0
        weight = weights[i % 3]
        total += val * weight
    return total % 10


# =============================================================================
# GENERATOR CLASS
# =============================================================================

class VectorAIdentityGenerator:
    """Deterministic generator for Vector A Frankenstein Synthetic Identities."""

    def __init__(self, seed: int = 42, frankenstein_ratio_mean: float = 0.75):
        self.seed = seed
        self.frankenstein_ratio_mean = frankenstein_ratio_mean
        self.rng = random.Random(seed)

    def _generate_synthetic_ssn(self, area_block: str = "9") -> str:
        """Generate a guardrailed synthetic US SSN using SSA non-issuable blocks.
        
        SSA Non-issuable guardrail rules:
        - Area numbers 900-999 (never issued by SSA).
        - Area number 666, 000 (never issued).
        - Group number 00 (invalid).
        - Serial number 0000 (invalid).
        All generated SSNs strictly use 9XX-XX-XXXX or 000-XX-XXXX to prevent
        any real citizen PII collision while maintaining token syntax.
        """
        if area_block == "9":
            area = self.rng.randint(900, 999)
        elif area_block == "666":
            area = 666
        elif area_block == "000":
            area = 0
        else:
            area = self.rng.randint(900, 999)
            
        group = self.rng.randint(10, 99)
        serial = self.rng.randint(1000, 9999)
        return f"{area:03d}-{group:02d}-{serial:04d}"

    def _generate_phone(self, area_code: str) -> str:
        """Generate a fictitious E.164 phone number using NANP reserved 555-01XX range."""
        # NANP reserved range 555-0100 through 555-0199 strictly for fictitious use
        line = self.rng.randint(100, 199)
        return f"+1{area_code}5550{line:03d}"[-12:]  # Format: +1XXXXXXXXXX

    def _generate_profile(self, index: int, archetype: str) -> Dict[str, Any]:
        """Generate a single identity profile and document metadata bundle."""
        profile_hash = hashlib.sha256(f"{self.seed}_{index}".encode()).hexdigest()[:8].upper()
        profile_id = f"ID-{profile_hash}"

        # -------------------------------------------------------------------------
        # 1. ARCHETYPE PARAMETERIZATION & PROVENANCE
        # -------------------------------------------------------------------------
        if archetype == "BENCHMARK_LEGITIMATE":
            is_synthetic = False
            synthesis_type = "BENCHMARK_LEGITIMATE"
            attack_technique_id = "CLEAN"
            frankenstein_ratio = 0.0
            evasion_target_tier = "TIER_1_EVASION"
            anchor_entity_type = "ACTIVE_ADULT"
        elif archetype == "FRANKENSTEIN_STOLEN_ANCHOR":
            is_synthetic = True
            synthesis_type = "FRANKENSTEIN_STOLEN_ANCHOR"
            attack_technique_id = self.rng.choice(["TECH_A_02", "TECH_A_04"])
            frankenstein_ratio = round(self.rng.uniform(0.65, 0.90), 2)
            evasion_target_tier = self.rng.choice(["TIER_1_EVASION", "TIER_2_EVASION", "TIER_3_EVASION"])
            anchor_entity_type = self.rng.choice([
                "CHILD_MINOR_SSN", "DECEASED_INDIVIDUAL", "DORMANT_FILE"
            ])
        else:  # FULLY_SYNTHETIC
            is_synthetic = True
            synthesis_type = "FULLY_SYNTHETIC"
            attack_technique_id = "TECH_A_01"
            frankenstein_ratio = 1.0
            evasion_target_tier = "TIER_1_EVASION"
            anchor_entity_type = "UNASSIGNED_AREA_BLOCK"

        # -------------------------------------------------------------------------
        # 2. STOLEN REAL ANCHOR FRAGMENT (Authentic PII baseline)
        # -------------------------------------------------------------------------
        metro = self.rng.choice(US_METROS)
        
        if archetype == "BENCHMARK_LEGITIMATE":
            anchor_birth_year = self.rng.randint(1965, 2001)
            # SSN issuance year aligned with birth state and childhood
            issuance_start = anchor_birth_year + self.rng.randint(0, 3)
            issuance_end = issuance_start + self.rng.randint(1, 3)
            anchor_issuance_year_range = f"{issuance_start}-{issuance_end}"
            anchor_issuing_state = self.rng.choice(metro["ssn_state_pool"])
            current_age = 2026 - anchor_birth_year
            anchor_bureau_vintage_months = max(12, int((current_age - 18) * 12 * self.rng.uniform(0.7, 1.0)))
        elif archetype == "FRANKENSTEIN_STOLEN_ANCHOR":
            if anchor_entity_type == "CHILD_MINOR_SSN":
                anchor_birth_year = self.rng.randint(2012, 2020)
                issuance_start = anchor_birth_year
                anchor_issuance_year_range = f"{issuance_start}-{issuance_start+2}"
                anchor_bureau_vintage_months = 0  # Child has no genuine trade lines
            elif anchor_entity_type == "DECEASED_INDIVIDUAL":
                anchor_birth_year = self.rng.randint(1930, 1960)
                issuance_start = anchor_birth_year + self.rng.randint(14, 25)
                anchor_issuance_year_range = f"{issuance_start}-{issuance_start+3}"
                anchor_bureau_vintage_months = self.rng.choice([0, self.rng.randint(180, 420)])
            else:  # DORMANT_FILE
                anchor_birth_year = self.rng.randint(1970, 1990)
                issuance_start = anchor_birth_year + self.rng.randint(0, 5)
                anchor_issuance_year_range = f"{issuance_start}-{issuance_start+3}"
                anchor_bureau_vintage_months = self.rng.randint(0, 18)  # Thin/dormant file
            # Regional anchor mismatch: stolen anchor from distant state
            other_states = [s for s in ["NY", "CA", "TX", "FL", "IL", "PA", "OH", "MI", "GA"] if s != metro["state"]]
            anchor_issuing_state = self.rng.choice(other_states)
        else:  # FULLY_SYNTHETIC
            anchor_birth_year = self.rng.randint(1975, 2003)
            anchor_issuance_year_range = "2015-2019"
            anchor_issuing_state = self.rng.choice(["NY", "CA", "TX", "FL", "WA"])
            anchor_bureau_vintage_months = 0

        anchor_national_id = self._generate_synthetic_ssn("9" if archetype != "FULLY_SYNTHETIC" else "000")

        # -------------------------------------------------------------------------
        # 3. FABRICATED DEMOGRAPHIC OVERLAY (Biographical, Address, Contact, Work)
        # -------------------------------------------------------------------------
        gender_roll = self.rng.random()
        if gender_roll < 0.48:
            gender = "M"
            first_name = self.rng.choice(FIRST_NAMES_MALE)
            middle_name = self.rng.choice(FIRST_NAMES_MALE)
        elif gender_roll < 0.96:
            gender = "F"
            first_name = self.rng.choice(FIRST_NAMES_FEMALE)
            middle_name = self.rng.choice(FIRST_NAMES_FEMALE)
        else:
            gender = "NON_BINARY"
            first_name = self.rng.choice(FIRST_NAMES_NEUTRAL)
            middle_name = self.rng.choice(FIRST_NAMES_NEUTRAL)

        last_name = self.rng.choice(LAST_NAMES)

        if archetype == "BENCHMARK_LEGITIMATE":
            dob_year = anchor_birth_year
        elif archetype == "FRANKENSTEIN_STOLEN_ANCHOR":
            # Frankenstein divergence: claimed adult age (25-45) despite child/deceased anchor
            dob_year = self.rng.randint(1982, 2000)
        else:
            dob_year = self.rng.randint(1980, 2002)

        dob_month = self.rng.randint(1, 12)
        dob_day = self.rng.randint(1, 28)
        claimed_dob = f"{dob_year:04d}-{dob_month:02d}-{dob_day:02d}"

        # Residential Address
        street_num = self.rng.randint(100, 9999)
        street_base = self.rng.choice(STREET_BASES)
        street_sfx = self.rng.choice(STREET_SUFFIXES)
        street_line1 = f"{street_num} {street_base} {street_sfx}"
        street_line2 = f"Apt {self.rng.randint(1, 400)}" if self.rng.random() < 0.45 else ""
        postal_code = f"{metro['zip_prefix']}{self.rng.randint(10, 99):02d}"

        if archetype == "BENCHMARK_LEGITIMATE":
            address_type = self.rng.choice(["SINGLE_FAMILY_RESIDENCE", "MULTI_FAMILY_APARTMENT"])
            is_cmra = False
            address_tenure_months = self.rng.randint(24, 180)
        elif archetype == "FRANKENSTEIN_STOLEN_ANCHOR":
            address_type = self.rng.choice([
                "COMMERCIAL_MAIL_RECEIVING_AGENCY", "VIRTUAL_OFFICE_DROP", "FREIGHT_FORWARDER", "MULTI_FAMILY_APARTMENT"
            ])
            is_cmra = address_type in ["COMMERCIAL_MAIL_RECEIVING_AGENCY", "VIRTUAL_OFFICE_DROP", "FREIGHT_FORWARDER"]
            address_tenure_months = self.rng.randint(1, 14)
        else:
            address_type = self.rng.choice(["COMMERCIAL_MAIL_RECEIVING_AGENCY", "MULTI_FAMILY_APARTMENT"])
            is_cmra = address_type == "COMMERCIAL_MAIL_RECEIVING_AGENCY"
            address_tenure_months = self.rng.randint(0, 6)

        # Contact Endpoints (Phone & Email)
        phone_number = self._generate_phone(metro["area_code"])
        
        if archetype == "BENCHMARK_LEGITIMATE":
            phone_line_type = "TIER_1_POSTPAID_WIRELESS"
            phone_carrier_name = self.rng.choice(CARRIERS_POSTPAID)
            phone_tenure_days = self.rng.randint(730, 3650)
            
            email_domain = self.rng.choice(DOMAINS_LEGITIMATE)
            email_pattern = self.rng.choice([
                f"{first_name.lower()}.{last_name.lower()}",
                f"{first_name[0].lower()}{last_name.lower()}{self.rng.randint(10, 99)}",
                f"{first_name.lower()}_{last_name.lower()}"
            ])
            email_address = f"{email_pattern}@{email_domain}"
            email_domain_age_days = self.rng.randint(1500, 7000)
            email_is_disposable = False
        elif archetype == "FRANKENSTEIN_STOLEN_ANCHOR":
            phone_line_type = self.rng.choice(["VOIP_VIRTUAL_BURNER", "PREPAID_MOBILE"])
            phone_carrier_name = self.rng.choice(CARRIERS_VOIP if phone_line_type == "VOIP_VIRTUAL_BURNER" else CARRIERS_PREPAID)
            phone_tenure_days = self.rng.randint(3, 45)  # Fresh burner line
            
            if self.rng.random() < 0.60:
                email_domain = self.rng.choice(DOMAINS_CUSTOM_SHELL)
                email_address = f"{first_name[0].lower()}{last_name.lower()}@{email_domain}"
                email_domain_age_days = self.rng.randint(10, 90)
                email_is_disposable = False
            else:
                email_domain = self.rng.choice(DOMAINS_LEGITIMATE)
                rand_suffix = hashlib.md5(f"{profile_id}".encode()).hexdigest()[:6]
                email_address = f"{first_name.lower()}{rand_suffix}@{email_domain}"
                email_domain_age_days = self.rng.randint(300, 2000)
                email_is_disposable = False
        else:  # FULLY_SYNTHETIC
            phone_line_type = "VOIP_VIRTUAL_BURNER"
            phone_carrier_name = self.rng.choice(CARRIERS_VOIP)
            phone_tenure_days = self.rng.randint(1, 15)
            
            email_domain = self.rng.choice(DOMAINS_DISPOSABLE)
            rand_user = hashlib.md5(f"{profile_id}_fake".encode()).hexdigest()[:10]
            email_address = f"{rand_user}@{email_domain}"
            email_domain_age_days = self.rng.randint(1, 30)
            email_is_disposable = True

        email_user = email_address.split("@")[0]
        email_entropy_score = calculate_shannon_entropy(email_user)

        # Employment & Financial Profile
        job = self.rng.choice(JOB_ROLES)
        job_title = job["title"]
        job_mult = job["multiplier"]

        if archetype == "BENCHMARK_LEGITIMATE":
            emp = self.rng.choice(EMPLOYERS_VERIFIED)
            employer_name = emp["name"]
            employer_state = metro["state"]
            employer_corporate_registry_verified = True
            base_sal = emp["base_salary"] * job_mult
            annual_income = round(float(self.rng.gauss(base_sal, base_sal * 0.08)), -2)
            annual_income = max(35000.0, min(350000.0, annual_income))
            employment_status = "FULL_TIME"
        elif archetype == "FRANKENSTEIN_STOLEN_ANCHOR":
            if self.rng.random() < 0.65:
                emp = self.rng.choice(EMPLOYERS_SHELL_SYNTHETIC)
                employer_corporate_registry_verified = False
            else:
                emp = self.rng.choice(EMPLOYERS_VERIFIED)
                employer_corporate_registry_verified = True
            employer_name = emp["name"]
            employer_state = self.rng.choice([metro["state"], "DE", "WY", "NV"])
            base_sal = emp["base_salary"] * job_mult
            # Inflated salary claim on synthetic profiles
            annual_income = round(float(self.rng.uniform(base_sal * 0.95, base_sal * 1.35)), -2)
            annual_income = max(45000.0, min(500000.0, annual_income))
            employment_status = self.rng.choice(["FULL_TIME", "SELF_EMPLOYED"])
        else:
            emp = self.rng.choice(EMPLOYERS_SHELL_SYNTHETIC)
            employer_name = emp["name"]
            employer_state = "DE"
            employer_corporate_registry_verified = False
            annual_income = round(float(self.rng.uniform(90000.0, 250000.0)), -2)
            employment_status = "SELF_EMPLOYED"

        # -------------------------------------------------------------------------
        # 4. DOCUMENT-METADATA FORENSIC BUNDLE
        # -------------------------------------------------------------------------
        doc_uuid = str(uuid.UUID(hashlib.md5(f"{profile_id}_doc".encode()).hexdigest()))
        doc_type = self.rng.choice(["DRIVERS_LICENSE", "NATIONAL_PASSPORT", "TAX_IDENTITY_CARD"])
        issuing_authority = f"{metro['state']}_DMV" if doc_type == "DRIVERS_LICENSE" else "US_DOS"

        issue_year = self.rng.randint(2021, 2024)
        issue_month = self.rng.randint(1, 12)
        issue_day = self.rng.randint(1, 28)
        doc_issue_date = f"{issue_year:04d}-{issue_month:02d}-{issue_day:02d}"
        doc_expiry_date = f"{issue_year+5:04d}-{issue_month:02d}-{issue_day:02d}"

        if archetype == "BENCHMARK_LEGITIMATE":
            template_alignment_score = round(self.rng.uniform(0.94, 0.99), 3)
            font_kerning_anomaly_score = round(self.rng.uniform(0.02, 0.12), 3)
            bounding_box_jitter_score = round(self.rng.uniform(0.01, 0.07), 3)
            photo_tamper_artifact_score = round(self.rng.uniform(0.01, 0.09), 3)
            ocr_confidence_score = round(self.rng.uniform(0.92, 0.99), 3)
            mrz_format_validity = True
            
            national_id_format_valid = True
            algorithmic_checksum_valid = True
            checksum_spoofing_method = "CALCULATED_VALID"
            mrz_check_digits_match = True
            barcode_pdf417_payload_match = True
            
            file_format = self.rng.choice(["JPEG", "PNG", "PDF"])
            exif_software_header = self.rng.choice(EXIF_HARDWARE)
            color_space = self.rng.choice(["sRGB", "Display-P3"])
            dpi_resolution = self.rng.choice([300, 600])
            compression_quantization_profile = "STANDARD_HARDWARE_CAMERA"
            layer_flattening_detected = False
            temporal_issuance_delta_days = self.rng.randint(-5, 14)
            metadata_creation_date = f"{issue_year:04d}-{issue_month:02d}-{max(1, issue_day-2):02d}T14:32:00Z"
            
        elif archetype == "FRANKENSTEIN_STOLEN_ANCHOR":
            if attack_technique_id == "TECH_A_04":  # Advanced Checksum Spoofing
                algorithmic_checksum_valid = True
                checksum_spoofing_method = "CALCULATED_VALID"
                mrz_check_digits_match = True
                barcode_pdf417_payload_match = False  # Barcode payload mismatches front OCR persona
            else:
                algorithmic_checksum_valid = self.rng.random() < 0.75
                checksum_spoofing_method = "ALGORITHMIC_BYPASS" if algorithmic_checksum_valid else "NAIVE_RANDOM_DIGIT"
                mrz_check_digits_match = self.rng.random() < 0.70
                barcode_pdf417_payload_match = False

            national_id_format_valid = True
            
            if evasion_target_tier == "TIER_3_EVASION":
                # High-effort synthetic attempting to fool Tier 1 & 2
                template_alignment_score = round(self.rng.uniform(0.88, 0.95), 3)
                font_kerning_anomaly_score = round(self.rng.uniform(0.20, 0.38), 3)
                bounding_box_jitter_score = round(self.rng.uniform(0.12, 0.28), 3)
                photo_tamper_artifact_score = round(self.rng.uniform(0.25, 0.48), 3)
                ocr_confidence_score = round(self.rng.uniform(0.88, 0.96), 3)
                mrz_format_validity = True
                exif_software_header = self.rng.choice([
                    "Adobe Photoshop 2024 (Windows)", "None/Stripped (Metadata Cleared)", "Apple iOS 16.6 (iPhone 14)"
                ])
                dpi_resolution = self.rng.choice([150, 300])
                compression_quantization_profile = "WEB_RECOMPRESSED"
                layer_flattening_detected = True
            else:
                template_alignment_score = round(self.rng.uniform(0.70, 0.88), 3)
                font_kerning_anomaly_score = round(self.rng.uniform(0.38, 0.75), 3)
                bounding_box_jitter_score = round(self.rng.uniform(0.25, 0.65), 3)
                photo_tamper_artifact_score = round(self.rng.uniform(0.45, 0.85), 3)
                ocr_confidence_score = round(self.rng.uniform(0.76, 0.91), 3)
                mrz_format_validity = self.rng.random() < 0.85
                exif_software_header = self.rng.choice(EXIF_SYNTHETIC)
                dpi_resolution = self.rng.choice([72, 150])
                compression_quantization_profile = "SYNTHETIC_GENERATOR_DEFAULT"
                layer_flattening_detected = True

            file_format = self.rng.choice(["PDF", "JPEG", "PNG"])
            color_space = self.rng.choice(["sRGB", "DeviceRGB"])
            temporal_issuance_delta_days = self.rng.randint(-1800, -30)  # Created years after stated issuance
            metadata_creation_date = "2026-08-16T22:15:00Z"
            
        else:  # FULLY_SYNTHETIC
            template_alignment_score = round(self.rng.uniform(0.55, 0.78), 3)
            font_kerning_anomaly_score = round(self.rng.uniform(0.48, 0.88), 3)
            bounding_box_jitter_score = round(self.rng.uniform(0.40, 0.80), 3)
            photo_tamper_artifact_score = round(self.rng.uniform(0.60, 0.95), 3)
            ocr_confidence_score = round(self.rng.uniform(0.65, 0.85), 3)
            mrz_format_validity = False
            
            national_id_format_valid = True
            algorithmic_checksum_valid = False
            checksum_spoofing_method = "NAIVE_RANDOM_DIGIT"
            mrz_check_digits_match = False
            barcode_pdf417_payload_match = False
            
            file_format = "PDF"
            exif_software_header = "ReportLab PDF Library v3.6.12"
            color_space = "DeviceRGB"
            dpi_resolution = 72
            compression_quantization_profile = "SYNTHETIC_GENERATOR_DEFAULT"
            layer_flattening_detected = True
            temporal_issuance_delta_days = -1200
            metadata_creation_date = "2026-08-16T23:00:00Z"

        # -------------------------------------------------------------------------
        # 5. ASSEMBLE GUARANTEED SCHEMA OBJECT
        # -------------------------------------------------------------------------
        profile = {
            "profile_id": profile_id,
            "synthesis_metadata": {
                "is_synthetic": is_synthetic,
                "synthesis_type": synthesis_type,
                "attack_technique_id": attack_technique_id,
                "frankenstein_ratio": frankenstein_ratio,
                "generation_seed": self.seed,
                "evasion_target_tier": evasion_target_tier
            },
            "real_fragment": {
                "anchor_national_id_type": "US_SSN",
                "anchor_national_id": anchor_national_id,
                "anchor_issuing_state": anchor_issuing_state,
                "anchor_issuance_year_range": anchor_issuance_year_range,
                "anchor_birth_year": anchor_birth_year,
                "anchor_bureau_vintage_months": anchor_bureau_vintage_months,
                "anchor_entity_type": anchor_entity_type
            },
            "fabricated_overlay": {
                "biographical": {
                    "first_name": first_name,
                    "middle_name": middle_name,
                    "last_name": last_name,
                    "claimed_date_of_birth": claimed_dob,
                    "claimed_gender": gender
                },
                "residential_address": {
                    "street_line1": street_line1,
                    "street_line2": street_line2,
                    "city": metro["city"],
                    "state": metro["state"],
                    "postal_code": postal_code,
                    "address_type": address_type,
                    "is_cmra": is_cmra,
                    "address_tenure_months": address_tenure_months
                },
                "contact_endpoints": {
                    "phone_number": phone_number,
                    "phone_line_type": phone_line_type,
                    "phone_carrier_name": phone_carrier_name,
                    "phone_tenure_days": phone_tenure_days,
                    "email_address": email_address,
                    "email_domain_age_days": email_domain_age_days,
                    "email_is_disposable": email_is_disposable,
                    "email_entropy_score": email_entropy_score
                },
                "employment_profile": {
                    "employer_name": employer_name,
                    "job_title": job_title,
                    "annual_income": annual_income,
                    "employment_status": employment_status,
                    "employer_state": employer_state,
                    "employer_corporate_registry_verified": employer_corporate_registry_verified
                }
            },
            "document_metadata": {
                "document_id": doc_uuid,
                "document_type": doc_type,
                "issuing_authority": issuing_authority,
                "document_issue_date": doc_issue_date,
                "document_expiry_date": doc_expiry_date,
                "field_layout_plausibility": {
                    "template_alignment_score": template_alignment_score,
                    "font_kerning_anomaly_score": font_kerning_anomaly_score,
                    "bounding_box_jitter_score": bounding_box_jitter_score,
                    "photo_tamper_artifact_score": photo_tamper_artifact_score,
                    "ocr_confidence_score": ocr_confidence_score,
                    "mrz_format_validity": mrz_format_validity
                },
                "checksum_validity": {
                    "national_id_format_valid": national_id_format_valid,
                    "algorithmic_checksum_valid": algorithmic_checksum_valid,
                    "checksum_spoofing_method": checksum_spoofing_method,
                    "mrz_check_digits_match": mrz_check_digits_match,
                    "barcode_pdf417_payload_match": barcode_pdf417_payload_match
                },
                "creation_tool_fingerprint": {
                    "file_format": file_format,
                    "exif_software_header": exif_software_header,
                    "color_space": color_space,
                    "dpi_resolution": dpi_resolution,
                    "compression_quantization_profile": compression_quantization_profile,
                    "layer_flattening_detected": layer_flattening_detected,
                    "metadata_creation_date": metadata_creation_date,
                    "temporal_issuance_delta_days": temporal_issuance_delta_days
                }
            }
        }

        return profile

    def generate_batch(self, count: int = 500) -> Dict[str, Any]:
        """Generate a complete labeled batch of identity profiles."""
        # Distribution: 30% Legitimate Benchmark, 55% Frankenstein Stolen Anchor, 15% Fully Synthetic
        legit_count = int(count * 0.30)
        franken_count = int(count * 0.55)
        fully_synth_count = count - legit_count - franken_count

        archetype_plan = (
            ["BENCHMARK_LEGITIMATE"] * legit_count +
            ["FRANKENSTEIN_STOLEN_ANCHOR"] * franken_count +
            ["FULLY_SYNTHETIC"] * fully_synth_count
        )
        self.rng.shuffle(archetype_plan)

        profiles = []
        for i, arch in enumerate(archetype_plan):
            profile = self._generate_profile(i, arch)
            profiles.append(profile)

        # Deterministic batch timestamp based on seed for reproducible JSON serialization
        generated_at = "2026-08-17T04:00:00Z"
        batch_id = f"batch_identity_v1_seed{self.seed}_n{count}"

        batch = {
            "batch_id": batch_id,
            "generated_at": generated_at,
            "generator_version": "1.0.0",
            "total_records": len(profiles),
            "profiles": profiles
        }

        return batch

    def generate_adversarial_heldout_batch(self, count: int = 500) -> Dict[str, Any]:
        """Generate a deliberately adversarial held-out batch of identity profiles.
        
        Specifically engineered to stress-test the detector against attackers who avoid
        every known Tier 1, Tier 2, and Tier 3 signal check:
        1. Tier 1 Evasion:
           - Valid barcode PDF417 payload match (front OCR demographic parity).
           - Valid algorithmic checksums (MOD11 / Luhn) and valid national ID format.
           - Valid MRZ check-digits.
           - Established aged domains (>1000 days), non-disposable inboxes.
           - Residential single/multi-family addresses (is_cmra = False).
        2. Tier 2 Evasion:
           - Plausible demographic alignment (SSN issuance year range aligns with birth + 18-20y).
           - Active adult anchor cohort (anchor_entity_type = 'ACTIVE_ADULT', zero child/deceased/unassigned SSNs).
           - Seasoned credit bureau vintage (48-180 months).
           - Aligned anchor state with residential state.
           - Postpaid wireless phone line with long tenure (>600 days).
           - Low entropy email username (<0.32).
           - Verified corporate employer registry with standard salary.
        3. Tier 3 Evasion:
           - Authentic optical hardware EXIF software headers (Apple iPhone 15 Pro, Fujitsu ScanSnap, Canon CanoScan).
           - 300+ DPI resolution.
           - Sub-pixel template alignment (>0.96).
           - Low font kerning anomaly score (<0.08).
           - Low photo tamper artifact score (<0.08).
           - Standard hardware camera quantization profile, zero layer flattening.
           - Plausible metadata creation timestamps (0-14 days delta).
        
        Cohort Composition:
        - 150 Benchmark Legitimate Profiles (including edge cases like young adults & fresh movers) [30%]
        - 350 Deliberately Adversarial Synthetic Profiles [70%]
          * ~45% Level A Expert Adversaries (full 3-tier camouflage, score < 0.25 -> ALLOW)
          * ~35% Level B Intermediate Adversaries (Tier 1 & Tier 3 fixed, subtle residual Tier 2/3 drift -> REVIEW)
          * ~20% Level C Partial Adversaries (Tier 1 fixed, slight anchor/forensic mismatch -> BLOCK/REVIEW)
        """
        legit_count = int(count * 0.30)
        adv_synth_count = count - legit_count

        profiles = []
        
        # 1. Generate Legitimate Cohort (including thin-file and mover edge-cases)
        for i in range(legit_count):
            p = self._generate_profile(i, "BENCHMARK_LEGITIMATE")
            # Inject realistic edge cases into ~15% of legitimate records
            if i % 7 == 0:
                # Young adult with 4-month credit vintage
                birth_yr = 2005
                p["real_fragment"]["anchor_birth_year"] = birth_yr
                p["real_fragment"]["anchor_issuance_year_range"] = f"{birth_yr+1}-{birth_yr+3}"
                p["fabricated_overlay"]["biographical"]["claimed_date_of_birth"] = f"{birth_yr}-05-12"
                p["real_fragment"]["anchor_bureau_vintage_months"] = 4
            elif i % 11 == 0:
                # Fresh mover with 3-month address tenure
                p["fabricated_overlay"]["residential_address"]["address_tenure_months"] = 3
            profiles.append(p)

        # 2. Generate Adversarial Synthetic Cohort
        for i in range(adv_synth_count):
            pidx = legit_count + i
            arch = "FRANKENSTEIN_STOLEN_ANCHOR" if (i % 4 != 0) else "FULLY_SYNTHETIC"
            p = self._generate_profile(pidx, arch)
            
            # Apply targeted adversarial evasion mutations
            meta = p["synthesis_metadata"]
            meta["is_synthetic"] = True
            meta["evasion_target_tier"] = "TIER_3_ADVERSARIAL_EVASION"
            
            doc_meta = p["document_metadata"]
            chk = doc_meta["checksum_validity"]
            layout = doc_meta["field_layout_plausibility"]
            tool_fp = doc_meta["creation_tool_fingerprint"]
            overlay = p["fabricated_overlay"]
            bio = overlay["biographical"]
            contact = overlay["contact_endpoints"]
            address = overlay["residential_address"]
            emp = overlay["employment_profile"]
            anchor = p["real_fragment"]

            # --- Tier 1 Evasion (100% of adversarial cohort fixes Tier 1 checks) ---
            chk["barcode_pdf417_payload_match"] = True
            chk["algorithmic_checksum_valid"] = True
            chk["checksum_spoofing_method"] = "CALCULATED_VALID"
            chk["national_id_format_valid"] = True
            chk["mrz_check_digits_match"] = True
            
            contact["email_is_disposable"] = False
            contact["email_domain_age_days"] = self.rng.randint(800, 3500)
            
            address["is_cmra"] = False
            address["address_type"] = self.rng.choice(["SINGLE_FAMILY_RESIDENCE", "MULTI_FAMILY_APARTMENT"])

            # Determine evasion sophistication tier for this adversarial profile
            evasion_skill_roll = self.rng.random()

            if evasion_skill_roll < 0.45:
                # === Level A: Full 3-Tier Camouflage (Expert Attacker) ===
                anchor["anchor_entity_type"] = "ACTIVE_ADULT"
                birth_yr = self.rng.randint(1975, 1996)
                anchor["anchor_birth_year"] = birth_yr
                anchor["anchor_issuance_year_range"] = f"{birth_yr+1}-{birth_yr+2}"
                anchor["anchor_bureau_vintage_months"] = self.rng.randint(72, 180)
                
                dob_m = self.rng.randint(1, 12)
                dob_d = self.rng.randint(1, 28)
                bio["claimed_date_of_birth"] = f"{birth_yr:04d}-{dob_m:02d}-{dob_d:02d}"
                
                matching_metros = [m for m in US_METROS if m["state"] == anchor["anchor_issuing_state"]]
                if matching_metros:
                    metro = self.rng.choice(matching_metros)
                    address["state"] = metro["state"]
                    address["city"] = metro["city"]
                    address["postal_code"] = f"{metro['zip_prefix']}{self.rng.randint(10, 99):02d}"
                address["address_tenure_months"] = self.rng.randint(24, 96)

                contact["phone_line_type"] = "TIER_1_POSTPAID_WIRELESS"
                contact["phone_carrier_name"] = self.rng.choice(CARRIERS_POSTPAID)
                contact["phone_tenure_days"] = self.rng.randint(600, 2400)
                contact["email_entropy_score"] = round(self.rng.uniform(0.18, 0.32), 2)

                emp["employer_corporate_registry_verified"] = True
                ver_emp = self.rng.choice(EMPLOYERS_VERIFIED)
                emp["employer_name"] = ver_emp["name"]
                emp["annual_income"] = round(float(self.rng.gauss(ver_emp["base_salary"], 8000)), -2)

                tool_fp["exif_software_header"] = self.rng.choice([
                    "Apple iPhone 15 Pro iOS 17.4",
                    "Fujitsu fi-7160 Document Scanner",
                    "Canon CanoScan LiDE 400",
                    "Sony Alpha a7 IV Firmware 2.0"
                ])
                tool_fp["dpi_resolution"] = self.rng.choice([300, 600])
                tool_fp["compression_quantization_profile"] = "STANDARD_HARDWARE_CAMERA"
                tool_fp["layer_flattening_detected"] = False
                tool_fp["temporal_issuance_delta_days"] = self.rng.randint(0, 10)
                
                layout["font_kerning_anomaly_score"] = round(self.rng.uniform(0.02, 0.07), 3)
                layout["photo_tamper_artifact_score"] = round(self.rng.uniform(0.02, 0.07), 3)
                layout["bounding_box_jitter_score"] = round(self.rng.uniform(0.01, 0.05), 3)
                layout["template_alignment_score"] = round(self.rng.uniform(0.96, 0.99), 3)

            elif evasion_skill_roll < 0.80:
                # === Level B: Intermediate Adversary (Subtle Residual Drift) ===
                anchor["anchor_entity_type"] = "ACTIVE_ADULT"
                birth_yr = self.rng.randint(1978, 1998)
                anchor["anchor_birth_year"] = birth_yr
                anchor["anchor_issuance_year_range"] = f"{birth_yr+1}-{birth_yr+3}"
                anchor["anchor_bureau_vintage_months"] = self.rng.randint(18, 48)
                
                bio["claimed_date_of_birth"] = f"{birth_yr:04d}-{self.rng.randint(1,12):02d}-{self.rng.randint(1,28):02d}"
                address["address_tenure_months"] = self.rng.randint(6, 20)

                contact["phone_line_type"] = "PREPAID_MOBILE"
                contact["phone_carrier_name"] = self.rng.choice(CARRIERS_PREPAID)
                contact["phone_tenure_days"] = self.rng.randint(120, 450)
                contact["email_entropy_score"] = round(self.rng.uniform(0.30, 0.48), 2)

                emp["employer_corporate_registry_verified"] = True
                emp["annual_income"] = round(float(self.rng.uniform(70000.0, 120000.0)), -2)

                tool_fp["exif_software_header"] = "Apple iOS 16.6 (iPhone 14)"
                tool_fp["dpi_resolution"] = 300
                tool_fp["compression_quantization_profile"] = "WEB_RECOMPRESSED"
                tool_fp["layer_flattening_detected"] = False
                tool_fp["temporal_issuance_delta_days"] = self.rng.randint(2, 25)

                layout["font_kerning_anomaly_score"] = round(self.rng.uniform(0.12, 0.24), 3)
                layout["photo_tamper_artifact_score"] = round(self.rng.uniform(0.10, 0.26), 3)
                layout["template_alignment_score"] = round(self.rng.uniform(0.91, 0.95), 3)

            else:
                # === Level C: Partial Adversary (Catches on 1-2 Defensive Tiers) ===
                anchor["anchor_entity_type"] = self.rng.choice(["ACTIVE_ADULT", "DORMANT_FILE"])
                birth_yr = self.rng.randint(1985, 2002)
                anchor["anchor_birth_year"] = birth_yr - self.rng.randint(2, 8)
                anchor["anchor_issuance_year_range"] = f"{anchor['anchor_birth_year']+1}-{anchor['anchor_birth_year']+3}"
                anchor["anchor_bureau_vintage_months"] = self.rng.randint(6, 24)
                
                bio["claimed_date_of_birth"] = f"{birth_yr:04d}-{self.rng.randint(1,12):02d}-{self.rng.randint(1,28):02d}"
                address["address_tenure_months"] = self.rng.randint(2, 12)

                contact["phone_line_type"] = "PREPAID_MOBILE"
                contact["phone_carrier_name"] = self.rng.choice(CARRIERS_PREPAID)
                contact["phone_tenure_days"] = self.rng.randint(45, 180)
                contact["email_entropy_score"] = round(self.rng.uniform(0.40, 0.65), 2)

                emp["employer_corporate_registry_verified"] = False
                emp["annual_income"] = round(float(self.rng.uniform(85000.0, 160000.0)), -2)

                tool_fp["exif_software_header"] = "Adobe Photoshop 2024 (Windows)"
                tool_fp["dpi_resolution"] = self.rng.choice([150, 300])
                tool_fp["compression_quantization_profile"] = "WEB_RECOMPRESSED"
                tool_fp["layer_flattening_detected"] = True
                tool_fp["temporal_issuance_delta_days"] = self.rng.randint(-30, 40)

                layout["font_kerning_anomaly_score"] = round(self.rng.uniform(0.22, 0.38), 3)
                layout["photo_tamper_artifact_score"] = round(self.rng.uniform(0.20, 0.42), 3)
                layout["template_alignment_score"] = round(self.rng.uniform(0.86, 0.92), 3)

            profiles.append(p)

        self.rng.shuffle(profiles)

        generated_at = "2026-08-18T04:00:00Z"
        batch_id = f"batch_identity_adversarial_v1_seed{self.seed}_n{count}"

        batch = {
            "batch_id": batch_id,
            "generated_at": generated_at,
            "generator_version": "1.0.0",
            "evaluation_type": "DELIBERATELY_ADVERSARIAL_HELDOUT",
            "total_records": len(profiles),
            "profiles": profiles
        }

        return batch


# =============================================================================
# CLI ENTRYPOINT
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Vector A Synthetic Identity & Document Fraud Batch Generator"
    )
    parser.add_argument("--n", type=int, default=500, help="Number of identity profiles to generate (default: 500)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for deterministic reproducibility (default: 42)")
    parser.add_argument(
        "--frankenstein-ratio",
        type=float,
        default=0.75,
        help="Mean proportion of demographic fields fabricated (default: 0.75)"
    )
    parser.add_argument(
        "--adversarial",
        action="store_true",
        help="Generate deliberately adversarial held-out batch avoiding Tier 1/2/3 signals"
    )
    parser.add_argument(
        "--output",
        type=str,
        default="data/generated/identity_batch.json",
        help="Target output JSON filepath"
    )
    parser.add_argument("--quiet", action="store_true", help="Suppress console summary output")

    args = parser.parse_args()

    generator = VectorAIdentityGenerator(seed=args.seed, frankenstein_ratio_mean=args.frankenstein_ratio)
    if args.adversarial:
        batch = generator.generate_adversarial_heldout_batch(count=args.n)
    else:
        batch = generator.generate_batch(count=args.n)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(batch, f, indent=2)

    if not args.quiet:
        print(f"============================================================")
        print(f"TRIAD Vector A Identity Generator — Session 05")
        print(f"============================================================")
        print(f"Batch ID:          {batch['batch_id']}")
        print(f"Generated At:      {batch['generated_at']}")
        print(f"Total Records:     {batch['total_records']}")
        print(f"Seed:              {args.seed}")
        print(f"Target Output:     {output_path.resolve()}")
        
        # Summary distribution
        types = {}
        for p in batch["profiles"]:
            st = p["synthesis_metadata"]["synthesis_type"]
            types[st] = types.get(st, 0) + 1
        print("Archetype Breakdown:")
        for k, v in types.items():
            print(f"  - {k:<30} : {v:>4} ({v/batch['total_records']*100:.1f}%)")
        print("PII Safety Guardrails Enforced:")
        print("  - SSN Non-Issuable Blocks (900-999 / 000): ACTIVE")
        print("  - NANP 555-01XX Reserved Exchange:        ACTIVE")
        print("  - Synthetic Test Domain TLDs:             ACTIVE")
        print(f"============================================================")


if __name__ == "__main__":
    main()
