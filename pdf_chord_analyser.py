import pymupdf
import re
import pandas as pd
import sys
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("pdf_chord_analyser.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def open_pdf(pdf_path):
    logger.info(f"Opening PDF file: {pdf_path}")
    return pymupdf.open(pdf_path)

def extract_text_from_page(page):
    logger.debug(f"Extracting text from page number: {page.number}")
    return page.get_text("text")

def split_text_into_lines(text):
    logger.debug("Splitting text into lines")
    return text.split("\n")

def is_title_line(line, chord_pattern):
    result = find_chords_in_line(line, chord_pattern) == 0
    result = result and line != "CONTENTS"
    result = result and line != "CHORUS"
    logger.debug(f"Checking if line is a title: {line} - Result: {result}")
    return result

def find_chords_in_line(line, chord_pattern):
    chords = chord_pattern.findall(line)
    logger.debug(f"Finding chords in line: {line} - Chords: {chords}")
    return chords

def create_new_song(title):
    logger.info(f"Creating new song with title: {title.strip()}")
    return {"title": title.strip(), "chords": set(), "chord_changes": 0}

def finalize_song(song):
    song["unique_chords"] = len(song["chords"])
    logger.info(f"Finalizing song: {song['title']} - Unique chords: {song['unique_chords']}")
    return song

def analyse_page(page, chord_pattern):
    text = extract_text_from_page(page)
    lines = split_text_into_lines(text)
    return lines

def analyse_lines(lines, chord_pattern, current_song):
    songs = []
    for line in lines:
        if is_title_line(line, chord_pattern):  # Basic title detection
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
    logger.info(f"Extracting songs and chords from PDF: {pdf_path}")
    doc = open_pdf(pdf_path)
    songs = []
    current_song = None
    # chord_pattern = re.compile(r"\b[A-G][#b]?m?(maj7|m7|7|dim|sus2|sus4|add9|aug)?\b")
    chord_pattern = re.compile(r"\b \(*.\)\b")

    for page in doc:
        lines = analyse_page(page, chord_pattern)
        result_songs, current_song = analyse_lines(lines, chord_pattern, current_song)
        songs.extend(result_songs)

    if current_song:
        songs.append(finalize_song(current_song))

    logger.info(f"Extraction complete. Total songs found: {len(songs)}")
    return songs

def convert_songs_to_dataframe(songs_data):
    logger.info("Converting songs data to DataFrame")
    df = pd.DataFrame(songs_data)
    df["chords"] = df["chords"].apply(lambda x: ", ".join(x))  # Convert sets to readable strings
    return df

def save_dataframe_to_csv(df, csv_path):
    logger.info(f"Saving DataFrame to CSV file: {csv_path}")
    df.to_csv(csv_path, index=False)

def main():
    if len(sys.argv) != 2:
        print("Usage: python pdf_chord_analyser.py <pdf_path>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    logger.info(f"Started processing PDF: {pdf_path}")
    songs_data = extract_songs_and_chords(pdf_path)

    df = convert_songs_to_dataframe(songs_data)
    save_dataframe_to_csv(df, "chord_analysis.csv")

    logger.info("Processing complete. Previewing output:")
    print(df.head())  # Preview the output

if __name__ == "__main__":
    main()
