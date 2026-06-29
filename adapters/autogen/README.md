# AutoGen Runtime Adapter

Microsoft AutoGen is treated as a runtime adapter target, not a model provider.

Generated files in `dist/autogen/` are derived from `dist/nunneri-runtime/` and map neutral Nunneri agents, commands, workflows, and approval gates into portable AutoGen-oriented JSON manifests.

This repository does not install AutoGen SDK dependencies. Consumers can use these manifests as an integration contract when they add AgentChat, Core, Studio, extensions, or distributed-runtime implementations.
