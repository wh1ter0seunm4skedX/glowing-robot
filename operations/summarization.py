import os
import time
from transformers import AutoModelForSeq2SeqLM, AutoTokenizer, SummarizationPipeline


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
