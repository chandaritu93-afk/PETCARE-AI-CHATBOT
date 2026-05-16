import os
from ragas import evaluate
from ragas.metrics import faithfulness, answer_relevancy, context_precision
from datasets import Dataset
from langchain_ollama import OllamaLLM, OllamaEmbeddings
from ragas.run_config import RunConfig

# 1. Light Model select karein
selected_model = "phi3" 

# Timeout ko 10 mins (600s) kar diya hai
llm = OllamaLLM(model=selected_model, timeout=600) 
embeddings = OllamaEmbeddings(model=selected_model)

# 2. RUN CONFIG: Ye sabse important part hai
# max_workers=1 ka matlab hai ki system par load nahi padega, ek-ek karke process hoga
run_config = RunConfig(max_workers=1, timeout=600)

print(f"🚀 Optimized Evaluation start ho raha hai (Model: {selected_model})...\n")

data_dict = {
    "question": [
        "What are symptoms of dog fever?",
        "What is rabies in pets?",
        "What vaccines are required for cats?"
    ],
    "answer": [
        "Dogs with fever show lethargy, loss of appetite, and high temperature.",
        "Rabies is a viral disease affecting the nervous system.",
        "Cats need vaccines like rabies and FVRCP."
    ],
    "contexts": [
        ["Dog fever symptoms include lethargy and high temperature"],
        ["Rabies affects nervous system in animals"],
        ["Cats vaccines include rabies and FVRCP"]
    ],
    "ground_truth": [
        "Dogs with fever show lethargy, loss of appetite, and high temperature.",
        "Rabies is a viral disease affecting the nervous system of animals.",
        "Cats require vaccines like rabies and FVRCP."
    ]
}

dataset = Dataset.from_dict(data_dict)

print("⏳ Ragas score nikal raha hai (One-by-one mode)... 5-8 minutes lag sakte hain, band mat karna.\n")

try:
    # 3. Evaluate with RunConfig
    result = evaluate(
        dataset,
        metrics=[faithfulness, answer_relevancy, context_precision],
        llm=llm,
        embeddings=embeddings,
        run_config=run_config
    )

    print("\n🔥 FINAL RESULT:\n")
    print(result)

except Exception as e:
    print(f"❌ Error: {e}")