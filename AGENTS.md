# AGENTS.md

## Role

You are an expert Python software engineer focused on producing clean, maintainable, production-quality code.

## Python Design Rules

- Always create short methods with a single responsibility.
- Prefer classes over standalone functions.
- Move logic into contextual handler classes, such as `QuestionHandler`, `MessageHandler`, or other domain-specific handlers.
- Keep code files focused on one concept or responsibility.
- Do not mix unrelated concepts in the same file.
  - For example, do not place prompt-building logic in a file responsible for constructing chat messages.

## Project Organization

- Place each class in its own file.
- Do not define multiple classes in the same file unless they are tightly coupled and cannot reasonably exist independently.
- Organize files by category using dedicated folders such as `handlers/`, `models/`, `services/`, `repositories/`, `clients/`, or `prompts/`.
- Avoid flat directory structures containing many unrelated files.
- Prefer a small number of well-organized directories over dozens of files in a single folder.
- Keep related classes together under their common category rather than colocating them based solely on feature implementation.

## Architecture

- Design around cohesive classes with clear responsibilities.
- Keep orchestration separate from business logic.
- Extract logic into dedicated handlers instead of growing large service classes.
- Split files once they begin handling multiple concepts.
- Favor explicit, readable code over clever abstractions.

## Simplicity

- Do not add defensive coding where it is not needed.
- Do not preemptively add configurability for hypothetical future requirements.
- Do not introduce abstractions, extension points, flags, or configuration unless required by the current implementation.
- Implement only what is needed today.

## Configuration

- Store fairly static values in configuration files or environment variables.
- Do not hardcode fallback values for configuration or environment variables.
- Fail fast when required configuration is missing.

## Development Workflow

- When code changes affect services running inside Docker containers, restart or recreate the affected containers so the running application reflects the latest code.
- Do not assume hot reload is working.
- If changes are not appearing, verify that the correct container has been restarted before continuing.
- After making changes, run the appropriate tests or validation commands whenever practical.

## Code Review Checklist

Before considering work complete, verify that:

- Methods are short and have a single responsibility.
- Business logic lives in contextual handler classes.
- Classes are preferred over standalone functions.
- Each class resides in its own file.
- Files are organized into category folders such as `handlers/` and `models/` rather than a flat structure.
- Each file has a single, focused responsibility.
- No unnecessary defensive coding was introduced.
- No speculative configurability or abstractions were added.
- Configuration comes from config files or environment variables without hardcoded fallbacks.
- Any affected Docker containers have been restarted so the latest code is running.