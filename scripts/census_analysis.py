import json, collections as C
rows = json.load(open('hf_census.json'))
def sig(c):
    nh, kv = c.get('num_attention_heads'), c.get('num_key_value_heads')
    act = (c.get('hidden_act') or c.get('hidden_activation') or '?')
    norm = 'RMSNorm' if c.get('rms_norm_eps') else ('LayerNorm' if (c.get('layer_norm_eps') or c.get('layer_norm_epsilon')) else '?')
    if c.get('kv_lora_rank'): att = 'MLA'
    elif nh and kv and kv == 1: att = 'MQA'
    elif nh and kv and kv < nh: att = 'GQA'
    elif nh: att = 'MHA'
    else: att = '?'
    pos = 'RoPE' if (c.get('rope_theta') or c.get('rope_scaling')) else '?'
    moe = 'MoE' if any(c.get(k) for k in ('num_local_experts', 'num_experts', 'n_routed_experts')) else 'dense'
    lt = c.get('layer_types') or []
    kinds = sorted(set(lt)) if isinstance(lt, list) else []
    hyb = 'hybrid:' + '+'.join(kinds) if any(('linear' in k or 'mamba' in k or 'conv' in k) for k in kinds) else ('swa-mix' if any('sliding' in k for k in kinds) or c.get('sliding_window') else 'full-attn')
    a = 'gated-SiLU' if act in ('silu', 'swish') else ('gated-GELU' if 'gelu' in act and act != 'gelu' else act)
    return (norm, a, pos, att, moe, hyb)
orig = [r for r in rows if r['config'] and not r['is_quantized'] and r['base_model_relation'] not in ('quantized', 'finetune', 'merge') and not r['base_model']]
print('originals with config:', len(orig))
cls = C.Counter((r['config'].get('architectures') or ['?'])[0] for r in orig)
sigs = C.Counter(sig(r['config']) for r in orig)
print('distinct architecture class names:', len(cls), ' distinct component signatures:', len(sigs))
core = ('RMSNorm', 'gated-SiLU', 'RoPE')
n_core = sum(1 for r in orig if sig(r['config'])[:3] == core)
print(f'share with RMSNorm+SwiGLU+RoPE core: {n_core}/{len(orig)} = {n_core/len(orig):.0%}')
print('attention:', C.Counter(sig(r['config'])[3] for r in orig).most_common())
print('ffn:', C.Counter(sig(r['config'])[4] for r in orig).most_common())
print('mixing:', C.Counter(sig(r['config'])[5].split(':')[0] for r in orig).most_common())
print('\ntop signatures and the class names that share them:')
by = C.defaultdict(C.Counter)
for r in orig: by[sig(r['config'])][(r['config'].get('architectures') or ['?'])[0]] += 1
for s, n in sigs.most_common(12):
    print(f'{n:>4}  {s}\n      names: {dict(by[s].most_common(10))}')
yr = C.Counter((r['created_at'] or '')[:4] for r in orig)
print('\ncreated year:', sorted(yr.items()))
json.dump([{'id': r['id'], 'created': r['created_at'], 'class': (r['config'].get('architectures') or ['?'])[0], 'sig': sig(r['config']), 'downloads': r['downloads']} for r in orig], open('census_originals.json', 'w'), indent=1)
