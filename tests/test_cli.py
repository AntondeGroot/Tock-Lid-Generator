import pytest

from tock_lid.cli import main


@pytest.mark.parametrize(
    ("option", "valid_example"),
    [("--font", "bodoni"), ("--style", "double")],
)
def test_unknown_choice_exits_with_a_message_listing_the_valid_ones(option, valid_example):
    with pytest.raises(SystemExit) as exit_info:
        main(["generate", option, "nope"])

    message = str(exit_info.value)
    assert message.startswith("error: Unknown")
    assert "'nope'" in message
    assert valid_example in message
