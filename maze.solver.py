import tkinter as tk
from tkinter import filedialog, messagebox
import random
import time

class MazeSolverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Maze Solver - DFS and BFS")

        self.rows = 12
        self.cols = 12
        self.cell_size = 40

        # Duvar bilgileri: h_walls (yatay duvarlar), v_walls (dikey duvarlar)
        self.h_walls = [[False for _ in range(self.cols)] for _ in range(self.rows + 1)]
        self.v_walls = [[False for _ in range(self.cols + 1)] for _ in range(self.rows)]
        
        self.start = (0, 0)
        self.end = (self.rows - 1, self.cols - 1)
        self.visited = set()
        self.step_path = []
        self.step_index = 0
        self.animation_id = None

        self.setup_gui()

        self.canvas = tk.Canvas(self.root, width=self.cols * self.cell_size, height=self.rows * self.cell_size)
        self.canvas.pack(side=tk.RIGHT, padx=10, pady=10)
        self.draw_maze()

    def setup_gui(self):
        panel = tk.Frame(self.root)
        panel.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        tk.Label(panel, text="").pack(expand=True)

        tk.Button(panel, text="Create Maze", command=self.create_maze).pack(pady=2)
        tk.Button(panel, text="Load Maze", command=self.load_maze).pack(pady=2)
        tk.Button(panel, text="Solve", command=self.solve_maze).pack(pady=2)
        tk.Button(panel, text="Step-by-Step", command=self.solve_step_by_step).pack(pady=2)
        tk.Button(panel, text="Reset", command=self.reset).pack(pady=2)
        tk.Button(panel, text="Compare DFS & BFS", command=self.compare_algorithms).pack(pady=2)

        self.algorithm_var = tk.StringVar(value="DFS")
        tk.Label(panel, text="Algorithm:").pack(pady=5)
        tk.Radiobutton(panel, text="DFS", variable=self.algorithm_var, value="DFS").pack()
        tk.Radiobutton(panel, text="BFS", variable=self.algorithm_var, value="BFS").pack()

        self.info_label = tk.Label(panel, text="", justify=tk.LEFT)
        self.info_label.pack(pady=10)
        tk.Label(panel, text="").pack(expand=True)

    def draw_maze(self):
        self.canvas.delete("all")
        
        # Hücreleri çiz
        for r in range(self.rows):
            for c in range(self.cols):
                x1, y1 = c * self.cell_size, r * self.cell_size
                x2, y2 = (c + 1) * self.cell_size, (r + 1) * self.cell_size
                
                color = "white"
                if (r, c) == self.start:
                    color = "lightgreen"
                elif (r, c) == self.end:
                    color = "lightcoral"
                elif (r, c) in self.visited:
                    color = "lightblue"
                
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="lightgray")

        # Yatay duvarları çiz
        for r in range(self.rows + 1):
            for c in range(self.cols):
                if self.h_walls[r][c]:
                    x1 = c * self.cell_size
                    x2 = (c + 1) * self.cell_size
                    y = r * self.cell_size
                    self.canvas.create_line(x1, y, x2, y, fill="black", width=3)

        # Dikey duvarları çiz
        for r in range(self.rows):
            for c in range(self.cols + 1):
                if self.v_walls[r][c]:
                    y1 = r * self.cell_size
                    y2 = (r + 1) * self.cell_size
                    x = c * self.cell_size
                    self.canvas.create_line(x, y1, x, y2, fill="black", width=3)

        # Başlangıç ve bitiş noktalarını işaretle
        start_x = self.start[1] * self.cell_size + self.cell_size // 2
        start_y = self.start[0] * self.cell_size + self.cell_size // 2
        self.canvas.create_text(start_x, start_y, text="A", font=("Arial", 16, "bold"), fill="darkgreen")

        end_x = self.end[1] * self.cell_size + self.cell_size // 2
        end_y = self.end[0] * self.cell_size + self.cell_size // 2
        self.canvas.create_text(end_x, end_y, text="B", font=("Arial", 16, "bold"), fill="darkred")

        # Çözüm yolunu çiz
        if len(self.step_path) > 1:
            for i in range(1, len(self.step_path)):
                r1, c1 = self.step_path[i - 1]
                r2, c2 = self.step_path[i]
                x1 = c1 * self.cell_size + self.cell_size // 2
                y1 = r1 * self.cell_size + self.cell_size // 2
                x2 = c2 * self.cell_size + self.cell_size // 2
                y2 = r2 * self.cell_size + self.cell_size // 2
                self.canvas.create_line(x1, y1, x2, y2, fill="red", width=4)

    def parse_maze_from_text_format(self, lines):
        """Metin formatındaki labirent dosyasını parse eder"""
        # Boş satırları temizle
        lines = [line.rstrip() for line in lines if line.strip()]
        
        if len(lines) < 2:
            raise ValueError("Dosya en az başlangıç ve bitiş koordinatlarını içermelidir")
        
        # Son iki satır koordinatları içerir
        try:
            start_coords = lines[-2].strip().split(',')
            end_coords = lines[-1].strip().split(',')
            start_row, start_col = int(start_coords[0]), int(start_coords[1])
            end_row, end_col = int(end_coords[0]), int(end_coords[1])
        except (ValueError, IndexError):
            raise ValueError("Geçersiz koordinat formatı. Beklenen format: 'satır,sütun'")
        
        # Duvar bilgilerini al (son iki satır hariç)
        wall_lines = lines[:-2]
        
        if not wall_lines:
            raise ValueError("Duvar bilgisi bulunamadı")
        
        # Labirent boyutunu hesapla
        # Satır sayısı: dikey duvar satırlarından çıkarılır
        v_wall_lines = [wall_lines[i] for i in range(1, len(wall_lines), 2)]
        h_wall_lines = [wall_lines[i] for i in range(0, len(wall_lines), 2)]
        
        self.rows = len(v_wall_lines)
        
        # Sütun sayısını yatay duvar satırından hesapla
        if h_wall_lines:
            # Yatay duvar satırındaki karakterleri say (boşluk dahil)
            sample_line = h_wall_lines[0]
            # Her hücre için bir duvar pozisyonu olacak
            self.cols = (len(sample_line) + 1) // 2
        else:
            self.cols = max(start_col, end_col) + 1
        
        # Boyutları koordinatlara göre ayarla
        self.rows = max(self.rows, max(start_row, end_row) + 1)
        self.cols = max(self.cols, max(start_col, end_col) + 1)
        
        # Duvar matrislerini yeniden başlat
        self.h_walls = [[False for _ in range(self.cols)] for _ in range(self.rows + 1)]
        self.v_walls = [[False for _ in range(self.cols + 1)] for _ in range(self.rows)]
        
        # Duvarları parse et
        for line_idx, line in enumerate(wall_lines):
            if line_idx % 2 == 0:  # Çift satırlar: yatay duvarlar (-)
                wall_row = line_idx // 2
                if wall_row <= self.rows:
                    col = 0
                    i = 0
                    while i < len(line) and col < self.cols:
                        char = line[i]
                        if char == '-':
                            if wall_row < len(self.h_walls) and col < len(self.h_walls[wall_row]):
                                self.h_walls[wall_row][col] = True
                        i += 1
                        if i < len(line) and line[i] == ' ':
                            i += 1  # Boşluğu atla
                        col += 1
            else:  # Tek satırlar: dikey duvarlar (|)
                wall_row = line_idx // 2
                if wall_row < self.rows:
                    col = 0
                    i = 0
                    while i < len(line) and col <= self.cols:
                        char = line[i]
                        if char == '|':
                            if col < len(self.v_walls[wall_row]):
                                self.v_walls[wall_row][col] = True
                        i += 1
                        if i < len(line) and line[i] == ' ':
                            i += 1  # Boşluğu atla
                        col += 1
        
        return (start_row, start_col), (end_row, end_col)

    def create_maze(self):
        """Rastgele labirent oluştur"""
        self.reset()
        
        # Rastgele yatay duvarlar
        for r in range(self.rows + 1):
            for c in range(self.cols):
                if random.random() < 0.3:
                    self.h_walls[r][c] = True
        
        # Rastgele dikey duvarlar
        for r in range(self.rows):
            for c in range(self.cols + 1):
                if random.random() < 0.3:
                    self.v_walls[r][c] = True
        
        # Sınır duvarlarını koy
        for c in range(self.cols):
            self.h_walls[0][c] = True  # Üst sınır
            self.h_walls[self.rows][c] = True  # Alt sınır
        for r in range(self.rows):
            self.v_walls[r][0] = True  # Sol sınır
            self.v_walls[r][self.cols] = True  # Sağ sınır
        
        self.draw_maze()
        self.info_label.config(text="Random maze created.")

    def load_maze(self):
        filename = filedialog.askopenfilename(title="Select maze file", 
                                            filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not filename:
            return
        try:
            with open(filename, "r") as f:
                lines = f.readlines()
            
            # Metin formatını parse et
            start, end = self.parse_maze_from_text_format(lines)
            self.start = start
            self.end = end
            
            self.visited.clear()
            self.step_path.clear()
            
            # Canvas boyutunu güncelle
            self.canvas.config(width=self.cols * self.cell_size, height=self.rows * self.cell_size)
            self.draw_maze()
            self.info_label.config(text=f"Maze loaded from {filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load maze:\n{e}")

    def can_move(self, from_pos, to_pos):
        """İki hücre arasında hareket mümkün mü kontrol et""" 
        r1, c1 = from_pos
        r2, c2 = to_pos
        
        # Hedef hücre sınırlar içinde mi
        if not (0 <= r2 < self.rows and 0 <= c2 < self.cols):
            return False
        
        # Yukarı hareket
        if r2 == r1 - 1 and c2 == c1:
            return not self.h_walls[r1][c1]
        # Aşağı hareket
        elif r2 == r1 + 1 and c2 == c1:
            return not self.h_walls[r1 + 1][c1]
        # Sol hareket
        elif r2 == r1 and c2 == c1 - 1:
            return not self.v_walls[r1][c1]
        # Sağ hareket
        elif r2 == r1 and c2 == c1 + 1:
            return not self.v_walls[r1][c1 + 1]
        
        return False

    def get_neighbors(self, r, c):
        """PDF'de belirtilen sıra: yukarı, sol, aşağı, sağ"""
        neighbors = []
        for dr, dc in [(-1, 0), (0, -1), (1, 0), (0, 1)]:
            new_pos = (r + dr, c + dc)
            if self.can_move((r, c), new_pos):
                neighbors.append(new_pos)
        return neighbors

    def dfs(self):
        """Depth-First Search (LIFO - Stack)"""
        stack = [(self.start, [self.start])]
        visited = set()
        
        while stack:
            current, path = stack.pop()  # LIFO (Son giren ilk çıkar)
            
            if current == self.end:
                return path
            
            if current in visited:
                continue
            
            visited.add(current)
            
            for neighbor in self.get_neighbors(*current):
                if neighbor not in visited:
                    stack.append((neighbor, path + [neighbor]))
        
        return None

    def bfs(self):
        """Breadth-First Search (FIFO - Queue)"""
        queue = [(self.start, [self.start])]
        visited = set()
        
        while queue:
            current, path = queue.pop(0)  # FIFO (İlk giren ilk çıkar)
            
            if current == self.end:
                return path
            
            if current in visited:
                continue
            
            visited.add(current)
            
            for neighbor in self.get_neighbors(*current):
                if neighbor not in visited:
                    queue.append((neighbor, path + [neighbor]))
        
        return None

    def solve_maze(self):
        self.visited.clear()
        algo = self.algorithm_var.get()
        start_time = time.time()
        
        if algo == "DFS":
            path = self.dfs()
        else:
            path = self.bfs()
        
        duration = time.time() - start_time
        
        if path:
            self.step_path = path
            self.draw_maze()
            self.info_label.config(text=f"{algo} solved. Path length: {len(path)} | Time: {duration:.4f}s")
        else:
            self.info_label.config(text=f"{algo} failed. No path found.")

    def solve_step_by_step(self):
        self.solve_maze()
        self.step_index = 0
        if self.step_path:
            self.animate_path()

    def animate_path(self):
        if self.step_index < len(self.step_path):
            self.visited.add(self.step_path[self.step_index])
            self.step_index += 1
            self.draw_maze()
            self.animation_id = self.root.after(200, self.animate_path)
        else:
            self.animation_id = None

    def reset(self):
        if self.animation_id:
            self.root.after_cancel(self.animation_id)
            self.animation_id = None
        
        # Duvar matrislerini temizle
        self.h_walls = [[False for _ in range(self.cols)] for _ in range(self.rows + 1)]
        self.v_walls = [[False for _ in range(self.cols + 1)] for _ in range(self.rows)]
        
        self.visited.clear()
        self.step_path.clear()
        self.start = (0, 0)
        self.end = (self.rows - 1, self.cols - 1)
        self.draw_maze()
        self.info_label.config(text="Reset done.")

    def compare_algorithms(self):
        self.visited.clear()

        start_time = time.time()
        dfs_path = self.dfs()
        dfs_time = time.time() - start_time

        start_time = time.time()
        bfs_path = self.bfs()
        bfs_time = time.time() - start_time

        result_text = "Comparison Results:\n"
        if dfs_path:
            result_text += f"DFS: Path length = {len(dfs_path)}, Time = {dfs_time:.4f}s\n"
        else:
            result_text += "DFS: No path found.\n"

        if bfs_path:
            result_text += f"BFS: Path length = {len(bfs_path)}, Time = {bfs_time:.4f}s"
        else:
            result_text += "BFS: No path found."

        self.info_label.config(text=result_text)

        # Sonucu görselleştir
        if dfs_path:
            self.step_path = dfs_path
        elif bfs_path:
            self.step_path = bfs_path
        else:
            self.step_path = []
        
        self.visited.clear()
        self.draw_maze()


if __name__ == "__main__":
    root = tk.Tk()
    app = MazeSolverApp(root)
    root.mainloop()