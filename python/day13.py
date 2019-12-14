""" Solution to Day 13 """

from collections import namedtuple
from enum import IntEnum

from intcode import Computer
import glasskey as gk

from common import asset

TILE_CHARS = [' ', '#', '8', '=', 'o']


class TileId(IntEnum):
    """ Enumeration of tile IDs """
    Empty = 0
    Wall = 1
    Block = 2
    Paddle = 3
    Ball = 4


class Tile(namedtuple("Tile", ["x", "y", "tile_id"])):
    """ Class representing a tile on the game screen """

    def __repr__(self):
        return TILE_CHARS[self.tile_id.value]


def _run_game(program, use_ai=True, playable=False):
    program[0] = 2
    computer = Computer(program)

    gk.start()
    grid = gk.create_grid(28, 46, "Breakout")
    grid.map_color(TILE_CHARS[TileId.Wall], gk.Colors.Gray)
    grid.map_color(TILE_CHARS[TileId.Paddle], gk.Colors.Magenta)
    grid.map_color(TILE_CHARS[TileId.Ball], gk.Colors.Magenta)

    paddle_x = 0
    ball_x = 0
    score = 0
    pressed = False
    while not computer.is_halted:
        while not computer.needs_input and not computer.is_halted:
            computer.step()
            if computer.num_outputs == 3:
                x = computer.read()
                y = computer.read()
                if x > -1:
                    tile_id = TileId(computer.read())
                    if tile_id == TileId.Block:
                        if y < 5:
                            color = gk.Colors.Purple
                        elif y < 8:
                            color = gk.Colors.Red
                        elif y < 11:
                            color = gk.Colors.Orange
                        elif y < 14:
                            color = gk.Colors.Yellow
                        elif y < 17:
                            color = gk.Colors.Green
                        else:
                            color = gk.Colors.Blue

                        grid.draw(y+2, x, [gk.Letter(TILE_CHARS[TileId.Block], color)])
                    else:
                        if tile_id == TileId.Paddle:
                            paddle_x = x
                        elif tile_id == TileId.Ball:
                            ball_x = x

                        grid.draw(y+2, x, TILE_CHARS[tile_id])
                else:
                    score = computer.read()
                    grid.draw(0, 0, str(score))

        if use_ai:
            if paddle_x < ball_x:
                computer.write(1)
            elif paddle_x > ball_x:
                computer.write(-1)
            else:
                computer.write(0)
        else:
            if gk.is_pressed(gk.Key.Left):
                if not pressed:
                    computer.write(-1)
                    pressed = True
            elif gk.is_pressed(gk.Key.Right):
                if not pressed:
                    computer.write(1)
                    pressed = True
            elif gk.is_pressed(gk.Key.Space):
                if not pressed:
                    computer.write(0)
                    pressed = True
            else:
                pressed = False

        grid.blit()
        if playable:
            gk.next_frame()

    gk.stop()

    return score


def _main():
    with open(asset("day13.txt")) as file:
        program = [int(code) for code in file.read().split(',')]

    tiles = []
    computer = Computer(program)
    while not computer.is_halted:
        computer.step()
        if computer.num_outputs == 3:
            x = computer.read()
            y = computer.read()
            tile_id = TileId(computer.read())
            tiles.append(Tile(x, y, tile_id))

    print("Part 1:", sum([tile.tile_id == TileId.Block for tile in tiles]))

    score = _run_game(program)
    print("Part 2:", score)


if __name__ == "__main__":
    _main()
