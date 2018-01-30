"""Starts the CESK machine"""

from pycparser.c_ast import Node
from utils import find_main
from cesk.structures import ConcreteValue, State, Ctrl, Envr, Stor

def main(ast):
    """Is a stub"""
    main_function = find_main(ast)[0]
    main_function.show()
    value_1 = ConcreteValue(5, "int")
    value_2 = ConcreteValue(3, "int")
    print(value_1 + value_2)
    print(value_1 - value_2)
    print(value_1 * value_2)
    print(value_1 / value_2)

    start_state = State(Ctrl(ast), Envr(), Stor())
    start_state.execute()
