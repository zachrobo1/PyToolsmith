from dataclasses import dataclass


@dataclass
class GeminiFunctionDeclaration:
    response: dict | None
    """
    Describes the output from the function in the OpenAPI JSON Schema Object format.
    """

    description: str
    """
    Description and purpose of the function. 
    Model uses it to decide how and whether to call the function.
    """

    name: str
    """
    The name of the function to call. Must start with a letter or an underscore. 
    Must be a-z, A-Z, 0-9, or contain underscores, dots and dashes, with a maximum 
    length of 64.
    """

    parameters: dict | None
    """
    Describes the parameters to this function in JSON Schema Object format. 
    Reflects the Open API 3.03 Parameter Object. string Key: the name of the parameter. 
    Parameter names are case sensitive. Schema Value: the Schema defining the type used
     for the parameter. For function with no parameters, this can be left unset. 
     Parameter names must start with a letter or an underscore and must only contain 
     chars a-z, A-Z, 0-9, or underscores with a maximum length of 64. Example with 1 
     required and 1 optional parameter: type: OBJECT properties: param1: type: STRING 
     param2: type: INTEGER required: - param1"""


@dataclass
class GeminiTool:
    function_declarations: list[GeminiFunctionDeclaration] | None
