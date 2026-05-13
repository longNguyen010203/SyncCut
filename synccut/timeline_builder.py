from __future__ import annotations

from pathlib import Path
from synccut.models import AlignmentSection, MatchResult, Scene, SectionAsset, TimedText
from synccut.timeline_validator import SUSPICIOUS_GAP_SEC
from synccut.validators import SyncCutError, normalize_match_text, normalize_match_word


def match_scene_to_alignment(scene: Scene, alignment: AlignmentSection) -> MatchResult:
    return _match_scene_to_alignment(scene, alignment, previous_local_end=0.0)


def build_timeline(
    scenes: list[Scene], sections: list[SectionAsset], source_scenes_path: Path
) -> dict:
    section_by_key = {section.section_key: section for section in sections}
    section_offsets = _section_offsets(sections)
    previous_local_end: dict[str, float] = {}

    timeline_entries = []
    for scene in sorted(scenes, key=lambda item: (item.section_order, item.section_key, item.scene_order)):
        section = section_by_key.get(scene.section_key)
        if section is None:
            raise SyncCutError(f"{scene.scene_id} in {scene.section_key}: missing section asset")

        previous_end = previous_local_end.get(scene.section_key, 0.0)
        match = _match_scene_to_alignment(scene, section.alignment, previous_local_end=previous_end)
        previous_local_end[scene.section_key] = match.local_end_sec

        section_offset = section_offsets[scene.section_key]
        start_sec = section_offset + match.local_start_sec
        end_sec = section_offset + match.local_end_sec
        timeline_entries.append(
            {
                "scene_id": scene.scene_id,
                "scene_order": scene.scene_order,
                "section": scene.section,
                "section_order": scene.section_order,
                "section_key": scene.section_key,
                "timing": {
                    "start_sec": start_sec,
                    "end_sec": end_sec,
                    "duration_sec": end_sec - start_sec,
                    "local_start_sec": match.local_start_sec,
                    "local_end_sec": match.local_end_sec,
                },
                "audio": {"path": section.audio_path},
                "alignment": {
                    "path": section.alignment_path,
                    "match_method": match.match_method,
                    "matched_units": match.matched_units,
                },
                "dialogue": {
                    "text": scene.dialogue.text,
                    "paragraphs": scene.dialogue.paragraphs,
                },
                "visual": {
                    "type": scene.visual.type,
                    "prompt": scene.visual.prompt,
                    "data": scene.visual.data,
                },
                "warnings": [],
            }
        )
    _smooth_suspicious_same_section_gaps(timeline_entries)

    section_entries = []
    for section in sorted(sections, key=lambda item: (item.section_order, item.section_key)):
        start = section_offsets[section.section_key]
        end = start + section.alignment.total_duration_sec
        section_entries.append(
            {
                "section_key": section.section_key,
                "section": section.section,
                "section_order": section.section_order,
                "audio_path": section.audio_path,
                "alignment_path": section.alignment_path,
                "local_duration_sec": section.alignment.total_duration_sec,
                "global_start_sec": start,
                "global_end_sec": end,
            }
        )

    total_duration = section_entries[-1]["global_end_sec"] if section_entries else 0.0
    return {
        "metadata": {
            "schema_version": "1.0",
            "generated_by": "synccut build-timeline",
            "source_scenes": str(source_scenes_path),
            "total_scenes": len(scenes),
            "total_sections": len(sections),
            "total_duration_sec": total_duration,
        },
        "sections": section_entries,
        "timeline": timeline_entries,
        "warnings": [],
    }


def _section_offsets(sections: list[SectionAsset]) -> dict[str, float]:
    offsets: dict[str, float] = {}
    offset = 0.0
    for section in sorted(sections, key=lambda item: (item.section_order, item.section_key)):
        offsets[section.section_key] = offset
        offset += section.alignment.total_duration_sec
    return offsets


def _smooth_suspicious_same_section_gaps(timeline_entries: list[dict]) -> None:
    previous_entry_by_section: dict[str, dict] = {}
    for entry in timeline_entries:
        section_key = entry["section_key"]
        previous = previous_entry_by_section.get(section_key)
        if previous is not None:
            previous_timing = previous["timing"]
            timing = entry["timing"]
            gap = timing["start_sec"] - previous_timing["end_sec"]
            if gap > SUSPICIOUS_GAP_SEC:
                previous_timing["end_sec"] = timing["start_sec"]
                previous_timing["local_end_sec"] = timing["local_start_sec"]
                previous_timing["duration_sec"] = (
                    previous_timing["end_sec"] - previous_timing["start_sec"]
                )
        previous_entry_by_section[section_key] = entry


