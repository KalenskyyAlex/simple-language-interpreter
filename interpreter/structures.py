"""
This module implements structures used in whole interpreter, like Tokens, Nodes and Functions

It is made, to provide error-handling just on site (inside of constructors), like type-checking;
implementation of private fields with only public getters. The whole idea is to make sure objects
keep being unchanged since creation
"""

from typing import Optional, Any
TOKEN_TYPES = ['kwd', 'int', 'float', 'str', 'bool', 'opr', 'fnc', 'var', 'sep']

class Token:
    """
    contains all info needed about code token (basically, it's type and value)

    once Token is created, it SHOULD NOT be changed for purpose of avoiding malfunctioning
    """
    def __init__(self, __type: Optional[str], __value: Optional[int | float | str | bool]):
        """
        creates Token instance

        raises an error if given parameters are invalid or 'None'

        once Token is created, it SHOULD NOT be changed for purpose of avoiding malfunctioning

        :param __type: type of token
        :param __value: value of token (token itself)
        """

        if __type is None:
            raise TypeError('TOKEN\'S TYPE CANNOT BE NONE')
        if __type not in TOKEN_TYPES:
            raise TypeError(f'GIVEN TYPE {__type} IS NOT A VALID TOKEN TYPE')

        if __value is None:
            raise TypeError('TOKEN\'S VALUE CANNOT BE NONE')

        self.__type: str = __type
        self.__value: int | float | str | bool = __value

    @property
    def type(self) -> str:
        """
        type of token should only be accessed via this method

        :return: type of token as a string
        """
        return self.__type

    @property
    def value(self) -> int | float | str | bool:
        """
        value of token should only be accessed via this method

        :return: value of token
        """
        return self.__value

    def __str__(self) -> str:
        return f'{self.__type}: {self.__value}'

    def __repr__(self) -> str:
        return self.__str__()


TokenType = Token

class Node:
    """
    Nodes are needed to form logical tree in min_parser.py

    once created, Node SHOULD NOT be changed for purpose of avoiding malfunctioning
    """
    def __init__(self, __operator: Optional[TokenType], __line_number: Optional[int],
                 right: Optional[Any] = None, left: Optional[Any] = None):
        """
        creates a Node

        :param right: right part of node -- either Token or another Node
        :param left: left part of node -- either Token or another Node
        :param operator: operator of node -- Token ONLY
        :param line_number: line number
        """

        self.right = right
        self.left = left

        if __operator is None:
            raise TypeError('NODE\'S OPERATOR CANNOT BE NONE')
        if not isinstance(__operator, Token):
            raise TypeError('NODE\'S OPERATOR MUST BE OF TYPE TOKEN ONLY')

        if __line_number is None:
            raise TypeError('NODE\'S LINE NUMBER CANNOT BE NONE')
        if __line_number <= 0:
            raise TypeError('NODE\'S LINE NUMBER MUST BE GREATER THAN ZERO')

        self.__line_number = __line_number
        self.__operator = __operator

    @property
    def operator(self) -> TokenType:
        """
        Node's operator should only be accessed via this method

        :return: operator of Node (token)
        """
        return self.__operator

    @property
    def line_number(self) -> int:
        """
        line number of Node should only be accessed via this method

        :return: line number of Node
        """
        return self.__line_number

    def __str__(self) -> str:
        node_to_str: str = f'line: {self.__line_number}\n'
        node_to_str += f'\tleft: {self.left}\n'
        node_to_str += f'\toperator: {self.__operator}\n'
        node_to_str += f'\tright: {self.right}\n'
        return node_to_str

    def __repr__(self) -> str:
        return self.__str__()


NodeType = Node

class Function:
    """
    Functions are root elements in logical tree created in min_parser.py

    once created, Function SHOULD NOT be changed for purpose of avoiding malfunctioning
    """
    def __init__(self, __name: Optional[str], __args: Optional[list[NodeType]],
                 __body: Optional[list[NodeType]], __line_number: Optional[int]):
        """
        creates Function

        raises an error if parameters are invalid or None

        once created, Function SHOULD NOT be changed for purpose of avoiding malfunctioning

        :param __name: name of the function
        :param __args: list arguments of the function
        :param __body: body of the function (list of lines of code)
        :param __line_number: line number of function (the line where function is declared)
        """
        if __name is None:
            raise TypeError('FUNCTION\'S NAME CANNOT BE NONE')
        if not __name.strip():
            raise TypeError('FUNCTION\'S NAME CANNOT BE AN EMPTY STRING')

        self.__name = __name

        if __args is None:
            raise TypeError('FUNCTION\'S ARGUMENTS CANNOT BE NONE (BUT CAN BE AN EMPTY LIST)')

        self.__args = __args

        if __body is None:
            raise TypeError('FUNCTION\'S BODY CANNOT BE NONE (BUT CAN BE AN EMPTY LIST)')

        self.__body = __body

        if __line_number is None:
            raise TypeError('FUNCTIONS\'S LINE NUMBER CANNOT BE NONE')
        if __line_number <= 0:
            raise TypeError('FUNCTIONS\'S LINE NUMBER CANNOT BE LOWER THAN ONE')

        self.__line_number = __line_number

    @property
    def name(self) -> str:
        """
        name of function should only be accessed via this method

        :return: name of function as a string
        """
        return self.__name

    @property
    def args(self) -> list[NodeType]:
        """
        arguments of function should only be accessed via this method

        :return: arguments of function as a list of Nodes
        """
        return self.__args

    @property
    def body(self) -> list[NodeType]:
        """
        body of function should only be accessed via this method

        :return: body of function as a list of Nodes
        """
        return self.__body

    @property
    def line_number(self) -> int:
        """
        line number of function should only be accessed via this method

        :return: line number of function
        """
        return self.__line_number


FunctionType = Function


if __name__ == '__main__':
    print('This module implements structures used in whole interpreter, like Tokens, Nodes and Functions\n')
    print()
    print('It is made, to provide error-handling just on site (inside of constructors), like type-checking;\n')
    print('implementation of private fields with only public getters. The whole idea is to make sure objects\n')
    print('keep being unchanged since creation\n')
