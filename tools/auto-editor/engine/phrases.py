"""Split timed words into caption/edit phrases using the style's phrase rules."""


def split(words, rules):
    phrases, cur = [], []
    brk = set(rules["break_before"])
    for i, w in enumerate(words):
        if cur:
            prev = cur[-1]
            dur = w["end"] - cur[0]["start"]
            gap = w["start"] - prev["end"]
            end_sent = prev["w"][-1:] in ".?!"
            clause = prev["w"][-1:] in ",;:" and len(cur) >= 2
            if (end_sent or clause or gap > rules["pause_break"] or len(cur) >= rules["max_words"]
                    or dur > rules["max_sec"] or (w["norm"] in brk and len(cur) >= 2)):
                phrases.append(cur)
                cur = []
        cur.append(w)
    if cur:
        phrases.append(cur)
    # never end a phrase on a weak word ("the", "to", "a"...): push it onto the next phrase
    weak = {"the", "a", "an", "to", "of", "your", "my", "his", "her", "their", "our", "and", "with", "for", "in", "on", "at", "that", "this", "is", "are", "was"}
    for k in range(len(phrases) - 1):
        while len(phrases[k]) > 2 and phrases[k][-1]["norm"] in weak and phrases[k][-1]["w"][-1:] not in ".?!,":
            phrases[k + 1].insert(0, phrases[k].pop())
    # fold a lonely single word into its neighbour when it's short and not sentence-final
    out = []
    for p in phrases:
        if out and len(p) == 1 and (p[0]["end"] - p[0]["start"]) < rules["min_sec"] and out[-1][-1]["w"][-1:] not in ".?!":
            out[-1] = out[-1] + p
        else:
            out.append(p)
    return [dict(i=k, start=p[0]["start"], end=p[-1]["end"], text=" ".join(x["w"] for x in p),
                 words=[dict(w=x["w"], start=x["start"], end=x["end"]) for x in p]) for k, p in enumerate(out)]
