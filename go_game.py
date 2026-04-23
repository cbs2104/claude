#!/usr/bin/env python3
"""
围棋游戏 - 命令行版
人机对弈，高强度心算模式
"""

import random
from typing import Optional

BOARD_SIZE = 19
EMPTY = 0
BLACK = 1  # 玩家
WHITE = 2  # 电脑


class GoGame:
    def __init__(self, board_size=BOARD_SIZE):
        self.size = board_size
        self.board = [[EMPTY for _ in range(board_size)] for _ in range(board_size)]
        self.current_player = BLACK
        self captures = {BLACK: 0, WHITE: 0}
        self.move_history = []

    def get_neighbors(self, x, y):
        """获取相邻位置"""
        neighbors = []
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nx, ny = x + dx, y + dy
            if 0 <= nx < self.size and 0 <= ny < self.size:
                neighbors.append((nx, ny))
        return neighbors

    def get_group(self, x, y, visited=None):
        """获取棋子群组（包含所有相连的同色棋子）"""
        if visited is None:
            visited = set()

        color = self.board[y][x]
        if color == EMPTY:
            return set()

        if (x, y) in visited:
            return set()

        visited.add((x, y))
        group = {(x, y)}

        for nx, ny in self.get_neighbors(x, y):
            if self.board[ny][nx] == color:
                group |= self.get_group(nx, ny, visited)

        return group

    def count_liberties(self, x, y):
        """计算气数"""
        color = self.board[y][x]
        if color == EMPTY:
            return 0

        group = self.get_group(x, y)
        liberties = set()

        for gx, gy in group:
            for nx, ny in self.get_neighbors(gx, gy):
                if self.board[ny][nx] == EMPTY:
                    liberties.add((nx, ny))

        return len(liberties)

    def remove_dead_stones(self, x, y):
        """移除死子"""
        color = self.board[y][x]
        opponent = WHITE if color == BLACK else BLACK

        dead_stones = set()
        for nx, ny in self.get_neighbors(x, y):
            if self.board[ny][nx] == opponent:
                if self.count_liberties(nx, ny) == 0:
                    group = self.get_group(nx, ny)
                    dead_stones |= group

        for gx, gy in dead_stones:
            self.board[gy][gx] = EMPTY

        if dead_stones:
            self.captures[color] += len(dead_stones)

        return dead_stones

    def is_valid_move(self, x, y, color):
        """检查落子是否合法"""
        if not (0 <= x < self.size and 0 <= y < self.size):
            return False, "位置超出棋盘范围"
        if self.board[y][x] != EMPTY:
            return False, "该位置已有棋子"
        if (x, y) in [m[0] for m in self.move_history[-2:]]:
            return False, "不能打劫（禁止全局同型）"

        self.board[y][x] = color
        if self.count_liberties(x, y) == 0:
            self.board[y][x] = EMPTY
            self.remove_dead_stones(x, y)
            if self.count_liberties(x, y) == 0:
                return False, "无气的子不能存活"

        self.board[y][x] = EMPTY
        return True, "合法"

    def make_move(self, x, y, color):
        """执行落子"""
        self.board[y][x] = color
        self.move_history.append(((x, y), color))

        dead = self.remove_dead_stones(x, y)
        return dead

    def parse_move(self, move_str):
        """解析用户输入的坐标"""
        move_str = move_str.strip().upper()
        if move_str == "PASS":
            return None, None
        if move_str == "END":
            return "END", "END"

        try:
            col = ord(move_str[0]) - ord('A')
            if col >= 9:
                col -= 1
            row = int(move_str[1:]) - 1
            return col, row
        except:
            return None, None

    def format_position(self, x, y):
        """将坐标转换为字母数字格式"""
        col = chr(ord('A') + x if x < 9 else ord('A') + x + 1)
        row = y + 1
        return f"{col}{row}"

    def count_territory(self):
        """计算实地（在终端计算）"""
        visited = set()
        black_territory = 0
        white_territory = 0

        for y in range(self.size):
            for x in range(self.size):
                if (x, y) in visited or self.board[y][x] != EMPTY:
                    continue

                territory = set()
                queue = [(x, y)]
                while queue:
                    cx, cy = queue.pop(0)
                    if (cx, cy) in visited:
                        continue
                    visited.add((cx, cy))
                    if self.board[cy][cx] != EMPTY:
                        continue
                    territory.add((cx, cy))
                    for nx, ny in self.get_neighbors(cx, cy):
                        if 0 <= nx < self.size and 0 <= ny < self.size:
                            if self.board[ny][nx] == EMPTY and (nx, ny) not in visited:
                                queue.append((nx, ny))

                borders = set()
                for tx, ty in territory:
                    for nx, ny in self.get_neighbors(tx, ty):
                        if self.board[ny][nx] != EMPTY:
                            borders.add(self.board[ny][nx])

                if borders == {BLACK}:
                    black_territory += len(territory)
                elif borders == {WHITE}:
                    white_territory += len(territory)

        return black_territory, white_territory

    def computer_move(self):
        """电脑AI - 简单策略"""
        valid_moves = []
        for y in range(self.size):
            for x in range(self.size):
                if self.board[y][x] == EMPTY:
                    is_valid, _ = self.is_valid_move(x, y, WHITE)
                    if is_valid:
                        score = self.evaluate_position(x, y, WHITE)
                        valid_moves.append((score, x, y))

        if not valid_moves:
            return None, None

        valid_moves.sort(reverse=True)

        # 添加一些随机性
        top_moves = [m for m in valid_moves if m[0] >= valid_moves[0][0] - 3]
        _, x, y = random.choice(top_moves)
        return x, y

    def evaluate_position(self, x, y, color):
        """评估位置分数"""
        score = 0

        # 气
        self.board[y][x] = color
        score += self.count_liberties(x, y) * 2
        self.board[y][x] = EMPTY

        # 提子评估（检查是否能提对方子）
        for nx, ny in self.get_neighbors(x, y):
            if self.board[ny][nx] != EMPTY and self.board[ny][nx] != color:
                if self.count_liberties(nx, ny) == 1:
                    score += 10

        # 角落和边（实地价值高）
        if (x == 0 or x == self.size - 1) and (y == 0 or y == self.size - 1):
            score += 8
        elif x == 0 or x == self.size - 1 or y == 0 or y == self.size - 1:
            score += 3

        # 避免自己在边角被吃
        self.board[y][x] = color
        if self.count_liberties(x, y) == 1:
            score -= 5
        self.board[y][x] = EMPTY

        return score

    def print_board_text(self):
        """用文本绘制棋盘（最后显示）"""
        print("\n    " + " ".join([chr(ord('A') + i) for i in range(self.size)]))
        print("  +" + "-" * (self.size * 2 - 1) + "+")
        for y in range(self.size):
            row_str = f"{y+1:2d} |"
            for x in range(self.size):
                if self.board[y][x] == EMPTY:
                    row_str += " ."
                elif self.board[y][x] == BLACK:
                    row_str += " X"
                else:
                    row_str += " O"
            print(row_str + " |")
        print("  +" + "-" * (self.size * 2 - 1) + "+")

    def play(self):
        """游戏主循环"""
        print("=" * 50)
        print("       围棋 - 命令行版 (19路)")
        print("=" * 50)
        print("\n游戏规则:")
        print("- 输入坐标落子，格式: 列字母+行数字 (如 A1, T15)")
        print("- 输入 PASS 停一手")
        print("- 输入 END 停一手并终局")
        print("- 你执黑先手")
        print("\n开始对局！\n")

        move_count = 0
        consecutive_pass = 0

        while True:
            if self.current_player == BLACK:
                print(f"\n【第 {move_count + 1} 手】轮到你落子 (黑)")
                print(f"目前提子: 黑={self.captures[BLACK]}, 白={self.captures[WHITE]}")

                move_str = input("\n请输入坐标 (如 Q16), PASS(停一手), END(终局): ").strip()

                if move_str.upper() == "PASS":
                    print("你选择停一手")
                    consecutive_pass += 1
                    self.current_player = WHITE
                    self.move_history.append(((None, None), BLACK))
                    continue
                elif move_str.upper() == "END":
                    print("终局！")
                    break

                x, y = self.parse_move(move_str)
                if x is None:
                    print("输入格式错误！请使用如 A1, Q16 格式")
                    continue

                is_valid, msg = self.is_valid_move(x, y, BLACK)
                if not is_valid:
                    print(f"非法落子: {msg}")
                    continue

                dead = self.make_move(x, y, BLACK)
                if dead:
                    print(f"✦ 提掉白子 {len(dead)} 颗！")

                consecutive_pass = 0
                self.current_player = WHITE
                move_count += 1

            else:
                print(f"\n【第 {move_count + 1} 手】电脑思考中 (白)...")
                x, y = self.computer_move()

                if x is None:
                    print("电脑选择停一手")
                    consecutive_pass += 1
                    self.current_player = BLACK
                    self.move_history.append(((None, None), WHITE))
                    continue

                dead = self.make_move(x, y, WHITE)
                pos = self.format_position(x, y)
                print(f"电脑落子于 {pos}")
                if dead:
                    print(f"✦ 提掉黑子 {len(dead)} 颗！")

                consecutive_pass = 0
                self.current_player = BLACK
                move_count += 1

            if consecutive_pass >= 2:
                print("\n双方停手，游戏结束！")
                break

        # 终局计算
        self.print_board_text()
        print("\n" + "=" * 50)
        print("           游戏结束 - 胜负判定")
        print("=" * 50)

        bt, wt = self.count_territory()
        black_score = bt + self.captures[BLACK]
        white_score = wt + self.captures[WHITE] + 6.5  # 黑贴6.5目

        print(f"\n黑棋: 实地 {bt} 目 + 提子 {self.captures[BLACK]} = {black_score} 目")
        print(f"白棋: 实地 {wt} 目 + 提子 {self.captures[WHITE]} + 贴目 6.5 = {white_score} 目")

        if black_score > white_score:
            print(f"\n★ 黑棋胜！{black_score - white_score:.1f} 目")
        elif white_score > black_score:
            print(f"\n★ 白棋胜！{white_score - black_score:.1f} 目")
        else:
            print("\n★ 和棋！")

        print(f"\n总手数: {move_count}")


if __name__ == "__main__":
    game = GoGame()
    game.play()