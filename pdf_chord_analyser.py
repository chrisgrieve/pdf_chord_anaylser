import fitz  # PyMuPDF
import re
import pandas as pd
import sys

def open_pdf(pdf_path):
    return fitz.open(pdf_path)

def extract_text_from_page(page):
    return page.get_text("text")

def split_text_into_lines(text):
    return text.split("\n")

def is_title_line(line):
    return len(line.strip()) > 3 and line.isupper()

def find_chords_in_line(line, chord_pattern):
    return chord_pattern.findall(line)

def create_new_song(title):
    return {"title": title.strip(), "chords": set(), "chord_changes": 0}

def finalize_song(song):
    song["unique_chords"] = len(song["chords"])
    return song

def analyse_page(page, chord_pattern):
    text = extract_text_from_page(page)
    lines = split_text_into_lines(text)
    return lines

def analyse_lines(lines, chord_pattern, current_song):
    songs = []
    for line in lines:
        if is_title_line(line):  # Basic title detection
            if current_song:
                songs.append(finalize_song(current_song))
            current_song = create_new_song(line)
        else:
            if current_song:
                chords = find_chords_in_line(line, chord_pattern)
                if chords:
                    current_song["chords"].update(chords)
                    current_song["chord_changes"] += max(0, len(chords) - 1)  # Count chord changes in a line
    return songs, current_song

def extract_songs_and_chords(pdf_path):
    doc = open_pdf(pdf_path)
    songs = []
    current_song = None
    chord_pattern = re.compile(r"\b[A-G][#b]?m?(maj7|m7|7|dim|sus2|sus4|add9|aug)?\b")

    for page in doc:
        lines = analyse_page(page, chord_pattern)
        result_songs, current_song = analyse_lines(lines, chord_pattern, current_song)
        songs.extend(result_songs)

    if current_song:
        songs.append(finalize_song(current_song))

    return songs

def convert_songs_to_dataframe(songs_data):
    df = pd.DataFrame(songs_data)
    df["chords"] = df["chords"].apply(lambda x: ", ".join(x))  # Convert sets to readable strings
    return df

def save_dataframe_to_csv(df, csv_path):
    df.to_csv(csv_path, index=False)

def main():
    if len(sys.argv) != 2:
        print("Usage: python pdf_chord_analyser.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    songs_data = extract_songs_and_chords(pdf_path)

    df = convert_songs_to_dataframe(songs_data)
    save_dataframe_to_csv(df, "chord_analysis.csv")

    print(df.head())  # Preview the output

if __name__ == "__main__":
    main()
