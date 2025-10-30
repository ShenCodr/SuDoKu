import random
import copy
import sys
import os

# -----------------------------------------------------------------
# ANSI 颜色代码 (用于高级要求：区分颜色)
# -----------------------------------------------------------------
class Colors:
    """定义终端输出的颜色"""
    # 用户输入的数字使用蓝色
    USER_INPUT = '\033[94m'
    # 原始给定的数字使用绿色
    GIVEN = '\033[92m'
    # 错误提示使用红色
    ERROR = '\033[91m'
    # 胜利提示使用洋红色
    WIN = '\033[95m'
    # 菜单标题使用黄色
    HEADER = '\033[93m'
    # 重置颜色
    ENDC = '\033[0m'

    @staticmethod
    def disable_colors():
        """在不支持的终端上禁用颜色"""
        Colors.USER_INPUT = ''
        Colors.GIVEN = ''
        Colors.ERROR = ''
        Colors.WIN = ''
        Colors.HEADER = ''
        Colors.ENDC = ''

if os.name == 'nt' and os.environ.get('TERM', '') == '':
    pass # 假设终端支持

# -----------------------------------------------------------------
# 数独核心逻辑 (生成器 & 求解器)
# -----------------------------------------------------------------

class SudokuLogic:
    """封装数独生成和求解的核心逻辑"""

    def __init__(self):
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = None

    def _find_empty_cell(self, grid):
        """找到下一个空格子 (0) """
        for r in range(9):
            for c in range(9):
                if grid[r][c] == 0:
                    return r, c
        return None

    def _is_valid(self, grid, r, c, num):
        """检查数字在行、列、3x3宫内是否有效"""
        # 检查行
        if num in grid[r]:
            return False
        # 检查列
        if num in [grid[i][c] for i in range(9)]:
            return False
        # 检查 3x3 宫
        start_row, start_col = 3 * (r // 3), 3 * (c // 3)
        for i in range(start_row, start_row + 3):
            for j in range(start_col, start_col + 3):
                if grid[i][j] == num:
                    return False
        return True

    def solve(self, grid_to_solve):
        """
        使用回溯法求解数独。
        返回 True 表示找到解，False 表示无解。
        """
        empty_cell = self._find_empty_cell(grid_to_solve)
        if not empty_cell:
            return True  # 没有空格子了，说明解完了

        r, c = empty_cell
        # 尝试 1-9
        for num in range(1, 10):
            if self._is_valid(grid_to_solve, r, c, num):
                grid_to_solve[r][c] = num
                
                if self.solve(grid_to_solve):
                    return True
                
                # 回溯
                grid_to_solve[r][c] = 0
        
        return False

    def generate_full_board(self):
        """
        生成一个完整的、被填满的数独终盘。
        """
        self.grid = [[0 for _ in range(9)] for _ in range(9)]
        
        # 为了随机性，我们随机填充第一行
        base = list(range(1, 10))
        random.shuffle(base)
        self.grid[0] = base
        
        # 基于第一行求解
        self.solve(self.grid)
        self.solution = copy.deepcopy(self.grid)
        return self.solution

    def create_puzzle(self, difficulty_level):
        """
        根据难度挖空
        1: 简单 (20)
        2: 中等 (40)
        3: 困难 (60)
        """
        if difficulty_level == 1:
            blanks = 20
        elif difficulty_level == 2:
            blanks = 40
        elif difficulty_level == 3:
            blanks = 60
        else:
            blanks = 20 # 默认简单

        # 先生成一个终盘
        full_board = self.generate_full_board()
        puzzle_board = copy.deepcopy(full_board)
        
        # 开始挖空
        cells_removed = 0
        attempts = 0 # 防止死循环
        while cells_removed < blanks and attempts < 1000:
            r = random.randint(0, 8)
            c = random.randint(0, 8)
            
            if puzzle_board[r][c] != 0:
                puzzle_board[r][c] = 0
                cells_removed += 1
            attempts += 1
            
        return puzzle_board, self.solution

# -----------------------------------------------------------------
# 游戏界面 & 菜单
# -----------------------------------------------------------------

def clear_screen():
    """清屏，让界面更整洁"""
    os.system('cls' if os.name == 'nt' else 'clear')

def print_board(board, original_puzzle_board):
    """
    打印游戏棋盘。
    使用 Unicode 字符来绘制更美观的方格。
    """
    
    # 顶部列号 (调整了间距以对齐)
    print(Colors.HEADER + "\n     1   2   3   4   5   6   7   8   9 (列)" + Colors.ENDC)
    
    # 顶部边框 (粗外框，细内T)
    print("   ┏━━━┯━━━┯━━━┳━━━┯━━━┯━━━┳━━━┯━━━┯━━━┓")
    
    for r in range(9):
        # 打印行号和左侧粗边框
        print(f"{Colors.HEADER}{r+1} {Colors.ENDC} ┃", end="") # 粗 ┃
        
        for c in range(9):
            # 打印数字 (用空格包裹，使其居中)
            num = board[r][c]
            char_to_print = ""
            if original_puzzle_board[r][c] != 0:
                # 原始数字 (绿色)
                char_to_print = f" {Colors.GIVEN}{num}{Colors.ENDC} "
            elif num != 0:
                # 用户填的 (蓝色)
                char_to_print = f" {Colors.USER_INPUT}{num}{Colors.ENDC} "
            else:
                # 空格
                char_to_print = " . "
            
            print(char_to_print, end="")
                
            # 打印列分隔符
            if (c + 1) % 3 == 0:
                print("┃", end="") # 粗 ┃ (3x3宫格分隔)
            else:
                print("│", end="") # 细 │ (单元格分隔)
        
        # 打印行号提示
        print(f" {Colors.HEADER}(行){Colors.ENDC}")
        
        # 打印行分隔符
        if (r + 1) % 3 == 0 and r < 8:
            # 粗 ┣┿╋ (3x3宫格分隔)
            print("   ┣━━━┿━━━┿━━━╋━━━┿━━━┿━━━╋━━━┿━━━┿━━━┫")
        elif r < 8:
            # 细 ┠┼╂ (单元格分隔)
            print("   ┠───┼───┼───╂───┼───┼───╂───┼───┼───┨")
    
    # 底部边框 (粗外框，细内T)
    print("   ┗━━━┷━━━┷━━━┻━━━┷━━━┷━━━┻━━━┷━━━┷━━━┛")


def show_rules():
    """显示游戏规则"""
    clear_screen()
    print(Colors.HEADER + "--- 游戏规则 (b) ---" + Colors.ENDC)
    print("，数独是一个基于逻辑的数字填充游戏。")
    print("你需要将 1 到 9 的数字填入 9x9 的网格中：")
    print("1. 每一行都必须包含 1 到 9 的所有数字，不能重复。")
    print("2. 每一列都必须包含 1 到 9 的所有数字，不能重复。")
    print("3. 每一个 3x3 的小宫格（共9个）也必须包含 1 到 9 的所有数字，不能重复。")
    print("\n按回车键返回主菜单...")
    input()

def show_key_instructions():
    """显示按键说明"""
    clear_screen()
    print(Colors.HEADER + "--- 按键说明 (c) ---" + Colors.ENDC)
    print("，请按照提示输入对应的按键：")
    print("\n[主菜单]")
    print("  a - 开始游戏")
    print("  b - 查看游戏规则")
    print("  c - 查看按键说明")
    print("  e - 退出游戏")
    print("\n[游戏界面中]")
    print("  a - 填入数字")
    print("  b - 检查当前答案是否正确")
    print("  c - 查看本局答案")
    print("  d - 新开一局（同难度）")
    print("  e - 返回上一级（重新选择难度）")
    print("\n按回车键返回主菜单...")
    input()

def get_user_input(user_board, puzzle_board):
    """
    获取用户输入的坐标和值。
    包含错误处理。
    """
    try:
        row_str = input("请输入行号 (1-9)，或输入'q'取消: ")
        if row_str.lower() == 'q': return
        row = int(row_str)

        col_str = input("请输入列号 (1-9)，或输入'q'取消: ")
        if col_str.lower() == 'q': return
        col = int(col_str)

        val_str = input("请输入数字 (1-9)，或输入'0'清空该格，或输入'q'取消: ")
        if val_str.lower() == 'q': return
        val = int(val_str)

        # 检查输入范围
        if not (1 <= row <= 9 and 1 <= col <= 9 and 0 <= val <= 9):
            print(Colors.ERROR + "\n输入错误，行、列、值都必须在 1-9 (清空为0) 范围内！" + Colors.ENDC)
            input("按回车键继续...")
            return

        # 转换为 0-based 索引
        r_idx, c_idx = row - 1, col - 1

        # 检查是否修改了原始数字
        if puzzle_board[r_idx][c_idx] != 0:
            original_val = puzzle_board[r_idx][c_idx]
            print(Colors.ERROR + 
                  f"\n对不起，原题中该位置 ({row}, {col}) 已经指定为 {original_val}，你不能修改这个值！" 
                  + Colors.ENDC)
            input("按回车键继续...")
            return
        
        # 允许用户修改自己填入的值
        user_board[r_idx][c_idx] = val
        print(f"设置 ({row}, {col}) 为 {val} 成功！")

    except ValueError:
        print(Colors.ERROR + "\n输入错误，请输入数字！" + Colors.ENDC)
        input("按回车键继续...")
    except Exception as e:
        print(Colors.ERROR + f"\n发生未知错误: {e}" + Colors.ENDC)
        input("按回G键继续...")

def check_result(user_board, solution_board, puzzle_board):
    """检查结果是否正确"""
    # 检查是否填满
    for r in range(9):
        for c in range(9):
            if user_board[r][c] == 0:
                print(Colors.ERROR + "\n棋盘还没有填满，请继续加油！" + Colors.ENDC)
                input("按回车键继续...")
                return False # 未完成

    # 检查是否和答案一致
    if user_board == solution_board:
        clear_screen()
        # 胜利时，用 puzzle_board 作为底板，这样原始数字是绿色，用户填的（现在也是正确的）是蓝色
        print_board(user_board, puzzle_board)
        print(Colors.WIN + """
        
        /\\_/\\
       ( o.o )  恭喜！
        > ^ <   完全正确！
                
        """ + Colors.ENDC) # 胜利庆祝界面
        input("按回车键返回难度选择...")
        return True # 胜利
    else:
        clear_screen()
        print_board(user_board, puzzle_board) # 传入 puzzle_board 来保持原始数字颜色
        print(Colors.ERROR + "\n很遗憾，结果不正确...")
        print("请再仔细检查一下！")
        # 高级要求：提示错误位置
        print("错误的位置 (行, 列) 有：")
        errors = []
        for r in range(9):
            for c in range(9):
                if user_board[r][c] != solution_board[r][c]:
                    errors.append(f"({r+1}, {c+1})")
        print(", ".join(errors) + " ")
        input("按回车键继续...")
        return False # 失败

def view_answer(solution_board, puzzle_board):
    """查看答案"""
    clear_screen()
    print(Colors.HEADER + "--- 答案 ---" + Colors.ENDC)
    print("，正确的答案是这个：")
    # 传入 puzzle_board 是为了正确给原始数字上色
    print_board(solution_board, puzzle_board) 
    print("\n记住答案了吗？")
    input("按回车键返回游戏...")


# -----------------------------------------------------------------
# 游戏主循环
# -----------------------------------------------------------------

def game_loop(difficulty_level):
    """游戏主界面循环"""
    
    # 1. 生成谜题
    logic = SudokuLogic()
    try:
        puzzle_board, solution_board = logic.create_puzzle(difficulty_level)
    except Exception as e:
        print(Colors.ERROR + f"生成谜题时出错: {e}。可能是求解器陷入困境了。")
        print("请尝试返回主菜单重试。")
        input()
        return 'exit' # 退出到难度选择
        
    # user_board 是玩家当前填写的棋盘
    user_board = copy.deepcopy(puzzle_board)
    
    # 2. 游戏循环
    while True:
        clear_screen()
        print_board(user_board, puzzle_board) #
        
        print(Colors.HEADER + "\n--- 游戏菜单---" + Colors.ENDC)
        print("a. 填入数字")
        print("b. 检查结果")
        print("c. 查看答案")
        print("d. 新开一局 (同难度)")
        print("e. 返回上一级 (重选难度)")
        choice = input("请输入选项 (a/b/c/d/e) : ").lower()

        if choice == 'a':
            get_user_input(user_board, puzzle_board) #
        
        elif choice == 'b':
            if check_result(user_board, solution_board, puzzle_board): #
                return 'win' # 胜利，退出循环，返回到难度选择
        
        elif choice == 'c':
            view_answer(solution_board, puzzle_board) #
            # 查看答案后可以继续游戏
        
        elif choice == 'd':
            print("正在重新生成同难度的谜题...") #
            return 'new_game' # 告诉上一层要新开一局
        
        elif choice == 'e':
            return 'exit' # 告诉上一层要返回难度菜单
        # ---------------------------------
        # ★★★ 秘密功能 ★★★
        # ---------------------------------
        elif choice == 'k':
            # 嘘... 魔法发生啦 ✨
            user_board = copy.deepcopy(solution_board)
            input("按回车键继续...")
        # ---------------------------------
        else:
            print(Colors.ERROR + "输入了无效的选项，请重新输入 (a/b/c/d/e) 。" + Colors.ENDC)
            input("按回车键继续...")


def difficulty_menu():
    """难度选择界面"""
    while True:
        clear_screen()
        print(Colors.HEADER + "--- 游戏难度选择 ---" + Colors.ENDC)
        print("1. 简单 (20个空格)")
        print("2. 中等 (40个空格)")
        print("3. 困难 (60个空格)")
        print("0. 返回主菜单")
        
        choice = input("请选择难度 (1/2/3/0) : ")
        
        if choice in ('1', '2', '3'):
            difficulty = int(choice)
            
            # 开启一个循环，用于实现 "d. 新开一局"
            while True:
                game_status = game_loop(difficulty)
                
                if game_status == 'exit': # 'e'
                    break # 退出 "d. 新开一局" 循环，返回难度选择
                elif game_status == 'new_game': # 'd'
                    continue # 继续 "d. 新开一局" 循环
                elif game_status == 'win': # 'b' 且胜利
                    break # 胜利了，也返回难度选择
        
        elif choice == '0':
            break # 返回主菜单
        
        else:
            print(Colors.ERROR + "输入错误，请输入 0, 1, 2, 或 3 。" + Colors.ENDC)
            input("按回车键继续...")

def main_menu():
    """主菜单/登入界面"""
    while True:
        clear_screen()
        print(Colors.WIN + """
    /\\_/\\
   ( > w < ) 欢迎来到命令行数独游戏！
   (       )
   (__ | __)
        """ + Colors.ENDC)
        print(Colors.HEADER + "--- 主菜单 ---" + Colors.ENDC)
        print("a. 开始游戏")
        print("b. 游戏规则")
        print("c. 按键说明")
        print("e. 退出游戏")
        
        choice = input("请选择 (a/b/c/e) : ").lower()
        
        if choice == 'a':
            difficulty_menu() #
        elif choice == 'b':
            show_rules() #
        elif choice == 'c':
            show_key_instructions() #
        elif choice == 'e':
            print("\n谢谢的游玩，再见！") #
            sys.exit()
        else:
            print(Colors.ERROR + "输入了无效的选项，请重新输入 (a/b/c/e) 。" + Colors.ENDC)
            input("按回车键继续...")

# -----------------------------------------------------------------
# 启动游戏
# -----------------------------------------------------------------
if __name__ == "__main__":
    main_menu()