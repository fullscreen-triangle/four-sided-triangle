# Four Sided Triangle 

## 0. Query-Processor / Semantic-ATDB (stages 0–1)
Need | Model | Why it fits
Fast instruction-following + key-value JSON extraction | microsoft/Phi-3-mini-4k-instruct | 3.8 B params, 4k context, excellent on structured-output tasks. CPU-friendly so you can fork a private copy for each session without saturating GPUs. Hugging Face
Heavy-duty transformation with bigger context windows | mistralai/Mixtral-8x22B-Instruct-v0.1 | Sparsely-activated MoE gives GPT-4-class quality for ill-posed user queries; run behind the orchestrator’s timeout guard. Hugging Face
Robust NER / slot filling | allenai/scibert_scivocab_uncased | Biomedical + sport-science vocabulary; fine-tune if you need sprint-specific entity tags.
Semantic “throttle” detector / reranker | BAAI/bge-reranker-base | Cross-encoder that outputs a single relevance score; drop it into stage1_semantic_atdb to pick the top transformation strategy when multiple prompts compete. Hugging Face

## 2. Domain Knowledge Extraction 

Role | Model | Notes
Biomechanics & physiology core | stanford-crfm/BioMedLM-2.7B | Trained on PubMed; small enough for LoRA + PEFT on your 170-paper sprint corpus. Use as base for Scientific-Sprint-LLM. Hugging Face
General sports statistics & reasoning | mistralai/Mixtral-8x22B-Instruct (shared with stage 0) | Keeps Olympic data in-house; gate behind orchestrator’s GPU quota.
Lightweight fallback | microsoft/Phi-3-mini-4k-instruct (shared) | Good in low-latency paths or on CPU nodes.

## 3. Parallel Reasoning 
Need | Model | Why
Math & gradient-style reasoning | Qwen/Qwen-2-7B-Instruct or deepseek-ai/deepseek-math-7b-rl | Both handle equation manipulation & symbolic maths, ideal for your multi-objective solver.
Fast internal CoT agent | Phi-3 again, with “let’s think” prompt trick – latency <900 ms on A100. | 

## 4.  Solution Generation
`candidates = orchestrator.sample(
    models=["phi3", "mixtral", "biomedlm"], 
    temperature=[0.7, 0.3, 0.9])
]`


## 5. Response Scoring 
Model | Why it works
OpenAssistant/reward-model-deberta-v3-large-v2 | Trained on human-preference pairs; outputs a scalar reward you can treat as P(R│Q) in your Bayesian formula. Hugging Face
Dataset for custom RM | datasets/openai/summarize_from_feedback



## 6. Ensemble Diversification
Model | Use
BAAI/bge-reranker-v2-m3 | Cross-encoder to compute pairwise diversity + quality scores before running your determinantal point process. Hugging Face



## 7. Threshold Verification 
Model | Slot
facebook/bart-large-mnli (or DeBERTa-MNLI) | Quick entailment test: does candidate answer logically follow from domain facts in working memory?

Wiring into the new backend
Model gateway – expose each HF checkpoint through a Text-Generation-Inference (TGI) container; the orchestrator’s interfaces.py just hits a REST endpoint with retry logic.

LoRA layers – save them in ./sprint-llm-distilled-* and merge on the fly (peft.auto_merge) so the orchestrator can hot-swap domain heads.

Resource tags – annotate each model in pipeline/stages.json with {"gpu":1,"vram":20} etc.; the orchestrator’s scheduler can then place heavy models on big boxes and keep Phi-3 on CPU shards.

Quality feedback loop – pipe the reward-model score plus your Pareto metrics back into the Process Monitor; bad runs automatically trigger a refined prompt template variant.