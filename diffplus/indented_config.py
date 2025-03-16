from typing import Dict, List

# Recursive type alias
IndentedConfigDict = Dict[str, "IndentedConfigDict"]


class IndentedConfig:
    #
    # Initializes a given config:
    #   - having blocks indented by "indent_char"
    #   - having comments starting by "comment_char"
    #
    # The config may be sanitized at init via the "sanitize" parameter.
    #
    def __init__(
        self,
        config: str,
        indent_char: str = " ",
        comment_char: str = "#",
        sanitize: bool = False,
    ) -> None:
        if not len(indent_char) == 1:
            raise ValueError('"indent_char" must be a char')
        if not len(comment_char) == 1:
            raise ValueError('"comment_char" must be a char')
        self.config = config
        self.indent_char = indent_char
        self.comment_char = comment_char
        if sanitize:
            self.sanitize()

    #
    # Returns a tree representation of the indented config as a dict:
    #   - the config must be correctly indented (call "sanitize" first if needed)
    #   - lines must be unique per indented block (as they are used as dict keys)
    #
    # A KeyError may be raised if the config is not correctly indented.
    #
    def to_dict(self) -> IndentedConfigDict:
        tree: IndentedConfigDict = {}
        last_parent = {0: tree}  # last parents encountered by indent level

        for line in self.config.splitlines():
            child_name = line.lstrip(self.indent_char)
            child_level = len(line) - len(child_name)
            last_parent[child_level][child_name] = {}
            last_parent[child_level + 1] = last_parent[child_level][child_name]

        return tree

    #
    # Sanitizes the indented config:
    #   - remove trailing spaces from lines
    #   - ignore blank lines and comments
    #   - fix lines not correctly indented
    #
    def sanitize(self) -> None:
        sanitized_indented_config: List[str] = []
        max_indent_level = 0

        for line in self.config.splitlines():
            # line may have trailing spaces, remove them
            line = line.rstrip()

            # line may be blank or may be a comment, ignore it
            if not line or line.lstrip().startswith(self.comment_char):
                continue

            # ensure or else fix line indentation level
            line_indent_level = len(line) - len(line.lstrip(self.indent_char))

            if not line_indent_level <= max_indent_level:
                line_indent_level = max_indent_level  # fix indent level
                line = line.lstrip(self.indent_char)  # remove bad indent
                line = line_indent_level * self.indent_char + line  # insert good indent

            max_indent_level = line_indent_level + 1

            # line is sanitized at this point
            sanitized_indented_config.append(line)

        # config has been sanitized
        self.config = "\n".join(sanitized_indented_config)

    #
    # Returns the indented config as an str.
    #
    def __str__(self) -> str:
        return self.config
