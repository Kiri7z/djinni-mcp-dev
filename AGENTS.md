# Project instructions

- Read README.md before making project changes.
- Write project documentation in English and communicate with the owner in Russian.
- Before implementing a capability, inspect available tools/skills and existing libraries or services. Record the selected option, license, evidence, and limitations in docs/research.md.
- Do not build custom parsers, exporters, comparison libraries, rounding utilities, protocol implementations, or other generic components when a suitable existing capability is available.
- This is not a ban on small application-specific glue code. Keep such code minimal and explain why it is needed.
- Do not begin implementation based on an unverified assumption about Djinni API, RSS, filters, authentication, or terms.
- Keep personal data and runtime artifacts under local/. Use synthetic data for examples and tests.
- Current scope includes public discovery plus an explicitly user-managed local profile, recommendation history, Markdown reports and exclusions. Do not access Djinni account state or send applications/messages.
- Read/import a CV only on the user's initial request or explicit refresh request. Questionnaire fields override matching CV fields. Never monitor documents or infer application/rejection status.
- Do not publish to GitHub or MCP Market as part of routine local work. Prepare and validate a reviewable result first.
- Test meaningful behavior and source failures; do not add speculative infrastructure or broad frameworks.
