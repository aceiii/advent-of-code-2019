#!/usr/bin/env python3

import sys
from enum import Enum
from operator import add, mul, lt, eq, truth, not_
from collections import deque
from itertools import permutations


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


class ArcadeCabinet(Computer):
    class Tile(Enum):
        EMPTY = 0
        WALL = 1
        BLOCK = 2
        HOR_PADDLE = 3
        BALL = 4

    TileMap = {
        Tile.EMPTY: ' ',
        Tile.WALL: '█',
        Tile.BLOCK: '▒',
        Tile.HOR_PADDLE: '▂',
        Tile.BALL: '●',
    }

    def __init__(self, program):
        super().__init__(program, self._processInput, self._processOutput)
        self._tiles = {}
        self._bounds = ((float('inf'), float('inf')),
                        (float('-inf'), float('-inf')))
        self._input_queue = []
        self._score = 0
        self._ball = None
        self._paddle = None

    def _processInput(self):
        score = self.score()
        print(self.display())

        ball_x, _ = self._ball
        paddle_x, _ = self._paddle
        if ball_x < paddle_x:
            return -1
        elif ball_x > paddle_x:
            return 1
        return 0

    def _processOutput(self, value):
        self._input_queue.append(value)
        if len(self._input_queue) == 3:
            x, y, value = self._input_queue
            self._input_queue = []

            if x == -1 and y == 0:
                self.setScore(value)
            else:
                tile = ArcadeCabinet.Tile(value)
                if tile is ArcadeCabinet.Tile.BALL:
                    self._ball = (x, y)
                elif tile is ArcadeCabinet.Tile.HOR_PADDLE:
                    self._paddle = (x, y)
                self.plot(x, y, tile)

    def plot(self, x, y, tile):
        self._tiles[(x, y)] = tile

        (min_x, min_y), (max_x, max_y) = self._bounds
        min_x = min(min_x, x)
        min_y = min(min_y, y)
        max_x = max(max_x, x)
        max_y = max(max_y, y)

        self._bounds = ((min_x, min_y), (max_x, max_y))

    def bounds(self):
        return self._bounds

    def display(self):
        (min_x, min_y), (max_x, max_y) = self.bounds()
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        rows = []
        rows.append(''.join(['╔']+(['═'] * width) + ['╗']))
        for y in range(height):
            row = ['║']
            for x in range(width):
                pos = (x, y)
                tile = ArcadeCabinet.Tile.EMPTY
                if pos in self._tiles:
                    tile = self._tiles[pos]
                row.append(ArcadeCabinet.TileMap[tile])
            row.append('║')
            rows.append(''.join(row))
        rows.append(''.join(['╚']+(['═'] * width) + ['╝']))
        rows.append(f"                          Score: {self._score:010}")
        return '\n'.join(rows)

    def setScore(self, score):
        self._score = score

    def score(self):
        return self._score

    def insertQuarters(self, count):
        self.set(0, count)

    def countTiles(self, tile):
        return list(self._tiles.values()).count(tile)


def part1(file):
    program = list(map(lambda x: int(x, 10), file.readline().split(',')))
    game = ArcadeCabinet(program)
    game.run()
    count = game.countTiles(ArcadeCabinet.Tile.BLOCK)
    print(f"Answer: {count}")


def part2(file):
    program = list(map(lambda x: int(x, 10), file.readline().split(',')))
    game = ArcadeCabinet(program)
    game.insertQuarters(2)
    game.run()
    score = game.score()
    print(game.display())
    print(f"Final Score: {score}")


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
