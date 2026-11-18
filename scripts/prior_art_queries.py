LLM = '("large language model" OR "large language models" OR LLM OR LLMs OR "foundation model" OR "foundation models" OR transformer OR "language model" OR "language models" OR "deep learning")'
OA_Q = {
  "Q1_novelty_critique": LLM + ' AND (hype OR "novelty claims" OR "incremental" OR "troubling trends" OR "reality check" OR "exposed" OR "illusion of progress" OR "marketing")',
  "Q2_arch_variants": '(transformer OR "language model") AND ("architectural modifications" OR "architecture modifications" OR "architectural variants" OR "do not transfer" OR "architectural convergence" OR "same architecture")',
  "Q3_hf_lineage": '("Hugging Face" OR HuggingFace) AND (lineage OR "family tree" OR "derivative models" OR "supply chain" OR "model ecosystem" OR "fine-tuned derivatives" OR merging)',
  "Q4_leaderboard": LLM + ' AND (leaderboard OR "benchmark contamination" OR "data contamination" OR "benchmark saturation") AND (illusion OR gaming OR overfitting OR critique OR inflated)',
  "Q5_openwashing": LLM + ' AND ("open-washing" OR openwashing OR "transparency index" OR "technical report" OR "release practices" OR "documentation practices")',
  "Q6_ml_rigor": '("machine learning" OR "deep learning" OR "neural network") AND ("troubling trends" OR "reality check" OR "progress is illusory" OR "are we really making much progress" OR "worrying analysis" OR "illusion of progress")',
  "Q7_metaphor_ai": '(anthropomorphism OR "misleading terminology" OR "reasoning claims" OR "AI hype") AND ' + LLM,
}
S2_Q = {
  "S1": '("large language models" | LLM) + (hype | novelty | "reality check" | "troubling trends" | exposed)',
  "S2": 'transformer + ("architectural modifications" | "do not transfer" | "architectural variants")',
  "S3": '"Hugging Face" + (lineage | "family tree" | "supply chain" | derivatives)',
  "S4": '("language models" | LLM) + (leaderboard | contamination) + (illusion | gaming | inflated)',
  "S5": '("language models" | LLM) + ("open-washing" | openwashing | "transparency index")',
}
AX_Q = {
  "A1": 'ti:"reality check" AND (abs:"language model" OR abs:transformer)',
  "A2": 'ti:exposed AND (abs:"language model" OR abs:LLM)',
  "A3": 'ti:hype AND (abs:"language model" OR abs:LLM)',
  "A4": 'abs:"Hugging Face" AND (abs:lineage OR abs:"family tree" OR abs:"supply chain")',
  "A5": 'ti:illusion AND (ti:leaderboard OR ti:progress) AND abs:"language model"',
  "A6": 'abs:"architectural" AND abs:"open-weight" AND abs:"language models" AND (abs:comparison OR abs:convergence)',
}
