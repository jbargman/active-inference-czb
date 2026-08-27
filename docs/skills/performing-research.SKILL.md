---
name: performing-research
description: How research work is executed for Jonas Bärgman — the interruption budget and the two operating modes (interactive versus batch/overnight), the numbered-query convention (Qs, tagged by severity and audience) that lets a session continue instead of blocking, reproducibility rules (every quoted number from a committed script), verification and test discipline, the rule that every parameter value carries a motivation, replication of published results when a component comes from a paper, documentation and handover conventions, model-tier awareness for deciding who a question can be deferred to, and the statistical conventions. Use when executing any research or analysis task, when starting or ending a work session, when writing or reading a handover, when a result is about to be quoted, and when work passes between models or sessions.
---

# Performing research with Jonas

**Status: active. Approved by Jonas on 2026-08-27.** The live copy is
`~/.claude/skills/performing-research/SKILL.md` and is authoritative; a tracked mirror
sits in the project repository at `docs/skills/performing-research.SKILL.md` so that
revisions are versioned. When the live copy changes, update the mirror in the same
commit. Revision history is at the end.

Applies to all research tasks for Jonas, in any of his repositories. The
WaymoActiveInference project is the worked example.

## 1 The interruption budget

**Jonas's time is the scarce resource, not compute.** The most common failure is not a
wrong result; it is a session that stops to ask, and a queue of work that does not get
done because he was asleep. Getting this wrong in either direction is costly: asking too
often wastes his sessions, never asking produces unreviewed claims that reach documents.

The resolution is **raise a query and continue, do not stop and ask**. Nearly every
question that would justify interrupting can instead be recorded as a numbered query and
carried forward — the work continues, and he reads the register when he is next
available.

## 2 Two modes

**Interactive mode** — he is present and responding. Ask when a decision is genuinely
his, but prefer a recorded query plus a stated default over a blocking question.

**Batch mode** — he has handed over a list ("work through these", "while I sleep") and
will not be available. Then:

- **Never block the queue.** Work every item, in order, to the end of the list.
- A failed acceptance criterion, a contradiction, a stop condition, a judgment call —
  all become **numbered queries** (§3), and the session moves to the next item.
- If an item genuinely cannot proceed (its input does not exist), record why, and
  continue with the rest.
- Do not silently expand scope to work around a blockage. Record the blockage.
- Report **card by card**, not as one lump: he needs to see which item each issue
  belongs to.

**The one carve-out.** Some actions are skipped rather than performed, even in batch
mode, because they cannot be undone and were never authorized: sending email or any
outward-facing message, publishing, deleting or overwriting work that is not this
session's own, anything spending money, and anything requiring credentials. Skip the
action, raise a query, continue the queue. This is not a blocking stop — the queue keeps
moving; only that one action waits.

## 3 Queries: the flagging convention

Anything a session records instead of stopping to ask is a **query** — Jonas also calls
them **Qs**. The word is deliberate: a query is a point raised that needs an answer, so
it covers a blocking defect and a passing remark equally, and it presumes no fault. Some
queries record a *result* rather than a problem.

Each query has an identifier, two fields, and a line of text:

```
@A.2.Q2(blocker, jonas): group vs hierarchical lapse moves the population spread 39%,
                         while held-out likelihood separates them by 0.6 units.
@A.3.Q1(blocker, review): the FAIL is misspecification, not refutation — noise
                          accumulates through 15 s of empty pre-onset clip.
@B.1.Q1(minor, review): cyclist width taken as 0.6 m; no source found in the data.
```

- **Identifier** `@<card>.Q<n>` — `n` counts within the card, and **is never reused**,
  including across re-runs of that card, so an identifier always denotes one thing.
- **Severity**: `blocker` (later work may be built on sand), `judgment` (a defensible
  choice was made; someone should confirm it), `minor` (worth knowing, nothing waits).
- **Audience**: `review` (a more capable model can settle it — a verdict, a
  contradiction with documented findings, unchecked interpretation) or `jonas` (only he
  can: scope, authorization, a preference, anything outward-facing, or a parameter whose
  motivation is weak, §5). These are different queues, and his is the scarce one, so
  never route to `jonas` what `review` can absorb.

Every query appears in the per-item work-log entry **and** in the end-of-session
summary, **blockers first** rather than in numeric order — past a handful of queries,
severity is what a reader needs before sequence.

