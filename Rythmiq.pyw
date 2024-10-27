from customtkinter import *
import pygame
import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinterdnd2 import DND_FILES, TkinterDnD

class RythmiqMain:
    def __init__(self, Root):
        self.Root = Root
        self.Root.title("Rythmiq")
        self.Root.iconbitmap(r"icon\Rythmiq.ico")
        self.Root.geometry("700x400")
        self.Root.configure(bg="#1e1e1e")

        pygame.mixer.init()
        pygame.mixer.music.set_endevent(pygame.USEREVENT)

        self.PlaylistDir = "playlist"
        os.makedirs(self.PlaylistDir, exist_ok=True)

        self.Frame = CTkFrame(master=Root, fg_color="#2a2a2a", border_color="#444444", border_width=2)
        self.Frame.pack(side=tk.LEFT, expand=True, fill="both", padx=10, pady=10)

        self.ControlFrame = CTkFrame(master=Root, fg_color="#2a2a2a")
        self.ControlFrame.pack(side=tk.RIGHT, fill=tk.Y, padx=10, pady=10)

        self.SongVar = StringVar()
        self.SongMenu = CTkOptionMenu(master=self.Frame, variable=self.SongVar, values=[], command=self.OnSongSelect)
        self.SongMenu.pack(pady=(10, 0), padx=10)

        self.PathFrame = CTkFrame(master=self.Frame, fg_color="#2a2a2a")
        self.PathFrame.pack(pady=(10, 0), padx=10, fill=tk.BOTH, expand=True)

        self.Canvas = tk.Canvas(master=self.PathFrame, bg="#2a2a2a")
        self.Canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.Scrollbar = CTkScrollbar(master=self.PathFrame, command=self.Canvas.yview)
        self.Scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.Canvas.configure(yscrollcommand=self.Scrollbar.set)
        self.Canvas.bind("<Configure>", lambda e: self.Canvas.configure(scrollregion=self.Canvas.bbox("all")))

        self.PathListFrame = CTkFrame(master=self.Canvas, fg_color="#2a2a2a")
        self.Canvas.create_window((0, 0), window=self.PathListFrame, anchor="nw")

        self.SelectedSongVar = StringVar()

        self.VolumeSlider = CTkSlider(master=self.Frame, from_=0, to=100, button_color="#00c5ff", progress_color="#444444", command=self.UpdateVolume)
        self.VolumeSlider.pack(anchor="s", expand=True, padx=10, pady=(5, 0))
        self.VolumeSlider.set(50)

        self.LoadButton = CTkButton(master=self.Frame, text="Load Music", command=self.LoadMusic, fg_color="#444444", font=("Helvetica", 12))
        self.LoadButton.pack(pady=(5, 10), padx=10, fill=tk.X)

        self.Frame.drop_target_register(DND_FILES)
        self.Frame.dnd_bind('<<Drop>>', self.Drop)

        self.PlayButton = CTkButton(master=self.ControlFrame, text="Play", command=self.PlayMusic, fg_color="#444444", font=("Helvetica", 12))
        self.PlayButton.pack(fill=tk.X, pady=5)

        self.PauseButton = CTkButton(master=self.ControlFrame, text="Pause/Resume", command=self.PauseMusic, fg_color="#444444", font=("Helvetica", 12))
        self.PauseButton.pack(fill=tk.X, pady=5)

        self.StopButton = CTkButton(master=self.ControlFrame, text="Stop", command=self.StopMusic, fg_color="#444444", font=("Helvetica", 12))
        self.StopButton.pack(fill=tk.X, pady=5)

        self.PrevButton = CTkButton(master=self.ControlFrame, text="Previous", command=self.PrevMusic, fg_color="#444444", font=("Helvetica", 12))
        self.PrevButton.pack(fill=tk.X, pady=5)

        self.NextButton = CTkButton(master=self.ControlFrame, text="Next", command=self.NextMusic, fg_color="#444444", font=("Helvetica", 12))
        self.NextButton.pack(fill=tk.X, pady=5)

        self.InfoFrame = CTkFrame(master=self.ControlFrame, fg_color="#333333")
        self.InfoFrame.pack(side=tk.BOTTOM, fill=tk.X, padx=5, pady=10)

        self.InfoLabel = CTkLabel(self.InfoFrame, text="Current Song: None", fg_color="#333333", text_color="#ffffff", font=("Helvetica", 12))
        self.InfoLabel.pack(fill=tk.X, padx=10, pady=5)

        self.VolumeLabel = CTkLabel(self.InfoFrame, text="Volume: 50%", fg_color="#333333", text_color="#ffffff", font=("Helvetica", 12))
        self.VolumeLabel.pack(fill=tk.X, padx=10, pady=5)

        self.PositionLabel = CTkLabel(self.InfoFrame, text="Song Position: 0/0", fg_color="#333333", text_color="#ffffff", font=("Helvetica", 12))
        self.PositionLabel.pack(fill=tk.X, padx=10, pady=5)

        self.ReloadButton = CTkButton(master=self.InfoFrame, text="Load Playlist", command=self.LoadSongsFromPlaylist, fg_color="#005f99", font=("Helvetica", 12))
        self.ReloadButton.pack(pady=(5, 0))

        self.CurrentSong = None
        self.IsPaused = False
        self.Songs = []
        self.CurrentPosition = 0

        self.LoadSongsFromPlaylist()
        self.Root.after(100, self.CheckMusicEnd)

    def LoadSongsFromPlaylist(self):
        self.Songs = []
        self.SongMenu.configure(values=[])

        for widget in self.PathListFrame.winfo_children():
            widget.destroy()

        for song in os.listdir(self.PlaylistDir):
            if song.endswith(".mp3"):
                full_path = os.path.join(self.PlaylistDir, song)
                self.Songs.append(full_path)
                self.SongMenu.configure(values=self.Songs)
                self.AddSongRadioButton(full_path)

    def AddSongRadioButton(self, path):
        radio = CTkRadioButton(master=self.PathListFrame, text=path, variable=self.SelectedSongVar, value=path, command=self.RadioButtonSelect)
        radio.pack(anchor="w", padx=10, pady=2)

    def UpdateVolume(self, Value):
        Volume = float(Value) / 100
        pygame.mixer.music.set_volume(Volume)
        self.VolumeLabel.configure(text=f"Volume: {int(Value)}%")

    def LoadMusic(self):
        Songs = filedialog.askopenfilenames(title="Select Music Files", filetypes=(("MP3 Files", "*.mp3"), ("All Files", "*.*")))
        for Song in Songs:
            shutil.copy(Song, self.PlaylistDir)
        self.LoadSongsFromPlaylist()

    def PlayMusic(self):
        if self.SelectedSongVar.get() and os.path.exists(self.SelectedSongVar.get()):
            self.CurrentSong = self.SelectedSongVar.get()
            try:
                pygame.mixer.music.load(self.CurrentSong)
                pygame.mixer.music.set_volume(self.VolumeSlider.get() / 100)
                if self.IsPaused:
                    pygame.mixer.music.play(start=self.CurrentPosition / 1000)
                else:
                    pygame.mixer.music.play()
                self.IsPaused = False
                self.CurrentPosition = 0
                self.UpdateInfo()
            except pygame.error as e:
                messagebox.showerror("Error", f"Failed to play music: {str(e)}")
        else:
            messagebox.showerror("Error", "No song selected!")

    def UpdateInfo(self):
        if self.CurrentSong:
            SongName = os.path.basename(self.CurrentSong)
            SongNameDisplay = SongName[:10] + '...' if len(SongName) > 10 else SongName
            TotalSongs = len(self.Songs)
            CurrentIndex = self.Songs.index(self.CurrentSong) + 1
            self.InfoLabel.configure(text=f"Current Song: {SongNameDisplay}")
            self.PositionLabel.configure(text=f"Song Position: {CurrentIndex}/{TotalSongs}")

    def CheckMusicEnd(self):
        if not pygame.mixer.music.get_busy():
            self.NextMusic()
        self.Root.after(100, self.CheckMusicEnd)

    def PauseMusic(self):
        if self.CurrentSong:
            if self.IsPaused:
                self.CurrentPosition = pygame.mixer.music.get_pos()
                pygame.mixer.music.unpause()
                self.IsPaused = False
            else:
                self.CurrentPosition = pygame.mixer.music.get_pos()
                pygame.mixer.music.pause()
                self.IsPaused = True
        else:
            messagebox.showerror("Error", "No song is currently playing!")

    def StopMusic(self):
        pygame.mixer.music.stop()
        self.IsPaused = False
        self.SelectedSongVar.set("")
        self.SongVar.set("")
        self.InfoLabel.configure(text="Current Song: None")
        self.PositionLabel.configure(text="Song Position: 0/0")
        self.CurrentSong = None

    def NextMusic(self):
        if self.Songs and self.CurrentSong is not None and not self.IsPaused:
            current_index = self.Songs.index(self.CurrentSong)
            self.CurrentSong = self.Songs[(current_index + 1) % len(self.Songs)]
            self.SelectedSongVar.set(self.CurrentSong)
            self.SongVar.set(self.CurrentSong)
            self.PlayMusic()

    def PrevMusic(self):
        if self.Songs and self.CurrentSong is not None and not self.IsPaused:
            current_index = self.Songs.index(self.CurrentSong)
            self.CurrentSong = self.Songs[(current_index - 1) % len(self.Songs)]
            self.SelectedSongVar.set(self.CurrentSong)
            self.SongVar.set(self.CurrentSong)
            self.PlayMusic()

    def Drop(self, Event):
        Files = Event.data.splitlines()
        for File in Files:
            if File.endswith(".mp3"):
                shutil.copy(File, self.PlaylistDir)
        self.LoadSongsFromPlaylist()

    def OnSongSelect(self, selected_song=None):
        if selected_song is None:
            selected_song = self.SelectedSongVar.get()
        if selected_song and os.path.exists(selected_song):
            self.CurrentSong = selected_song
            self.UpdateInfo()
            self.SelectedSongVar.set(selected_song)

    def RadioButtonSelect(self):
        self.SongVar.set(self.SelectedSongVar.get())

if __name__ == "__main__":
    Root = TkinterDnD.Tk()
    App = RythmiqMain(Root)
    Root.mainloop()
