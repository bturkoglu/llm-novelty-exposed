"""Component census of popular open-weight text-generation models on Hugging Face.
Public API + public config.json only. Gated repos are recorded as gated (not bypassed)."""
import json, time, sys
from pathlib import Path
import httpx, certifi
OUT = Path(__file__).parent / "hf_census.json"
H = {"User-Agent": "ResearchOS/0.1 (academic study of open model configurations)"}
c = httpx.Client(headers=H, timeout=30, verify=certifi.where(), follow_redirects=True)
def api(params):
    r = c.get("https://huggingface.co/api/models", params=params); r.raise_for_status(); return r.json()
seen, models = set(), []
for sort in ("downloads", "likes", "trendingScore"):
    for m in api({"pipeline_tag": "text-generation", "sort": sort, "direction": -1, "limit": 400, "full": "true", "cardData": "true"}):
        if m["id"] in seen: continue
        seen.add(m["id"]); m["_list"] = sort; models.append(m)
print("listed", len(models), flush=True)
KEYS = ["architectures", "model_type", "num_hidden_layers", "hidden_size", "intermediate_size", "num_attention_heads",
        "num_key_value_heads", "head_dim", "vocab_size", "max_position_embeddings", "rope_theta", "rope_scaling",
        "hidden_act", "hidden_activation", "tie_word_embeddings", "rms_norm_eps", "layer_norm_eps", "layer_norm_epsilon",
        "num_local_experts", "num_experts", "n_routed_experts", "num_experts_per_tok", "sliding_window",
        "attention_bias", "kv_lora_rank", "q_lora_rank", "layer_types", "torch_dtype", "use_sliding_window", "text_config"]
rows = []
for i, m in enumerate(models):
    tags = m.get("tags") or []; card = m.get("cardData") or {}
    row = {"id": m["id"], "list": m["_list"], "downloads": m.get("downloads"), "likes": m.get("likes"),
           "created_at": m.get("createdAt"), "gated": m.get("gated"), "library": m.get("library_name"),
           "base_model": card.get("base_model"), "base_model_relation": card.get("base_model_relation"),
           "is_quantized": any(t in tags for t in ("gguf", "awq", "gptq", "exl2", "4-bit", "8-bit", "mlx")) or any(s in m["id"].lower() for s in ("gguf", "awq", "gptq", "-bnb", "mlx", "fp8", "int4")),
           "license": card.get("license"), "arxiv": [t[6:] for t in tags if t.startswith("arxiv:")], "config": None, "config_status": None}
    if m.get("gated"):
        row["config_status"] = "gated_not_fetched"
    else:
        try:
            r = c.get(f"https://huggingface.co/{m['id']}/resolve/main/config.json")
            if r.status_code == 200:
                cfg = r.json(); tc = cfg.get("text_config") if isinstance(cfg.get("text_config"), dict) else {}
                row["config"] = {k: (cfg.get(k) if cfg.get(k) is not None else tc.get(k)) for k in KEYS if k != "text_config"}
                row["config"]["has_text_config"] = bool(tc)
                row["config_status"] = "ok"
            else: row["config_status"] = f"http_{r.status_code}"
        except Exception as e: row["config_status"] = "error:" + type(e).__name__
        time.sleep(0.4)
    rows.append(row)
    if i % 100 == 0: print(i, flush=True)
json.dump(rows, open(OUT, "w"), indent=1)
import collections
print(collections.Counter(r["config_status"] for r in rows))
