# Instructor guide

## Recommended duration

75-100 minutes.

- 10 minutes: architecture and migration context
- 15 minutes: setup and mock run
- 20 minutes: agent contract exercise
- 20 minutes: routing and cross-domain tests
- 15 minutes: trace review
- 10-20 minutes: production discussion or real-tool extension

## Facilitation guidance

Do not begin with Python internals. Start with the business problem and agent boundaries. The core lesson is that agent descriptions and contracts are part of the orchestration design.

Use mock mode first so authentication or service availability does not block learning. Move to Foundry only after participants have validated the flow.

## Debrief questions

1. Did the router select the minimum required specialists?
2. Which description changes improved or degraded routing?
3. What evidence did the Strategy Advisor use?
4. Where should authorization be enforced?
5. Which parts need deterministic control in production?
6. When would you convert this into an explicit Agent Framework workflow?

## Important caveats

- The included data is synthetic.
- The sample is advisory and does not make credit decisions.
- The sample tool adapters are placeholders for governed integrations.
- Package APIs may evolve; validate the current Agent Framework documentation before delivering the lab.
