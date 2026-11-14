# 09 · Scheduling + posting

**Trigger:** a reel is approved (08).

## Steps
1. Check it's both **PASS** (07) and **approved** (08). Either missing, it doesn't go in.
2. Slot it from the client's fixed slots (in `CONTENT-RULES.md`), keeping the week's balance (04 step 1).
3. Schedule in **Blotato** with the approved caption. [NEED: Blotato account, pricing and API checked before setup]
4. Check the CTA keyword's automation is live before the post date.
5. Verify the queue: right file, right caption, right slot.
6. Post day: check it went out. Move the file to `posted/`.

**Done when:** every approved reel is scheduled and checked in the queue.

## Rules
- Slots are set at onboarding and don't change mid-month.
- A fix after scheduling = pull it, re-QC, re-approve, new slot. It never posts as it was.
- Legacy: Kyle Ritchie stays on Metricool (drag files in, Frame links break, verify by thumbnail).