**Compile the register with a script**, never by hand: the work log stays the source of
truth, so a query cannot leave the register without leaving the log. Record an answer by
appending `RESOLVED <card>.Q<n>: <what was decided and why>` to the log, which moves the
query to the register's closed section and leaves the decision on the record. Working
example: `replication/czb/collect_queries.py` → `out/query_register.md`.

**A query is not a substitute for doing the work.** Raise it *and* proceed with the best
defensible choice, stating what was chosen. A query saying "did not attempt" is only
correct when attempting was impossible.

## 4 Session checklist

Copy this into the session and tick as you go:

```
- [ ] Read the entry-sequence documents (standing handover -> dated handovers -> plan -> work orders)
- [ ] Confirm the mode: interactive or batch
- [ ] Full test suite green BEFORE starting
- [ ] For each item: execute, check acceptance criteria, raise a query for anything unresolved
- [ ] For each item: append its own worklog paragraph, with tags inline
- [ ] Full test suite green AFTER, before committing
- [ ] Commit, message naming the item(s)
- [ ] End-of-session summary: what was done, per item, and every query repeated, blockers first
```

## 5 Parameters carry their motivation

**Every parameter value has a stated reason, next to the value.** A number in code with
no justification is unusable by anyone who comes later — they cannot tell whether it was
derived, measured, inherited from a source, or invented.

- Derived or measured: state the derivation or the measurement.
- Inherited from a paper or released code: cite it, and say where it differs from any
  other version of the same value.
- Chosen for convenience: say so, explicitly.
- **If the motivation is weak, raise a query addressed to `jonas`.** Weak means: it works but you
  cannot say why that value rather than a neighboring one, or it was tuned to make an
  output look right.

This is the "no voodoo constants" rule (Anthropic, n.d., citing Ousterhout): *if you do
not know the right value, how will anyone after you?*
Values that move a result substantially must be restated wherever the result is quoted.

## 6 Implementations from papers get replicated

**When a core component is implemented from a published paper, propose to Jonas that a
published result be replicated to verify the implementation** — and say which result you
would target and what would count as agreement.

An implementation that matches the equations can still disagree with the source, and
only a replication finds it. In this project the practice has repeatedly paid: comparing
against the authors' deposited runs showed our pipeline recovers their brake onsets to a
median error of 0.0 s; it also revealed that the paper's own worked example does not
match its deposit, and that the released code differs from its supplementary information
in more than a dozen documented places. None of that was visible from the equations.

Prefer a published number that is (a) quantitative, (b) not the one the implementation
was tuned on, and (c) cheap to reproduce. Where a deposit of the authors' own outputs
exists, it beats the paper's printed figures.

## 7 Reproducibility

**A result that exists only in a session transcript does not exist.** Every number that
will be quoted — in a document, a commit message, or a report to Jonas — comes from a
committed script whose output is written to a tracked file.

The cautionary tale is real. A paired-difference analysis run in-session produced
"θ_C − θ_B = 0.061, 95% HDI [0.037, 0.107], same sign on every resample", and it entered
a results document, a handbook chapter and a README. Reproduced as a committed script the
next day, it emerged that two of three variance sources had been held fixed; the true
statement was P ≈ 0.97 with an interval grazing zero. It stood for a day because nobody
could re-run it.

- Generated artifacts are **never** hand-edited — regenerate. This includes tables,
  figures, and Word/PDF builds.
- Log the exact invocation of every long-running command next to its output.
- Record seeds; re-run with a second seed before quoting anything stochastic.
- Store what a plot was drawn from, not just the plot.
- Gitignored intermediates are fine if the regenerating command is committed and works.
- When a document quotes a table, name the file it came from.

Follows Sandve et al. (2013), rules 1, 2, 4, 6, 7 and 9.

## 8 Verification

- **Run the full property-test suite before starting and before committing.** Within a
  batch, a targeted subset after each item is enough; the full suite must be green
  before any commit.
- New behavior gets new property tests, testing the *claim* rather than that the code
  runs.
- **Verifying by two independent routes is encouraged, not required** — a closed form
  against a numeric evaluation, a statistic against a differently-constructed estimate.
  Use it where a result is load-carrying or surprising.
- **A result contradicting a documented finding is surfaced, never silently
  reconciled**: name the document, quote the disagreement, raise a query for `review`.
- Never loosen an acceptance criterion to make something pass. Record the failure —
  that is the finding.
