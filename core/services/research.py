from __future__ import annotations

import re
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from typing import Any
from urllib.parse import urlparse

import httpx
from duckduckgo_search import DDGS

from core.schemas import CompanyResearch, JobDescriptionData


DATE_PATTERNS = [
    re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b"),
    re.compile(r"\b(\d{1,2}/\d{1,2}/20\d{2})\b"),
    re.compile(r"\b([A-Z][a-z]{2,8}\s+\d{1,2},\s+20\d{2})\b"),
]

PREFERRED_SOURCE_HINTS = (
    "linkedin.com",
    "greenhouse.io",
    "lever.co",
    "ashbyhq.com",
    "workdayjobs.com",
    "indeed.com",
    "glassdoor.",
    "wellfound.com",
    "theorg.com",
    "crunchbase.com",
    "pitchbook.com",
    "bloomberg.com",
    "reuters.com",
)

LOW_SIGNAL_SOURCE_HINTS = (
    "baidu.com",
    "zhihu.com",
    "pinterest.",
    "facebook.com",
)


class WebResearchService:
    def analyze_market(self, jd: JobDescriptionData) -> CompanyResearch:
        query_base = " ".join(part for part in [jd.role_title, jd.company_name, "job"] if part).strip()
        if not query_base:
            return CompanyResearch(notes_en=["No company or role title was available for web research."], notes_he=["לא היה מספיק מידע על חברה או תפקיד כדי לבצע מחקר רשת."])

        search_results = self._search(query_base)
        company_results = self._search(" ".join(part for part in [jd.company_name or "", "funding layoffs news stability"] if part).strip())
        search_results = self._rank_and_filter(search_results)
        company_results = self._rank_and_filter(company_results)
        combined = search_results + company_results

        posting_dates = [dt for dt in (self._extract_date(item) for item in search_results) if dt]
        oldest_days = None
        if posting_dates:
            oldest = min(posting_dates)
            oldest_days = max(0, (datetime.now(timezone.utc) - oldest).days)

        repeated_signal = len({item["href"] for item in search_results if item.get("href")}) >= 3
        stability_signal = self._infer_stability(company_results)
        company_snapshot = self._summarize_company(company_results, jd.company_name)
        sources = [item["href"] for item in combined if item.get("href")][:8]

        notes_en = []
        notes_he = []
        if oldest_days is not None:
            notes_en.append(f"Earliest public role signal found is approximately {oldest_days} days old.")
            notes_he.append(f"האיתות הציבורי המוקדם ביותר שנמצא למשרה הוא מלפני כ-{oldest_days} ימים.")
        if repeated_signal:
            notes_en.append("Multiple indexed postings or references suggest this role may have been reposted or syndicated.")
            notes_he.append("נמצאו כמה מופעים מאונדקסים, מה שמרמז שהמשרה ייתכן שפורסמה מחדש או הופצה בכמה מקומות.")
        else:
            notes_en.append("No strong reposting pattern was found in the indexed public results.")
            notes_he.append("לא נמצא דפוס חזק של פרסום מחדש בתוצאות הציבוריות שנמצאו.")
        if company_snapshot:
            notes_en.append(company_snapshot)
            notes_he.append(f"תקציר חברה: {company_snapshot}")

        return CompanyResearch(
            company_name=jd.company_name,
            company_snapshot=company_snapshot,
            stability_signal=stability_signal,
            role_market_age_days=oldest_days,
            reposted_role_signal=repeated_signal,
            posting_evidence_count=len(search_results),
            sources=sources,
            notes_en=notes_en,
            notes_he=notes_he,
        )

    def _search(self, query: str) -> list[dict[str, Any]]:
        if not query:
            return []
        try:
            with DDGS() as ddgs:
                return list(ddgs.text(query, max_results=5))
        except Exception:
            return []

    def _rank_and_filter(self, items: list[dict[str, Any]]) -> list[dict[str, Any]]:
        ranked: list[tuple[int, dict[str, Any]]] = []
        seen: set[str] = set()
        for item in items:
            href = item.get("href", "")
            if not href or href in seen:
                continue
            seen.add(href)
            host = urlparse(href).netloc.lower()
            score = 0
            if any(hint in host for hint in PREFERRED_SOURCE_HINTS):
                score += 3
            if any(hint in host for hint in LOW_SIGNAL_SOURCE_HINTS):
                score -= 3
            if jd_terms := (item.get("title", "") + " " + item.get("body", "")).lower():
                if "careers" in jd_terms or "job" in jd_terms or "hiring" in jd_terms:
                    score += 1
                if "forum" in jd_terms or "question" in jd_terms:
                    score -= 1
            ranked.append((score, item))
        ranked.sort(key=lambda pair: pair[0], reverse=True)
        return [item for score, item in ranked if score >= -1][:5]

    def _extract_date(self, item: dict[str, Any]) -> datetime | None:
        haystacks = [item.get("body", ""), item.get("title", ""), item.get("href", "")]
        for haystack in haystacks:
            for pattern in DATE_PATTERNS:
                match = pattern.search(haystack or "")
                if not match:
                    continue
                value = match.group(1)
                for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%B %d, %Y", "%b %d, %Y"):
                    try:
                        return datetime.strptime(value, fmt).replace(tzinfo=timezone.utc)
                    except ValueError:
                        continue
        href = item.get("href")
        if not href:
            return None
        try:
            response = httpx.head(href, timeout=5, follow_redirects=True)
            last_modified = response.headers.get("last-modified")
            if last_modified:
                dt = parsedate_to_datetime(last_modified)
                return dt.astimezone(timezone.utc)
        except Exception:
            return None
        return None

    def _infer_stability(self, company_results: list[dict[str, Any]]) -> str:
        text = " ".join((item.get("title", "") + " " + item.get("body", "")) for item in company_results).lower()
        if any(term in text for term in ["layoff", "bankruptcy", "shutdown", "insolvency"]):
            return "watchlist"
        if any(term in text for term in ["funding", "profit", "expansion", "growth", "hiring"]):
            return "positive"
        if company_results:
            return "mixed"
        return "unknown"

    def _summarize_company(self, company_results: list[dict[str, Any]], company_name: str) -> str:
        if not company_results:
            return f"No strong public signal was collected for {company_name or 'the company'}."
        top = company_results[0]
        body = top.get("body", "").strip()
        return body[:220] if body else f"Public search results were found for {company_name or 'the company'}, but only limited stability evidence was available."
