"""
Pathologist reference data for the accessioning workflow.

Display name format: "First [Middle] Last"
Sorted alphabetically by last name.
"""

MD_LIST = [
    {"last": "Asgari",          "first": "Masoud",       "middle": None,           "display_name": "Masoud Asgari"},
    {"last": "Babaidorabad",    "first": "Nasim",        "middle": None,           "display_name": "Nasim Babaidorabad"},
    {"last": "Behl",            "first": "Preeti",       "middle": None,           "display_name": "Preeti Behl"},
    {"last": "Campos",          "first": "Marite A.",    "middle": None,           "display_name": "Marite A. Campos"},
    {"last": "Chang",           "first": "Harvey",       "middle": None,           "display_name": "Harvey Chang"},
    {"last": "Chaudhari",       "first": "Prakash",      "middle": None,           "display_name": "Prakash Chaudhari"},
    {"last": "Connolly",        "first": "Stephen G.",   "middle": None,           "display_name": "Stephen G. Connolly"},
    {"last": "Costa",           "first": "Michael",      "middle": None,           "display_name": "Michael Costa"},
    {"last": "Cui",             "first": "Shijun",       "middle": None,           "display_name": "Shijun Cui"},
    {"last": "Emery",           "first": "Shawn",        "middle": None,           "display_name": "Shawn Emery"},
    {"last": "Fogel",           "first": "Steven",       "middle": None,           "display_name": "Steven Fogel"},
    {"last": "Hardee",          "first": "Steven",       "middle": None,           "display_name": "Steven Hardee"},
    {"last": "Hare",            "first": "Donovan",      "middle": "Robert",       "display_name": "Donovan Robert Hare"},
    {"last": "Haydel",          "first": "Dana",         "middle": None,           "display_name": "Dana Haydel"},
    {"last": "Kaabipour",       "first": "Emad",         "middle": None,           "display_name": "Emad Kaabipour"},
    {"last": "Land",            "first": "Terry",        "middle": None,           "display_name": "Terry Land"},
    {"last": "Limjoco",         "first": "Teresa",       "middle": None,           "display_name": "Teresa Limjoco"},
    {"last": "Nguyen",          "first": "Tuan",         "middle": None,           "display_name": "Tuan Nguyen"},
    {"last": "Ohan",            "first": "Hovsep",       "middle": None,           "display_name": "Hovsep Ohan"},
    {"last": "Perez-Valles",    "first": "Christy",      "middle": None,           "display_name": "Christy Perez-Valles"},
    {"last": "Rodgers",         "first": "Melissa",      "middle": None,           "display_name": "Melissa Rodgers"},
    {"last": "Setarehshenas",   "first": "Roya",         "middle": None,           "display_name": "Roya Setarehshenas"},
    {"last": "Shaker",          "first": "Nada",         "middle": None,           "display_name": "Nada Shaker"},
    {"last": "Starshak",        "first": "Phillip E.",   "middle": None,           "display_name": "Phillip E. Starshak"},
    {"last": "Victorio",        "first": "Anthony R.",   "middle": None,           "display_name": "Anthony R. Victorio"},
    {"last": "Wassimi",         "first": "Spogmai",      "middle": None,           "display_name": "Spogmai Wassimi"},
    {"last": "Watson",          "first": "Ashley",       "middle": None,           "display_name": "Ashley Watson"},
]

# Filtered subset: only pathologists eligible for bone marrow case assignment
BONE_MARROW_ELIGIBLE = [
    entry for entry in MD_LIST
    if entry["last"] in {"Babaidorabad", "Hardee", "Starshak"}
]