- Negative results are stated plainly and kept. Several of this project's most useful
  outputs are negative.

## 9 Documentation and handovers

- **Markdown is the source of truth**; Word and PDF are generated from it. Never edit a
  generated file. If a build fails because Jonas has the file open, write a `-vN` name
  and say so.
- **House style** for anything addressed to him: the `jonas-academic-writing` skill.
- **Citations follow APA style (currently 7th edition), always**, unless Jonas says
  otherwise for a particular piece of work or a venue demands its own format. In text:
  `(Sandve et al., 2013)`, or `Sandve et al. (2013)` when the authors are the subject
  of the sentence. Reference lists are alphabetical by first author, give the DOI as a
  full `https://doi.org/...` link, and carry a retrieval date only for sources with no
  fixed publication date. This applies everywhere a source is named — manuscripts,
  internal notes, code docstrings, commit messages and these skill files alike. Bare
  URLs are not citations.
- **Decisions are recorded with their reasoning and their location**, so they can be
  reopened knowing what they rested on.
- **The handover chain, within a repository or a chat**: a standing `handover.md` is the
  entry point; each work arc adds a dated `handover_YYYY-MM-DD.md` covering only that
  arc; the standing file points at the dated ones in order. Correct older files in place
  with a bracketed dated note rather than rewriting — the correction history is part of
  the record.
- **Precedence, stated the same way every time**: the repository beats any handover
  file; the latest dated file beats earlier ones; a handover that disagrees with the
  code is wrong, and should be said to be wrong out loud.
- A handover is written for someone who was not there: what the arc was, what was
  decided and why, what changed on disk, where to pick up, what the writing session may
  have got wrong, and every outstanding tag.

## 10 Know your own tier

A session must know whether it has anyone to defer to. Capability ranking, from
Anthropic's current model line-up (verified via the `claude-api` skill, table cached
2026-06-24; per-million input/output pricing given as the tier proxy):

| Tier | Models | IDs | $/1M in-out |
|---|---|---|---|
| 1 (top) | Claude Fable 5; Claude Mythos 5 (Project Glasswing) | `claude-fable-5`, `claude-mythos-5` | 10 / 50 |
| 2 | Claude Opus 5 (then Opus 4.8, 4.7, 4.6) | `claude-opus-5`, … | 5 / 25 |
| 3 | Claude Sonnet 5 (then Sonnet 4.6) | `claude-sonnet-5`, … | 2 / 10 |
| 4 | Claude Haiku 4.5 | `claude-haiku-4-5` | 1 / 5 |

Fable 5 is Anthropic's most capable widely released model; Mythos 5 shares its
capabilities. Your own model is named in your session environment — if you cannot
determine it, say so rather than guessing.

**If you are tier 1, there is nobody above you.** A `review` query does not summon a
better model; it only reaches Jonas, whose time is the thing being protected. Therefore:
resolve what you can rather than deferring it, reserve the `jonas` audience for what
genuinely needs him, and **self-review before finishing** — re-derive your own quoted numbers from their
committed scripts, since no stronger reviewer follows you. Review gates should be run at
tier 1 where possible.

**If you are tier 2 or below**, the `review` audience is a real escalation path: raise
the query, make the best defensible choice, and keep going.

## 11 What warrants a query

Not a list of reasons to stop — a list of things that must not pass silently:

1. An acceptance criterion failed, or a stop condition fired.
2. A result contradicts a documented finding.
3. A verdict, a pass/fail call, or an interpretation that will become a claim.
4. A new design decision: a scenario geometry, a change to a model's structure, a new
   uncertainty scheme.
5. Tests failed for reasons that are not obviously this session's own edit.
6. An error in earlier work, including a stronger model's. Reporting this is expected
   and welcome; fixing it quietly is not.
7. A parameter whose motivation is weak (§5).
8. An action in the §2 carve-out — skipped, not performed.

## 12 Statistical practice

- **State the uncertainty convention and resample every source of variance.** If two
  quantities are compared, ask what is shared between them and what is not: the shared
  part cancels, the independent parts do not. Holding one source fixed converts strong
  evidence into false certainty.
- **Compare as a difference, not as two intervals.**
- **Model comparisons are held out** — leave-one-condition-out or
  leave-one-participant-out — and the fold scheme is reported with the score.
