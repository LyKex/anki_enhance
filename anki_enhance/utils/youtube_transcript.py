"""YouTube transcript utilities.

This module fetches transcripts from YouTube URLs using `youtube-transcript-api`.
It does NOT download audio; it only uses available captions.

Notes:
- Works best when the video has captions enabled (manual or auto-generated).
- Some videos disable transcript access.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Optional


_YT_ID_PATTERNS: list[re.Pattern[str]] = [
    # https://www.youtube.com/watch?v=VIDEOID
    re.compile(r"(?:youtube\.com/watch\?.*v=)([A-Za-z0-9_-]{11})"),
    # https://youtu.be/VIDEOID
    re.compile(r"(?:youtu\.be/)([A-Za-z0-9_-]{11})"),
    # https://www.youtube.com/shorts/VIDEOID
    re.compile(r"(?:youtube\.com/shorts/)([A-Za-z0-9_-]{11})"),
    # https://www.youtube.com/embed/VIDEOID
    re.compile(r"(?:youtube\.com/embed/)([A-Za-z0-9_-]{11})"),
]


@dataclass(frozen=True)
class TranscriptResult:
    """Transcript fetch result."""

    video_id: str
    language: str
    text: str


def extract_youtube_video_id(url_or_id: str) -> str:
    """Extract YouTube video id from a URL or accept a raw 11-char video id."""

    s = url_or_id.strip()

    # raw ID
    if re.fullmatch(r"[A-Za-z0-9_-]{11}", s):
        return s

    for pat in _YT_ID_PATTERNS:
        m = pat.search(s)
        if m:
            return m.group(1)

    raise ValueError(
        f"Could not extract YouTube video id from: {url_or_id!r}. "
        "Expected a full URL or an 11-character video id."
    )


def _join_transcript_chunks(chunks: Iterable[dict]) -> str:
    parts: list[str] = []
    for ch in chunks:
        t = (ch.get("text") or "").strip()
        if not t:
            continue
        # youtube-transcript-api uses '\n' inside captions sometimes
        parts.append(t.replace("\n", " "))
    # collapse extra spaces
    return re.sub(r"\s+", " ", " ".join(parts)).strip()


def fetch_youtube_transcript(
    url_or_id: str,
    languages: Optional[list[str]] = None,
) -> TranscriptResult:
    """Fetch transcript text from a YouTube URL.

    Args:
        url_or_id: YouTube URL or raw video id.
        languages: Preferred language codes in priority order.
            Example: ["en", "en-US", "fr"]. If None, defaults to ["en"].

    Returns:
        TranscriptResult with video_id, selected language, and transcript text.

    Raises:
        ValueError: if video id can't be parsed.
        RuntimeError: if transcript was fetched but is empty.
        youtube_transcript_api._errors exceptions: if transcript can't be retrieved.
    """

    video_id = extract_youtube_video_id(url_or_id)
    if languages is None or len(languages) == 0:
        languages = ["en"]

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import (
            NoTranscriptFound,
            TranscriptsDisabled,
            VideoUnavailable,
            RequestBlocked,
            IpBlocked,
        )
    except ImportError as e:
        raise ImportError(
            "Missing dependency youtube-transcript-api. "
            "Install with: uv add youtube-transcript-api (or pip install youtube-transcript-api)"
        ) from e

    try:
        api = YouTubeTranscriptApi()
        fetched_transcript = api.fetch(video_id, languages=languages)
        # Extract text from snippets
        text = " ".join(snippet.text for snippet in fetched_transcript.snippets)
        if not text:
            raise RuntimeError("Transcript was fetched but empty.")
        return TranscriptResult(
            video_id=video_id, language=fetched_transcript.language_code, text=text
        )

    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable, RequestBlocked, IpBlocked) as e:
        raise


def fetch_youtube_transcript_precise(
    url_or_id: str,
    languages: Optional[list[str]] = None,
    prefer_generated: bool = False,
) -> TranscriptResult:
    """Fetch transcript and accurately report which language track was used.

    This version uses list() to pick the first available language.

    Args:
        prefer_generated: if True, prefer auto-generated transcript when both exist.
            Defaults to False (prefer manually created transcripts).

    Raises:
        ValueError: if video id can't be parsed.
        RuntimeError: if no transcript in requested languages or transcript is empty.
        youtube_transcript_api._errors exceptions: if transcript can't be retrieved.
    """

    video_id = extract_youtube_video_id(url_or_id)
    if languages is None or len(languages) == 0:
        languages = ["en"]

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        from youtube_transcript_api._errors import (
            NoTranscriptFound,
            TranscriptsDisabled,
            VideoUnavailable,
            RequestBlocked,
            IpBlocked,
        )
    except ImportError as e:
        raise ImportError(
            "Missing dependency youtube-transcript-api."
        ) from e

    try:
        api = YouTubeTranscriptApi()
        transcripts = api.list(video_id)

        chosen = None
        chosen_lang = None

        for lang in languages:
            # Try exact language in manual/generated based on preference.
            if prefer_generated:
                try:
                    chosen = transcripts.find_generated_transcript([lang])
                    chosen_lang = chosen.language_code
                    break
                except NoTranscriptFound:
                    # Try manually created as fallback
                    try:
                        chosen = transcripts.find_manually_created_transcript([lang])
                        chosen_lang = chosen.language_code
                        break
                    except NoTranscriptFound:
                        # Continue to next language
                        continue
            else:
                try:
                    chosen = transcripts.find_manually_created_transcript([lang])
                    chosen_lang = chosen.language_code
                    break
                except NoTranscriptFound:
                    # Try generated as fallback
                    try:
                        chosen = transcripts.find_generated_transcript([lang])
                        chosen_lang = chosen.language_code
                        break
                    except NoTranscriptFound:
                        # Continue to next language
                        continue

        if chosen is None:
            # If we exhausted all languages, raise NoTranscriptFound with all requested languages
            # This will use the package's error message which includes available transcripts
            raise NoTranscriptFound(video_id, languages, transcripts)

        fetched_transcript = chosen.fetch()
        # Extract text from snippets
        text = " ".join(snippet.text for snippet in fetched_transcript.snippets)
        if not text:
            raise RuntimeError("Transcript was fetched but empty.")

        return TranscriptResult(video_id=video_id, language=chosen_lang or languages[0], text=text)

    except (NoTranscriptFound, TranscriptsDisabled, VideoUnavailable, RequestBlocked, IpBlocked) as e:
        raise
