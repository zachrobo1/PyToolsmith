from collections.abc import Callable
from typing import TypeVar

T = TypeVar("T")

BatchRunnerType = Callable[[list[Callable[[], T]]], list[T]]


def DEFAULT_BATCH_RUNNER(callables: list[Callable[[], T]]) -> list[T]:
    results = []
    for callable in callables:
        results.append(callable())

    return results


SET_RUNNER: BatchRunnerType | None = None


def get_batch_runner() -> BatchRunnerType:
    if SET_RUNNER is not None:
        return SET_RUNNER
    return DEFAULT_BATCH_RUNNER


def set_batch_runner(batch_runner: BatchRunnerType) -> None:
    global SET_RUNNER
    SET_RUNNER = batch_runner


def unset_batch_runner() -> None:
    global SET_RUNNER
    SET_RUNNER = None
