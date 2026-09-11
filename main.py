import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from transformers import pipeline

emotion_analyzer = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=None
)

def print_section(title):
    print("\n" + "="*8 + f" {title} " + "="*8)


print("=== AI Meeting Intelligence Assistant ===")

control_text = """10 GB for only XX euros every month

Just for you, get 10GB of 4G, 1000 minutes and 1000 SMS every month!

Donʼt miss your only chance to get it all for only %%Renewal_Cost%% euros each month.

Activate by %%End_Due_User%%.

By activating, you accept the TERMS AND CONDITIONS

Active Now

More details"""

persado_text = """10 GB for only XX euros every month

{First_Name}, reward yourself with a special offer!

At only %%Renewal_Cost%% euros each month, youʼll have:

10GB in 4G
1000 minutes
1000 SMS

...expires shortly!

By activating, you accept the TERMS AND CONDITIONS

Activate with a click

More details"""


while True:
    text = input("\nEnter meeting text (type 'exit' to stop):\n")

    if text.lower() == "exit":
        print("Exiting program...")
        break

    # -------- Summary --------
    sentences = text.split(".")
    summary = sentences[0] if sentences else text

    print_section("Summary")
    print(summary.strip())

    # -------- Action Items --------
    pattern = r"(\w+) will ([^\.]+)"
    actions = re.findall(pattern, text)

    print_section("Action Items")
    if actions:
        for person, task in actions:
            print(f"- {person} → {task}")
    else:
        print("No action items found")

    # -------- Sentiment Analysis --------
    train_texts = [
        "this is great", "good progress", "happy with results", "excellent work",
        "bad results", "this is terrible", "not good", "very poor performance",
        "amazing improvement", "horrible outcome"
    ]

    train_labels = [1,1,1,1, 0,0,0,0, 1,0]  # MUST match length = 10

    count_vectorizer = CountVectorizer()
    X_train = count_vectorizer.fit_transform(train_texts)

    model = LogisticRegression()
    model.fit(X_train, train_labels)

    test_vec = count_vectorizer.transform([text])
    sentiment = model.predict(test_vec)[0]
    prob = model.predict_proba(test_vec)[0][sentiment]

    print_section("Sentiment")
    print("Positive 😊" if sentiment == 1 else "Negative 😐")
    print("Confidence:", round(prob, 2))

    # -------- Topic Extraction --------
    tfidf = TfidfVectorizer(stop_words='english')
    X_tfidf = tfidf.fit_transform([text])

    words = tfidf.get_feature_names_out()
    scores = X_tfidf.toarray()[0]

    # Remove names dynamically
    names_to_remove = [person.lower() for person, _ in actions]

    # Remove weak words
    weak_words = [
        "discussed", "need", "will", "should", "meeting",
        "fix", "handle", "good", "bad", "results"
    ]

    scores_dict = dict(zip(words, scores))

    filtered_scores = {
        word: score
        for word, score in scores_dict.items()
        if word.lower() not in names_to_remove
        and word.lower() not in weak_words
    }

    top_topics = sorted(filtered_scores, key=filtered_scores.get, reverse=True)[:3]

    print_section("Key Topics")
    print(", ".join(top_topics))
