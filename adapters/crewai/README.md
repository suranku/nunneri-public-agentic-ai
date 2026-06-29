# CrewAI Runtime Adapter

CrewAI is treated as a runtime adapter target, not a model provider.

Generated files in `dist/crewai/` are derived from `dist/nunneri-runtime/` and map neutral Nunneri agents, commands, workflows, and approval gates into portable CrewAI-oriented JSON manifests.

This repository does not install CrewAI SDK dependencies. Consumers can use these manifests as an integration contract when they add a runnable CrewAI application.
