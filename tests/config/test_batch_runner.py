from pytoolsmith.pytoolsmith_config import batch_runner


def test_default_batch_runner():
    """Test that the default batch runner executes functions sequentially."""
    results = []

    def func1():
        results.append(1)
        return "one"

    def func2():
        results.append(2)
        return "two"

    def func3():
        results.append(3)
        return "three"

    callables = [func1, func2, func3]

    # Use the default batch runner
    output = batch_runner.DEFAULT_BATCH_RUNNER(callables)

    # Check that functions were executed in order
    assert results == [1, 2, 3]
    # Check that return values were collected correctly
    assert output == ["one", "two", "three"]


def test_get_batch_runner_default():
    """Test that get_batch_runner returns the default runner when none is set."""
    # Ensure no custom runner is set
    batch_runner.unset_batch_runner()

    # Get the current batch runner
    runner = batch_runner.get_batch_runner()

    # Should be the default runner
    assert runner == batch_runner.DEFAULT_BATCH_RUNNER


def test_set_and_get_batch_runner():
    """Test that set_batch_runner correctly sets a custom runner."""

    # Define a custom batch runner that reverses the order
    def custom_runner(callables):
        results = []
        for callable in reversed(callables):
            results.append(callable())
        return results

    # Set the custom runner
    batch_runner.set_batch_runner(custom_runner)

    # Get the current batch runner
    runner = batch_runner.get_batch_runner()

    # Should be our custom runner
    assert runner == custom_runner

    # Test that it works as expected
    def func1():
        return 1

    def func2():
        return 2

    def func3():
        return 3

    callables = [func1, func2, func3]

    # Use the custom batch runner through get_batch_runner
    output = runner(callables)

    # Check that functions were executed in reverse order
    assert output == [3, 2, 1]


def test_unset_batch_runner():
    """Test that unset_batch_runner reverts to the default runner."""

    # Define a custom batch runner
    def custom_runner(callables):
        return [callable() for callable in callables]

    # Set the custom runner
    batch_runner.set_batch_runner(custom_runner)

    # Verify it's set
    assert batch_runner.get_batch_runner() == custom_runner

    # Unset the custom runner
    batch_runner.unset_batch_runner()

    # Should revert to the default runner
    assert batch_runner.get_batch_runner() == batch_runner.DEFAULT_BATCH_RUNNER


def test_batch_runner_with_different_return_types():
    """Test that batch runner handles different return types correctly."""

    def func1():
        return 42

    def func2():
        return "hello"

    def func3():
        return [1, 2, 3]

    callables = [func1, func2, func3]

    # Use the default batch runner
    output = batch_runner.get_batch_runner()(callables)

    # Check that return values with different types were collected correctly
    assert output == [42, "hello", [1, 2, 3]]
