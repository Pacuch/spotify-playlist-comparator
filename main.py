import base64
import tkinter
import spotipy
from PIL import ImageTk, Image
from spotipy import SpotifyException
from spotipy.oauth2 import SpotifyClientCredentials
import tkinter as tk
import re
from tkinter import constants

root = tk.Tk()
root.title('Spotify Playlist Comparator')
root.iconbitmap(r'utils\img\icon.ico')
root.resizable(width=False, height=False)

root.minsize(width=600, height=600)
root.maxsize(width=800, height=800)


def fill_input(entry, label):
    string = entry.get()

    if len(string) == 0:
        label.configure(text='Do not leave entry empty!')
    elif validate_entry_for_spotify_playlist(string):
        label.configure(text='Playlist approved!')
        return string
    else:
        label.configure(text='Re enter correct playlist link')
        raise NameError


def clicked_and_text():
    clear_listbox(listbox_tracks)
    try:
        first = fill_input(entryFirstPlaylist, labelFirst)
    except NameError as e:
        pass
    try:
        second = fill_input(entrySecondPlaylist, labelSecond)
    except NameError as e:
        pass
    try:
        list_of_tracks = compare_two_playlists(first, second)
        text = 'THERE ARE ' + str(len(list_of_tracks)) + ' SAME TRACKS!'
        change_label_text(label_summary, text)

        sorted_playlist = sorted(
            list_of_tracks,
            key=lambda t: t[0]  # 0 sort by artist, 1 sort by name of song
        )

        for item in sorted_playlist:
            add_track_to_listbox(item[0] + ' - ' + item[1], listbox_tracks)
    except NameError as e:
        pass


def validate_entry_for_spotify_playlist(string):
    pattern_playlist = re.compile(r'^https?://open.spotify.com/playlist/[a-zA-Z0-9]{22}$')
    pattern_playlist_long = re.compile(r'^https?://open.spotify.com/playlist/[a-zA-Z0-9]{22}\?si=[a-z0-9]{16}$')
    return pattern_playlist.match(string) or pattern_playlist_long.match(string)


def add_track_to_listbox(track, listbox):
    return listbox.insert(constants.END, track)


def clear_listbox(listbox):
    return listbox.delete(0, constants.END)


def callback(event):
    selection = event.widget.curselection()
    if selection:
        index = selection[0]
        data = event.widget.get(index)
        label_selected_item.configure(text=data)
    else:
        label_selected_item.configure(text="")


def get_playlist_uri(playlist_link):
    return playlist_link.split("/")[-1].split("?")[0]


def get_track_uri_name(track_uri):
    return track_uri.split(":")[-1]


def get_tracks_from_playlist_uri_name(playlist_link):
    tracks = []
    for item in get_tracks_from_playlist(playlist_link):
        tracks.append(get_track_uri_name(item[3]))
    return tracks


def get_tracks_from_playlist(playlist_link):
    tracks = []
    playlist_uri = get_playlist_uri(playlist_link)
    i = 1

    for track in spotify.playlist_items(playlist_uri, limit=1)["items"]:
        track_uri = track["track"]["uri"]
        track_name = track["track"]["name"]
        track_artist = track["track"]["album"]["artists"][0]["name"]
        result = i, track_artist, track_name, get_playlist_uri(track_uri)
        tracks.append(result)
        i += 1

    return tracks


def get_playlist_tracks(playlist_id):
    try:
        results = spotify.playlist_items(playlist_id)
    except SpotifyException as exception:
        if exception.http_status == 404:
            return None

    tracks = results['items']
    while results['next']:
        results = spotify.next(results)
        tracks.extend(results['items'])
    return tracks


def compare_two_playlists(playlist_first, playlist_second):
    first = get_playlist_tracks(playlist_first)
    sec = get_playlist_tracks(playlist_second)

    if (first or sec) is None:
        return None

    list_first = [(song["track"]["album"]["artists"][0]["name"], song["track"]["name"], song["track"]["uri"]) for song in first]
    list_to_comp = [(song["track"]["album"]["artists"][0]["name"], song["track"]["name"], song["track"]["uri"]) for song in sec]

    return set(list_first) & set(list_to_comp)


def change_label_text(label, how_many_tracks):
    return label.configure(text=how_many_tracks)


canvas = tk.Canvas(root, height=1000, width=700, bg='#07301E')
canvas.pack()

frame = tk.Frame(root, bg='white')
frame.place(relwidth=0.85, relheight=0.85, relx=0.075, rely=0.075)

img = ImageTk.PhotoImage(Image.open(r'utils\img\spo.png'))
label = tk.Label(frame, image=img, width=140, height=140)
label.pack(pady=20)

labelEnterFirstPlaylist = tk.Label(frame, text='Enter first playlist link below.', bg='white').pack()
entryFirstPlaylist = tk.Entry(frame, width=75, bg='#d6d6d6')
entryFirstPlaylist.pack()

labelFirst = tk.Label(frame, text="", font="Courier 10 bold", bg='white')
labelFirst.pack()

labelEnterSecondPlaylist = tk.Label(frame, text='Enter second playlist link below to compare.', bg='white').pack()
entrySecondPlaylist = tk.Entry(frame, width=75, bg='#d6d6d6')
entrySecondPlaylist.pack()

labelSecond = tk.Label(frame, text="", font="Courier 10 bold", bg='white')
labelSecond.pack()

button_compare = tk.Button(frame, text='Compare Playlists!', padx=10, pady=10,  command=clicked_and_text)
button_compare.pack(pady=6)

label_summary = tk.Label(frame, text="", font="Courier 10 bold", bg='white')
label_summary.pack()

listbox_tracks = tk.Listbox(frame)
listbox_tracks.pack(padx=55, side=tkinter.TOP, fill=tkinter.X, expand=True)

label_selected_item = tk.Label(frame, text="", font="Courier 10 bold", bg='white')
label_selected_item.pack()

listbox_tracks.bind("<<ListboxSelect>>", callback)

root.mainloop()

# ------------------------------------------------------------------------------------------------------------------------

cid = base64.b64decode('NGU1M2Q4OGQ4ZWYyNGZmNWE0OWQyNGI2Yzg1NmRmZDE=')
secret = base64.b64decode('YzAzZmE0YWJjNmNkNDIwYWI3NDlkZDA2ZDVlYjc5Mjg=')

client_credentials_manager = SpotifyClientCredentials(client_id=cid, client_secret=secret)
spotify = spotipy.Spotify(client_credentials_manager=client_credentials_manager)

