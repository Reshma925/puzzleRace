import customtkinter as ctk
from PIL import Image, ImageTk
from copy import deepcopy
import os, random


ctk.set_appearance_mode("light")
ctk.set_default_color_theme("blue")

GOAL_3 = [[1,2,3],[4,5,6],[7,8,0]]
GOAL_4 = [[1,2,3,4],[5,6,7,8],[9,10,11,12],[13,14,15,0]]
DIRS   = [(-1,0),(1,0),(0,-1),(0,1)]


# ------------------ helpers ------------------
def find_zero(st):
    for r in range(len(st)):
        for c in range(len(st[0])):
            if st[r][c] == 0:
                return r, c


def manhattan(st):
    size = len(st)
    d = 0
    for r in range(size):
        for c in range(size):
            v = st[r][c]
            if v != 0:
                tr, tc = divmod(v-1, size)
                d += abs(r - tr) + abs(c - tc)
    return d


def buddy_path_3x3(start):
    open_list = [(manhattan(start), start, [])]
    visited = set()

    while open_list:
        open_list.sort(key=lambda x: x[0])
        _, state, path = open_list.pop(0)

        if state == GOAL_3:
            return path + [state]

        visited.add(str(state))
        zr, zc = find_zero(state)

        for dr, dc in DIRS:
            nr, nc = zr + dr, zc + dc
            if 0 <= nr < 3 and 0 <= nc < 3:
                nxt = deepcopy(state)
                nxt[zr][zc], nxt[nr][nc] = nxt[nr][nc], 0
                if str(nxt) not in visited:
                    open_list.append((manhattan(nxt), nxt, path + [state]))
    return []


def buddy_path_4x4(start):
    s = deepcopy(start)
    p = [deepcopy(s)]
    for _ in range(300):
        zr, zc = find_zero(s)
        dr, dc = random.choice(DIRS)
        nr, nc = zr + dr, zc + dc
        if 0 <= nr < 4 and 0 <= nc < 4:
            s[zr][zc], s[nr][nc] = s[nr][nc], 0
        p.append(deepcopy(s))
        if s == GOAL_4:
            break
    return p


