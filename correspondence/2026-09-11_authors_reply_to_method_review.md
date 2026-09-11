# Reply from the authors of Schumann et al. (2026) to our review

*Filed 2026-09-11, when Jonas passed it on with the note: "I do not think there are any
actions to be taken, but file the answer away." Sent by one of the paper's authors, writing
as Julian Schumann's co-author; the sender's name was not part of the text passed on. It
answers the analysis Jonas sent the authors, which rests on `docs/method_review.md`
(2026-08-23) and the authors' edition of the handbook (`docs/handbook_authors/`).*

*Private correspondence. This folder is excluded from every transfer bundle by the `never`
rule in `transfer/transfer_policy.yaml`, and the letter should not be quoted outside the
project without the sender's agreement.*

## The letter, verbatim

> Thank you for reaching out, it's very kind of you to do this. Let me reassure you that
> both Julian and I were actually happy and excited to receive your analysis. Your doing
> this shows that our work is immediately relevant, and, being a strong proponent of open
> science himself, Julian got very enthusiastic to look into everything right away. So if
> he was affected emotionally by this, the effect is positive😊
>
> Julian contacted you earlier about this but did not elaborate on our follow-up findings.
> In short, it turned out there were no errors in the model itself or in the simulations.
> All issues your analysis flagged were either due to several errors in reporting (e.g., a
> mislabeled scenario in a figure caption, typos in equations) or limitations/simplifications
> of the model that were not explicitly discussed in the paper but are not errors (like the
> starting point of evidence accumulation or off-road behavior). Still, to correct the typos
> and labeling issues, Julian will prepare an official correction for Nature Communications.
>
> Overall, we were quite relieved that after such a detailed replication study, there
> weren't any serious issues in the model design/implementation. Of course, we would have
> been quite unhappy if we found something that impacted our claims in the paper. But that
> would be not because you did the analysis but because we missed those when working on the
> model. So thanks a lot for your work, we really appreciate it!
>
> NB1: this is my take based on how I know Julian, and I might be off in my estimate of how
> he was (not) affected by the process. So feel free to approach him by email on in person
> at ITSC to talk about this.
>
> NB2: it doesn't seem Claude hallucinated any of the issues, but it did interpret some
> things quite one-sidedly (for instance, the implications of road departures). We can
> elaborate more at ITSC if you're interested.

## What it says, in five points

1. **No errors in the model or the simulations**, in the authors' assessment after their
   own follow-up.
2. **Every flagged issue falls into one of two classes**: errors in reporting (a mislabeled
   scenario in a figure caption, typos in equations), or limitations and simplifications
   that the paper did not discuss but that are not errors (the starting point of evidence
   accumulation; the off-road behavior).
3. **An official correction to Nature Communications** is being prepared by Julian
   Schumann for the typos and the labeling.
4. **An open invitation** to talk with Julian Schumann, by e-mail or at ITSC.
5. **On the analysis itself (NB2):** none of the issues was hallucinated, but some were
   interpreted one-sidedly; the road departures are the example given, and the authors
   offer to elaborate at ITSC.

## How it bears on our documents

Recorded so that anyone writing to the authors, or revising these documents, starts from
it. No document is changed now, per Jonas.

- **It does not contradict a finding of fact.** Our review never claimed an error in the
  model or the simulations: `docs/method_review.md` §1 states that the mechanism "is
  implemented in the released code and does what the paper says it does", and that the
  authors' code reproduces their deposit to the timestep. The difference is in
  classification and emphasis: we listed three things that "did not hold up as well", and
  the authors class them as reporting errors or undiscussed limitations.
- **The road departures (NB2)** are `docs/method_review.md` §4.1, whose closing sentence is
  marked [Opinion] ("a human driver facing the 25 m/s, 3.5 s gap condition would not leave
  the road in half of the trials"), and chapter 05 of the authors' edition, which reads the
  departures "as a property of the lane-change control at speed rather than as a deliberate
  trade-off [Opinion]". Those are the two places the authors' comment points at. What the
  other side of the interpretation is, they have offered to explain at ITSC.
- **The starting point of evidence accumulation** is `docs/method_review.md` §4.2, and
  chapters 02 and 05 of the authors' edition (the pre-conflict drift and `EA_init`). The
  authors class it as a simplification rather than an error; the review called it "the most
  important methodological point", marked [Opinion].
- **The mislabeled scenario in a figure caption** plausibly accounts for §4.3 of the review
  (the Fig. 3 worked examples not matching the deposit, and the Fig. 3b explanation
  reading reversed). That is our reading of their sentence, not something they said; worth
  confirming when the correction appears.
- **The typos in equations** correspond, as far as we can tell, to the SI items in
  `docs/method_review.md` §5 and §8 (for example the severity factor of SI Eq. 48).

**When the correction is published:** add a dated note to `docs/method_review.md` §4.3 and
§8, and to the passages of the authors' edition that cite the affected captions or
equations, pointing at the correction.
