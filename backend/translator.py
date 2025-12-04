from deep_translator import GoogleTranslator, MyMemoryTranslator
import time
import re

def translate_text(text: str, source_lang: str = "hi", target_lang: str = "en") -> str:
    """
    Translate text from source language to target language using high-quality translation services.
    Uses multiple translation services with fallback for better accuracy.

    Args:
        text: Text to translate
        source_lang: Source language code ('en' or 'hi')
        target_lang: Target language code ('en' or 'hi')

    Returns:
        Translated text
    """
    try:
        # Convert language codes if needed
        # deep-translator uses standard codes
        source = source_lang
        target = target_lang

        # Maximum chunk size - MyMemory has 500 char limit
        max_chunk_size = 450  # Keep safely under MyMemory's 500 char limit

        if len(text) <= max_chunk_size:
            # Translate in one go
            return _translate_with_fallback(text, source, target)
        else:
            # Split into chunks and translate
            chunks = _split_text_into_chunks(text, max_chunk_size)

            # Translate each chunk
            translated_chunks = []
            for i, chunk in enumerate(chunks):
                print(f"Translating chunk {i+1}/{len(chunks)}")
                try:
                    translated_chunk = _translate_with_fallback(chunk, source, target)
                    translated_chunks.append(translated_chunk)

                    # Add delay to avoid rate limiting
                    if i < len(chunks) - 1:
                        time.sleep(0.5)  # Increased delay for better reliability

                except Exception as e:
                    print(f"Error translating chunk {i+1}: {e}")
                    # If translation fails for a chunk, keep original text
                    translated_chunks.append(chunk)

            # Join without double newlines to avoid breaking formatting
            return " ".join(translated_chunks)

    except Exception as e:
        raise Exception(f"Translation error: {str(e)}")


def _translate_with_fallback(text: str, source: str, target: str) -> str:
    """
    Attempt translation with multiple services for best quality.
    Preserves numbers, dates, and special characters.

    Priority:
    1. MyMemory (most accurate, free)
    2. Google Translate (reliable fallback)
    """
    if not text.strip():
        return text

    # Preserve numbers and special patterns
    text_to_translate, placeholders = _preserve_numbers_and_patterns(text)

    # Map language codes to MyMemory format
    mymemory_lang_map = {
        'en': 'en-US',
        'hi': 'hi-IN',
    }

    mymemory_source = mymemory_lang_map.get(source, source)
    mymemory_target = mymemory_lang_map.get(target, target)

    # Try MyMemory first (better quality for Hindi-English)
    translated_result = None
    try:
        translator = MyMemoryTranslator(source=mymemory_source, target=mymemory_target)
        result = translator.translate(text_to_translate)

        # MyMemory sometimes returns the original if no translation available
        if result and result != text_to_translate:
            print(f"Translated with MyMemory: {len(text)} -> {len(result)} chars")
            translated_result = result
    except Exception as e:
        print(f"MyMemory translation failed: {e}")

    # Fallback to Google Translate
    if not translated_result:
        try:
            translator = GoogleTranslator(source=source, target=target)
            result = translator.translate(text_to_translate)

            if result:
                print(f"Translated with Google: {len(text)} -> {len(result)} chars")
                translated_result = result
        except Exception as e:
            print(f"Google translation failed: {e}")

    # If all translation services fail, use original
    if not translated_result:
        print("Warning: All translation services failed, returning original text")
        translated_result = text_to_translate

    # Restore numbers and patterns
    final_result = _restore_numbers_and_patterns(translated_result, placeholders)
    return final_result


