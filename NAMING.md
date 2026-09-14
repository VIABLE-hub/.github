# Repository names and maturity

New components use `viable-<family>-<component>[-<variant>]` with lowercase kebab-case.
Families: `protocol`, `crypto`, `service`, `wallet`, `sdk`, `tool`, `app`, `infra`,
`demo`, `research`, `benchmark`, `docs`. Use language suffixes only for platform or SDK distinctions.

Existing repository URLs remain stable until a reviewed migration updates consumers,
submodules, CI and release references. Human-readable README titles and accurate
repository descriptions take priority over cosmetic URL changes.

Label maturity explicitly: Research, Prototype, Pilot, Supported release, Reference,
Planned or Archived. A repository's existence or successful build is not certification.
Private code and research are not made public merely for presentation.
