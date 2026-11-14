# Beat maps for Eoin's personal yap reels. One image per beat; the image hard-cuts on the first word of its beat.
# beat = (cue word, occurrence, image key, keyword or None, keyword position)
#   cue word is matched against the whisper words (lowercase, punctuation stripped); occurrence is 1-based.
#   image key -> jobs/yap-assets/cards/<key>.jpg ("end" = end card, keyword drawn on a dimmed library card).
#   keyword = the line written into the image's dead space; colour alternates white / orange by beat.
#   position = where the dead space is: L, R, T, B, C, TL, TR, BL, BR.
# title = (title, subtitle, [3 strip keys]), held from 0s until the first beat's cue word.
# QUERIES = what fetch.py searched for each key (kept so the pick can be re-pulled).

TAKES = {
    "a": {
        "src": "C054FAEA-CF3C-4B19-8E47-BF9C128AB0A9",
        "name": "Knowledge is power",
        "title": ("Knowledge Is Power", "(only if it's applied)", ["library", "munger", "workshop"]),
        "beats": [
            ("now", 1, "unread_books", "collecting", "T"),
            ("wealth", 1, "munger", "a wealth of\nknowledge", "L"),
            ("without", 1, "couch_tutorials", "without applying it", "T"),
            ("useless", 1, "dusty_books", "useless", "C"),
            ("gone", 1, "grad_caps", None, None),
            ("level", 1, "degree_frame", "status", "C"),
            ("what", 1, "builder_late", "what gets\nnoticed", "TL"),
            ("creates", 1, "results", "results", "T"),
            ("again", 1, "buffett", "never stop\nlearning", "BR"),
            ("diverse", 1, "chess", "different problems", "T"),
            ("empowers", 1, "jobs_iphone", "old problems\na new way", "BL"),
            ("so", 1, "workbench", "use it", "L"),
            ("stay", 1, "end", "Stay learning.\nStay powerful.", "C"),
        ],
    },
    "b": {
        "src": "05F51BB5-27E8-45E7-8F9A-6BDE9FE53AD7",
        "name": "Bandwagon or awakening",
        "title": ("Bandwagon or Awakening?", "(the rise of entrepreneurship)", ["laptop_sunset", "lambo", "dawn_run"]),
        "beats": [
            ("it's", 1, "nathaniel", "something\ndifferent", "TL"),
            ("admired", 1, "applause", "admired", "T"),
            ("wasn't", 1, "cubicles", "not socially\nacceptable", "C"),
            ("nonconformity", 1, "odd_one", "nonconformity", "L"),
            ("entrepreneurship", 2, "ceo_bio", None, None),
            ("people", 1, "aware", "more aware", "T"),
            ("deciding", 1, "walk_out", "not\nlistening", "R"),
            ("told", 1, "classroom", "what you've\nbeen told", "T"),
            ("generation", 1, "rent_queue", "our\ngeneration", "L"),
            ("result", 1, "rent_queue", "the old\nsystem", "L"),
            ("but", 1, "snooze", "not all an\nawakening", "L"),
            ("riches", 1, "dubai", None, None),
            ("money", 1, "cash", None, None),
            ("go", 1, "guru", None, None),
            ("which", 1, "fork", "which one?", "T"),
            ("think", 1, "journal", "reasons", "TR"),
            ("because", 3, "closed_shop", "quits", "L"),
            ("whereas", 1, "dawn_run", "keeps\ngoing", "R"),
            ("change", 1, "dawn_run", "the change\nwas the point", "R"),
            ("so", 2, "mirror", "do you want change?", "T"),
            ("or", 2, "feed", "or someone\nelse's desires?", "TL"),
        ],
    },
}

QUERIES = {
    "library": "grand old library bookshelves dark", "workshop": "man welding sparks dark workshop",
    "laptop_beach": "digital nomad laptop beach", "laptop_sunset": "digital nomad laptop beach",
    "lambo": "dubai lamborghini influencer", "unread_books": "stack of unread books on desk aesthetic",
    "munger": "charlie munger reading books", "couch_tutorials": "watching youtube on laptop in bed at night",
    "dusty_books": "dusty old books cobwebs", "grad_caps": "graduates throwing caps",
    "degree_frame": "framed university degree on wall", "builder_late": "young man coding late at night dark room",
    "results": "champions lifting trophy", "buffett": "warren buffett reading newspaper office",
    "chess": "chess game close up", "jobs_iphone": "steve jobs iphone keynote 2007",
    "workbench": "hands woodworking workshop", "nathaniel": "nathaniel pov saxophone 10000 people",
    "applause": "crowd applauding standing ovation", "cubicles": "rows of office cubicles",
    "odd_one": "one red umbrella among black umbrellas", "ceo_bio": "instagram bio ceo founder entrepreneur",
    "aware": "crowd of young people city street", "walk_out": "man quitting job leaving office",
    "classroom": "students exam hall rows", "rent_queue": "dublin rental viewing queue",
    "snooze": "man hitting snooze alarm clock in bed", "dubai": "dubai lamborghini influencer",
    "cash": "stack of cash money", "guru": "get rich quick guru rented lamborghini course",
    "fork": "fork in the road", "journal": "man writing in journal at desk morning light",
    "closed_shop": "closed sign on shop door", "dawn_run": "lone runner at dawn empty road",
    "mirror": "man looking in mirror dark moody", "feed": "person scrolling instagram phone at night",
}
