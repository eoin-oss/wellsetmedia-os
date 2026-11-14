"""The locked scripts. Edit here, re-run generate.py.

Source of truth is clients/kyle-ritchie/content/VIRAL-FORMATS-GUIDE.md —
this file mirrors it so the generator can read it. If they disagree, the guide wins.
"""

VIDEOS = {
    "01": {
        "slug": "01-make-more-money",
        "title": "10/10 habits to brainwash yourself to make more money",
        "sub": "",
        "items": [
            "Use visualisation to connect to the feeling of already having",
            "Only speak about money as if it's abundant. Never from lack",
            "Close the gap between thought and action",
            "Spend time around people who earn more than you",
            "Never break a promise to yourself — even the smallest",
            "Track every micro piece of evidence you're becoming the new version",
            "Don't negotiate or flinch when you pay for things",
            "Remove “there isn't enough” from any vocabulary you speak out loud",
        ],
    },
    "02": {
        "slug": "02-dangerously-present",
        "title": "10/10 habits to be dangerously present",
        "sub": "(backed by neuroscience)",
        # items as Kyle said them on camera, 7 Oct 2026 (5-8 differ from the 4 Oct guide)
        "items": [
            "No stimulation for the first 30 minutes after you wake up",
            "Feel your feet every single time you walk",
            "Notice the smallest sound you can hear right now",
            "Feel how the surface beneath you is supporting you",
            "Watch your thoughts arrive without grabbing onto any of them",
            "Meditate daily, even for 5 minutes",
            "Take one slow deep breath in through your nose and focus on the breath leaving your body",
            "Hold your focus on one object, every single aspect of it, and notice your mind clear",
        ],
        # one image per item, matched to the line (7 Oct rule: semantic, moody film, soft halation)
        "images": ["present-04.jpg", "present-walk.jpg", "present-14.jpg", "present-10.jpg",
                   "present-12.jpg", "present-meditate.jpg", "present-23.jpg", "present-24.jpg"],
    },
    "03": {
        "slug": "03-ridiculous-flow",
        "title": "10/10 habits to reach a ridiculous amount of flow",
        "sub": "",
        "items": [
            "Remove all distractions",
            "Complete one task at a time",
            "Create ultimate clarity — clarity is power",
            "Be organised as fuck",
            "Live as if the result is already done",
            "Seven to eight hours of sleep, every night, consistently",
            "Sauna",
            "Tell people you love them",
        ],
    },
    "04": {
        "slug": "04-obscenely-abundant",
        "title": "10/10 habits to be obscenely abundant",
        "sub": "",
        "items": [],          # not written yet
    },
    "05": {
        "slug": "05-delusionally-confident",
        "title": "10/10 habits to be delusionally confident",
        "sub": "",
        "items": [
            "Always follow through on your word. Never break a promise to yourself",
            "Take action fast",
            "Act like the guy before you become the guy",
            "Close the gap between thought and action — create undeniable evidence that you are who you say you are",
            "Be connected to God",
            "Be around positive people",
            "Compliment strangers",
            "Train consistently",
        ],
    },
    "06": {
        "slug": "06-disgustingly-motivated",
        "title": "10/10 habits to be disgustingly motivated",
        "sub": "",
        "items": [],          # not written yet
    },
    "07": {
        "slug": "07-psycho-cybernetics",
        "title": "Psycho-Cybernetics in 60 seconds",
        "sub": "",
        # Kyle's Frame read, 9 Oct 2026. Images abstract but tied to each concept
        "items": [
            "Self-image",
            "Success mechanism",
            "Failure mechanism",
            "Negative feedback",
            "Synthetic experience",
            "Theatre of the mind",
            "De-hypnotise yourself",
            "Emotional scar tissue",
            "Let it happen",
            "Boundaries of the possible",
        ],
        "cover": [f"pc-c{i}.jpg" for i in range(1, 7)],
        "images": [f"pc-{i:02d}.jpg" for i in range(1, 11)],
    },
    "08": {
        "slug": "08-flow-state",
        "title": "10/10 habits to unlock a ridiculous amount of flow state",
        "sub": "",
        # Kyle's Frame read, 9 Oct 2026, items as spoken
        "items": [
            "Remove all distractions from your physical and digital environment",
            "Complete one task at a time",
            "Create ultimate clarity, because clarity is power",
            "Be organised as fuck",
            "Live as if the result is already done",
            "7 to 8 hours of sleep every single night, consistently",
            "Sauna 4 to 7 times per week",
            "Tell people you love them",
        ],
        "cover": [f"fs-c{i}.jpg" for i in range(1, 7)],
        "images": [f"fs-{i:02d}.jpg" for i in range(1, 9)],
    },
}
