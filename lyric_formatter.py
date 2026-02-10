#!/usr/bin/env python3
"""악보 이미지에서 가사를 추출하고 송폼 기준으로 정렬/번역하는 간단한 CLI."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List


@dataclass
class Section:
    name: str
    block_count: int = 1


def parse_song_form(song_form_text: str) -> List[Section]:
    """송폼 텍스트를 Section 목록으로 파싱한다.

    지원 형식 예시:
    - Verse 1
    - Chorus x2
    - Bridge:3
    """

    sections: List[Section] = []
    for raw_line in song_form_text.splitlines():
        line = raw_line.strip()
        if not line:
            continue

        matched = re.match(r"^(.*?)(?:\s*(?:x|:)\s*(\d+))?$", line, flags=re.IGNORECASE)
        if not matched:
            continue

        name = matched.group(1).strip()
        count = int(matched.group(2) or 1)
        sections.append(Section(name=name, block_count=max(1, count)))

    if not sections:
        raise ValueError("송폼이 비어 있습니다. 최소 1개 이상의 섹션을 입력해 주세요.")

    return sections


def extract_lyrics_from_image(image_path: Path, lang: str = "kor+eng") -> str:
    """Tesseract OCR로 이미지에서 텍스트를 추출한다."""

    try:
        import pytesseract
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError(
            "OCR을 위해 pytesseract와 Pillow가 필요합니다. `pip install -r requirements.txt`를 실행하세요."
        ) from exc

    image = Image.open(image_path)
    return pytesseract.image_to_string(image, lang=lang)


def clean_lyrics(raw_text: str) -> List[str]:
    """OCR 결과를 가사 라인 목록으로 정리한다."""

    lines: List[str] = []
    for line in raw_text.splitlines():
        text = re.sub(r"\s+", " ", line).strip()
        text = re.sub(r"[^가-힣a-zA-Z0-9\s'.,!?-]", "", text)
        if text:
            lines.append(text)
    return lines


def chunk_words(text_lines: Iterable[str], words_per_line: int = 5, lines_per_block: int = 2) -> List[List[str]]:
    """한국어 가사를 n어절 단위로 나누고, m줄씩 블록으로 묶는다."""

    words: List[str] = []
    for line in text_lines:
        words.extend(line.split())

    lyric_lines = [" ".join(words[i : i + words_per_line]) for i in range(0, len(words), words_per_line)]

    blocks: List[List[str]] = []
    for i in range(0, len(lyric_lines), lines_per_block):
        block = lyric_lines[i : i + lines_per_block]
        if len(block) < lines_per_block:
            block += [""] * (lines_per_block - len(block))
        blocks.append(block)

    return blocks


def expand_sections(sections: List[Section]) -> List[str]:
    expanded: List[str] = []
    for section in sections:
        for index in range(section.block_count):
            if section.block_count == 1:
                expanded.append(section.name)
            else:
                expanded.append(f"{section.name} ({index + 1}/{section.block_count})")
    return expanded


def translate_to_english(lines: List[str]) -> List[str]:
    """두 줄의 한국어 가사를 영어로 번역한다."""

    try:
        from deep_translator import GoogleTranslator
    except ImportError as exc:
        raise RuntimeError(
            "번역을 위해 deep-translator가 필요합니다. `pip install -r requirements.txt`를 실행하세요."
        ) from exc

    translator = GoogleTranslator(source="ko", target="en")
    result: List[str] = []
    for line in lines:
        if not line.strip():
            result.append("")
        else:
            result.append(translator.translate(line))
    return result


def format_output(section_titles: List[str], blocks: List[List[str]]) -> str:
    entries: List[str] = []
    for index, title in enumerate(section_titles):
        kr_block = blocks[index] if index < len(blocks) else ["", ""]
        en_block = translate_to_english(kr_block)
        entry = [
            f"[{title}]",
            f"KR 1: {kr_block[0]}",
            f"KR 2: {kr_block[1]}",
            f"EN 1: {en_block[0]}",
            f"EN 2: {en_block[1]}",
        ]
        entries.append("\n".join(entry))
    return "\n\n".join(entries)


def load_song_form(song_form_arg: str) -> str:
    maybe_file = Path(song_form_arg)
    if maybe_file.exists() and maybe_file.is_file():
        return maybe_file.read_text(encoding="utf-8")
    return song_form_arg


def main() -> None:
    parser = argparse.ArgumentParser(description="악보 이미지 가사 -> 송폼 정렬 + 영문 번역")
    parser.add_argument("--image", required=True, type=Path, help="악보 이미지 경로")
    parser.add_argument("--song-form", required=True, help="송폼 텍스트 또는 파일 경로")
    parser.add_argument("--output", default="output_lyrics.txt", type=Path, help="출력 텍스트 파일")
    parser.add_argument("--ocr-lang", default="kor+eng", help="Tesseract OCR 언어 옵션")

    args = parser.parse_args()

    raw_text = extract_lyrics_from_image(args.image, lang=args.ocr_lang)
    cleaned = clean_lyrics(raw_text)
    if not cleaned:
        raise RuntimeError("OCR 결과에서 가사를 찾지 못했습니다.")

    song_form = parse_song_form(load_song_form(args.song_form))
    section_titles = expand_sections(song_form)

    lyric_blocks = chunk_words(cleaned, words_per_line=5, lines_per_block=2)

    output_text = format_output(section_titles, lyric_blocks)
    args.output.write_text(output_text, encoding="utf-8")

    print(f"완료: {args.output}")


if __name__ == "__main__":
    main()
