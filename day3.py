#!/usr/bin/env python3

import sys
from operator import add
from enum import Enum


class Orientation(Enum):
    NONE = 0
    HORIZONTAL = 1
    VERTICAL = 2


class Dir(Enum):
    UP = 'U'
    DOWN = 'D'
    LEFT = 'L'
    RIGHT = 'R'


def parse_rule(rule):
    dir = Dir(rule[0])
    dist = int(rule[1:], 10)
    return (dir, dist)


def parse_rules(line):
    return list(map(parse_rule, line.split(',')))


def get_next_pos(pos, rule):
    dir, dist = rule
    x, y = pos

    if dir == Dir.UP:
        y += dist
    elif dir == Dir.DOWN:
        y -= dist
    elif dir == Dir.LEFT:
        x -= dist
    elif dir == Dir.RIGHT:
        x += dist

    return (x, y)


def segments_from_rules(rules):
    segments = []
    current_pos = (0, 0)
    for rule in rules:
        next_pos = get_next_pos(current_pos, rule)
        segments.append((current_pos, next_pos))
        current_pos = next_pos
    return segments


def segment_orientation(segment):
    (x1, y1), (x2, y2) = segment
    xdiff = abs(x2 - x1)
    ydiff = abs(y2 - y1)
    if xdiff == 0 and ydiff == 0:
        return Orientation.NONE
    elif xdiff == 0:
        return Orientation.VERTICAL
    return Orientation.HORIZONTAL


def intersect_segments(seg1, seg2):
    hor_segment = seg1
    vert_segment = seg2

    orient = segment_orientation(seg1)
    if orient == orient.VERTICAL:
        vert_segment = seg1
        hor_segment = seg2

    min_x = min(hor_segment[0][0], hor_segment[1][0])
    max_x = max(hor_segment[0][0], hor_segment[1][0])
    min_y = min(vert_segment[0][1], vert_segment[1][1])
    max_y = max(vert_segment[0][1], vert_segment[1][1])
    x = vert_segment[0][0]
    y = hor_segment[0][1]

    if x <= min_x or x >= max_x or y <= min_y or y >= max_y:
        return None

    return (x, y)


def find_intersections(segments1, segments2):
    results = []
    for seg1 in segments1:
        for seg2 in segments2:
            if segment_orientation(seg1) == segment_orientation(seg2):
                continue
            intersection = intersect_segments(seg1, seg2)
            if intersection:
                results.append(intersection)
    return results


def manhattan_distance(pos):
    x, y = pos
    return abs(x) + abs(y)


def part1(file):
    rules1 = parse_rules(file.readline())
    rules2 = parse_rules(file.readline())
    segments1 = segments_from_rules(rules1)
    segments2 = segments_from_rules(rules2)
    intersections = find_intersections(segments1, segments2)
    dists = sorted(map(manhattan_distance, intersections))
    print(f"Answer: {dists[0]}")


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