def _match_scene_to_alignment(
    scene: Scene, alignment: AlignmentSection, *, previous_local_end: float
) -> MatchResult:
    for matcher in (
        _match_paragraphs,
        _match_sentences,
        _match_paragraph_substring,
        _match_word_span,
    ):
        result = matcher(scene, alignment, previous_local_end=previous_local_end)
        if result is not None:
            return result

    excerpt = scene.dialogue.text[:80]
    raise SyncCutError(
        f"{scene.scene_id} in {scene.section_key}: could not match dialogue to alignment text: {excerpt}"
    )


def _match_paragraphs(
    scene: Scene, alignment: AlignmentSection, *, previous_local_end: float
) -> MatchResult | None:
    scene_paragraphs = [normalize_match_text(paragraph) for paragraph in scene.dialogue.paragraphs]
    candidates = [
        (index, paragraph)
        for index, paragraph in enumerate(alignment.paragraphs)
        if paragraph.start >= previous_local_end
    ]

    for start_position, (start_index, start_paragraph) in enumerate(candidates):
        if normalize_match_text(start_paragraph.text) != scene_paragraphs[0]:
            continue

        matched = [(start_index, start_paragraph)]
        candidate_position = start_position + 1
        for scene_paragraph in scene_paragraphs[1:]:
            while candidate_position < len(candidates):
                paragraph_index, paragraph = candidates[candidate_position]
                candidate_position += 1
                if normalize_match_text(paragraph.text) == scene_paragraph:
                    matched.append((paragraph_index, paragraph))
                    break
            else:
                matched = []
                break

        if matched:
            return MatchResult(
                local_start_sec=matched[0][1].start,
                local_end_sec=matched[-1][1].end,
                match_method="paragraph",
                matched_units=[f"paragraph:{index}" for index, _ in matched],
            )
    return None


def _match_paragraph_substring(
    scene: Scene, alignment: AlignmentSection, *, previous_local_end: float
) -> MatchResult | None:
    if len(scene.dialogue.paragraphs) != 1:
        return None

    scene_paragraph = normalize_match_text(scene.dialogue.paragraphs[0])
    for index, paragraph in enumerate(alignment.paragraphs):
        if paragraph.start < previous_local_end:
            continue
        if scene_paragraph in normalize_match_text(paragraph.text):
            return MatchResult(
                local_start_sec=paragraph.start,
                local_end_sec=paragraph.end,
                match_method="paragraph",
                matched_units=[f"paragraph:{index}"],
            )
    return None


def _match_sentences(
    scene: Scene, alignment: AlignmentSection, *, previous_local_end: float
) -> MatchResult | None:
    sentences = _alignment_sentences(alignment, previous_local_end=previous_local_end)
    target = normalize_match_text(scene.dialogue.text)
    if not target or not sentences:
        return None

    for start_index in range(len(sentences)):
        pieces: list[str] = []
        for end_index in range(start_index, len(sentences)):
            pieces.append(normalize_match_text(sentences[end_index][1].text))
            combined = normalize_match_text(" ".join(pieces))
            if combined == target:
                matched = sentences[start_index : end_index + 1]
                return MatchResult(
                    local_start_sec=matched[0][1].start,
                    local_end_sec=matched[-1][1].end,
                    match_method="sentence",
                    matched_units=[unit for unit, _ in matched],
                )
            if len(combined) > len(target) and not target.startswith(combined):
                break
    return None


def _match_word_span(
    scene: Scene, alignment: AlignmentSection, *, previous_local_end: float
) -> MatchResult | None:
    target_words = _normalized_words(scene.dialogue.text)
    words = [
        (index, word, normalize_match_word(word.text))
        for index, word in enumerate(alignment.words)
        if word.start >= previous_local_end
    ]
    words = [(index, word, normalized) for index, word, normalized in words if normalized]
    if not target_words or len(words) < len(target_words):
        return None

    matches: list[list[tuple[int, TimedText, str]]] = []
    span_length = len(target_words)
    for start_index in range(0, len(words) - span_length + 1):
        span = words[start_index : start_index + span_length]
        if [item[2] for item in span] == target_words:
            matches.append(span)

    if not matches:
        return None
    if len(matches) > 1:
        raise SyncCutError(
            f"{scene.scene_id} in {scene.section_key}: ambiguous word-span match for dialogue"
        )

    match = matches[0]
    return MatchResult(
        local_start_sec=match[0][1].start,
        local_end_sec=match[-1][1].end,
        match_method="word_span",
        matched_units=[f"word:{index}" for index, _, _ in match],
    )


def _alignment_sentences(
    alignment: AlignmentSection, *, previous_local_end: float
) -> list[tuple[str, TimedText]]:
    sentences: list[tuple[str, TimedText]] = []
    for paragraph_index, paragraph in enumerate(alignment.paragraphs):
        for sentence_index, sentence in enumerate(paragraph.sentences):
            if sentence.start >= previous_local_end:
                sentences.append((f"sentence:{paragraph_index}:{sentence_index}", sentence))
    return sentences


def _normalized_words(value: str) -> list[str]:
    words = [normalize_match_word(word) for word in normalize_match_text(value).split()]
    return [word for word in words if word]
