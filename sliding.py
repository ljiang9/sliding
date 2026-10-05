#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""sliding —— 终端 15 数字拼图（滑动拼图）。

用法:
    python -m sliding              # 4x4 交互开局
    python -m sliding --size 3     # 3x3 (8 拼图)
    python -m sliding --shuffle 50 --seed 42
    python -m sliding --auto wasd   # 脚本化移动序列(验证用)

规则: 用 WASD 移动空格旁的数字,目标是把数字按 1..n*n-1 顺序复原,
空格回到右下角。初始局面由随机合法移动打乱,保证可解。
"""

import argparse
import random
import secrets
import sys

BLANK = 0

MOVES = {
    "w": (-1, 0),  # 把空格上方的数字往下移? 这里定义: 空格向 w 方向移动
    "s": (1, 0),
    "a": (0, -1),
    "d": (0, 1),
}


def solved_board(size):
    """返回 size x size 的目标局面(1..n*n-1, 右下角为 0)。"""
    n = size * size
    return [i % n for i in range(1, n + 1)]


def find_blank(board, size):
    idx = board.index(BLANK)
    return divmod(idx, size)


def apply_move(board, size, key):
    """尝试把空格按 key 方向移动; 非法移动返回 False, 不改变局面。"""
    if key not in MOVES:
        return False
    r, c = find_blank(board, size)
    dr, dc = MOVES[key]
    nr, nc = r + dr, c + dc
    if not (0 <= nr < size and 0 <= nc < size):
        return False
    i = r * size + c
    j = nr * size + nc
    board[i], board[j] = board[j], board[i]
    return True


def is_solved(board, size):
    return board == solved_board(size)


def inversion_count(board):
    tiles = [t for t in board if t != BLANK]
    inv = 0
    for i in range(len(tiles)):
        for j in range(i + 1, len(tiles)):
            if tiles[i] > tiles[j]:
                inv += 1
    return inv


def is_solvable(board, size):
    """逆序数奇偶性判定(教科书判据)。

    size 为奇数: 逆序数为偶数 ⟺ 可解;
    size 为偶数: 逆序数 + 空格所在行(从下往上数)为偶数 ⟺ 可解。
    """
    inv = inversion_count(board)
    if size % 2 == 1:
        return inv % 2 == 0
    r, _ = find_blank(board, size)
    row_from_bottom = size - r
    # 目标局面: inv=0, 空格在倒数第 1 行, 和为 1(奇)——可解 ⟺ 和为奇数
    return (inv + row_from_bottom) % 2 == 1


def shuffle_board(size, steps, rng):
    """从目标局面出发做 steps 次随机合法移动; 结果一定可解。"""
    board = solved_board(size)
    keys = list(MOVES)
    for _ in range(steps):
        apply_move(board, size, rng.choice(keys))
    return board


def render(board, size, moves):
    lines = []
    width = len(str(size * size - 1))
    for r in range(size):
        row = board[r * size:(r + 1) * size]
        cells = [
            (" " * width) if t == BLANK else str(t).rjust(width)
            for t in row
        ]
        lines.append(" ".join(cells))
    lines.append(f"步数: {moves}")
    return "\n".join(lines)


def play_interactive(size, steps, seed):
    rng = random.Random(seed) if seed is not None else secrets.SystemRandom()
    board = shuffle_board(size, steps, rng)
    moves = 0
    print(f"数字拼图 {size}x{size} | 移动: WASD, q 退出")
    while True:
        print(render(board, size, moves))
        if is_solved(board, size):
            print(f"🎉 复原成功! 共用 {moves} 步。")
            return 0
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print(f"\n已退出, 步数 {moves}。")
            return 0
        if cmd in ("q", "quit"):
            print(f"已退出, 步数 {moves}。")
            return 0
        if len(cmd) != 1 or cmd not in MOVES:
            print("输入 w/a/s/d 移动, q 退出。")
            continue
        if not apply_move(board, size, cmd):
            print("这一步不合法(空格已到边缘)。")
            continue
        moves += 1


def play_auto(size, steps, seed, seq):
    rng = random.Random(seed) if seed is not None else secrets.SystemRandom()
    board = shuffle_board(size, steps, rng)
    moves = 0
    ok = 0
    bad = 0
    for key in seq:
        if apply_move(board, size, key):
            moves += 1
            ok += 1
        else:
            bad += 1
    print(render(board, size, moves))
    print(f"auto: 序列 {len(seq)} 步, 合法 {ok}, 非法 {bad}, solved={is_solved(board, size)}")
    return 0


def main(argv=None):
    ap = argparse.ArgumentParser(description="终端数字拼图 (sliding puzzle)")
    ap.add_argument("--size", type=int, default=4, help="棋盘边长 (默认 4)")
    ap.add_argument("--shuffle", type=int, default=100, help="打乱步数 (默认 100)")
    ap.add_argument("--seed", type=int, default=None, help="随机种子")
    ap.add_argument("--auto", type=str, default=None,
                    help="脚本化移动序列, 如 --auto wasd (验证用)")
    args = ap.parse_args(argv)
    if args.size < 2 or args.size > 9:
        print("error: --size 取值范围 2-9", file=sys.stderr)
        return 2
    if args.shuffle < 0:
        print("error: --shuffle 不能为负", file=sys.stderr)
        return 2
    if args.auto is not None:
        seq = [ch for ch in args.auto.strip().lower()]
        return play_auto(args.size, args.shuffle, args.seed, seq)
    return play_interactive(args.size, args.shuffle, args.seed)


if __name__ == "__main__":
    raise SystemExit(main())
