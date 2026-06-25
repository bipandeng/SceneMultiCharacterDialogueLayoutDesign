# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

An experimentation workspace for Microsoft's AutoGen agent framework. Not a packaged application — standalone scripts exploring agent + tool-use patterns. Uses PyCharm as the IDE.

## Running scripts

Scripts use top-level `await` (see `autogen_test.py`). They work in an interactive Python session; to run as a plain script, wrap the entry point with `asyncio.run()`:

```bash
python -c "import asyncio; import autogen_test"
# or add `asyncio.run(main())` and run directly
python autogen_test.py
```

## Dependencies

No `requirements.txt` or `pyproject.toml` — packages are expected to be installed in the active interpreter:

- `autogen-agentchat`
- `autogen-ext[openai]`

## Model configuration

`autogen_test.py` uses `OpenAIChatCompletionClient` against an OpenAI-compatible endpoint serving `qwen3.5-plus`. The API key is currently hardcoded in the script — if refactoring, move it to an environment variable rather than leaving it in source.
