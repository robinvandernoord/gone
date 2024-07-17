import os
import signal

from src import gone
import typing as t
import sys


@gone.args
def no_args1(*args: None):
    assert not args
    return "with return"


@gone.args
def no_args2():
    return "with return"


@gone.result
def no_return(*args: int):
    assert args
    return "without return"


@gone.inout
def no_inout(*args: None):
    assert not args
    return "without return"


T = t.TypeVar("T")


def with_input_output(*args: T) -> tuple[T, ...]:
    return args


def test_args():
    assert no_args1(1, 2, "3")
    assert no_args2(1, 2, "3")


def test_return():
    assert no_return(1, 2, "3") is None


def test_both():
    assert no_inout(1, 2, "3") is None


def test_non_decorator():
    assert with_input_output(213) == (213,)
    assert with_input_output(213, 456) == (213, 456)

    without_input_output = gone.inout(with_input_output)
    assert without_input_output() is None
    assert without_input_output(123) is None
    assert without_input_output(123, 456, keyw='...') is None


def test_lambda():
    fn = gone.inout(lambda: "lambda")
    assert fn() is None
    assert fn(123) is None
    assert fn(key="abc") is None


def test_callback():
    flag = False

    def sigint_handler():
        nonlocal flag
        flag = True

    # listen to signal:
    signal.signal(signal.SIGFPE, gone.inout(sigint_handler))
    # just `sigint_handler` would crash because it's getting unexpected args

    # send signal:
    os.kill(os.getpid(), signal.SIGFPE)

    # signals are technically async but the handler should be called before we get to this point:
    assert flag