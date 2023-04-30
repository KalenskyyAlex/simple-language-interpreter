from typing import Optional

# region Declared types

TokenType = type['Token']
NodeType = type['Node']

# endregion

class Token:
    def __init__(self, __type: str, value: int | float | str | bool):
        self.__type = __type
        self.value = value

    @property
    def type(self):
        return self.__type

class Node:
    def __init__(self, right: Optional[NodeType] | Optional[TokenType],
                 left: Optional[NodeType] | Optional[TokenType], operator: TokenType):
        self.right = right
        self.left = left

        if operator is None:
            raise TypeError('NODE\'S OPERATOR CANNOT BE NULL')
        self.operator = operator
