from flask import Flask, render_template, request  # type: ignore[import]
import os

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
VERB_FILE = os.path.join(BASE_DIR, "verbs.txt")


def clean(s: str) -> str:
    if not isinstance(s, str):
        return ""
    return (
        s.replace("\ufeff", "")
         .replace("\u200b", "")
         .replace("\xa0", " ")
         .strip()
    )


def load_verbs(filename):
    verbs_list = []
    index = {}

    try:
        with open(filename, "r", encoding="utf-8") as f:
            for raw_line in f:
                line = clean(raw_line)

                if not line:
                    continue
                if line.startswith("#"):
                    continue

                parts = [clean(p) for p in line.split(",")]
                if len(parts) != 3:
                    continue

                base, past, pp = parts
                entry = {"base": base, "past": past, "pp": pp}
                verbs_list.append(entry)

                def add_forms(form_string, entry):
                    for form in form_string.split("/"):
                        form_clean = clean(form).lower()
                        if form_clean:
                            index[form_clean] = entry

                add_forms(base, entry)
                add_forms(past, entry)
                add_forms(pp, entry)

    except FileNotFoundError:
        print(f"Verb file '{filename}' not found.")
    except Exception as e:
        print(f"Error loading verbs: {e}")

    return verbs_list, index


verbs, index = load_verbs(VERB_FILE)


@app.route("/", methods=["GET", "POST"])
def home():
    query = ""
    result = None
    status = ""

    if request.method == "POST":
        query = clean(request.form.get("verb", "").lower())
        if not query:
            status = "Please enter a verb."
        else:
            if query in index:
                entry = index[query]
                result = entry
                status = f"Found verb for: '{query}'"
            else:
                status = f"No verb found for: '{query}'"

    return render_template("index.html", query=query, result=result, status=status)


if __name__ == "__main__":
    app.run(debug=True)
