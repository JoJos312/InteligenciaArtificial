import heapq
import time
import tkinter as tk
from tkinter import Button, Label

goal_state = [[1, 2, 3], [4, 5, 6], [7, 8, 0]]


def find_position(state, tile):
    for i, row in enumerate(state):
        if tile in row:
            return (i, row.index(tile))
    return None


def heuristic(state):
    cost = 0
    for i in range(len(state)):
        for j in range(len(state[i])):
            if state[i][j] != 0:
                goal_i, goal_j = find_position(goal_state, state[i][j])
                cost += abs(i - goal_i) + abs(j - goal_j)
    return cost


def generate_moves(state):
    moves = []
    x, y = find_position(state, 0)
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    for dx, dy in directions:
        nx, ny = x + dx, y + dy
        if 0 <= nx < len(state) and 0 <= ny < len(state[0]):
            new_state = [row[:] for row in state]
            new_state[x][y], new_state[nx][ny] = new_state[nx][ny], new_state[x][y]
            moves.append(new_state)
    return moves


def solve_puzzle(initial_state):
    start_time = time.time()
    priority_queue = []
    heapq.heappush(priority_queue, (heuristic(initial_state), 0, initial_state, []))
    visited = set()

    while priority_queue:
        _, moves, current_state, path = heapq.heappop(priority_queue)
        if current_state == goal_state:
            end_time = time.time()
            return path + [current_state], len(path), end_time - start_time

        state_tuple = tuple(tuple(row) for row in current_state)
        if state_tuple in visited:
            continue
        visited.add(state_tuple)

        for next_state in generate_moves(current_state):
            new_path = path + [current_state]
            heapq.heappush(
                priority_queue,
                (
                    heuristic(next_state) + len(new_path),
                    len(new_path),
                    next_state,
                    new_path,
                ),
            )

    return None, 0, 0


class PuzzleGUI:
    def __init__(self, root, solution, moves, time_taken):
        self.root = root
        self.solution = solution
        self.step = 0
        self.labels = []

        self.frame = tk.Frame(root)
        self.frame.pack()

        for i in range(3):
            row_labels = []
            for j in range(3):
                label = Label(
                    self.frame,
                    text="",
                    font=("Arial", 24),
                    width=4,
                    height=2,
                    borderwidth=2,
                    relief="ridge",
                )
                label.grid(row=i, column=j)
                row_labels.append(label)
            self.labels.append(row_labels)

        self.button_frame = tk.Frame(root)
        self.button_frame.pack()

        self.prev_button = Button(
            self.button_frame, text="Anterior", command=self.prev_step
        )
        self.prev_button.grid(row=0, column=0)

        self.next_button = Button(
            self.button_frame, text="Siguiente", command=self.next_step
        )
        self.next_button.grid(row=0, column=1)

        self.info_label = Label(
            root,
            text=f"Movimientos: {moves} | Tiempo: {time_taken:.4f} segundos",
            font=("Arial", 12),
        )
        self.info_label.pack()

        self.update_board()

    def update_board(self):
        if 0 <= self.step < len(self.solution):
            current_state = self.solution[self.step]
            for i in range(3):
                for j in range(3):
                    value = current_state[i][j]
                    self.labels[i][j].config(text=str(value) if value != 0 else "")

    def next_step(self):
        if self.step < len(self.solution) - 1:
            self.step += 1
            self.update_board()

    def prev_step(self):
        if self.step > 0:
            self.step -= 1
            self.update_board()


def main():
    initial_state = [[3, 1, 2], [4, 7, 0], [5, 6, 8]]

    solution, moves, time_taken = solve_puzzle(initial_state)
    if solution:
        root = tk.Tk()
        root.title("8-Puzzle Solver")
        app = PuzzleGUI(root, solution, moves, time_taken)
        root.mainloop()
    else:
        print("No se encontró solución.")


if __name__ == "__main__":
    main()