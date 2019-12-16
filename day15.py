#!/usr/bin/env python3

import sys
from enum import Enum
from operator import add, mul, lt, eq, truth, not_
from collections import deque
from itertools import permutations
from time import sleep


class OpCode(Enum):
    ADD = 1
    MULTIPLY = 2
    INPUT = 3
    OUTPUT = 4
    JMP_IF_TRUE = 5
    JMP_IF_FALSE = 6
    LESS_THAN = 7
    EQUALS = 8
    OFFSET = 9
    HALT = 99


class ParamMode(Enum):
    POSITION = 0
    IMMEDIATE = 1
    RELATIVE = 2


def int_input():
    while True:
        try:
            return int(input("Input> "), 10)
        except ValueError:
            print("Invalid integer value. Try again.")


def std_output(value):
    print(value)


class Computer(object):
    _id = 0

    def __init__(self, op_codes, input_device, output_device):
        self._data = op_codes[:]
        self._index = 0
        self._counter = 0
        self._offset = 0
        self._input = input_device
        self._output = output_device

        Computer._id += 1
        self._id = Computer._id

    def id(self):
        return self._id

    def index(self):
        return self._index

    def step(self, size):
        self._index += size
        return size

    def data(self):
        return self._data[:]

    def reserve(self, index):
        if index >= len(self._data):
            self._data = self._data + ([0] * (index - len(self._data) + 1))

    def get(self, index):
        if index < 0:
            raise IndexError('Index is negative')
        self.reserve(index)
        return self._data[index]

    def set(self, index, value):
        self.reserve(index)
        self._data[index] = value

    def op(self):
        value = self.get(self.index())
        return OpCode(value % 100)

    def offset(self):
        return self._offset

    def mode(self, index):
        value = self.get(self.index())
        place = 10**(2 + index)
        return ParamMode((value // place) % 10)

    def param(self, index, immediate=False):
        mode = ParamMode.IMMEDIATE if immediate else self.mode(index)
        value = self.get(self.index() + index + 1)
        if mode is ParamMode.IMMEDIATE:
            return value
        elif mode is ParamMode.RELATIVE:
            return self.get(self.offset() + value)
        return self.get(value)

    def input(self):
        value = self._input()
        if type(value) is int or value is None:
            return value
        return int(value, 10)

    def output(self, value):
        self._output(value)

    def tick(self):
        self._counter += 1

        op_code = self.op()
        if op_code is OpCode.HALT:
            return 0

        if op_code is OpCode.ADD or op_code is OpCode.MULTIPLY:
            op = add
            if op_code is OpCode.MULTIPLY:
                op = mul

            num1 = self.param(0)
            num2 = self.param(1)
            index = self.param(2, True)
            if self.mode(2) is ParamMode.RELATIVE:
                index += self.offset()
            value = op(num1, num2)
            self.set(index, value)
            return 4

        if op_code is OpCode.INPUT:
            index = self.param(0, True)
            if self.mode(0) is ParamMode.RELATIVE:
                index += self.offset()
            value = self.input()
            if value is None:
                return 0
            self.set(index, value)
            return 2

        if op_code is OpCode.OUTPUT:
            value = self.param(0)
            self.output(value)
            return 2

        if op_code is OpCode.JMP_IF_TRUE or op_code is OpCode.JMP_IF_FALSE:
            test = self.param(0)
            target = self.param(1)
            op = truth if op_code is OpCode.JMP_IF_TRUE else not_
            jump = 3
            if op(test):
                jump = target - self.index()
            return jump

        if op_code is OpCode.LESS_THAN or op_code is OpCode.EQUALS:
            num1 = self.param(0)
            num2 = self.param(1)
            index = self.param(2, True)
            if self.mode(2) is ParamMode.RELATIVE:
                index += self.offset()
            op = lt if op_code is OpCode.LESS_THAN else eq
            self.set(index, 1 if op(num1, num2) else 0)
            return 4

        if op_code is OpCode.OFFSET:
            offset = self.param(0)
            self._offset += offset
            return 2

    def stopped(self):
        return self.op() == OpCode.HALT

    def run(self):
        while self.step(self.tick()):
            pass


class Move(Enum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4


class Status(Enum):
    INVALID = 0
    VALID = 1
    FOUND = 2


class Block(Enum):
    EMPTY = 0
    WALL = 1


class RepairDroid(Computer):
    MoveMap = {
        Move.NORTH: (0, -1),
        Move.SOUTH: (0, 1),
        Move.WEST:  (-1, 0),
        Move.EAST:  (1, 0),
    }

    ReverseMoveMap = {v: k for k, v in MoveMap.items()}

    BlockMap = {
        Block.EMPTY: '█',
        Block.WALL: '+',
    }

    def __init__(self, program):
        super().__init__(program, self._processInput, self._processOutput)
        pos = (0, 0)
        self._pos = pos
        self._path = []
        self._blocks = {}
        self._blocks[pos] = Block.EMPTY
        self._bounds = ((0, 0), (0, 0))
        self._target = None
        self._move = None
        self._queued_input = deque([Move.NORTH])
        self._move_offset = 0

    def _processInput(self):
        if not self._queued_input:
            return None

        move = self._queued_input.popleft()
        self._move = move
        return move.value

    def _processOutput(self, value):
        prev_pos = self.pos()
        x, y = prev_pos
        dx, dy = RepairDroid.MoveMap[self._move]
        pos = (x + dx, y + dy)
        status = Status(value)

        if self._path and pos == self._path[-1]:
            assert(status is Status.VALID)
            self._pos = self._path.pop()
        else:
            if status is Status.FOUND:
                self._target = pos
                self._path.append(prev_pos)
                self._pos = pos
                self.setBlock(pos, Block.EMPTY)
                return

            if status is Status.VALID:
                self._path.append(prev_pos)
                self._pos = pos
                self.setBlock(pos, Block.EMPTY)
            else:
                self.setBlock(pos, Block.WALL)

        # =======================
        print(self.display())
        # =======================

        x, y = self.pos()

        moves = [Move.NORTH, Move.EAST, Move.SOUTH, Move.WEST]
        offset = self._move_offset
        for move_index in range(offset, offset + len(moves)):
            move = moves[move_index % len(moves)]
            dx, dy = RepairDroid.MoveMap[move]
            pos = (x + dx, y + dy)
            if pos not in self._blocks:
                self._queued_input.append(move)
                self._move_offset = move_index % len(moves)
                break
        else:
            if self._path:
                dx, dy = self._path[-1]
                diff = (dx - x, dy - y)
                move = RepairDroid.ReverseMoveMap[diff]
                self._queued_input.append(move)

    def setBlock(self, pos, block):
        self._blocks[pos] = block
        self.extendBounds(pos)

    def extendBounds(self, pos):
        x, y = pos
        (min_x, min_y), (max_x, max_y) = self._bounds
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x)
        max_y = max(max_y, y)
        self._bounds = ((min_x, min_y), (max_x, max_y))

    def pos(self):
        return self._pos

    def block(self):
        return self._blocks[self.pos()]

    def neighbours(self):
        positions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        x, y = self.pos()
        return [(x + dx, y + dy) for (dx, dy) in positions]

    def locate(self):
        while not self._target and self._queued_input:
            self.run()
        return self._path

    def bounds(self):
        return self._bounds

    def displayAll(self):
        (min_x, min_y), (max_x, max_y) = self.bounds()
        rows = []
        rows.append(''.join(['╔'] + (['═'] * (max_x - min_x + 1)) + ['╗']))
        current_pos = self.pos()
        prev_pos = self._path[-1] if self._path else None
        for y in range(min_y, max_y + 1):
            row = ['║']
            for x in range(min_x, max_x + 1):
                pos = (x, y)
                if pos == current_pos:
                    row.append('◆')
                    continue
                if prev_pos and prev_pos == pos:
                    row.append('◇')
                    continue
                if pos not in self._blocks:
                    row.append(' ')
                    continue
                row.append(RepairDroid.BlockMap[self._blocks[pos]])
            row.append('║')
            rows.append(''.join(row))
        rows.append(''.join(['╚'] + (['═'] * (max_x - min_x + 1)) + ['╝']))
        return '\n'.join(rows)

    def display(self):
        x, y = self.pos()
        width = 78
        height = 16
        min_x = x - (width // 2)
        max_x = min_x + width
        min_y = y - (height // 2)
        max_y = min_y + height
        rows = []
        rows.append(''.join(['╔'] + (['═'] * (max_x - min_x + 1)) + ['╗']))
        current_pos = self.pos()
        prev_pos = self._path[-1] if self._path else None
        for y in range(min_y, max_y + 1):
            row = ['║']
            for x in range(min_x, max_x + 1):
                pos = (x, y)
                if pos == current_pos:
                    row.append('◆')
                    continue
                if prev_pos and prev_pos == pos:
                    row.append('◇')
                    continue
                if pos not in self._blocks:
                    row.append(' ')
                    continue
                row.append(RepairDroid.BlockMap[self._blocks[pos]])
            row.append('║')
            rows.append(''.join(row))
        rows.append(''.join(['╚'] + (['═'] * (max_x - min_x + 1)) + ['╝']))
        return '\n'.join(rows)


def part1(file):
    program = list(map(lambda x: int(x, 10), file.readline().split(',')))
    droid = RepairDroid(program)
    path = droid.locate()
    print(f"Answer: {len(path)}")


def part2(file):
    # TOOD: Second part of day
    pass


def main(part, file):
    if file.isatty():
        print("Awaiting input from stdin...")

    if part == 1:
        part1(file)
    elif part == 2:
        part2(file)


if __name__ == "__main__":
    if (len(sys.argv) < 2 or len(sys.argv) > 3 or (sys.argv[1] != "1" and sys.argv[1] != "2")):
        print(f"usage: {sys.argv[0]} part [filename]")
        print(f"")
        exit(1)

    input_file = sys.stdin

    if (len(sys.argv) == 3):
        try:
            filename = sys.argv[2]
            input_file = open(filename)
        except FileNotFoundError as e:
            print(e)
            exit(1)

    with input_file:
        main(int(sys.argv[1], 10), input_file)