# ------------------ MAIN CLASS ------------------
class PuzzleRace:
    def __init__(self):
        self.win = ctk.CTk()
        self.win.geometry("1500x850")
        self.win.title("Puzzle Race 🧩 — Player vs Buddy")

        self.mode = "3x3"

        # *** TWO boards ***
        self.player_board = []
        self.buddy_board  = []

        # shared images
        self.images = []
        self.image_name = None

        # steps
        self.player_steps = 0
        self.buddy_steps  = 0

        # completion states
        self.player_done = False
        self.buddy_done  = False

        self.build_ui()
        self.load_images()
        self.new_game()
        self.update_labels()

        self.win.mainloop()


    # ---------------- UI BUILD ----------------
    def build_ui(self):
        top = ctk.CTkFrame(self.win, fg_color="#4E8DF5", corner_radius=0)
        top.pack(fill="x")
        ctk.CTkLabel(top, text="Puzzle Race 🧩",
                     font=("Comic Sans MS", 36, "bold"),
                     text_color="white").pack(pady=10)

        main = ctk.CTkFrame(self.win)
        main.pack(expand=True, fill="both")

        # left panel
        left = ctk.CTkFrame(main, width=330)
        left.pack(side="left", fill="y", padx=10)

        ctk.CTkLabel(left, text="Images",
                     font=("Comic Sans MS", 24, "bold")).pack(pady=10)
        self.img_frame = ctk.CTkScrollableFrame(left, width=300)
        self.img_frame.pack(expand=True, fill="y", padx=10)

        ctk.CTkButton(left, text="Shuffle 🌀", command=self.shuffle,
                      font=("Comic Sans MS", 22), height=50).pack(fill="x", pady=8)
        ctk.CTkButton(left, text="Buddy Try 🤝", command=self.buddy_play,
                      font=("Comic Sans MS", 22), height=50).pack(fill="x", pady=8)
        ctk.CTkButton(left, text="I Give Up 😅", fg_color="#E74C3C",
                      command=self.player_quits,
                      font=("Comic Sans MS", 22), height=50).pack(fill="x", pady=8)
        ctk.CTkButton(left, text="Toggle Size (3x3/4x4)",
                      command=self.toggle_mode,
                      font=("Comic Sans MS", 20), height=50).pack(fill="x", pady=8)

        # PLAYER BOARD
        mid = ctk.CTkFrame(main)
        mid.pack(side="left", expand=True)

        ctk.CTkLabel(mid, text="Player Board 🎮",
                     font=("Comic Sans MS", 26, "bold")).pack(pady=8)
        self.player_canvas = ctk.CTkCanvas(mid, width=500, height=500, highlightthickness=0)
        self.player_canvas.pack(pady=10)

        # BUDDY BOARD
        right = ctk.CTkFrame(main)
        right.pack(side="right", expand=True)

        ctk.CTkLabel(right, text="Buddy Board 🤖",
                     font=("Comic Sans MS", 26, "bold")).pack(pady=8)
        self.buddy_canvas = ctk.CTkCanvas(right, width=500, height=500, highlightthickness=0)
        self.buddy_canvas.pack(pady=10)

        # status bar
        status = ctk.CTkFrame(self.win)
        status.pack(fill="x", pady=10)

        self.player_lbl = ctk.CTkLabel(status, text="Player Moves: 0",
                                       font=("Comic Sans MS", 26))
        self.player_lbl.pack(side="left", padx=20)

        self.buddy_lbl  = ctk.CTkLabel(status, text="Buddy Moves:  0",
                                       font=("Comic Sans MS", 26))
        self.buddy_lbl.pack(side="left", padx=20)

        self.winner_lbl = ctk.CTkLabel(status, text="",
                                       font=("Comic Sans MS", 32, "bold"),
                                       text_color="#154360")
        self.winner_lbl.pack(side="right", padx=20)


    # -------- IMAGE LOADING ----------
    def load_images(self):
        for w in self.img_frame.winfo_children():
            w.destroy()

        imgs = [f for f in os.listdir("images") if f.lower().endswith((".jpg",".png",".jpeg"))]
        if not imgs:
            return

        self.image_name = imgs[0]

        for img in imgs:
            im = Image.open(f"images/{img}").resize((150,150))
            imgtk = ImageTk.PhotoImage(im)
            b = ctk.CTkButton(self.img_frame, image=imgtk, text="",
                              width=160, height=160,
                              command=lambda x=img: self.select_image(x))
            b.image = imgtk
            b.pack(pady=6)


    # -------- GAME SETUP ----------
    def select_image(self, name):
        self.image_name = name
        self.slice_image()
        self.redraw_all()

    def toggle_mode(self):
        self.mode = "4x4" if self.mode=="3x3" else "3x3"
        self.new_game()

    def new_game(self):
        size = 3 if self.mode=="3x3" else 4

        base = [[size*r+c+1 for c in range(size)] for r in range(size)]
        base[size-1][size-1] = 0

        self.player_board = deepcopy(base)
        self.buddy_board  = deepcopy(base)

        self.shuffle_board(self.player_board)
        self.shuffle_board(self.buddy_board)

        self.player_steps = self.buddy_steps = 0
        self.player_done  = self.buddy_done  = False
        self.winner_lbl.configure(text="")

        self.slice_image()
        self.redraw_all()
        self.update_labels()


    def shuffle_board(self, board):
        size = len(board)
        for _ in range(200):
            zr,zc = find_zero(board)
            dr,dc = random.choice(DIRS)
            nr,nc = zr+dr, zc+dc
            if 0<=nr<size and 0<=nc<size:
                board[zr][zc],board[nr][nc] = board[nr][nc],0


    def slice_image(self):
        if not self.image_name:
            self.images=[None]
            return

        size = len(self.player_board)
        board=500
        tile=board//size

        img=Image.open(f"images/{self.image_name}").resize((board,board))
        self.images=[]

        for i in range(size*size-1):
            r,c = divmod(i,size)
            piece=img.crop((c*tile,r*tile,(c+1)*tile,(r+1)*tile))
            self.images.append(ImageTk.PhotoImage(piece))
        self.images.append(None)


    # -------- DRAWING ----------
    def draw(self, canvas, board):
        canvas.delete("all")
        size=len(board)
        tile=500//size

        for r in range(size):
            for c in range(size):
                v=board[r][c]
                if v!=0:
                    canvas.create_image(c*tile,r*tile,anchor='nw', image=self.images[v-1])
                else:
                    canvas.create_rectangle(c*tile,r*tile,c*tile+tile,r*tile+tile,
                                            fill="#000",outline="")

    def redraw_all(self):
        self.draw(self.player_canvas, self.player_board)
        self.draw(self.buddy_canvas,  self.buddy_board)
        self.player_canvas.bind("<Button-1>", self.player_click)


    # -------- PLAYER MOVES ----------
    def player_click(self,event):
        size=len(self.player_board)
        tile=500//size
        c=event.x//tile
        r=event.y//tile
        self.player_move(r,c)

    def player_move(self,r,c):
        zr,zc=find_zero(self.player_board)
        if abs(r-zr)+abs(c-zc)==1:
            self.player_board[zr][zc],self.player_board[r][c]= \
            self.player_board[r][c],0

            self.player_steps+=1
            self.redraw_all()
            self.update_labels()
            self.check_end()


    # -------- CONTROL ----------
    def shuffle(self):
        self.new_game()

    def player_quits(self):
        self.player_done=False
        self.buddy_play(force=True)


    # -------- BUDDY ----------
    def buddy_play(self, force=False):
        size=len(self.buddy_board)
        path = buddy_path_3x3(deepcopy(self.buddy_board)) if size==3 else buddy_path_4x4(deepcopy(self.buddy_board))
        self.play_buddy_path(path,0,force)

    def play_buddy_path(self,path,i,force):
        if i>=len(path):
            self.check_end(force=True)
            return

        self.buddy_board=deepcopy(path[i])
        if i>0:self.buddy_steps+=1

        self.redraw_all()
        self.update_labels()
        self.win.after(200,lambda:self.play_buddy_path(path,i+1,force))


    # -------- WIN LOGIC ----------
    def check_end(self, force=False):
        goal=GOAL_3 if len(self.player_board)==3 else GOAL_4

        # if player reached goal anytime
        if self.player_board == goal:
            self.player_done=True

        # if buddy reached goal anytime
        if self.buddy_board == goal:
            self.buddy_done=True

        # QUIT or buddy solved while player didn't
        if force and not self.player_done:
            self.show("Buddy Wins 😎")
            return

        # buddy solved first
        if self.buddy_done and not self.player_done:
            self.show("Buddy Wins 😎")
            return

        # player solved first
        if self.player_done and not self.buddy_done:
            self.show("You Win 🎉")
            return

        # both solved → compare steps
        if self.player_done and self.buddy_done:
            if self.player_steps < self.buddy_steps:
                self.show("You Win 🎉")
            elif self.buddy_steps < self.player_steps:
                self.show("Buddy Wins 😎")
            else:
                self.show("Draw 😮")
            return


    def show(self,msg):
        self.winner_lbl.configure(text=msg)

    def update_labels(self):
        self.player_lbl.configure(text=f"Player Moves: {self.player_steps}")
        self.buddy_lbl.configure(text=f"Buddy Moves:  {self.buddy_steps}")


# --------------------
if __name__=="__main__":
    PuzzleRace()



