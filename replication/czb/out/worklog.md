# CZB work-order log

One paragraph per completed card, appended in order, per the session pattern in
`docs/czb_work_orders.md` §4. Each entry states the card, what was produced, whether the
acceptance criteria were met, and anything a successor should know.

## 2026-08-27 — Card S.1: draft the `perform-research` skill

Drafted `C:/Users/bargman/.claude/skills/perform-research/SKILL.md` (210 lines, within
the card's ~300-line limit). Contents follow the card's five required areas —
reproducibility, verification, documentation, the between-model handover protocol, and
statistical practice — each written as rules already in force in this repository rather
than as new proposals, with the 2026-08-26 paired-difference overstatement used as the
worked cautionary tale for the "no in-session-only numbers" rule. The research step
covered Anthropic's skill-authoring guidance (fetched and verified: frontmatter limits,
sub-500-line body, one-level-deep references, matching freedom to task fragility, no
time-sensitive content), Sandve et al. (2013) *Ten Simple Rules for Reproducible
Computational Research* (fetched and verified; rules 1, 2, 4, 6, 7 and 9 are the ones
borrowed), the published `softaworks/agent-toolkit` session-handoff skill (verified
structure — its section set and its no-unresolved-placeholders validation rule are
borrowed), and LangChain's handoff documentation, a context-rot discussion and the
Center for Open Science preregistration pages (read via search summaries only, and
marked unverified in the draft accordingly). Frontmatter validated against the
documented constraints: name 16 characters, lowercase and hyphens, no reserved words;
description 737 characters, third person, states both what the skill covers and when to
use it. Acceptance criteria met: the file exists, is under the line limit, cites its
sources, and ends with an explicit "for Jonas's review" note. The card's stop condition
was exercised rather than guessed around — seven items where I could not tell whether a
practice is project law or one session's habit are listed as open questions in the
draft's §7 (scope, name form, one-card-per-session strictness, whether an executing
session may ever write interpretation, whether two-route verification is a hard
requirement, whether full-suite testing stays non-negotiable as suites grow, and whether
the skill should ship a session-start script). **Note for Jonas:** placing the file
under `~/.claude/skills/` makes it discoverable to sessions immediately, so the body's
first line marks it as an unapproved draft; if you want it genuinely inert until you
have read it, move the directory aside and restore it after review. No repository code
was touched; the full test suite (123 tests across four files) passed before and after.

## 2026-08-27 — Card S.1 (revision v2): the skill reworked after Jonas's comments

Jonas read v1 and made one structural objection and several additions. The objection:
the escalation conditions were too strict for how he actually works — he often queues a
batch of tasks and is unavailable (overnight), and a session that stops to ask wastes
the batch. The skill was rebuilt around that. Renamed to `performing-research`
(Anthropic's gerund convention, which he approved), so the old `perform-research`
directory was removed. New §1 states the interruption budget explicitly — his time is
the scarce resource, and the resolution is *flag and continue, do not stop and ask*.
New §2 defines interactive versus batch mode: in batch mode nothing blocks the queue,
with a single carve-out for actions that cannot be undone and were never authorized
(sending mail, publishing, deleting others' work, spending money, using credentials) —
those are skipped and tagged, not performed, and the queue still moves. New §3 defines
the flagging convention he asked for: `@REVIEW` (a more capable model should assess) and
`@JONAS` (only he can settle it), each with severity `(blocker|judgment|minor)`, both
greppable, both required in the per-item worklog entry *and* the end-of-session summary,
with the rule that a tag never substitutes for making the best defensible choice. §4 is
the session checklist he suggested trying. §5 is his new rule that every parameter value
carries a motivation, with weak motivations tagged `@JONAS` (this coincides with the
no-voodoo-constants guidance in Anthropic's skill docs, cited). §6 is his other addition:
when a core component comes from a paper, propose replicating a published result to
verify the implementation — grounded in what that practice already caught here (OSF
deposit agreement at 0.0 s median onset error; the paper's worked example not matching
its own deposit; thirteen code-versus-SI differences). §10 answers his question about
model tiers: the ranking was taken from the bundled `claude-api` skill rather than from
memory — tier 1 Fable 5 / Mythos 5, tier 2 Opus 5, tier 3 Sonnet 5, tier 4 Haiku 4.5 —
with the operational consequence that a tier-1 session has nobody above it, so it must
resolve rather than defer and must self-review its own quoted numbers. His other answers
are folded in: scope is all research tasks, the handover chain applies within a
repository or chat, smaller items may share a session, two-route verification is not
mandatory. Two of his answers asked what the implications were rather than settling the
question, so §14 carries proposals instead of rules: (a) an executing session **may**
write interpretation but tags it `@REVIEW(judgment)` as unreviewed — refusing outright
would gut batch mode — with the stricter "no verdict prose" kept only for designated
verdict cards; (b) full test suite at session start and before every commit, targeted
subset between items inside a batch, so nothing broken is ever committed while per-item
cost stays low. File is 292 lines, within the card's limit; frontmatter validated
(name 19 characters, description 817 of 1024). @JONAS(judgment): the skill is still a
draft and still lives outside version control — its revisions are not tracked the way
the handbook's rounds are; a canonical copy in a repository is offered in §14. Full
suite (123 tests) green before and after; no repository code touched.

## 2026-08-27 — Card S.1 (v3): skill approved and made active

Jonas approved the skill and the batch-mode carve-out as written, and added one general
rule: APA style for all citations and reference lists unless he says otherwise. That is
now §9 of the skill, and §13 was rewritten as a proper APA reference list with the
in-text citations converted to author-date form; the verification status of each source
is kept as a note beneath it, since the provenance rule requires distinguishing what was
fetched in full from what was read only as a search summary. The DRAFT banner is
replaced by an active status line. He also asked for the skill to be tracked, so it is
now mirrored at `docs/skills/performing-research.SKILL.md`, byte-identical and verified
by `diff`, with `docs/skills/README.md` recording that the live user-level copy stays
authoritative, that the mirror must be updated in the same commit, and why the mirror is
deliberately not laid out as `.claude/skills/` (a second active copy would compete with
the live one). He will say when he edits the live copy. No tags outstanding from this
revision; the skill is 318 lines, still within the card's limit. No repository code
touched.
