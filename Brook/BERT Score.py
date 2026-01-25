from bert_score import score

candidates = ["Bonjour, Anastasiia"]
references = ["Salut, Ana Banana"]

P, R, F1 = score(
    candidates,
    references,
    lang="fr",
    model_type="xlm-roberta-base",
    rescale_with_baseline=True
)

print(F1.item())
