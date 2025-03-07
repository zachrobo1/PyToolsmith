import inspect
from enum import EnumType
from types import GenericAlias, UnionType
# noinspection PyUnresolvedReferences
from typing import (
    Any,
    Callable,
    NewType,
    Self,
    _LiteralGenericAlias,
    _UnionGenericAlias,
    get_args,
    get_origin,
)

from pydantic import BaseModel, model_validator
from typing_extensions import TypeVar

from .pytoolsmith_config import get_format_map
from .pytoolsmith_config.mappings import get_type_map
from .tool_parameters import ToolParameters

# TODO: figure out how to type this so response type is clear if it's a string or a dict.
R = TypeVar("R", dict, str, list[str])


class ToolDefinition(BaseModel):
    """Defines a tool to be used for an LLM conversation."""

    function: Callable[..., R]
    """The function to call."""

    injected_parameters: list[str] = []
    """The parameters that should be ignored when making the LLM tool definition"""

    additional_parameters: dict[str, dict] = {}
    """Additional parameters to add to parameters for the LLM tool definition, 
    for example: the minimum value of a parameter

    Examples:
        {"k": {"minimum": 1}} # Set the minimum value of the k parameter to 1

    """

    user_message: str | None = None
    """An optional message to show the user while the tool is being called."""

    @model_validator(mode="after")
    def ensure_schema_builds(self) -> Self:
        try:
            self.build_json_schema()
        except KeyError as e:
            raise ValueError(
                f"Invalid input parameter type: {e.args[0]}. "
                f"Set a type for this in the PyToolSmith type mapping configuration."
            )
        except Exception as e:
            raise ValueError(f"Error building tool: {e}")
        return self

    @property
    def name(self) -> str:
        return self.function.__name__

    def build_json_schema(
            self,
    ) -> ToolParameters:
        """Builds a tool JSON schema for use in Bedrock from the tool definition."""

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

        return ToolParameters(
            name=self.name,
            required_parameters=required_parameters,
            input_properties=param_map,
            description=description,
        )

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
                    additional_parameters={},  # No additional parameters for array items
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
            elif issubclass(param_type, BaseModel):
                schema_dict.update(param_type.model_json_schema())
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

        if issubclass(param_type, BaseModel):
            param_type = BaseModel

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

        if "Args:" not in docstring:
            return docstring

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
        """Tries to create a default value from the given default value. If it can't, returns None."""

        if isinstance(default_value, str | int | float | bool):
            return default_value
        if default_value is None:
            return "null"
        return None
