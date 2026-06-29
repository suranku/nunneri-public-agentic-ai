# Semantic Kernel Runtime Adapter

Microsoft Semantic Kernel is treated as a runtime adapter target, not a model provider.

Generated files in `dist/semantic-kernel/` are derived from `dist/nunneri-runtime/` and map neutral Nunneri agents, commands, workflows, and approval gates into portable Semantic Kernel-oriented JSON manifests.

This repository does not install Semantic Kernel dependencies. Consumers can use these manifests as an integration contract when they add runnable agent orchestration.
