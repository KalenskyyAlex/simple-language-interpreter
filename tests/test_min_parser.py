# pylint: skip-file
import sys

sys.path.insert(0, '../interpreter')

from min_parser import *  # noqa
from commons import *  # noqa

# region Testing

def test_fill_body_dry_run_none():
	assert True


# endregion

# TODO test make_line
# TODO test has_nesting
# TODO test nest
# TODO test operate_separators
# TODO test operate_calls
# TODO test operate_helper
# TODO test operate_...
# TODO test make_tree
# TODO test print_tree
