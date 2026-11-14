# Haynes: Application Question Best Practices (CANON)

_Source: Jeremy Haynes, Inner Circle weekly group call, ~14 December 2024. Transcript: `_source-pdfs/haynes-application-best-practices-2024-12-transcript.txt`._

**What this is:** how to build the application (and scheduler) in a call funnel. Load it any time an application, qualifying form or booking step is written or audited.

**Sister canon:** `Ads/haynes-demographic-spectrum.md` (section 5, pixel conditioning on the datapoint that tracks buyers), `Ads/haynes-high-converting-ads.md` (the ad frames people before they reach the form), `Ads/haynes-if-this-then-that-diagnostics.md` (when booking or show rates break).

---

## Rule 0: every question does one of two jobs, or it gets cut

1. **Qualifier.** It routes the person to the pixeled path or the unpixeled path.
2. **Sales ammo.** The closer actually uses it on the call, and the automation (pre-call texts, emails, hammer-them content) actually changes based on it.

If a question does neither, delete it. It only adds friction and raises the cost per call. Haynes polls rooms and finds about half of businesses think their closers use application data, and most of them are wrong. **Secret shop your own funnel.** Fill it out a specific way. If the pre-call texts, emails, the closer's selfie video and the call itself never mention your answers, remove those questions.

Copying another business's application is pointless, because a good application is built around what that specific sales team uses.

## Question 1: easy, multiple choice, useful on the call

- Something anyone can answer in one tap that starts the flow.
- It can be a qualifier, but **never the money qualifier**, and **never contact details** (no name, email or phone first).
- It should change the direction of the sales conversation. Example: "How many properties do you own: 0 / 1-5 / 6+". Buyers with at least one property bought at 3.3x the rate of those with none, and the call runs differently for each.
- Set the ranges where the conversation changes. Evoke Advisors ($23B AUM, $1M minimum) uses $1M / $5M / $10M / $25M / $50M / $100M+, because a $1M household and a $100M household live in different worlds: different problems, selling points, communication style, number of touchpoints and meetings. 46% of their leads come through at $5M+.

## Question 2: the financial qualifier, stated directly

Haynes's wording: "This costs [X] on average. Assuming we get on the call and everything makes sense for you, do you have this amount available, or can you get approved for funding?"

The answers:
- **Yes, I have it** -> continue.
- **No, that's too expensive** -> out. The wording matters: a plain "no" can be flipped on a call, but "too expensive" is "broke bait", and it lets low-budget people identify themselves. Plant broke bait in later questions too.
- **I can get approved for funding** -> a logic branch to a follow-up with the funding partner's actual criteria. Under about $5K a day in spend, a direct credit question is usually fine because it's buried in logic. At higher spend, ask it compliantly: "If you went to a car dealership for financing, would you get approved with favorable terms based on your current score?"

Sometimes questions 1 and 2 are all you need before contact details.

## Questions 3 onward: sales ammo only

- Ask the sales team what they want to know. Some answers will be useless ("do they have money and want to do it now"). Others reflect how the process really works.
- A follow-up question that only appears based on an earlier answer is a cheap way to get detail without friction.
- **Urgency questions are ammo, not qualifiers.** Don't disqualify "within a year". Use it on the call to build urgency.
- **"Will you be at a desk with undivided attention?" doesn't belong in the form.** Put it in reminders and pre-call messages.
- Short typed answers are fine after question 2. More friction filters for intent, but it also screens out the needs-convinced 30%, who can still buy if the automation and sales process are built for them.

## Routing and the pixel

- **Qualified** -> calendar -> confirmation page that fires the pixel event.
- **Unqualified but sellable** -> can still book, but goes to a separate, unpixeled confirmation and shows up in the closer's calendar with a different label so they know how to approach it. The ads manager under-reports total calls (say 9 shown vs 12 booked), and that's intentional, because what the ads manager sees decides who Meta goes after next.
- **Too expensive** -> out, unpixeled. You can still capture them and route them to a downsell or a checkout page if one exists. James (alcohol-free offer) captures under-$150K applicants for a $5K offer and adds about $30K a week while spending $15-20K a day, without pixeling them.

## Form mechanics

- **One question visible at a time.** Showing every question at once looks like a lot of work and loses people.
- **Application and scheduler in the same step.** Separating them costs **about 50% of qualified applicants on average** (Haynes says this isn't an exaggeration). Combined, almost every qualified person books.
- **Contact details come last, then a partial submit, then the calendar,** with name, email and phone prefilled so all they do is pick a time.
- **Tools:** Typeform plus Calendly wins his split tests (in a recent test, $125 vs $190 cost per call against a combined GoHighLevel setup). GoHighLevel can work if it's a survey with one question at a time and the calendar embedded as HTML in the last step, set to no redirect. If you must separate them, a strong setter team that chases qualified non-bookers recovers some of the loss.

## Use the answers before the call

- Send a **pre-call selfie video** that names their answers ("Saw you already own two homes in Phoenix...") and links to a video for their situation. Haynes's own buyers say this is what tipped them over.
- **Segment automation by answer:** separate hammer-them sequences for each meaningful answer band. A big gap in close rate between segments ("people with a property buy 3.3x more") points to communication that isn't adapted to the weaker segment. It isn't a reason to celebrate the stronger one.
