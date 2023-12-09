from .indented_config import IndentedConfig
from re import sub, M


class IncrementalDiff:
    #
    # For colored diff (same ANSI colors as Git).
    #
    _COLOR_GREEN = "\033[32m"
    _COLOR_RESET = "\033[m"

    #
    # Initializes an incremental diff between two indented configs:
    #   - the diff will look for A items missing in B items
    #   - if "merge" is True, the diff will include B items as well
    #
    # Merging is useful to preview a full config before applying it.
    # Coloring is useful to better visualize the changes in the diff.
    #
    def __init__(
        self, a: IndentedConfig, b: IndentedConfig, merge=False, colored=False
    ):
        self.a = a
        self.b = b
        self.merge = merge
        self.colored = colored

    #
    # Returns the incremental diff as a dict.
    #
    def to_dict(self):
        return IncrementalDiff._to_dict(self.a.to_dict(), self.b.to_dict(), self.merge)

    #
    # Returns the incremental diff as an str.
    #
    def __str__(self):
        str_ = IncrementalDiff._to_str(self.to_dict(), indent_char=self.a.indent_char)
        if self.colored:
            str_ = sub(
                r"^(\+.*)$", rf"{self._COLOR_GREEN}\1{self._COLOR_RESET}", str_, flags=M
            )
        return str_.rstrip("\n")  # just a little hack to remove the last newline char

    #
    # Builds an incremental diff recursively between A and B; returns it as a dict.
    # New items from A are prepended by "+" to tell them from existing ones from B.
    #
    @staticmethod
    def _to_dict(a, b, merge=False):
        new_items = {}

        for item in a.keys():
            if item not in b.keys():
                # item not in B yet, add it with all of its children
                new_items[f"+{item}"] = a[item]
            else:
                # item already in B, look for diff into its children
                new_children = IncrementalDiff._to_dict(a[item], b[item], merge)
                if new_children:
                    new_items[item] = new_children

        if merge:
            b.update(new_items)
            return b

        return new_items

    #
    # Builds a pretty str recursively from an incremental diff; returns it.
    # It is pretty as it indents lines and adds a "+" in front of new ones.
    #
    @staticmethod
    def _to_str(incrdiff, indent_char=" ", indent_level=0, is_new=False):
        str_ = ""

        for item in incrdiff:
            plus = is_new or item.startswith("+")
            str_ += "+" if plus else " "
            str_ += indent_level * indent_char + item.lstrip("+") + "\n"
            str_ += IncrementalDiff._to_str(
                incrdiff[item], indent_char, indent_level + 1, plus
            )

        return str_
