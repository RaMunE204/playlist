import tkinter as tk
from tkinter import ttk, messagebox
import threading
import time

class Song:
    def __init__(self, title, artist, duration):
        self.title = title
        self.artist = artist
        self.duration = duration
        self.prev = None
        self.next = None

class Playlist:
    def __init__(self):
        self.head = None
        self.tail = None
        self.current = None
        self.song_map = {}
        self.history = []

    def add_song(self, title, artist, duration):
        if title in self.song_map:
            return
        new_song = Song(title, artist, duration)
        self.song_map[title] = new_song
        if not self.head:
            self.head = self.tail = self.current = new_song
        else:
            self.tail.next = new_song
            new_song.prev = self.tail
            self.tail = new_song

    def remove_song(self, title):
        if title not in self.song_map:
            return
        song = self.song_map[title]
        if song.prev:
            song.prev.next = song.next
        if song.next:
            song.next.prev = song.prev
        if song == self.head:
            self.head = song.next
        if song == self.tail:
            self.tail = song.prev
        if song == self.current:
            self.current = song.next or song.prev
        del self.song_map[title]

    def next_song(self):
        if self.current and self.current.next:
            self.history.append(self.current)
            self.current = self.current.next

    def prev_song(self):
        if self.current and self.current.prev:
            self.history.append(self.current)
            self.current = self.current.prev

    def go_back(self):
        if self.history:
            self.current = self.history.pop()

class Playlist_2:
    def __init__(self, root):
        self.root = root
        self.root.title("Playlist")
        self.playlist = Playlist()
        self.playing = False
        self.thread = None
        self.stop_event = threading.Event()
        self.setup_ui()

    def setup_ui(self):
        self.title_entry = ttk.Entry(self.root)
        self.artist_entry = ttk.Entry(self.root)
        self.duration_entry = ttk.Entry(self.root)
        self.title_entry.grid(row=0, column=0)
        self.artist_entry.grid(row=0, column=1)
        self.duration_entry.grid(row=0, column=2)

        ttk.Button(self.root, text="Add", command=self.add_song).grid(row=0, column=3)
        ttk.Button(self.root, text="Remove", command=self.remove_song).grid(row=0, column=4)

        self.song_list = tk.Listbox(self.root, width=50)
        self.song_list.grid(row=1, column=0, columnspan=5)

        self.now_playing = ttk.Label(self.root, text="Now Playing: Nothing ")
        self.now_playing.grid(row=2, column=0, columnspan=5)

        self.progress = ttk.Progressbar(self.root, length=300)
        self.progress.grid(row=3, column=0, columnspan=5, pady=5)

        ttk.Button(self.root, text="Prev", command=self.prev_song).grid(row=4, column=0)
        self.play_btn = ttk.Button(self.root, text="Play", command=self.toggle_play)
        self.play_btn.grid(row=4, column=1)
        ttk.Button(self.root, text="Next", command=self.next_song).grid(row=4, column=2)
        ttk.Button(self.root, text="Back", command=self.go_back).grid(row=4, column=3)

        self.search_entry = ttk.Entry(self.root)
        self.search_entry.grid(row=5, column=0, columnspan=2, padx=5)
        ttk.Button(self.root, text="Find", command=self.find_song).grid(row=5, column=2)

    def add_song(self):
        t = self.title_entry.get()
        a = self.artist_entry.get()
        d = self.duration_entry.get()
        if not t or not a or not d.isdigit():
            messagebox.showerror("Error", "Fill all fields correctly")
            return
        self.playlist.add_song(t, a, int(d))
        self.update_list()
        self.title_entry.delete(0, tk.END)
        self.artist_entry.delete(0, tk.END)
        self.duration_entry.delete(0, tk.END)

    def remove_song(self):
        sel = self.song_list.curselection()
        if not sel:
            return
        title = self.song_list.get(sel[0]).split(" - ")[0]
        self.stop()
        self.playlist.remove_song(title)
        self.update_list()

    def update_list(self):
        self.song_list.delete(0, tk.END)
        node = self.playlist.head
        while node:
            self.song_list.insert(tk.END, f"{node.title} - {node.artist}")
            node = node.next
        self.update_now_playing()

    def update_now_playing(self):
        song = self.playlist.current
        if song:
            self.now_playing.config(text=f"Now Playing: {song.title} - {song.artist}")
        else:
            self.now_playing.config(text="Now Playing: Nothing")
        self.progress['value'] = 0

    def toggle_play(self):
        if not self.playlist.current:
            return
        self.playing = not self.playing
        self.play_btn.config(text="Pause" if self.playing else "Play")
        if self.playing:
            self.stop_event.clear()
            self.thread = threading.Thread(target=self.play_song)
            self.thread.start()
        else:
            self.stop_event.set()

    def play_song(self):
        song = self.playlist.current
        for i in range(song.duration):
            if not self.playing or self.stop_event.is_set():
                break
            self.progress['value'] = (i + 1) * 100 / song.duration
            time.sleep(1)
        else:
            if self.playing:
                self.next_song()
        self.stop_event.clear()

    def stop(self):
        self.stop_event.set()
        if self.thread and self.thread.is_alive():
            self.thread.join()
        self.progress['value'] = 0

    def next_song(self):
        self.stop()
        self.playlist.next_song()
        self.update_now_playing()
        if self.playing:
            self.toggle_play()

    def prev_song(self):
        self.stop()
        self.playlist.prev_song()
        self.update_now_playing()
        if self.playing:
            self.toggle_play()

    def go_back(self):
        self.stop()
        self.playlist.go_back()
        self.update_now_playing()
        if self.playing:
            self.toggle_play()

    def find_song(self):
        title = self.search_entry.get()
        if title in self.playlist.song_map:
            node = self.playlist.head
            idx = 0
            while node:
                if node.title == title:
                    break
                node = node.next
                idx += 1
            self.song_list.selection_clear(0, tk.END)
            self.song_list.selection_set(idx)
            self.song_list.see(idx)
            self.now_playing.config(text=f"Found: {node.title} - {node.artist}")
        else:
            messagebox.showinfo("Not Found", f"'{title}' not in playlist")

if __name__ == "__main__":
    root = tk.Tk()
    app = Playlist_2(root)
    root.mainloop()
