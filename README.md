# PyToolsmith

A lightweight Python library that simplifies the process of exposing functions as tools for Large Language Models.

### Status

[![codecov](https://codecov.io/gh/zachrobo1/PyToolsmith/graph/badge.svg?token=5SQEOF1TV2)](https://codecov.io/gh/zachrobo1/PyToolsmith)

### Todo

1. Get generalized tool definition class up
2. Build anthropic and openai-specific serializers... what's the best way? Could do class-based, or just one-size fits
   all
    - How much does it make sense to rely on the OAI / Anth models to build these? Could couple tightly, or make pure
      dicts...
3. Build out library
    - How do we specify which params are injectable on a library level? Ideally type hint..
    - How are we going to handle serialization for loading function
        - Library level? Would be good to re-use serializers. Or could do it per-tool
        - Could we potentially take advantage of the `Config` on pydantic models.



