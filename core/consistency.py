from __future__ import annotations

from rapidfuzz import fuzz

from core.schemas import ConsistencyMismatch, ParsedDocument


def compare_resume_versions(pdf_doc: ParsedDocument, docx_doc: ParsedDocument) -> tuple[float, list[ConsistencyMismatch]]:
    pdf = pdf_doc.structured
    docx = docx_doc.structured
    if not pdf or not docx:
        return 0.0, []

    mismatches: list[ConsistencyMismatch] = []
    fields = [
        ("phone", pdf.contact.phone, docx.contact.phone),
        ("email", pdf.contact.email, docx.contact.email),
        ("location", pdf.contact.location, docx.contact.location),
        ("summary", pdf.summary, docx.summary),
        ("job_titles", " | ".join(item.job_title for item in pdf.experience), " | ".join(item.job_title for item in docx.experience)),
        ("company_names", " | ".join(item.employer for item in pdf.experience), " | ".join(item.employer for item in docx.experience)),
        ("dates", " | ".join(item.date_range for item in pdf.experience), " | ".join(item.date_range for item in docx.experience)),
        ("achievements", " | ".join(pdf.quantified_achievements), " | ".join(docx.quantified_achievements)),
    ]
    total_score = 0.0
    for name, left, right in fields:
        ratio = fuzz.token_sort_ratio(left or "", right or "") if (left or right) else 100
        total_score += ratio
        if ratio < 85:
            mismatches.append(
                ConsistencyMismatch(
                    field=name,
                    pdf_value=left[:200],
                    docx_value=right[:200],
                    severity="high" if ratio < 60 else "medium",
                )
            )
    return round(total_score / len(fields), 2), mismatches

