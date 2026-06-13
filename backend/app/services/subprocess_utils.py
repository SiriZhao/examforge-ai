import contextlib
import subprocess
import sys
from collections.abc import Iterator
from typing import Any


def subprocess_no_window_kwargs() -> dict[str, Any]:
    if not sys.platform.startswith("win"):
        return {}
    startupinfo = subprocess.STARTUPINFO()
    startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return {
        "startupinfo": startupinfo,
        "creationflags": subprocess.CREATE_NO_WINDOW,
    }


@contextlib.contextmanager
def hide_subprocess_windows() -> Iterator[None]:
    if not sys.platform.startswith("win"):
        yield
        return

    original_popen = subprocess.Popen

    class NoWindowPopen(original_popen):  # type: ignore[misc]
        def __init__(self, *args: Any, **kwargs: Any) -> None:
            kwargs.update(subprocess_no_window_kwargs())
            super().__init__(*args, **kwargs)

    subprocess.Popen = NoWindowPopen  # type: ignore[assignment]
    try:
        yield
    finally:
        subprocess.Popen = original_popen  # type: ignore[assignment]