def _preserve_numbers_and_patterns(text: str) -> tuple:
    """
    Replace numbers, dates, and special patterns with translation-proof placeholders.
    Uses numeric placeholders that won't be translated by APIs.
    """
    placeholders = {}
    counter = 0

    # Patterns to preserve (ordered from most specific to least specific)
    # More specific patterns MUST come before generic ones
    patterns = [
        # URLs (very specific, must be first)
        (r'https?://[^\s]+', 'URL'),

        # Email addresses (very specific)
        (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', 'EMAIL'),

        # Phone numbers (specific pattern with separators)
        (r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b', 'PHONE'),

        # Dates (various formats, contain multiple numbers)
        (r'\b\d{1,2}[-/]\d{1,2}[-/]\d{2,4}\b', 'DATE'),
        (r'\b\d{4}[-/]\d{1,2}[-/]\d{1,2}\b', 'DATE'),

        # Times (specific pattern with colons)
        (r'\b\d{1,2}:\d{2}(?::\d{2})?\s*(?:AM|PM|am|pm)?\b', 'TIME'),

        # Currency amounts (numbers with currency symbols)
        (r'(?:Rs\.?\s*|₹\s*|USD\s*|\$\s*|€\s*|£\s*)\d+(?:,\d{3})*(?:\.\d{2})?', 'CURRENCY'),

        # Numbers with units
        (r'\b\d+(?:\.\d+)?\s*(?:%|kg|km|m|cm|mm|g|mg|ml|l|GB|MB|KB|Rs|₹|\$|€|£)\b', 'NUMUNIT'),

        # Percentages
        (r'\b\d+(?:\.\d+)?%', 'PERCENT'),

        # Large numbers with commas
        (r'\b\d{1,3}(?:,\d{3})+(?:\.\d+)?\b', 'BIGNUM'),

        # Decimals and floats
        (r'\b\d+\.\d+\b', 'DECIMAL'),

        # Regular integers (MUST be last as it's most generic)
        (r'\b\d+\b', 'NUM'),
    ]

    # Collect all matches with their positions and pattern info
    all_matches = []
    for pattern, pattern_type in patterns:
        for match in re.finditer(pattern, text):
            all_matches.append({
                'start': match.start(),
                'end': match.end(),
                'text': match.group(),
                'pattern_type': pattern_type
            })

    # Sort by start position (ascending) and by length (descending) to handle overlaps
    # Prefer longer matches at the same position (more specific patterns)
    all_matches.sort(key=lambda x: (x['start'], -(x['end'] - x['start'])))

    # Track replaced ranges to avoid overlaps
    replaced_ranges = []
    matches_to_replace = []

    for match in all_matches:
        # Check if this match overlaps with any already replaced range
        overlaps = False
        for r_start, r_end in replaced_ranges:
            if not (match['end'] <= r_start or match['start'] >= r_end):
                overlaps = True
                break

        if not overlaps:
            matches_to_replace.append(match)
            replaced_ranges.append((match['start'], match['end']))

    # Now replace in reverse order by position (right to left) to preserve positions
    modified_text = text
    for match in reversed(matches_to_replace):
        original = match['text']
        # Use large unique numbers as placeholders - translation APIs typically preserve numbers
        # Start from 999999900 to avoid collision with real numbers
        placeholder = str(999999900 + counter)
        placeholders[placeholder] = original
        modified_text = modified_text[:match['start']] + placeholder + modified_text[match['end']:]
        counter += 1

    return modified_text, placeholders


def _restore_numbers_and_patterns(text: str, placeholders: dict) -> str:
    """
    Restore the original numbers and patterns from placeholders.
    """
    result = text
    for placeholder, original in placeholders.items():
        result = result.replace(placeholder, original)
    return result


def _split_text_into_chunks(text: str, max_size: int) -> list:
    """
    Split text into chunks while preserving sentence and line boundaries.
    Respects MyMemory's 500 character limit.
    """
    chunks = []

    # Split by lines first to preserve structure
    lines = text.split('\n')
    current_chunk = ""

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # If single line is too long, split by sentences
        if len(line) > max_size:
            # Split by sentence endings
            sentences = line.replace('. ', '.|').replace('। ', '।|').replace('? ', '?|').replace('! ', '!|').split('|')

            for sentence in sentences:
                sentence = sentence.strip()
                if not sentence:
                    continue

                # If sentence is still too long, split by words
                if len(sentence) > max_size:
                    words = sentence.split()
                    temp_chunk = ""
                    for word in words:
                        if len(temp_chunk) + len(word) + 1 <= max_size:
                            temp_chunk += word + " "
                        else:
                            if temp_chunk:
                                chunks.append(temp_chunk.strip())
                            temp_chunk = word + " "
                    if temp_chunk:
                        if len(current_chunk) + len(temp_chunk) <= max_size:
                            current_chunk += temp_chunk
                        else:
                            if current_chunk:
                                chunks.append(current_chunk.strip())
                            current_chunk = temp_chunk
                else:
                    # Add sentence to current chunk
                    if len(current_chunk) + len(sentence) + 2 <= max_size:
                        current_chunk += sentence + " "
                    else:
                        if current_chunk:
                            chunks.append(current_chunk.strip())
                        current_chunk = sentence + " "
        else:
            # Line fits in max_size, try to add to current chunk
            if len(current_chunk) + len(line) + 2 <= max_size:
                current_chunk += line + " "
            else:
                if current_chunk:
                    chunks.append(current_chunk.strip())
                current_chunk = line + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks


def detect_language(text: str) -> str:
    """
    Detect the language of the given text.

    Args:
        text: Text to analyze

    Returns:
        Language code (e.g., 'en', 'hi')
    """
    try:
        # Use Google Translator for language detection
        from deep_translator import single_detection
        lang = single_detection(text, api_key='auto')
        return lang
    except Exception as e:
        print(f"Error detecting language: {e}")
        return "unknown"
