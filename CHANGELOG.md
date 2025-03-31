# Changelog

All notable changes to PyToolsmith will be documented in this file.

## 0.1.10 - March 30, 2025

### Added

- Added support for excluding tools (opposite of `subset`)

### Bux Fixes

- Fixed a bug where the `use_cache_control` was getting set for every tool, rather than just the last call.

## 0.1.9 - March 24, 2025

### Added

- Added support for creating the user message for a tool call with the batch tool.
- Support for setting a custom serialization function to be used with the batch tool added.

## 0.1.8 - March 23, 2025

### Added

- Added batch tool for Anthropic.

## 0.1.7 - March 17, 2025

### Bux Fixes

- Fixed a bug where overload calls didn't match the actual method call.

## 0.1.6 - March 15, 2025

### Bux Fixes

- Fixed a bug where non-copyable objects that are passed in to a tool call are handled.

## 0.1.5 - March 14, 2025

### Added

- Support for tooling groups added
- Support for custom tool messages added

## 0.1.4 - March 10, 2025

### Added

- Additional methods on `ToolLibrary` to support subsetting of tools. These include:
    - `get_all_tool_names()` - Returns a list of tool names as a string.
    - `get_tool_descriptions()` - Returns a dictionary of `{tool_name: tool_description}`
    - `subset()` - From a list of tool names, returns a new `ToolLibrary` with only those tools.

### Updated

- Updated Readme to have some additional sections, as well as better examples & formatting.
- Updated `ToolDefinition` to save its tool schema rather than re-generating it every time `build_json_schema` is
  called.

## 0.1.3 - March 9, 2025

### Added

- Basic tool calling support, without custom serialization.

## 0.1.2 - March 9, 2025

### Added

- Dataclasses to define most major types
- Additional tests for tool library

### Updated

- Removed dependency on pydantic to make library as lightweight as possible

## 0.1.1 - March 7, 2025

### Added

- Support for OpenAI

### Updated

- Updated ReadMe to have better examples & formatting.

## 0.1.0 - March 6, 2025

### Added

- Initial release with support for Anthropic and AWS Bedrock