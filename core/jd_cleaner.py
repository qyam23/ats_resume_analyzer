from __future__ import annotations

import re


NOISE_PATTERNS = [
    r"skip to main content",
    r"agree\s*&\s*join linkedin.*",
    r"new to linkedin\?.*",
    r"sign in to see who you already know.*",
    r"email or phone password.*",
    r"forgot password\?.*",
    r"cookie policy",
    r"user agreement",
    r"privacy policy",
    r"copyright policy",
    r"brand policy",
    r"guest controls",
    r"community guidelines",
    r"see who you know",
    r"get notified about new .* jobs",
    r"referrals increase your chances.*",
    r"show more show less",
    r"join now",
    r"sign in",
]

LANGUAGE_NOISE = {
    "العربية",
    "বাংলা",
    "čeština",
    "dansk",
    "deutsch",
    "english",
    "español",
    "français",
    "עברית",
    "italiano",
    "nederlands",
    "português",
    "русский",
    "svenska",
    "tagalog",
    "türkçe",
    "简体中文",
    "正體中文",
}

SECTION_HINTS = [
    "about the job",
    "about this job",
    "job description",
    "responsibilities",
    "requirements",
    "qualifications",
    "דרישות",
    "תיאור",
]


def clean_job_description_text(text: str) -> str:
    cleaned = text.replace("\r", "\n")
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    cleaned = _prefer_job_section(cleaned)
    cleaned = _strip_inline_noise(cleaned)
    cleaned = _drop_noise_lines(cleaned)
    cleaned = re.sub(r"\s{2,}", " ", cleaned)
    cleaned = re.sub(r"\n\s+", "\n", cleaned)
    return cleaned.strip()[:12000]


def _prefer_job_section(text: str) -> str:
    lowered = text.lower()
    positions = [lowered.find(hint) for hint in SECTION_HINTS if lowered.find(hint) != -1]
    if not positions:
        return text
    start = min(positions)
    prefix = text[:start].strip()
    if prefix and len(prefix) < 800:
        lead_lines = []
        for raw_line in prefix.splitlines():
            line = raw_line.strip()
            if not line:
                continue
            lowered_line = line.lower()
            if any(re.search(pattern, lowered_line) for pattern in NOISE_PATTERNS):
                continue
            if _is_language_noise(line):
                continue
            lead_lines.append(line)
            if len(lead_lines) >= 3:
                break
        if lead_lines:
            return "\n".join(lead_lines + [text[start:]])
    return text[start:]


def _drop_noise_lines(text: str) -> str:
    kept: list[str] = []
    for raw_line in re.split(r"[\n|•]+", text):
        line = raw_line.strip(" \t.-–—")
        if not line:
            continue
        lowered = line.lower()
        if any(re.search(pattern, lowered) for pattern in NOISE_PATTERNS):
            continue
        if _is_language_noise(line):
            continue
        if re.search(r"\b(unrelated|not related|not relevant)\s+to\b", lowered):
            continue
        if len(line) < 3:
            continue
        kept.append(line)
    return "\n".join(kept)


def _strip_inline_noise(text: str) -> str:
    cleaned = text
    inline_patterns = [
        r"linkedin skip to main content",
        r"cookie policy",
        r"user agreement",
        r"privacy policy",
        r"copyright policy",
        r"brand policy",
        r"guest controls",
        r"community guidelines",
        r"show more show less",
        r"sign in",
        r"join now",
    ]
    for pattern in inline_patterns:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)
    for item in LANGUAGE_NOISE:
        cleaned = re.sub(re.escape(item), " ", cleaned, flags=re.IGNORECASE)
    return cleaned


def _is_language_noise(line: str) -> bool:
    lowered = line.lower()
    if "language" in lowered and len(line) < 120:
        return True
    language_hits = sum(1 for item in LANGUAGE_NOISE if item.lower() in lowered)
    return language_hits >= 2
