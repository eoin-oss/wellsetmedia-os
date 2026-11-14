# 11 · Text hooks (every video)

**Rule: every video that ships gets a text hook.** Reels, podcast clips, seminar shorts, talking heads, client and
own. No hook, not done. Checked at the review-reel step of [10](./10-finish-to-approval.md).

The text hook is the on-screen title that runs from frame one. It works with the spoken hook, it doesn't repeat it.

## 1 · What it says (substance)

- **Subject + one of three:** the dream outcome, a teaser (curiosity gap), or a state change (from → to).
  Or a mix. "FROM A SCARED LITTLE BOY / TO THIS" = state change. "HOW TO MAKE A MAN / STEAL A TV" = teaser.
- **Add a charge, never summarise.** The text sits beside the spoken promise and adds a warning, admission,
  contradiction or removal ([HOOK-PATTERNS](../content/HOOK-PATTERNS.md) #4). If it's the same words he says in
  the first 3s, rewrite it.
- **Specific beats vague.** Real numbers from the clip: "22 days" not "a few weeks", "50K" not "loads".
  Only numbers the video actually says. Never a price we charge (no price in videos, ever).
- **Use the niche's words.** The words the top accounts in the niche use (the weekly-research hook bank), and
  the client's own terms ("contracted", "reference experiences", "self hypnosis").
- **True to the clip.** No claim the client doesn't make on camera. No swearing on Kyle.

## 2 · How it's written (form)

- **Two lines.** Break where the phrase breaks: never split words that belong together
  ("LITTLE BOY" stays on one line). Short videos can go one line; never three unless it can't fit.
- **No filler or transition words:** and, but, so, then, therefore, just.
- **No punctuation** except brackets ( ) and quotation marks " ". No commas, full stops, question marks,
  dashes. Apostrophes inside words are fine.
- **All caps.**

## 3 · How it looks

- **Font:** extremely readable. House default = RODE Noto Sans CJK SC B, solid white, all caps, no shadow on black,
  no animation. (CapCut's default is fine for quick edits.)
- **Placement:**
  - **9:16 with a band** (podcast clips, 4:5 picture inside 9:16): centred in the black band above the picture,
    last line about 44px above the picture's top edge.
  - **Full-frame 9:16:** about a third of the way down, never over the eyes or mouth.
- **On for the whole video** when it sits in a band; at least through the spoken hook when it's over picture.

## 4 · Check before handover

- [ ] Every video in the batch has one
- [ ] Two lines, natural break, nothing clipped at the edges (render a still of each)
- [ ] No punctuation except ( ) and " "
- [ ] One specific detail (number, name, the client's own word)
- [ ] Not a repeat of the spoken hook
- [ ] Logged in the client's hook list (job `text-hooks.tsv` for podcast clips) so wins can be tracked in
      [HOOK-PATTERNS](../content/HOOK-PATTERNS.md)

## Tools

Podcast clips (sidecap 9:16): write the `line` column in `jobs/<job>/text-hooks.tsv` (`|` = line break), then
`python3 tools/auto-editor/engine/podhook916_plain.py jobs/<job> jobs/<job>/text-hooks.tsv`. It retexts the title
in place (deleting these titles crashes Resolve).

Source: Kallaway's text-hook breakdown (level one) + Eoin's hook log, 21 Oct 2026. First run: Kyle x James Hempton
podcast clips, 21 hooks.
