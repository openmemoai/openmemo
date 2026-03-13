"""
Memory Consolidation Engine — Autonomous Memory Evolution.

Transforms raw memories into patterns, rules, and playbooks through:
  1. Duplicate detection (content similarity)
  2. Memory clustering (keyword-based grouping)
  3. Pattern extraction (cluster → pattern)
  4. Playbook generation (patterns → operational playbook)
  5. Memory decay (remove noise)

Supports optional LLM callbacks for smarter extraction.
"""

import re
import time
import uuid
import logging
from typing import List, Dict, Callable, Optional
from dataclasses import dataclass, field

logger = logging.getLogger("openmemo")

STOP_WORDS = {
    "the", "a", "an", "is", "are", "was", "were", "in", "on", "at", "to",
    "for", "of", "and", "or", "but", "not", "with", "this", "that", "it",
    "be", "have", "do", "what", "how", "when", "where", "who", "which",
    "my", "your", "i", "we", "they", "he", "she", "its", "our", "their",
    "can", "will", "should", "would", "could", "may", "been", "being",
    "had", "has", "does", "did", "about", "after", "before", "from",
    "into", "through", "then", "than", "so", "if", "as", "by", "up",
}


@dataclass
class ConsolidationConfig:
    duplicate_threshold: float = 0.75
    cluster_min_size: int = 3
    decay_days: int = 60
    decay_confidence_threshold: float = 0.3
    promotion_confidence: float = 0.9
    promotion_cluster_size: int = 3
    max_scan_cells: int = 100000


@dataclass
class ConsolidationResult:
    duplicates_merged: int = 0
    clusters_found: int = 0
    patterns_extracted: int = 0
    playbooks_generated: int = 0
    memories_decayed: int = 0
    memories_removed: int = 0
    promoted: int = 0
    duration_ms: float = 0.0

    def to_dict(self) -> dict:
        return {
            "duplicates_merged": self.duplicates_merged,
            "clusters_found": self.clusters_found,
            "patterns_extracted": self.patterns_extracted,
            "playbooks_generated": self.playbooks_generated,
            "memories_decayed": self.memories_decayed,
            "memories_removed": self.memories_removed,
            "promoted": self.promoted,
            "duration_ms": round(self.duration_ms, 1),
        }


def _extract_keywords(text: str) -> set:
    words = set(re.findall(r'\w{3,}', text.lower()))
    return words - STOP_WORDS


def _content_similarity(text_a: str, text_b: str) -> float:
    kw_a = _extract_keywords(text_a)
    kw_b = _extract_keywords(text_b)
    if not kw_a or not kw_b:
        return 0.0
    intersection = kw_a & kw_b
    union = kw_a | kw_b
    return len(intersection) / len(union) if union else 0.0


