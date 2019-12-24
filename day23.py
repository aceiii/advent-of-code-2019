#!/usr/bin/env python3

import sys
from computer import Computer, parse_program
from collections import deque


class NetworkComputer(object):
    def __init__(self, addr, program, network):
        self._addr = addr
        self._computer = Computer(program, self._processInput, self._output)
        self._network = network
        self._processing = None
        self._write_buffer = []
        self._inputMode = 0

    def _input(self):
        return self._addr

    def _input2(self):
        value = self._processing
        self._processing = None
        if value:
            return value
        if self.net_buffer(self._addr):
            x, y = self.net_buffer(self._addr).popleft()
            self._processing = y
            return x
        return -1

    def _processInput(self):
        if self._inputMode:
            return self._input2()
        self._inputMode = 1
        return self._input()

    def _output(self, value):
        self._write_buffer.append(value)
        if len(self._write_buffer) == 3:
            addr, x, y = self._write_buffer
            self._write_buffer = []
            self.net_buffer(addr).append((x, y))

    def net_buffer(self, addr):
        if addr not in self._network:
            self._network[addr] = deque()
        return self._network[addr]

    def step(self):
        return self._computer.step()

    def stopped(self):
        return self._computer.stopped()


def part1(file):
    N = 50
    program = parse_program(file)
    network = {}
    computers = [NetworkComputer(n, program, network) for n in range(N)]
    target = 255
    while target not in network:
        for comp in computers:
            if comp.stopped():
                continue
            comp.step()
    x, y = network[target].popleft()
    print(f"Answer: {y}")


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
