+++
date = '2025-12-01T22:52:50+01:00'
draft = false
title = 'Advent of Code - Day 1: Secret Entrance'
tags = ["python", "aoc"]
+++
The [Advent of Code][aoc] is an annual set of Christmas-themed computer programming challenges maintained by software engineer [Eric Wastl][eric_wastl]. It has been running since 2015; the [2025 edition][aoc_2025] consists of 12 puzzles and starts at [Dec. 1][aoc_2025_day_01]. Each puzzle consists of two parts, the second parts unlocks after solving the first successfully. Normally part 1 is rather straightforward, while part 2 is often tricky and / or much harder.

<!--more-->
I have been solving some of the puzzles (on a recreational level) in previous years. This year I want to blog a bit about them. I will be solving puzzles using Python and try to create decent programs. The goal is not to come up with worlds best or most optimal solution: the end result should be a tested (using [pytest][pytest_docu]) and readable solution explained on this blog. This is the page for [Day 1: Secret Entrance][aoc_2025_day_01].

## Table of Contents <!-- omit in toc -->

- [Part 1 - landing on zero](#part-1---landing-on-zero)
- [Part 2 - landing on or passing zero](#part-2---landing-on-or-passing-zero)

## Part 1 - landing on zero

For the first parts you have to enter the secret North Pole base. However there is a problem... you need a password. In order to get the password you have to execute a number of rotations of a dial on a safe and count the numbers of time you land on `0` between consecutive rotations.

The dial has numbers from `0` to `99` (in order). Instructions look like `L68` (turn left 68 clicks), `R55` (turn right 55 clicks), etc. The dial is a circle, turning the dial _left_ from `0` one click makes it point at `99` and _right_ from `99` point at `0`.

This puzzle is rather straightforward: the basics is just a [modulo][modulo] operation which is the `%` operator in Python. While it's possible to combine Parts 1 and 2, I have chosen not to. The [modulo][real_python_modulo] works by returning the remainder after an integer division, .e.g. `7 % 3 = 1` (because `7 = 2 * 3 + 1`). We can use this to keep the dial in the `0` .. `99` range, for example: `(0 - 10) % 100 = 90` and `(90 + 15) % 100 = 5`.

First we need a function to parse a command into a direction and number of clicks. For convenience, lets also convert  _left_ (`L`) rotations to negative clicks and  _right_ (`R`) to positive clicks:

```python
def parse_rotation(rotation):
    direction, clicks = rotation[0], int(rotation[1:])
    if direction == "L":
        return -clicks
    return clicks
```

We can now just add clicks to the current dial position and automatically get left (negative) or right (positive) rotation. We then use the module [modulo][modulo] operation to make sure we stay between `0` and `99`. Finally, we just have to count the number of times we land on zero:

```python
START_POSITION = 50
DIAL_SIZE = 100

def part_1(rotations: PuzzleInputType) -> int:
    position = START_POSITION
    times_landed_on_zero = 0
    for rotation in rotations:
        clicks = parse_rotation(rotation)
        position = (position + clicks) % DIAL_SIZE
        if position == 0:
            times_landed_on_zero += 1
    return times_landed_on_zero
```

The function expects a `rotations` of type `PuzzleInputType` as input parameter. These are the rotations as a list of strings (`list[str]`): one string per rotation, e.g. `["L68", "R55, ...]`. For the full solution, including testing with [pytest][pytest_docu], see: [aoc2025_day01_secret_entrance.py]({{< param "github.bh1428_aoc" >}}/src/aoc2025_day01_secret_entrance.py#L78).

## Part 2 - landing on or passing zero

For part 2 you not only need the times you land on zero (from part 1) but also how often you pass zero during dialing. For instance: when the current number is `90` and you dial `15` to the right you land on `5`. For part 1 this would not count, for part 2 this counts as _passing zero_. To make things easy we can use a combination of [modulo `%` and floor division `//`][modulo_and_floor_division] instead of checking where we land. The modulo will give our end position and the absolute value of the floor division can be used for the number of rounds we made during dialing. We can even combine the two using the Python [`divmod()`][divmod]. Note: we could have used [`divmod()`][divmod] in part 1 as well, but I chose not to.

However, there is one tricky aspect when dialing to the left: we may have to correct our counts. Dialing to the right is never a problem, for example:

| Description                          | Start # | Rotation | End # | divmod(number, dial_size)   |
| :----------------------------------- | :-----: | :------: | :---: | :-------------------------- |
| Start from zero, not landing on zero |   `0`   |  `R25`   | `25`  | `divmod(25, 100) = (0, 25)` |
| Landing on zero                      |  `50`   |  `R50`   | `100` | `divmod(100, 100) = (1, 0)` |
| Shooting past zero                   |  `90`   |  `R15`   | `105` | `divmod(105, 100) = (1, 5)` |
| Extra round, landing on zero         |  `75`   |  `R225`  | `300` | `divmod(300, 100) = (3, 0)` |
| Extra round, not landing on zero     |  `80`   |  `R225`  | `305` | `divmod(305, 100) = (3, 5)` |

As shown, the result from `divmod(new_position, dial_size)` is a tuple where the first element is the number of rounds we made and the second the number we land on. When we turn to the left we need corrections, e.g (remember... the number of rounds is the __absolute__ value of the _floor division_):

| Description                          | Start # | Rotation | End #  | divmod(number, dial_size)      | Comment                         |
| :----------------------------------- | :-----: | :------: | :----: | :----------------------------- | ------------------------------- |
| Start from zero, not landing on zero |   `0`   |  `L25`   | `-25`  | `divmod(-25, 100) = (-1, 75)`  | Incorrect, we did not pass zero |
| Landing on zero                      |  `50`   |  `L50`   |  `0`   | `divmod(0, 100) = (0, 0)`      | Incorrect, missing zero landing |
| Shooting past zero                   |   `5`   |  `L15`   | `-10`  | `divmod(-10, 100) = (-1, 90)`  | Correct                         |
| Extra round, landing on zero         |   `5`   |  `L205`  | `-200` | `divmod(-200, 100) = (-2, 0)`  | Incorrect, missing zero landing |
| Extra round, not landing on zero     |   `5`   |  `R225`  | `-220` | `divmod(-220, 100) = (-3, 80)` | Correct                         |

In conclusion: we can use [`divmod()`][divmod], but when turn left we have to make a correction when we start from `0` or land on `0`. This gives us the following solution:

```python
START_POSITION = 50
DIAL_SIZE = 100

def part_2(rotations: PuzzleInputType) -> int:
    position = START_POSITION
    landing_on_or_passing_zero = 0
    for rotation in rotations:
        clicks = parse_rotation(rotation)
        rounds, new_position = divmod(position + clicks, DIAL_SIZE)
        landing_on_or_passing_zero += abs(rounds)
        if clicks < 0:
            if position == 0:
                landing_on_or_passing_zero -= 1
            if new_position == 0:
                landing_on_or_passing_zero += 1
        position = new_position
    return landing_on_or_passing_zero
```

Again, the function expects a `rotations` of type `PuzzleInputType` as input parameter. This is the same list of strings (`list[str]`) as for _part 1_. For the full solution, including test cases, see: [aoc2025_day01_secret_entrance.py]({{< param "github.bh1428_aoc" >}}/src/aoc2025_day01_secret_entrance.py#L94).

[aoc_2025_day_01]: https://adventofcode.com/2025/day/1
[aoc_2025]: https://adventofcode.com/2025
[aoc]: https://adventofcode.com/
[divmod]: https://docs.python.org/3/library/functions.html#divmod
[eric_wastl]: https://was.tl/
[modulo_and_floor_division]: https://docs.python.org/3/reference/expressions.html#index-68
[modulo]: https://en.wikipedia.org/wiki/Modulo
[pytest_docu]: https://docs.pytest.org/en/stable/
[real_python_modulo]: https://realpython.com/python-modulo-operator/
