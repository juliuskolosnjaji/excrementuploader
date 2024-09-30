import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import yt_dlp as youtube_dl
import requests
import os
import webbrowser

class FileUploaderApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Uploader")

        self.file_paths = []

        # Create and place widgets
        self.label = tk.Label(root, text="Select files to upload or paste YouTube URL")
        self.label.pack(pady=10)

        self.youtube_url_label = tk.Label(root, text="YouTube URL:")
        self.youtube_url_label.pack(pady=5)

        self.youtube_url_entry = tk.Entry(root, width=50)
        self.youtube_url_entry.pack(pady=5)

        self.download_button = tk.Button(root, text="Download & Add MP3", command=self.download_youtube_video)
        self.download_button.pack(pady=5)

        self.select_button = tk.Button(root, text="Select Files", command=self.select_files)
        self.select_button.pack(pady=5)

        self.upload_button = tk.Button(root, text="Upload Files", command=self.upload_files)
        self.upload_button.pack(pady=5)

        self.file_listbox = tk.Listbox(root, selectmode=tk.SINGLE, width=50, height=10)
        self.file_listbox.pack(pady=10)
        self.file_listbox.bind("<Delete>", self.delete_file)

        self.progress_label = tk.Label(root, text="")
        self.progress_label.pack(pady=10)

        self.progress_bar = ttk.Progressbar(root, length=400, mode='determinate')
        self.progress_bar.pack(pady=5)

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="Select Files",
            filetypes=(("All Files", "*.*"),)
        )
        for file in files:
            if file not in self.file_paths:
                self.file_paths.append(file)
        self.update_file_list()

    def update_file_list(self):
        self.file_listbox.delete(0, tk.END)
        for file in self.file_paths:
            self.file_listbox.insert(tk.END, os.path.basename(file))
        self.progress_label.config(text=f"{len(self.file_paths)} file(s) selected")

    def delete_file(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            index = selection[0]
            removed_file = self.file_paths.pop(index)
            self.file_listbox.delete(index)
            self.progress_label.config(text=f"{len(self.file_paths)} file(s) selected")

    def download_youtube_video(self):
        url = self.youtube_url_entry.get().strip()
        if not url:
            messagebox.showwarning("No URL", "Please enter a YouTube URL.")
            return

        ydl_opts = {
            'format': 'bestaudio/best',
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'outtmpl': 'downloads/%(title)s.%(ext)s',
            'quiet': True
        }

        try:
            with youtube_dl.YoutubeDL(ydl_opts) as ydl:
                info_dict = ydl.extract_info(url, download=True)
                mp3_file = ydl.prepare_filename(info_dict).replace('.webm', '.mp3').replace('.m4a', '.mp3')
                self.file_paths.append(mp3_file)
                self.update_file_list()
                messagebox.showinfo("Download Complete", f"Downloaded and converted to MP3: {os.path.basename(mp3_file)}")
        except Exception as e:
            messagebox.showerror("Download Failed", f"Error downloading video: {str(e)}")

    def upload_files(self):
        if not self.file_paths:
            messagebox.showwarning("No Files", "Please select files to upload.")
            return

        base_url = "https://excrementgaming.com/uploads/"
        uploaded_files_urls = []
        total_files = len(self.file_paths)
        completed_files = 0

        try:
            for file_path in self.file_paths:
                file_name = os.path.basename(file_path)
                with open(file_path, "rb") as file_data:
                    response = requests.post("https://excrementgaming.com/upload.php", files={"fileToUpload": (file_name, file_data)})
                    response.raise_for_status()
                    completed_files += 1
                    progress = (completed_files / total_files) * 100
                    self.progress_bar['value'] = progress
                    self.root.update_idletasks()  # Update the progress bar

                    # Generate the URL based on the known upload pattern
                    uploaded_file_url = base_url + file_name
                    uploaded_files_urls.append(uploaded_file_url)

            # Show a success message after all files are uploaded and display the links
            if uploaded_files_urls:
                self.show_uploaded_urls(uploaded_files_urls)
        except requests.exceptions.RequestException as e:
            # Show error if the request failed
            messagebox.showerror("Upload Failed", str(e))

    def show_uploaded_urls(self, urls):
        # Create a new window to show the uploaded URLs
        url_window = tk.Toplevel(self.root)
        url_window.title("Uploaded Files")
        url_window.geometry("500x300")

        info_label = tk.Label(url_window, text="Uploaded file URLs (click to copy):")
        info_label.pack(pady=10)

        for url in urls:
            link = tk.Label(url_window, text=url, fg="blue", cursor="hand2")
            link.pack(pady=2)
            # Bind click event to copy the URL to the clipboard
            link.bind("<Button-1>", lambda e, url=url: self.copy_to_clipboard(url))

    def copy_to_clipboard(self, url):
        # Copy the URL to the clipboard
        self.root.clipboard_clear()  # Clear clipboard
        self.root.clipboard_append(url)  # Append the URL to the clipboard
        messagebox.showinfo("Copied to Clipboard", f"Copied: {url}")

    def open_url(self, url):
        webbrowser.open_new(url)

if __name__ == "__main__":
    root = tk.Tk()
    app = FileUploaderApp(root)
    root.mainloop()
