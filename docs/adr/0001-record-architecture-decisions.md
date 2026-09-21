# 0001. Record architecture decisions

* Status: accepted
* Date: 2026-09-21

## Context

The port re-creates a large R package in a different language. Many structural choices are not forced by R, such as how packages are cut and how R’s generic methods are mapped to Python along with the analysis results. These decisions are made once and shape every later module. Without a record, the reasons behind them get lost, and each new unit reopens the same questions.

PORTING_NOTES.md records where individual symbols deviate from R. It does not cover decisions about the package's overall structure.

## Decision

* Architectural decisions are recorded as ADRs in docs/adr/, one file per decision, using the template.md format.
decision, in the format of template.md.
* A decision counts as architectural when it constrains more than one module or is expensive to reverse.
or is expensive to reverse.
* Per-symbol differences from R stay in PORTING_NOTES.md.
* An accepted record is not edited. A changed decision gets a new record that supersedes the old one.
supersedes the old one.

## Consequences

* New code can be checked against a written rule rather than a recollection.
* Anyone taking over the repository can see why it is built the way it is.
* Each structural decision costs a short write-up before the code lands.