class ConsolidationEngine:
    def __init__(self, store=None, config: ConsolidationConfig = None,
                 embed_fn: Callable = None,
                 llm_fn: Optional[Callable] = None):
        self.store = store
        self.config = config or ConsolidationConfig()
        self.embed_fn = embed_fn
        self.llm_fn = llm_fn
        self._embedding_cache: Dict[str, List[float]] = {}

    def _get_embedding(self, text: str) -> Optional[List[float]]:
        if not self.embed_fn:
            return None
        if text not in self._embedding_cache:
            try:
                vec = self.embed_fn(text)
                if vec is not None:
                    self._embedding_cache[text] = vec
            except Exception:
                return None
        return self._embedding_cache.get(text)

    def _semantic_similarity(self, text_a: str, text_b: str) -> float:
        vec_a = self._get_embedding(text_a)
        vec_b = self._get_embedding(text_b)
        if vec_a is not None and vec_b is not None:
            dot = sum(a * b for a, b in zip(vec_a, vec_b))
            norm_a = sum(a * a for a in vec_a) ** 0.5
            norm_b = sum(b * b for b in vec_b) ** 0.5
            if norm_a > 0 and norm_b > 0:
                return dot / (norm_a * norm_b)
        return _content_similarity(text_a, text_b)

    def run(self, agent_id: str = None, scene: str = None) -> ConsolidationResult:
        start = time.time()
        result = ConsolidationResult()

        cells = self.store.list_cells(
            limit=self.config.max_scan_cells,
            agent_id=agent_id or None,
            scene=scene or None,
        )

        if not cells:
            result.duration_ms = (time.time() - start) * 1000
            return result

        clusters = self._cluster(cells)
        result.clusters_found = len(clusters)

        patterns = self._extract_patterns(clusters)
        result.patterns_extracted = len(patterns)

        playbooks = self._generate_playbooks(patterns, clusters)
        result.playbooks_generated = len(playbooks)

        cells, merged = self._deduplicate(cells)
        result.duplicates_merged = merged

        promoted = self._promote_memories(cells)
        result.promoted = promoted

        decayed, removed = self._decay_memories(cells)
        result.memories_decayed = decayed
        result.memories_removed = removed

        result.duration_ms = (time.time() - start) * 1000
        logger.info("[openmemo:consolidation] completed in %.0fms: %s",
                    result.duration_ms, result.to_dict())
        return result

    def _deduplicate(self, cells: List[dict]) -> tuple:
        if len(cells) < 2:
            return cells, 0

        merged = 0
        to_remove = set()

        for i in range(len(cells)):
            if cells[i]["id"] in to_remove:
                continue
            for j in range(i + 1, len(cells)):
                if cells[j]["id"] in to_remove:
                    continue

                sim = self._semantic_similarity(
                    cells[i].get("content", ""),
                    cells[j].get("content", ""),
                )

                if sim >= self.config.duplicate_threshold:
                    keep, drop = self._pick_stronger(cells[i], cells[j])
                    to_remove.add(drop["id"])
                    merged += 1

                    keep_meta = keep.get("metadata", {})
                    if isinstance(keep_meta, str):
                        import json
                        try:
                            keep_meta = json.loads(keep_meta)
                        except:
                            keep_meta = {}
                    drop_meta = drop.get("metadata", {})
                    if isinstance(drop_meta, str):
                        import json
                        try:
                            drop_meta = json.loads(drop_meta)
                        except:
                            drop_meta = {}

                    keep_conf = keep_meta.get("confidence", 0.5)
                    drop_conf = drop_meta.get("confidence", 0.5)
                    new_conf = max(keep_conf, drop_conf)
                    keep_meta["confidence"] = new_conf
                    keep_meta["merged_count"] = keep_meta.get("merged_count", 1) + 1
                    keep["metadata"] = keep_meta
                    keep["access_count"] = keep.get("access_count", 0) + drop.get("access_count", 0)
                    self.store.put_cell(keep)
                    self.store.delete_cell(drop["id"])

        remaining = [c for c in cells if c["id"] not in to_remove]
        return remaining, merged

    def _pick_stronger(self, cell_a: dict, cell_b: dict) -> tuple:
        meta_a = cell_a.get("metadata", {})
        meta_b = cell_b.get("metadata", {})
        if isinstance(meta_a, str):
            import json
            try: meta_a = json.loads(meta_a)
            except: meta_a = {}
        if isinstance(meta_b, str):
            import json
            try: meta_b = json.loads(meta_b)
            except: meta_b = {}

        score_a = meta_a.get("confidence", 0.5) + cell_a.get("access_count", 0) * 0.1
        score_b = meta_b.get("confidence", 0.5) + cell_b.get("access_count", 0) * 0.1

        if len(cell_a.get("content", "")) > len(cell_b.get("content", "")):
            score_a += 0.1

        if score_a >= score_b:
            return cell_a, cell_b
        return cell_b, cell_a

    def _cluster(self, cells: List[dict]) -> List[List[dict]]:
        if len(cells) < self.config.cluster_min_size:
            return []

        cell_keywords = []
        for c in cells:
            kw = _extract_keywords(c.get("content", ""))
            cell_keywords.append((c, kw))

        assigned = set()
        clusters = []

        cluster_threshold = 0.25

        for i, (cell_i, kw_i) in enumerate(cell_keywords):
            if cell_i["id"] in assigned:
                continue

            cluster = [cell_i]
            assigned.add(cell_i["id"])

            for j, (cell_j, kw_j) in enumerate(cell_keywords):
                if i == j or cell_j["id"] in assigned:
                    continue

                sim = self._semantic_similarity(
                    cell_i.get("content", ""),
                    cell_j.get("content", ""),
                )

                if sim >= cluster_threshold:
                    cluster.append(cell_j)
                    assigned.add(cell_j["id"])

            if len(cluster) >= self.config.cluster_min_size:
                clusters.append(cluster)

        return clusters

    def _extract_patterns(self, clusters: List[List[dict]]) -> List[dict]:
        patterns = []

        for cluster in clusters:
            contents = [c.get("content", "") for c in cluster]

            if self.llm_fn:
                try:
                    pattern = self.llm_fn("extract_pattern", contents)
                    if isinstance(pattern, dict) and pattern.get("pattern"):
                        pattern_cell = self._store_pattern(
                            pattern["pattern"],
                            confidence=pattern.get("confidence", 0.8),
                            source_ids=[c["id"] for c in cluster],
                            scene=cluster[0].get("scene", ""),
                            agent_id=cluster[0].get("agent_id", ""),
                        )
                        patterns.append(pattern_cell)
                        continue
                except Exception:
                    pass

            pattern_text = self._rule_based_pattern(contents)
            if pattern_text:
                pattern_cell = self._store_pattern(
                    pattern_text,
                    confidence=min(0.9, 0.5 + len(cluster) * 0.05),
                    source_ids=[c["id"] for c in cluster],
                    scene=cluster[0].get("scene", ""),
                    agent_id=cluster[0].get("agent_id", ""),
                )
                patterns.append(pattern_cell)

        return patterns

    def _rule_based_pattern(self, contents: List[str]) -> str:
        all_keywords = {}
        for content in contents:
            for kw in _extract_keywords(content):
                all_keywords[kw] = all_keywords.get(kw, 0) + 1

        common = sorted(
            [(kw, count) for kw, count in all_keywords.items()
             if count >= max(2, len(contents) // 2)],
            key=lambda x: x[1], reverse=True,
        )

        if not common:
            return ""

        theme_words = [kw for kw, _ in common[:5]]
        theme = " ".join(theme_words)

        pattern = f"Pattern detected across {len(contents)} memories: {theme}. "
        pattern += f"Common themes: {', '.join(theme_words[:8])}."

        return pattern

    def _store_pattern(self, content: str, confidence: float,
                       source_ids: List[str], scene: str = "",
                       agent_id: str = "") -> dict:
        cell_id = str(uuid.uuid4())
        cell = {
            "id": cell_id,
            "note_id": cell_id,
            "content": content,
            "cell_type": "pattern",
            "facts": [],
            "stage": "mastery",
            "importance": confidence,
            "access_count": 0,
            "last_accessed": time.time(),
            "created_at": time.time(),
            "agent_id": agent_id,
            "scene": scene,
            "scope": "shared",
            "conversation_id": "",
            "connections": [],
            "metadata": {
                "confidence": confidence,
                "source_ids": source_ids,
                "generated_by": "consolidation",
            },
        }
        self.store.put_cell(cell)

        if hasattr(self.store, 'put_edge'):
            for src_id in source_ids[:10]:
                self.store.put_edge({
                    "edge_id": str(uuid.uuid4())[:12],
                    "memory_a": cell_id,
                    "memory_b": src_id,
                    "relation_type": "extends",
                    "confidence": confidence,
                    "created_at": time.time(),
                    "metadata": {},
                })

        return cell

    def _generate_playbooks(self, patterns: List[dict],
                            clusters: List[List[dict]]) -> List[dict]:
        playbooks = []

        if not patterns:
            return playbooks

        if self.llm_fn:
            for pattern in patterns:
                try:
                    result = self.llm_fn("generate_playbook", pattern.get("content", ""))
                    if isinstance(result, dict) and result.get("playbook"):
                        pb = self._store_playbook(
                            result["playbook"],
                            confidence=result.get("confidence", 0.85),
                            pattern_id=pattern["id"],
                            scene=pattern.get("scene", ""),
                            agent_id=pattern.get("agent_id", ""),
                        )
                        playbooks.append(pb)
                        continue
                except Exception:
                    pass

            return playbooks

        for i, pattern in enumerate(patterns):
            if i >= len(clusters):
                continue
            cluster = clusters[i]
            playbook_text = self._rule_based_playbook(
                pattern.get("content", ""),
                [c.get("content", "") for c in cluster],
            )
            if playbook_text:
                pb = self._store_playbook(
                    playbook_text,
                    confidence=min(0.9, 0.6 + len(cluster) * 0.03),
                    pattern_id=pattern["id"],
                    scene=pattern.get("scene", ""),
                    agent_id=pattern.get("agent_id", ""),
                )
                playbooks.append(pb)

        return playbooks

    def _rule_based_playbook(self, pattern: str, contents: List[str]) -> str:
        if len(contents) < 2:
            return ""

        steps = []
        seen = set()
        for content in contents:
            short = content.strip()[:100]
            key = short.lower()
            if key not in seen:
                seen.add(key)
                steps.append(short)

        if not steps:
            return ""

        lines = [f"Playbook (auto-generated from {len(contents)} memories):"]
        lines.append(f"Context: {pattern[:150]}")
        lines.append("Steps:")
        for i, step in enumerate(steps[:10], 1):
            lines.append(f"  {i}. {step}")

        return "\n".join(lines)

    def _store_playbook(self, content: str, confidence: float,
                        pattern_id: str, scene: str = "",
                        agent_id: str = "") -> dict:
        cell_id = str(uuid.uuid4())
        cell = {
            "id": cell_id,
            "note_id": cell_id,
            "content": content,
            "cell_type": "playbook",
            "facts": [],
            "stage": "mastery",
            "importance": confidence,
            "access_count": 0,
            "last_accessed": time.time(),
            "created_at": time.time(),
            "agent_id": agent_id,
            "scene": scene,
            "scope": "shared",
            "conversation_id": "",
            "connections": [],
            "metadata": {
                "confidence": confidence,
                "pattern_id": pattern_id,
                "generated_by": "consolidation",
            },
        }
        self.store.put_cell(cell)

        if hasattr(self.store, 'put_edge'):
            self.store.put_edge({
                "edge_id": str(uuid.uuid4())[:12],
                "memory_a": cell_id,
                "memory_b": pattern_id,
                "relation_type": "extends",
                "confidence": confidence,
                "created_at": time.time(),
                "metadata": {},
            })

        return cell

    def _promote_memories(self, cells: List[dict]) -> int:
        promoted = 0
        for c in cells:
            if c.get("cell_type") in ("pattern", "playbook"):
                continue

            meta = c.get("metadata", {})
            if isinstance(meta, str):
                import json
                try:
                    meta = json.loads(meta)
                except:
                    meta = {}

            confidence = meta.get("confidence", 0.5)
            access_count = c.get("access_count", 0)

            if (confidence >= self.config.promotion_confidence and
                    access_count >= self.config.promotion_cluster_size):
                c["cell_type"] = "pattern"
                c["stage"] = "mastery"
                c["importance"] = min(1.0, c.get("importance", 0.5) * 1.2)
                meta["promoted_to_pattern"] = True
                c["metadata"] = meta
                self.store.put_cell(c)
                promoted += 1

        return promoted

    def _decay_memories(self, cells: List[dict]) -> tuple:
        now = time.time()
        decayed = 0
        removed = 0

        for c in cells:
            if c.get("cell_type") in ("pattern", "playbook", "rules"):
                continue

            last_access = c.get("last_accessed", c.get("created_at", now))
            age_days = (now - last_access) / 86400

            meta = c.get("metadata", {})
            if isinstance(meta, str):
                import json
                try:
                    meta = json.loads(meta)
                except:
                    meta = {}

            confidence = meta.get("confidence", 0.5)

            if age_days > self.config.decay_days and confidence < self.config.decay_confidence_threshold:
                self.store.delete_cell(c["id"])
                removed += 1
            elif age_days > self.config.decay_days // 2:
                c["importance"] = max(0.1, c.get("importance", 0.5) * 0.9)
                c["metadata"] = meta
                self.store.put_cell(c)
                decayed += 1

        return decayed, removed

    def detect_duplicates(self, cells: List[dict] = None,
                          agent_id: str = None) -> List[dict]:
        if cells is None:
            cells = self.store.list_cells(limit=1000, agent_id=agent_id or None)

        duplicates = []
        for i in range(len(cells)):
            for j in range(i + 1, len(cells)):
                sim = self._semantic_similarity(
                    cells[i].get("content", ""),
                    cells[j].get("content", ""),
                )
                if sim >= self.config.duplicate_threshold:
                    duplicates.append({
                        "cell_a": cells[i]["id"],
                        "cell_b": cells[j]["id"],
                        "content_a": cells[i].get("content", "")[:100],
                        "content_b": cells[j].get("content", "")[:100],
                        "similarity": round(sim, 3),
                    })

        return duplicates

    def get_patterns(self, agent_id: str = None, scene: str = None) -> List[dict]:
        cells = self.store.list_cells(limit=1000, agent_id=agent_id or None,
                                      scene=scene or None)
        patterns = [c for c in cells if c.get("cell_type") in ("pattern", "playbook", "rules")]
        return patterns
