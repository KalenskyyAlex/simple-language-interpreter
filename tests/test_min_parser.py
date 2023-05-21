# pylint: skip-file
from interpreter.min_parser import *  # noqa
from interpreter.utils.commons import *  # noqa

# region Testing parse_line

def test_parse_line_dry_run_invalid():
	assert parse_line(None, 1) is None
	assert parse_line([], 0) is None
	assert parse_line([], -1) is None
	assert True

def test_parse_line_simple_inputs():
	assert True

# endregion

# TODO test parse_line
# TODO test __has_nesting
# TODO test __nest
# TODO test __operate_separators
# TODO test __parse_calls
# TODO test __parse_helper
# TODO test operate_...
# TODO test parse
# TODO test print_tree
