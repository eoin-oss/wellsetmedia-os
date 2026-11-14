---
name: feedback-sfx-impacts-quieter
description: hard rule for every edit style: booms/hits, whooshes and flashes 4 dB quieter than the 19 Oct Kallaway levels
metadata:
  type: feedback
---
Booms/hits, whooshes and flashes sit 4 dB under the 19 Oct levels in every style: whoosh about -19 dB, boom/hit/stamp
about -13 to -15 dB at the peak, flash about -16 dB. Pops and clicks unchanged.
**Why:** after approving the Kallaway build (19 Oct) Eoin said they're a little loud: "one more hard rule".
**How to apply:** already set in jobs/themvsus/build.py SFXK + modes/kallaway-split/mode.json + the auto-edit skill;
carry it into every new style's SFX table. Related: [[feedback-show-what-he-points-at]].
