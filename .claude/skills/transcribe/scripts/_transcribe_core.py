"""
Core transcription + speaker diarization logic.
Called by transcribe.py — do not run directly.

Outputs a speaker-labeled transcript to the given output path.
Format:
    DATE: M/D

    [Teacher]: ...
    [Student]: ...
    [Teacher]: ...
    ...

The more-talkative speaker is assigned "Teacher" (safe heuristic for 1-on-1 ESL).
"""

import sys
import time
from collections import defaultdict
from itertools import groupby
from pathlib import Path


def transcribe_with_diarization(audio_path: str, output_path: str, lesson_date: str, model_size: str = "base"):
    from faster_whisper import WhisperModel

    print("⏳ 加载 Whisper 模型...")
    t0 = time.time()
    model = WhisperModel(model_size, device="cpu", compute_type="float32")
    print(f"✓ 模型加载完成 ({time.time() - t0:.2f}秒)")

    print("🎙️ 开始转录（保留时间戳）...")
    t1 = time.time()
    segments_gen, info = model.transcribe(
        audio_path,
        condition_on_previous_text=False,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
        word_timestamps=False,
    )
    segments_list = list(segments_gen)
    print(f"✓ 转录完成! ({time.time() - t1:.1f}秒)")
    print(f"检测到的语言: {info.language} (概率: {info.language_probability:.2f})")

    # --- Speaker diarization via resemblyzer (no account needed) ---
    print("🗣️ 开始说话人识别 (resemblyzer)...")
    t2 = time.time()
    try:
        import numpy as np
        from resemblyzer import VoiceEncoder, preprocess_wav
        from sklearn.cluster import KMeans
        from pathlib import Path as _Path

        encoder = VoiceEncoder("cpu")
        wav = preprocess_wav(_Path(audio_path))

        # Build one embedding per Whisper segment using its audio slice
        sample_rate = 16000
        embeddings = []
        valid_indices = []
        for i, seg in enumerate(segments_list):
            start_sample = int(seg.start * sample_rate)
            end_sample = int(seg.end * sample_rate)
            chunk = wav[start_sample:end_sample]
            if len(chunk) < sample_rate * 0.5:   # skip chunks < 0.5s (too short)
                embeddings.append(None)
            else:
                embeddings.append(encoder.embed_utterance(chunk))
                valid_indices.append(i)

        # K-means with k=2 (always exactly 2 speakers in 1-on-1 ESL)
        valid_embeddings = np.array([embeddings[i] for i in valid_indices])
        kmeans = KMeans(n_clusters=2, random_state=0, n_init=10).fit(valid_embeddings)

        # Assign labels; short/silent segments inherit nearest neighbour label
        label_map = {}
        for idx, cluster in zip(valid_indices, kmeans.labels_):
            label_map[idx] = cluster
        # Fill gaps with the previous label (or 0 as default)
        last = 0
        for i in range(len(segments_list)):
            if i not in label_map:
                label_map[i] = last
            else:
                last = label_map[i]

        # Heuristic: speaker with more total speaking time → Teacher
        time_by_cluster = defaultdict(float)
        for i, seg in enumerate(segments_list):
            time_by_cluster[label_map[i]] += seg.end - seg.start
        teacher_cluster = max(time_by_cluster, key=lambda c: time_by_cluster[c])

        def role_for(cluster_id):
            return "Teacher" if cluster_id == teacher_cluster else "Student"

        labeled = [(role_for(label_map[i]), seg.text.strip())
                   for i, seg in enumerate(segments_list)]

        print(f"✓ 说话人识别完成 ({time.time() - t2:.1f}秒)")

    except ImportError:
        print("⚠️  resemblyzer or sklearn not installed — falling back to flat transcript")
        print("    Run: pip install resemblyzer scikit-learn")
        transcript = " ".join(seg.text.strip() for seg in segments_list)
        Path(output_path).write_text(f"DATE: {lesson_date}\n\n{transcript}", encoding="utf-8")
        return
    except Exception as e:
        print(f"⚠️  Diarization failed ({e}) — falling back to flat transcript")
        transcript = " ".join(seg.text.strip() for seg in segments_list)
        Path(output_path).write_text(f"DATE: {lesson_date}\n\n{transcript}", encoding="utf-8")
        return

    # --- Collapse consecutive same-speaker segments into turns ---
    lines = []
    for role, group in groupby(labeled, key=lambda x: x[0]):
        text = " ".join(t for _, t in group).strip()
        if text:
            lines.append(f"[{role}]: {text}")

    transcript_content = "\n".join(lines)
    char_count = len(transcript_content)

    Path(output_path).write_text(
        f"DATE: {lesson_date}\n\n{transcript_content}", encoding="utf-8"
    )
    print(f"✓ 输出文件: {output_path}")
    print(f"文件大小: {char_count} 字符")
    print(f"说话人: {{'Teacher': teacher_cluster, 'Student': 1 - teacher_cluster}}")


if __name__ == "__main__":
    # Called as: python3 _transcribe_core.py <audio> <output> <date> <model>
    audio_path, output_path, lesson_date, model_size = sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4]
    transcribe_with_diarization(audio_path, output_path, lesson_date, model_size)
