import tkinter as tk
from tkinter import filedialog, messagebox
from PIL import Image
import piexif
import os

def dms(decimal):
    """Convert decimal coordinates into degrees, minutes, seconds format for EXIF"""
    degrees = int(decimal)
    minutes = int((abs(decimal) - abs(degrees)) * 60)
    seconds = float((abs(decimal) - abs(degrees) - minutes / 60) * 3600)
    return ((abs(degrees), 1), (minutes, 1), (int(seconds * 100), 100))

def get_lat_ref(lat):
    return 'N' if lat >= 0 else 'S'

def get_lng_ref(lng):
    return 'E' if lng >= 0 else 'W'

def embed_gps_and_keywords(image_path, lat, lng, alt, keywords):
    img = Image.open(image_path)
    exif_dict = piexif.load(img.info.get("exif", b""))

    gps_ifd = {
        piexif.GPSIFD.GPSLatitudeRef: get_lat_ref(lat),
        piexif.GPSIFD.GPSLatitude: dms(lat),
        piexif.GPSIFD.GPSLongitudeRef: get_lng_ref(lng),
        piexif.GPSIFD.GPSLongitude: dms(lng),
        piexif.GPSIFD.GPSAltitudeRef: 0 if alt >= 0 else 1,
        piexif.GPSIFD.GPSAltitude: (int(abs(alt * 100)), 100),
    }

    # Add keywords in the XPKeywords EXIF tag (in UTF-16LE as per EXIF standard)
    user_comment = "; ".join(keywords.split(","))
    keyword_bytes = user_comment.encode("utf-16le")
    exif_dict["0th"][piexif.ImageIFD.XPKeywords] = keyword_bytes

    exif_dict["GPS"] = gps_ifd
    exif_bytes = piexif.dump(exif_dict)

    output_path = os.path.splitext(image_path)[0] + "_tagged.jpg"
    img.save(output_path, exif=exif_bytes)
    return output_path

def open_file():
    file_path = filedialog.askopenfilename(filetypes=[("Image Files", "*.jpg *.jpeg")])
    if file_path:
        selected_file.set(file_path)

def tag_photo():
    try:
        lat = float(entry_lat.get())
        lng = float(entry_lng.get())
        alt = float(entry_alt.get())
        keywords = entry_keywords.get()
        path = selected_file.get()

        if not path:
            messagebox.showerror("Error", "Please select a photo.")
            return

        output = embed_gps_and_keywords(path, lat, lng, alt, keywords)
        messagebox.showinfo("Success", f"Photo saved with tags:\n{output}")
    except Exception as e:
        messagebox.showerror("Error", str(e))

# GUI Setup
root = tk.Tk()
root.title("GeoTagger - Tag Images with GPS & Keywords")

selected_file = tk.StringVar()

tk.Label(root, text="Selected Photo:").grid(row=0, column=0, sticky="e")
tk.Entry(root, textvariable=selected_file, width=50).grid(row=0, column=1)
tk.Button(root, text="Browse", command=open_file).grid(row=0, column=2)

tk.Label(root, text="Latitude:").grid(row=1, column=0, sticky="e")
entry_lat = tk.Entry(root)
entry_lat.grid(row=1, column=1)

tk.Label(root, text="Longitude:").grid(row=2, column=0, sticky="e")
entry_lng = tk.Entry(root)
entry_lng.grid(row=2, column=1)

tk.Label(root, text="Altitude (m):").grid(row=3, column=0, sticky="e")
entry_alt = tk.Entry(root)
entry_alt.grid(row=3, column=1)

tk.Label(root, text="Keywords (comma-separated):").grid(row=4, column=0, sticky="e")
entry_keywords = tk.Entry(root, width=50)
entry_keywords.grid(row=4, column=1, columnspan=2)

tk.Button(root, text="Tag Photo", command=tag_photo, bg="#4CAF50", fg="white").grid(row=5, column=1, pady=10)

root.mainloop()
