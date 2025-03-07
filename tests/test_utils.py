from pytoolsmith.utils import remove_keys


def test_remove_keys():
    input_dict = {
        "hello": "world",
        "nested": {
            "key": 1,
            "format": "value",
        }
    }
    result = remove_keys(input_dict, ["hello", "format"])

    assert result == {"nested": {"key": 1}}
