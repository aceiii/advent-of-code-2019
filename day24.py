#!/usr/bin/env python3

import sys


def within_bounds(pos, width, height):
    x, y = pos
    return x >= 0 and x < width and y >= 0 and y < height


def pos_index(pos, width, height):
    x, y = pos
    return (y * width) + x


def index_pos(index, width, height):
    y = index // width
    x = index - (y * width)
    return x, y


def neighbours(index, width, height):
    x, y = index_pos(index, width, height)
    n = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    tiles = [(x + dx, y + dy) for dx, dy in n]
    tiles = filter(lambda p: within_bounds(p, width, height), tiles)
    return map(lambda p: pos_index(p, width, height), tiles)


def simulate_bugs(bugs, width, height):
    new_bugs = []
    bug = '#'
    empty = '.'
    for index, block in enumerate(bugs):
        adjacent = (bugs[i] for i in neighbours(index, width, height))
        count = sum(1 if adj is bug else 0 for adj in adjacent)
        if block == bug and count == 1:
            new_bugs.append(bug)
        elif block != bug and (count == 1 or count == 2):
            new_bugs.append(bug)
        else:
            new_bugs.append(empty)
    return ''.join(new_bugs)


def part1(file):
    lines = list(map(str.strip, file.readlines()))
    height = len(lines)
    width = len(lines[0])
    bugs = ''.join(lines)
    states = set([bugs])
    while True:
        bugs = simulate_bugs(bugs, width, height)
        if bugs in states:
            break
        states.add(bugs)
    bits = [i for i in range(len(bugs)) if bugs[i] == '#']
    answer = sum(2**i for i in bits)
    print(f"Answer: {answer}")


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
