from __future__ import annotations

from core.language_utils import is_probably_hebrew
from core.schemas import ConsistencyMismatch, JobDescriptionData, RecommendationBlock, ResumeStructuredData


def build_recommendations(
    resume: ResumeStructuredData,
    jd: JobDescriptionData,
    missing_keywords: list[str],
    formatting_issues: list[str],
    mismatches: list[ConsistencyMismatch],
) -> RecommendationBlock:
    english: list[str] = []
    hebrew: list[str] = []

    if missing_keywords:
        english.append(f"Add or strengthen these keywords where accurate: {', '.join(missing_keywords[:8])}.")
        hebrew.append(f"הוסיפו או חזקו את מילות המפתח הבאות רק אם הן מדויקות: {', '.join(missing_keywords[:8])}.")
    if formatting_issues:
        english.extend(f"Fix ATS formatting risk: {issue}" for issue in formatting_issues[:4])
        hebrew.extend(f"תקנו סיכון פורמטי ל-ATS: {issue}" for issue in formatting_issues[:4])
    if mismatches:
        english.append("Resolve the mismatches between the PDF and DOCX versions before applying.")
        hebrew.append("פתרו את אי-ההתאמות בין גרסת ה-PDF לגרסת ה-DOCX לפני שליחת המועמדות.")
    if not resume.summary:
        english.append(f"Write a tighter summary aligned to the role '{jd.role_title or 'target job'}'.")
        hebrew.append(f"כתבו תקציר ממוקד יותר שמותאם לתפקיד '{jd.role_title or 'תפקיד היעד'}'.")

    headline = jd.role_title or "target role"
    english.append(f"Suggested headline: {headline} | Multilingual, ATS-optimized, results-driven candidate.")
    hebrew.append(f"כותרת מוצעת: {headline} | מועמד/ת דו-לשוני/ת, מותאם/ת ATS ומבוסס/ת תוצאות.")

    if resume.quantified_achievements:
        english.append(f"Rewrite bullets to foreground metrics, for example: {resume.quantified_achievements[0]}")
        hebrew.append(f"שכתבו בולטים כך שהמדדים יופיעו בהתחלה, למשל: {resume.quantified_achievements[0]}")
    else:
        english.append("Add quantified bullets with percentages, revenue, savings, scope, or delivery speed.")
        hebrew.append("הוסיפו בולטים כמותיים עם אחוזים, הכנסות, חיסכון, היקף או מהירות ביצוע.")

    if is_probably_hebrew(resume.summary):
        english.append("Consider adding an English summary if you apply to global or English-speaking companies.")
        hebrew.append("שקלו להוסיף גם תקציר באנגלית אם אתם מגישים מועמדות לחברות גלובליות או דוברות אנגלית.")

    return RecommendationBlock(english=english, hebrew=hebrew)

