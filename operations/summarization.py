import os
import random
import time
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, SummarizationPipeline
from utils.database_utils import create_connection, close_connection, set_target_db, config
from mysql.connector import Error


def summarize_text(parsed_text):
    script_dir = os.path.dirname(__file__)  # Get the directory where the script is located
    model_dir = os.path.join(script_dir, '../het5_summarization')

    try:
        # Ensure local_files_only is set to True to prevent any online access
        model = AutoModelForSeq2SeqLM.from_pretrained(model_dir, local_files_only=True)
        tokenizer = AutoTokenizer.from_pretrained(model_dir, local_files_only=True)
    except EnvironmentError as e:
        print(f"Error loading model or tokenizer: {e}")
        return "Model loading failed, check model files."

    summarizer = SummarizationPipeline(model=model, tokenizer=tokenizer)

    # Summary settings
    summary_settings = {
        "min_length": 20,
        "max_length": 100,
        "num_beams": 1,
    }

    # Generate summary
    summary = summarizer(parsed_text, **summary_settings)[0]["summary_text"]
    return summary


def fetch_random_pages():
    set_target_db('dev_db')  # Set the database to dev_db
    conn = create_connection()
    if not conn:
        print("Failed to connect to the database.")
        return []

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, title FROM pages ORDER BY RAND() LIMIT 10")
        pages = cursor.fetchall()
        return pages
    except Error as e:
        print(f"Error fetching random pages: {e}")
        return []
    finally:
        close_connection(conn)


def fetch_page_text(page_id):
    conn = create_connection()
    if not conn:
        print("Failed to connect to the database.")
        return ""

    try:
        cursor = conn.cursor()
        cursor.execute("SELECT clean_text FROM pages WHERE id = %s", (page_id,))
        result = cursor.fetchone()
        return result[0] if result else ""
    except Error as e:
        print(f"Error fetching page text: {e}")
        return ""
    finally:
        close_connection(conn)


def show_random_pages():
    pages = fetch_random_pages()
    if not pages:
        return

    for page_id, title in pages:
        print(f"Page ID: {page_id}, Title: {title}")


def select_page_and_summarize():
    pages = fetch_random_pages()
    if not pages:
        return

    for page_id, title in pages:
        print(f"Page ID: {page_id}, Title: {title}")

    while True:
        user_input = input("\nEnter the ID of the page you want to summarize (or type 'exit' to quit): ")
        if user_input.lower() == 'exit':
            print("Exiting program. Goodbye.")
            break

        try:
            page_id = int(user_input)
            if page_id in [page[0] for page in pages]:
                text = fetch_page_text(page_id)
                if text:
                    print("Summarization process started...")
                    start_time = time.time()
                    summary = summarize_text(text)
                    end_time = time.time()
                    print("Summarization process ended.")
                    print(f"Time taken for summarization: {end_time - start_time:.2f} seconds")
                    print("\nSummary:")
                    print(summary)
                else:
                    print("No text found for the selected page.")
            else:
                print("Invalid ID selected.")
        except ValueError:
            print("Invalid input. Please enter a valid ID.")

if __name__ == "__main__":
    show_random_pages()
    select_page_and_summarize()
