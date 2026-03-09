import re


def optimize_srt_cleaning(input_text):
    # Combined regex to remove indices and timestamps in a single pass
    # Removes: (line number) + (timestamp)
    pattern = r"(?m)^\d+$\n^\d{2}:\d{2}:\d{2},\d{3} --> \d{2}:\d{2}:\d{2},\d{3}$"
    cleaned = re.sub(pattern, "", input_text)
    lines = [line.strip() for line in cleaned.splitlines() if line.strip()]
    return "\n".join(lines)
