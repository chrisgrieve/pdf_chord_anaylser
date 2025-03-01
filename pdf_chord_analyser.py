import fitz  # PyMuPDF
import re
import pandas as pd
import sys


def extract_songs_and_chords(pdf_path):
    doc = fitz.open(pdf_path)
    songs = []
    current_song = None
    chord_pattern = re.compile(r"\b[A-G][#b]?m?(maj7|m7|7|dim|sus2|sus4|add9|aug)?\b")

    for page in doc:
        text = page.get_text("text")
        lines = text.split("\n")

        for line in lines:
            if len(line.strip()) > 3 and line.isupper():  # Basic title detection
                if current_song:
                    current_song["unique_chords"] = len(current_song["chords"])
                    songs.append(current_song)
                current_song = {"title": line.strip(), "chords": set(), "chord_changes": 0}
            else:
                if current_song:
                    chords = chord_pattern.findall(line)
                    if chords:
                        current_song["chords"].update(chords)
                        current_song["chord_changes"] += max(0, len(chords) - 1)  # Count chord changes in a line

    if current_song:
        current_song["unique_chords"] = len(current_song["chords"])
        songs.append(current_song)

    return songs


def main():
    if len(sys.argv) != 2:
        print("Usage: python pdf_chord_analyser.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    songs_data = extract_songs_and_chords(pdf_path)

    # Convert to DataFrame and save to CSV
    df = pd.DataFrame(songs_data)
    df["chords"] = df["chords"].apply(lambda x: ", ".join(x))  # Convert sets to readable strings
    df.to_csv("chord_analysis.csv", index=False)

    print(df.head())  # Preview the output


if __name__ == "__main__":
    main()