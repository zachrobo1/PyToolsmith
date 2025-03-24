from collections.abc import Callable
from dataclasses import dataclass, field
from enum import EnumType
import inspect
from types import GenericAlias, UnionType

# noinspection PyUnresolvedReferences
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    NewType,
    _LiteralGenericAlias,
    _UnionGenericAlias,
    get_args,
    get_origin,
    overload,
)

from typing_extensions import TypeVar

from .pytoolsmith_config import get_format_map
from .pytoolsmith_config.mappings import get_type_map
from .pytoolsmith_config.serialization import serialize_batch_tool_args
from .tool_parameters import ToolParameters

if TYPE_CHECKING:
    from .tool_library import ToolLibrary

R = TypeVar("R", dict, str, list[str])


@dataclass
class ToolDefinition:
    """Defines a tool to be used for an LLM conversation."""

    function: Callable[..., R]
    """The function to call."""

    injected_parameters: list[str] = field(default_factory=list)
    """The parameters that should be ignored when making the LLM tool definition"""

    additional_parameters: dict[str, dict] = field(default_factory=dict)
    """Additional parameters to add to parameters for the LLM tool definition, 
    for example: the minimum value of a parameter

    Examples:
        {"k": {"minimum": 1}} # Set the minimum value of the k parameter to 1

    """

    user_message: str | None = None
    """
    An optional message to show the user while the tool is being called. Can use 
    mustache syntax to insert values from the function call. However- be certain that 
    these values will be able to be cast to a string!
    """

    tool_group: str | None = None
    """
    An optional group that the tool belongs to. 
    Can be used as a way to filter which tools the LLM gets using `subset`.
    """

    _schema_cache: ToolParameters | None = field(default=None, init=False, repr=False)
    """A cached version of the schema for the tool."""

    _tool_library: "ToolLibrary | None" = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        """Validate the schema can be built after initialization."""
        try:
            self.build_json_schema()
        except KeyError as e:
            raise ValueError(
                f"Invalid input parameter type: {e.args[0]}. "
                f"Set a type for this in the PyToolSmith type mapping configuration."
            )
        except Exception as e:
            raise ValueError(f"Error building tool: {e}")

    @property
    def name(self) -> str:
        return self.function.__name__

    def set_tool_library(self, tool_library: "ToolLibrary"):
        self._tool_library = tool_library

    def build_json_schema(
            self,
    ) -> ToolParameters:
        """Builds a tool JSON schema for use in Bedrock from the tool definition."""
        if self._schema_cache:
            return self._schema_cache

        func = self.function
        additional_parameters = self.additional_parameters

        sig = inspect.signature(func)

        param_desc_map = {}
        description = ""
        if func.__doc__:
            param_desc_map = self._extract_param_descriptions()
            description = self._extract_function_descriptions()

        required_parameters = []
        param_map: dict[str, dict] = {}

        for param_name, param_info in sig.parameters.items():
            # Ignore injected parameters
            if param_name in self.injected_parameters:
                continue

            param_map[param_name], is_required = self._get_type_for_parameter(
                param_name, param_info, param_desc_map, additional_parameters
            )
            if is_required:
                required_parameters.append(param_name)

        # Store result in cache before returning
        self._schema_cache = ToolParameters(
            name=self.name,
            required_parameters=required_parameters,
            input_properties=param_map,
            description=description,
        )
        return self._schema_cache

    @overload
    def call_tool(self, llm_parameters: dict[str, Any],
                  hardset_parameters: dict[str, Any],
                  include_message: Literal[False] = False) -> Any:
        ...

    @overload
    def call_tool(self, llm_parameters: dict[str, Any],
                  hardset_parameters: dict[str, Any],
                  include_message: Literal[True] = True) -> tuple[Any, str | None]:
        ...

    def call_tool(
            self,
            llm_parameters: dict[str, Any],
            hardset_parameters: dict[str, Any],
            include_message: bool = False
    ) -> Any | tuple[Any, str | None]:
        """
        Calls the tool with the given parameters. 
        If `include_message` is True, will also return a user message.
        """
        # So, for the batch tool, we need to change the hard-set 
        # parameters to include the tool library.
        if self.name == "batch_tool":
            hardset_parameters = {
                "tool_library": self._tool_library,
                "hardset_parameters": hardset_parameters
            }

        # Merge the library parameters with the LLM parameters
        parameters = self._combine_parameters(llm_parameters, hardset_parameters)

        result = self.function(**parameters)

        if include_message:
            message = self.format_message_for_call(llm_parameters, hardset_parameters)

            return result, message
        return result

    def format_message_for_call(self, llm_parameters: dict[str, Any],
                                hardset_parameters: dict[str, Any]) -> str | None:
        """Formats the user message for the tool call."""
        if self.name == "batch_tool":
            # Handle the batch tool differently:
            msgs = []
            for invocation in llm_parameters["invocations"]:
                tool = self._tool_library.get_tool_from_name(invocation["name"])
                msg = tool.format_message_for_call(
                    llm_parameters=serialize_batch_tool_args(invocation["arguments"]),
                    hardset_parameters=hardset_parameters
                )
                if msg:
                    msgs.append(msg)

            return "\n".join(msgs) if msgs else None

        parameters = self._combine_parameters(llm_parameters, hardset_parameters)
        message = self.user_message
        if message and "{{" in message:
            for key, value in parameters.items():
                message = message.replace("{{" + key + "}}", str(value))
        return message

    def _combine_parameters(self, llm_parameters: dict[str, Any],
                            hardset_parameters: dict[str, Any]) -> dict[str, Any]:
        """Merge the library parameters with the LLM parameters"""
        parameters = {}
        for k, v in llm_parameters.items():
            parameters[k] = v
        for injected_parameter in self.injected_parameters:
            parameters[injected_parameter] = hardset_parameters[injected_parameter]
        return parameters

    def _get_type_for_parameter(
            self,
            param_name: str,
            param_info: inspect.Parameter,
            param_desc_map: dict[str, str],
            additional_parameters: dict[str, Any],
            is_array_item: bool = False,
    ) -> tuple[dict, bool]:
        is_required = False

        # Could be multiple, so we store it here...
        param_type_options: list[type] = []
        if isinstance(param_info.annotation, UnionType | _UnionGenericAlias):
            param_type_options.extend(get_args(param_info.annotation))
        else:
            param_type_options.append(param_info.annotation)

        schemas = []
        for param_type in param_type_options:
            list_args = self._get_list_options(param_type)
            param_type = self._strip_aliases(param_type)

            param_json_type = self._get_json_type(param_type)

            schema_dict = {
                "type": param_json_type,
            }

            # Handle array types by defining their items
            if param_json_type == "array" and list_args:
                # Get the type of items in the array
                item_type = list_args[0]

                # Create a mock Parameter object for the item type
                mock_param = inspect.Parameter(
                    name="item",
                    kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
                    annotation=item_type,
                )

                # Recursively get the schema for the item type
                item_schema, _ = self._get_type_for_parameter(
                    param_name="item",
                    param_info=mock_param,
                    param_desc_map={},  # No descriptions for array items
                    additional_parameters={},  # No addl. parameters for array items
                    is_array_item=True,  # Flag that we're processing an array item
                )

                schema_dict["items"] = item_schema

            enums = []
            if isinstance(param_type, EnumType):
                # Handle enums
                enums.extend([enum.value for enum in param_type])
            elif isinstance(param_type, _LiteralGenericAlias):
                # Handle literals
                enums.extend(get_args(param_type))
            elif hasattr(param_type, "model_json_schema"):
                # Handle types with model_json_schema method (like v2 Pydantic models)
                schema_dict.update(param_type.model_json_schema())
            elif hasattr(param_type, "schema"):
                # Handle types with model_json_schema method (like v1 Pydantic models)
                schema_dict.update(param_type.schema())
            else:
                # Handle additional format updates.
                for formattable_type, format_value in get_format_map().items():
                    if issubclass(param_type, formattable_type):
                        schema_dict["format"] = format_value
                        break

            if enums:
                schema_dict["enum"] = enums

            schemas.append(schema_dict)

        if len(schemas) == 1:
            param_map = schemas[0]
        else:
            param_map = {"anyOf": schemas}

        # Only add description and handle required/default for top-level parameters
        if not is_array_item:
            if param_name in param_desc_map:
                param_map["description"] = param_desc_map[param_name]

            default_value = self._create_default_value(param_info.default)

            if default_value is not None:
                param_map["default"] = default_value
            else:
                is_required = True

            if param_name in additional_parameters:
                param_map.update(additional_parameters[param_name])

        return param_map, is_required

    def _extract_param_descriptions(self) -> dict[str, str]:
        """
        Extracts argument descriptions from a Google-style docstring.

        Returns:
            dict: A dictionary mapping argument names to their descriptions.
        """
        docstring = self.function.__doc__
        arg_descriptions = {}

        # Return empty dict if docstring is None or empty
        if not docstring:
            return arg_descriptions

        # Split the docstring into lines but only strip right whitespace
        lines = [line.rstrip() for line in docstring.split("\n")]

        # Find the Args section
        try:
            args_start = next(
                i for i, line in enumerate(lines) if line.strip() == "Args:"
            )
        except StopIteration:
            return arg_descriptions

        # Process lines after 'Args:' until we hit another section or end
        current_arg = None
        current_description = []

        for line in lines[args_start + 1:]:
            stripped_line = line.strip()
            # Check if we've hit another section (non-indented line ending with ':')
            if stripped_line.endswith(":") and not line.startswith(" "):
                break

            # If line starts with spaces, it's either a new argument or continuation
            if line.startswith("    "):
                # Check if it's a new argument
                if " (" in stripped_line or ":" in stripped_line:
                    # Save previous argument if exists
                    if current_arg:
                        arg_descriptions[current_arg] = "".join(
                            current_description
                        ).replace("\n", "")
                        current_description = []

                    # Parse new argument
                    if " (" in stripped_line:
                        current_arg = stripped_line.split(" (")[0]
                    else:
                        current_arg = stripped_line.split(":")[0]

                    current_description.append(line.split(":")[-1].lstrip())
                else:
                    # This is a continuation of the previous description
                    current_description.append(" " + line.lstrip())

        # Add the last argument
        if current_arg:
            arg_descriptions[current_arg] = "".join(current_description).replace(
                "\n", ""
            )

        return arg_descriptions

    @staticmethod
    def _get_json_type(param_type: type) -> str:
        """Returns the JSON type mapping for a given type."""

        if isinstance(param_type, _LiteralGenericAlias):
            param_type = [type(arg) for arg in get_args(param_type)][0]

        if hasattr(param_type, "model_json_schema"):
            return "object"

        if hasattr(param_type, "schema"):
            return "object"

        if isinstance(param_type, EnumType):
            param_type = [type(enum.value) for enum in param_type][0]

        return get_type_map()[param_type]

    @staticmethod
    def _strip_aliases(param_type: type) -> type:
        """Strips aliases from the param type."""

        # NewTypes suck, so we have to do this
        # noinspection PyTypeChecker
        if isinstance(param_type, NewType):
            # noinspection PyUnresolvedReferences
            param_type = param_type.__supertype__

        # Get the origin so we can handle dict[str, str], etc.
        if isinstance(param_type, GenericAlias):
            param_type = get_origin(param_type)

        return param_type

    @staticmethod
    def _get_list_options(param_type: type) -> tuple[type, ...] | None:
        if isinstance(param_type, GenericAlias):
            return get_args(param_type)
        return None

    def _extract_function_descriptions(self) -> str:
        docstring = self.function.__doc__

        if not docstring or "Args:" not in docstring:
            return docstring or ""

        # Split the docstring into lines but only strip right whitespace
        lines = [line.rstrip() for line in docstring.split("\n")]

        desc_parts = []
        hit_args = False
        for line in lines:
            if hit_args:
                if "Returns:" in line:
                    desc_parts.append(" " + line.strip())
                    hit_args = False
            else:
                if "Args:" in line:
                    hit_args = True
                else:
                    desc_parts.append(" " + line.strip())

        return "".join(desc_parts).replace("\n", " ").strip()

    @staticmethod
    def _create_default_value(default_value: Any) -> str | None:
        """
        Tries to create a default value from the given default value. 
        If it can't, returns None.
        """

        if isinstance(default_value, str | int | float | bool):
            return default_value
        if default_value is None:
            return "null"
        return None
