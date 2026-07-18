import streamlit as st
import re
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# -------- Title --------
st.title("🧠 AI Meeting Intelligence Assistant")
st.caption("AI-powered meeting analysis using NLP and Machine Learning")

# -------- Sample Button --------
if st.button("✨ Use Sample Text"):
    text = "We discussed the model performance. John will fix the dataset. Priya will handle deployment."
else:
    text = ""

# -------- Input --------
text = st.text_area("✍️ Enter meeting text", value=text, height=150)

# -------- Analyze --------
if st.button("🚀 Analyze"):

    if not text.strip():
        st.warning("Please enter some text")
    else:
        # -------- Summary --------
        sentences = text.split(".")
        summary = sentences[0] if sentences else text

        # -------- Action Items --------
        pattern = r"(\w+) will ([^\.]+)"
        actions = re.findall(pattern, text)

        # -------- Sentiment --------
        train_texts = [
            "this is great", "good progress", "happy with results", "excellent work",
            "bad results", "this is terrible", "not good", "very poor performance",
            "amazing improvement", "horrible outcome"
        ]
        train_labels = [1,1,1,1,0,0,0,0,1,0]

        vectorizer = CountVectorizer()
        X = vectorizer.fit_transform(train_texts)

        model = LogisticRegression()
        model.fit(X, train_labels)

        vec = vectorizer.transform([text])
        sentiment = model.predict(vec)[0]
        prob = model.predict_proba(vec)[0][sentiment]

        # -------- Topics --------
        tfidf = TfidfVectorizer(stop_words='english')
        X_tfidf = tfidf.fit_transform([text])

        words = tfidf.get_feature_names_out()
        scores = X_tfidf.toarray()[0]

        names_to_remove = [p.lower() for p, _ in actions]
        weak_words = [
            "discussed", "need", "will", "should", "meeting",
            "fix", "handle", "good", "bad", "results"
        ]

        scores_dict = dict(zip(words, scores))

        filtered = {
            w: s for w, s in scores_dict.items()
            if w.lower() not in names_to_remove and w.lower() not in weak_words
        }

        top = sorted(filtered, key=filtered.get, reverse=True)[:3]

        # -------- UI OUTPUT --------
        st.divider()

        st.subheader("📌 Summary")
        st.success(summary.strip())

        st.subheader("🧾 Action Items")
        if actions:
            for person, task in actions:
                st.write(f"👉 **{person}** → {task}")
        else:
            st.info("No action items found")

        st.subheader("😊 Sentiment")
        if sentiment == 1:
            st.success(f"Positive 😊 (Confidence: {round(prob,2)})")
        else:
            st.error(f"Negative 😐 (Confidence: {round(prob,2)})")

        st.subheader("🔑 Key Topics")
        st.write(", ".join(top))

# -------- Footer --------
st.markdown("---")
st.caption("Built with Python, scikit-learn, and Streamlit")