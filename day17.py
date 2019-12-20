#!/usr/bin/env python3

import sys
from collections import deque
from computer import Computer, parse_program, int_input, std_output


def neighbours(pos):
    x, y = pos
    tiles = [(0, -1), (1, 0), (0, 1), (-1, 0)]
    for tx, ty in tiles:
        yield (x + tx, y + ty)


def is_intersection(pos, view):
    x, y = pos
    c = '#'
    if view[y][x] == c and all(view[j][i] == c for i, j in neighbours(pos)):
        return True
    return False


def is_corner(pos, view):
    x, y = pos
    c = '#'
    if view[y][x] != c:
        return False

    tiles = filter(lambda x: x == c, (view[j][i] for i, j in neighbours(pos)))
    if len(tiles) != 2:
        return False

    (x1, y1), (x2, y2) = tiles
    low, high = sorted((abs(x2 - x1), abs(y2 - y1)))

    return True if low == 0 and high == 1 else False


def is_deadend(pos, view):
    pass



def find_intersections(view):
    height = len(view)
    width = len(view[0])
    target = '#'
    intersections = []
    for y in range(1, height - 1):
        for x in range(1, width - 1):
            pos = (x, y)
            if is_intersection(pos, view):
                intersections.append(pos)
    return intersections


def find_robot(view):
    height = len(view)
    width = len(view[0])
    target = ['<', '^', 'v', '>']
    facing = {
        '<': (-1, 0),
        '>': (1, 0),
        '^': (0, -1),
        'v': (0, 1),
    }
    for y in range(height):
        for x in range(width):
            c = view[y][x]
            if c in target:
                return (x, y), facing[c]


def get_next_tile(pos, facing, view):
    x, y = pos
    dx, dy = facing
    x, y = x + dx, y + dy
    height = len(view)
    width = len(view[0])
    if y < 0 or y >= height or x < 0 or x >= width:
        return None
    if view[y][x] == '#':
        return (x, y)


def left_turn(facing):
    x, y = facing
    return (y, -x)


def right_turn(facing):
    x, y = facing
    return (-y, x)


def get_left_turn(pos, facing, view):
    x, y = pos
    dx, dy = left_turn(facing)
    x, y = x + dx, y + dy
    height = len(view)
    width = len(view[0])
    if y < 0 or y >= height or x < 0 or x >= width:
        return None, (dx, dy)
    return ((x, y) if view[y][x] == '#' else None), (dx, dy)


def get_right_turn(pos, facing, view):
    x, y = pos
    dx, dy = right_turn(facing)
    x, y = x + dx, y + dy
    height = len(view)
    width = len(view[0])
    if y < 0 or y >= height or x < 0 or x >= width:
        return None, (dx, dy)
    return ((x, y) if view[y][x] == '#' else None), (dx, dy)


def build_steps(robot, view):
    pos, facing = find_robot(view)
    steps = []
    target = '#'
    while pos:
        next_pos = get_next_tile(pos, facing, view)
        if next_pos:
            pos = next_pos
            if steps and type(steps[-1]) is int:
                steps[-1] += 1
            else:
                steps.append(1)
            continue
        next_pos, new_facing = get_right_turn(pos, facing, view)
        if next_pos:
            pos = next_pos
            facing = new_facing
            steps.append('R')
            steps.append(1)
            continue
        next_pos, new_facing = get_left_turn(pos, facing, view)
        if next_pos:
            pos = next_pos
            facing = new_facing
            steps.append('L')
            steps.append(1)
            continue
        pos = None
    return steps


def compact(steps, actions=None, procedures=None):
    if actions is None:
        actions = []

    if procedures is None:
        procedures = []

    if not steps:
        return [(actions, procedures)]

    valid_states = []
    max_len = 10
    max_procedures = 3
    for i in range(min(max_len, len(steps))):
        procedure = ','.join(str(s) for s in steps[:i+1])
        rest_steps = steps[i+1:]
        next_actions = actions[:]
        next_procedures = procedures[:]

        if procedure in next_procedures:
            action = next_procedures.index(procedure)
            next_actions.append(action)
        else:
            next_procedures.append(procedure)
            next_actions.append(len(next_procedures) - 1)

        if len(next_procedures) <= max_procedures and len(next_actions) <= max_len:
            results = compact(rest_steps, next_actions, next_procedures)
            for result in results:
                new_actions, new_procedures = result
                if len(new_procedures) <= max_procedures and len(new_actions) <= max_len:
                    valid_states.append(result)

    return valid_states


def part1(file):
    buffer = []

    def chr_output(value):
        buffer.append(chr(value))

    program = parse_program(file)
    computer = Computer(program, int_input, chr_output)
    computer.run()

    view = ''.join(buffer).strip().split('\n')
    intersections = find_intersections(view)
    alignment = sum(x * y for x, y in intersections)
    print(f"Answer: {alignment}")


def part2(file):
    debug = True
    buffer = deque()

    def chr_output(value):
        buffer.append(chr(value))

    def chr_input():
        return ord(buffer.popleft())

    program = parse_program(file)
    computer = Computer(program, int_input, chr_output)
    computer.run()
    view = list(map(str.strip, ''.join(buffer).strip().split('\n')))
    height = len(view)
    width = len(view[0])

    robot = find_robot(view)
    steps = build_steps(robot, view)
    actions, procedures = compact(steps)[-1]
    actions = ','.join('ABC'[i] for i in actions) + '\n'

    buffer.clear()
    buffer.extend(actions)
    for procedure in procedures:
        buffer.extend(procedure + '\n')
    buffer.extend(('y' if debug else 'n') + '\n')

    map_buffer = [[]]
    map_buffer_offset = height + 7

    def map_output(value):
        nonlocal map_buffer
        nonlocal map_buffer_offset

        if value > 255:
            print(value)
            return

        c = chr(value)

        if map_buffer_offset > 0:
            sys.stdout.write(c)
            if c == '\n':
                map_buffer_offset -= 1
            return

        map_buffer[-1].append(c)

        if c == '\n':
            map_buffer.append([])
            return

        if len(map_buffer) > height:
            cur_buffer, map_buffer = map_buffer[:-1], map_buffer[-1:]
            sys.stdout.write(''.join(''.join(s) for s in cur_buffer))

    computer = Computer(program, chr_input, map_output)
    computer.set(0, 2)
    computer.run()


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
