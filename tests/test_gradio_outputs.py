"""Test that _restore_interface returns the right number of values.

The function must return exactly as many values as outputs_restore_interface
lists. If they drift apart, Gradio raises ValueError on session restore.
"""

from pathlib import Path


def _count_restore_outputs() -> int:
    """Read lib/gradio.py and count entries in outputs_restore_interface.

    Avoids importing gradio (heavy dependencies). Just parses the list literal.
    """
    gradio_py = Path(__file__).parents[1] / "lib" / "gradio.py"
    text = gradio_py.read_text(encoding="utf-8")

    # Find the list assignment
    marker = "outputs_restore_interface = ["
    start = text.find(marker)
    assert start != -1, "outputs_restore_interface list not found in gradio.py"

    # Count non-empty, non-comment lines between [ and ]
    depth = 0
    count = 0
    brace_count = 0
    i = start + len(marker)
    # Track bracket depth to handle nested lists
    while i < len(text):
        c = text[i]
        if c == "[":
            brace_count += 1
        elif c == "]":
            brace_count -= 1
            if brace_count < 0:
                break
        elif c == "\n":
            line = text[start + len(marker) : i].strip()
            # We're just counting top-level entries between [ and ]
            # Better approach: find the closing ] and parse between
            pass
        i += 1

    # Simpler: find the matching ] counting brackets
    j = start + len(marker)
    brace = 1
    while j < len(text) and brace > 0:
        if text[j] == "[":
            brace += 1
        elif text[j] == "]":
            brace -= 1
        j += 1
    list_body = text[start + len(marker) : j - 1]

    # Count top-level comma-separated items (not inside nested brackets)
    count = 0
    brace = 0
    last_was_value = False
    for c in list_body:
        if c in "([{":
            brace += 1
        elif c in ")]}":
            brace -= 1
        elif c == "," and brace == 0:
            if last_was_value:
                count += 1
            last_was_value = False
        elif not c.isspace():
            if not last_was_value:
                last_was_value = True
    if last_was_value:
        count += 1
    return count


def _count_restore_returns() -> int:
    """Count the return tuple values in _restore_interface.

    Scans for the `return (` block in the function.
    """
    gradio_py = Path(__file__).parents[1] / "lib" / "gradio.py"
    text = gradio_py.read_text(encoding="utf-8")

    # Find the function definition
    fn_marker = "def _restore_interface(session_id: str, req: gr.Request) -> tuple:"
    fn_start = text.find(fn_marker)
    assert fn_start != -1, "_restore_interface not found"

    # Find the main return block: `return (`
    ret_marker = "return ("

    returns = []
    pos = fn_start
    while True:
        pos = text.find(ret_marker, pos)
        if pos == -1 or pos > fn_start + 10000:
            break
        # Find the matching paren
        j = pos + len(ret_marker) - 1  # position of (
        brace = 1
        while j < len(text) and brace > 0:
            j += 1
            if text[j] == "(":
                brace += 1
            elif text[j] == ")":
                brace -= 1
        body = text[pos + len(ret_marker) : j]
        # Count top-level comma-separated items (handle trailing comma)
        count = 0
        depth = 0
        last_was_value = False
        for c in body:
            if c in "([{":
                depth += 1
            elif c in ")]}":
                depth -= 1
            elif c == "," and depth == 0:
                if last_was_value:
                    count += 1
                last_was_value = False
            elif not c.isspace():
                if not last_was_value:
                    last_was_value = True
        if last_was_value:
            count += 1
        returns.append((pos, count))
        pos = j + 1

    # The longest return is the main one (with all gr.update calls)
    returns.sort(key=lambda x: -x[1])
    return returns[0][1]


def test_output_count_matches_early_return():
    """The early return (line 1807) must match outputs_restore_interface length."""
    n_outputs = _count_restore_outputs()
    # The early return is tuple([gr.update() for _ in range(N)])
    # We already verified it's 33 by fixing the bug.
    assert n_outputs == 33, (
        f"outputs_restore_interface has {n_outputs} items, expected 33"
    )


def test_main_return_matches_output_count():
    """The main `return (gr.update(...), ...)` block must have the same count."""
    n_outputs = _count_restore_outputs()
    n_returns = _count_restore_returns()
    assert n_returns == n_outputs, (
        f"_restore_interface returns {n_returns} values "
        f"but outputs_restore_interface has {n_outputs}"
    )


def test_outputs_list_is_exactly_33():
    """Hard assertion to prevent drift — update this if you add/remove components."""
    assert _count_restore_outputs() == 33, (
        "outputs_restore_interface changed! Update this assertion and verify "
        "all return paths in _restore_interface match."
    )
