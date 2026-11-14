# Take-picker brief (no-script shoots)

Input: `takes.txt` (one line per take: id, start second, text) after the speaker filter and stutter fixes.
Output: `takes_keep.json`, a JSON list of take ids **in playback order**.

Pick the version of the piece the speaker was trying to say:
1. For every point he makes, keep the **last complete, clean take**: the final attempt that finishes the thought
   without a stumble. Earlier attempts, half-sentences and abandoned openings go.
2. If a later take is worse (cuts off, grammar breaks: "nothing else can't"), keep the better earlier one; "final" means
   final *working* take.
3. Drop: banter, meta-talk ("how do you say that again", "how long do we have"), reactions ("yeah", "fuck me"),
   instructions to/from the crew, anything addressed to someone off camera.
4. The kept takes must read as one clean monologue: hook/claim -> explanation -> payoff/advice. Don't reorder unless the
   order on camera breaks the logic.
5. Never invent or splice words inside a take. If a point never got a clean take, leave it out and say so.
Write a one-line reason per dropped *content* take (not per "yeah") in `takes_reasons.md`.
