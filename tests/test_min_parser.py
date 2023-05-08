# pylint: skip-file
import sys

sys.path.insert(0, '../interpreter')

from min_parser import *  # noqa
from utils.commons import *  # noqa

# region Testing parse_line

def test_make_line_dry_run_none():
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
