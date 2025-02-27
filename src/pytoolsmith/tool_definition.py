from copy import deepcopy
from typing import Any, Callable

from pydantic import BaseModel


class ToolDefinition(BaseModel):
    """Defines a tool to be used for an LLM conversation."""

    function: Callable
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

    @property
    def name(self) -> str:
        return self.function.__name__

    def build_json_schema(
            self,
    ) -> AwsBedrockToolParam:
        """Builds a tool JSON schema for use in Bedrock from the tool definition."""

        func = self.function
        additional_parameters = self.additional_parameters

        sig = inspect.signature(func)

        param_desc_map = {}
        description = ""
        if func.__doc__:
            param_desc_map = _extract_param_descriptions(func.__doc__)
            description = _extract_function_descriptions(func.__doc__)

        required_parameters = []
        param_map: dict[str, dict] = {}

        for param_name, param_info in sig.parameters.items():
            # Ignore injected parameters
            if param_name in self.injected_parameters:
                continue

            param_map[param_name], is_required = _get_type_for_parameter(
                param_name, param_info, param_desc_map, additional_parameters
            )
            if is_required:
                required_parameters.append(param_name)

        input_schema = AwsBedrockToolInputSchema(
            type="object",
            properties=param_map,
            required=required_parameters,
        )

        return AwsBedrockToolParam(
            name=self.name,
            inputSchema=AwsBedrockToolSchemaJson(json_val=input_schema),
            description=description,
        )

    def call_tool(
            self, llm_parameters: dict[str, Any], library_parameters: dict[str, Any]
    ) -> Any:
        """Calls the tool with the given parameters."""

        # Merge the library parameters with the LLM parameters
        parameters = deepcopy(llm_parameters)
        library_parameters = deepcopy(library_parameters)
        for injected_parameter in self.injected_parameters:
            parameters[injected_parameter] = library_parameters[injected_parameter]

        return self.function(**jencode(parameters))