- **Decision rules are stated before the experiment runs**, including what would count
  as failure. This is the preregistration logic (Center for Open Science, n.d.) at the
  scale of one analysis.
- **Name the ensemble a claim is about**, and do not generalize past it.

## 13 References

Anthropic. (n.d.). *Skill authoring best practices*. Retrieved August 27, 2026, from
https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices

Center for Open Science. (n.d.). *Preregistration*. Retrieved August 27, 2026, from
https://www.cos.io/initiatives/prereg

LangChain. (n.d.). *Handoffs*. Retrieved August 27, 2026, from
https://docs.langchain.com/oss/python/langchain/multi-agent/handoffs

MindStudio. (n.d.). *Context rot in AI agents: What it is and how to fix it with session
handoffs*. Retrieved August 27, 2026, from
https://www.mindstudio.ai/blog/context-rot-ai-agents-session-handoff-fix

Sandve, G. K., Nekrutenko, A., Taylor, J., & Hovig, E. (2013). Ten simple rules for
reproducible computational research. *PLOS Computational Biology, 9*(10), Article
e1003285. https://doi.org/10.1371/journal.pcbi.1003285

softaworks. (n.d.). *session-handoff* [Agent skill]. GitHub. Retrieved August 27, 2026,
from https://github.com/softaworks/agent-toolkit/tree/main/skills/session-handoff

**Verification status**, per §7's provenance rule: Anthropic (n.d.), Sandve et al.
(2013) and softaworks (n.d.) were fetched and read in full. Center for Open Science
(n.d.), LangChain (n.d.) and MindStudio (n.d.) were read only as search summaries —
treat their specific wording as unverified. The model line-up in §10 comes from the
bundled `claude-api` skill, whose table was cached 2026-06-24.

## 14 Revision history and open items

**v2, 2026-08-27 — rebuilt after Jonas's first review.** Settled by him: scope is all
research tasks; the handover chain applies within a repository or chat; the name follows
Anthropic's gerund convention; smaller items may share a session, and larger ones too
when he says so; two-route verification is not a hard requirement; a checklist is worth
trying (§4). Added at his request: batch mode and the flagging convention (§§1–3),
parameter motivation (§5), replication of published results (§6), and tier awareness
(§10).

Two points he asked for implications on rather than settling outright. Both are now in
force as written:

1. **May an executing session write interpretation?** The old work-order rule said "no
   verdict prose from the executing session" for one card. My proposal: an executing
   session **may** write interpretation — refusing to would gut batch mode — but marks
   it as a `(judgment, review)` query so a later reader knows it has not been checked. Only designated verdict cards keep the stricter "no verdict prose" rule.
2. **Full suite versus subset.** Implication of relaxing: a change can break something
   outside its own area and go unnoticed until later. Implication of not relaxing: as
   suites grow, every item in a batch pays minutes it does not need. §8 proposes the
   middle: full suite at session start and before every commit, targeted subset between
   items inside a batch. Nothing broken ever gets committed; per-item cost stays low.

**v4, 2026-08-27 — the query convention, after a first batch used it.** Cards A.1–A.4
were run as an overnight batch and raised nine queries, which was enough use to fix the
vocabulary and two details. Items are now **queries** (Jonas: "queries or Qs") rather
than tags: the identifier `@<card>.Q<n>` already read that way, the word spans a blocking
defect and a passing remark without implying fault, and some queries record a result
rather than a problem. Severity is now paired with an **audience** (`review` or
`jonas`), because the first batch's numbering had silently dropped the distinction and
those are different queues. Counters are never reused within a card; summaries list
blockers first; the register is compiled by script from the work log, and answers are
recorded with a `RESOLVED` line so decisions stay on the record.

**v3, 2026-08-27 — approved and made active.** Jonas endorsed the batch-mode carve-out
for unauthorized irreversible actions as written. Added: APA style for all citations and
reference lists (§9), applied to this file's own references (§13). Resolved: the skill
is mirrored into the project repository at `docs/skills/performing-research.SKILL.md`
so revisions are versioned; the live user-level copy stays authoritative, and Jonas
will say when he edits it.

Open, and worth revisiting once the convention has been used for a while: the two
proposals in items 1 and 2 above are in force as written, but neither has been tested
across a real overnight batch yet. If the query volume turns out wrong in either
direction — too many `minor` queries to read, or blockers buried among them — the
severity thresholds are the thing to tune first.
