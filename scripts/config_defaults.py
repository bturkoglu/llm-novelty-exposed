"""Config defaults per model (HF transformers 0d7a621): class attributes and __init__ defaults, via AST (no import)."""
import ast, json, sys
from pathlib import Path
ROOT = Path(sys.argv[1]) / "src/transformers/models"
def defaults(m):
    t = ast.parse((ROOT / m / f"configuration_{m}.py").read_text()); d = {}
    for c in [n for n in t.body if isinstance(n, ast.ClassDef)]:
        for s in c.body:
            if isinstance(s, ast.AnnAssign) and isinstance(s.target, ast.Name) and s.value is not None:
                try: d[s.target.id] = ast.literal_eval(s.value)
                except Exception: d[s.target.id] = ast.unparse(s.value)
            if isinstance(s, ast.FunctionDef) and s.name == "__init__":
                a = s.args; pos = a.args[len(a.args) - len(a.defaults):]
                for arg, v in list(zip(pos, a.defaults)) + list(zip(a.kwonlyargs, a.kw_defaults)):
                    if v is None: continue
                    try: d.setdefault(arg.arg, ast.literal_eval(v))
                    except Exception: d.setdefault(arg.arg, ast.unparse(v))
    return d
M = sys.argv[2:]; D = {m: defaults(m) for m in M}
keys = ["hidden_act", "rope_theta", "rope_parameters", "default_theta", "vocab_size", "hidden_size", "intermediate_size", "num_hidden_layers",
        "num_attention_heads", "num_key_value_heads", "head_dim", "max_position_embeddings", "rms_norm_eps", "tie_word_embeddings",
        "attention_bias", "mlp_bias", "sliding_window", "use_sliding_window", "attention_dropout"]
json.dump(D, open("config_defaults.json", "w"), indent=1, default=str)
print("key".ljust(24), *[m.ljust(14) for m in M])
for k in keys:
    if any(k in D[m] for m in M): print(k.ljust(24), *[str(D[m].get(k, "-"))[:14].ljust(14) for m in M])
