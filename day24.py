#!/usr/bin/env python3

import sys


def within_bounds(pos, width, height):
    x, y = pos
    return x >= 0 and x < width and y >= 0 and y < height


def pos_index(pos, width, height):
    x, y = pos
    index = (y * width) + x
    assert(index >= 0 and index < width * height)
    return index


def index_pos(index, width, height):
    assert(index >= 0 and index < width * height)
    y = index // width
    x = index - (y * width)
    return x, y


def neighbours(index, width, height):
    x, y = index_pos(index, width, height)
    n = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    tiles = [(x + dx, y + dy) for dx, dy in n]
    tiles = filter(lambda p: within_bounds(p, width, height), tiles)
    return map(lambda p: pos_index(p, width, height), tiles)


def recursive_neighbours(index, width, height):
    mid = (width // 2, height // 2)

    inner = {
        (1, 0): [(1, pos_index((0, y), width, height)) for y in range(height)],
        (-1, 0): [(1, pos_index((width-1, y), width, height)) for y in range(height)],
        (0, -1): [(1, pos_index((x, height-1), width, height)) for x in range(width)],
        (0, 1): [(1, pos_index((x, 0), width, height)) for x in range(width)],
    }

    x, y = index_pos(index, width, height)
    n = [(0, 1), (1, 0), (0, -1), (-1, 0)]
    tiles = []
    for dx, dy in n:
        pos = (x + dx, y + dy)
        px, py = pos
        if pos == mid:
            tiles.extend(inner[(dx, dy)])
            continue
        if px < 0 or px >= width or py < 0 or py >= height:
            mx, my = mid
            tiles.append((-1, pos_index((mx + dx, my + dy), width, height)))
            continue
        tiles.append((0, pos_index(pos, width, height)))
    return tiles


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


def simulate_bugs_recursive(bugs, width, height):
    bug = '#'
    empty = '.'
    size = width * height
    mid = (width // 2, height // 2)
    bugs = ([empty * size] * 2) + bugs[:] + ([empty * size] * 2)
    new_bugs = []
    for level in range(1, len(bugs)-1):
        bug_level = bugs[level]
        new_bug_line = []
        for index, block in enumerate(bug_level):
            if index_pos(index, width, height) == mid:
                new_bug_line.append(empty)
                continue

            adjacent = recursive_neighbours(index, width, height)
            count = 0

            for adj_level, adj_index in adjacent:
                adj_block = bugs[level + adj_level][adj_index]
                if adj_block is bug:
                    count += 1

            if block is bug and count == 1:
                new_bug_line.append(bug)
            elif block is not bug and (count == 1 or count == 2):
                new_bug_line.append(bug)
            else:
                new_bug_line.append(empty)
        new_bugs.append(''.join(new_bug_line))
    return new_bugs


def print_bug(bug, width, height):
    for y in range(height):
        print(bug[y*width:(y+1)*width])


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
    debug = False
    lines = list(map(str.strip, file.readlines()))
    height = len(lines)
    width = len(lines[0])
    bugs = [''.join(lines)]
    loop = 200
    for _ in range(loop):
        bugs = simulate_bugs_recursive(bugs, width, height)

    if debug:
        for level, bug in enumerate(bugs):
            print("Level {}".format(level))
            print_bug(bug, width, height)

    answer = sum(sum(1 for b in line if b == '#') for line in bugs)
    print(f"Answer: {answer}")


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
