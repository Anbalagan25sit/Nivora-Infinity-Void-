#!/usr/bin/env python
"""Run the required checks."""

print("=" * 80)
print("COMMAND 1: from livekit.agents import llm; print(dir(llm))")
print("=" * 80)
try:
    from livekit.agents import llm
    print(dir(llm))
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("COMMAND 2: import livekit.agents; print(livekit.agents.__version__)")
print("=" * 80)
try:
    import livekit.agents
    print(livekit.agents.__version__)
except Exception as e:
    print(f"Error: {e}")

print("\n" + "=" * 80)
print("COMMAND 3: FunctionContext and other attributes check")
print("=" * 80)
try:
    from livekit.agents import llm
    print(f"hasattr(llm, 'FunctionContext'): {hasattr(llm, 'FunctionContext')}")
    print(f"hasattr(llm, 'function_context'): {hasattr(llm, 'function_context')}")
    context_related = [x for x in dir(llm) if 'unction' in x or 'Context' in x or 'callable' in x or 'Tool' in x]
    print(f"Related attributes: {context_related}")
except Exception as e:
    print(f"Error: {e}")
