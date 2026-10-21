# Agents

Karma Mining is a small 2018 class project: score Reddit comments with a context similarity and a Bayesian ridge regressor, then show the ranking in a one-page UI. Keep that pipeline. Do not turn it into a new product, add a license, or retune the model "while you are here."

## Architecture

`python main.py` builds a Flask app, trains `regressor` from `DATA_FILE` (default `data/sample_comments.jsonl`), and serves:

| Route | Behavior |
| --- | --- |
| `GET /health` | `{"status": "ok"}` |
| `GET /combined/<post_id>` | The UI route. Fetch once, then `int(context * regression)`. |
| `GET /context_analyze/<post_id>` | Context scores only. |
| `GET /regressor1/<post_id>` | Regression scores only. |
| `GET /combined/demo` | First 12 bodies of the training file. No Reddit call. |

`demo` is a reserved post id. All three scoring routes return `[{"comment": "...", "score": ...}]`, highest score first. Ties break on comment text, reverse alphabetical, because the sort key is `(score, text)` with `reverse=True`.

`contextual.score` tokenizes with NLTK (`word_tokenize`), keeps alphabetic tokens, drops English stopwords, and sums cosine similarity against every comment in the batch, including itself. Vocabulary order is sorted so the same text yields the same vector. Identical bodies collapse to one dict key. Stopword-only comments score 0.

`regressor` fits at construction:

1. `StemmedCountVectorizer` (Snowball English stemmer, scikit-learn English stopwords, not NLTK's).
2. `TfidfTransformer`.
3. `SelectKBest(score_func=f_regression, k=min(1000, n_features))`.
4. `BayesianRidge`.

`FEATURE_COUNT` stays 1000. The course report mentions 8000. Do not "correct" it.

`reddit_client.py` is the only place credentials are read. `elastic.py` is an offline loader for a JSONL dump. The API never imports it.

The page is Vite + React in `frontend/`. `OneRingToRuleThemAll` is the single screen: header, post-id form, comment table, footer. It calls `/combined/<id>`. There is no client router. `VITE_API_URL` overrides the API origin (default `http://localhost:8080`).

## Conventions

- Python is formatted with Ruff (88 columns, double quotes). `ruff check` selects E, F, I, and UP.
- Leave the class names `contextual` and `regressor` as they are. Call sites and the report use them.
- Runtime pins live in `requirements.txt`. pytest and Ruff are in `requirements-dev.txt`. The frontend lockfile is `frontend/package-lock.json`.
- Do not commit `.env`, virtualenvs, `node_modules`, `frontend/dist`, or NLTK data.
- New tests should not call Reddit or Elasticsearch. Inject a fake client or hit post id `demo`.
- CORS is open so the dev server on port 3000 can call the API. A GET must not send a JSON content type; that forces a preflight the 2018 page did send.

## Commands

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt -r requirements-dev.txt
ruff check .
ruff format .
pytest
python main.py
```

```bash
cd frontend
npm ci
npm test
npm start
npm run build
```

CI is `.github/workflows/ci.yml`: Python 3.12 (Ruff, pytest) and Node 22 (Vitest, Vite build).

The first `contextual.score` call downloads `punkt`, `punkt_tab`, and `stopwords` if they are missing.

## Gotchas

- The original `data1.txt` training dump and `data2.txt` Elasticsearch dump are not in the repo. The sample JSONL is synthetic text with a planted "excellent explanation" vs "garbage nonsense" signal so the demo is visibly sorted. It is not the CMPE 255 model.
- Combined scores truncate with `int()`. A product of 5.9 becomes 5. Negative predictions stay negative or become 0.
- Context and regression are multiplied, not averaged and not normalized. Do not rescale one side without a reason; it changes every displayed integer.
- `f_regression` replaced `SelectKBest`'s old default `f_classif`. ANOVA F-scores are NaN on current scikit-learn when a karma value appears once, so feature selection was silently arbitrary. k is still 1000 when the vocabulary is large enough.
- Stemming happens only in the regressor. The report describes stemming as a general preprocessing step. Adding it to `contextual` changes scores.
- Only top-level comments are scored. `replace_more(limit=0)` does not fetch collapsed replies. On PRAW 8, `limit` is keyword-only.
- Training runs in `create_app` when no model is injected. Tests that do not need the real model pass fakes. The session fixture in `tests/conftest.py` trains once on the sample file.
- A huge `DATA_FILE` is loaded fully into memory and turned into a dense array after `SelectKBest`. That is the original startup behavior.
- Reddit script-app auth needs client id, secret, username, and password. Read-only installed-app auth is not what this project used.
- The old UI called `http://0.0.0.0:8080`, which browsers will not connect to. The API still binds `0.0.0.0` so a container can reach it. The page uses `localhost`.
- `elastic.py` skips any body that contains the substring `[deleted]`, not only exact deleted comments. That matches the 2018 script.
- Heroku's `Procfile` is unchanged in purpose (`python main.py`). Nothing in CI deploys it.

## Secrets

Credentials belong in the environment. `.env.example` lists the names. If you find a hardcoded client id, secret, password, or host that identifies someone's cluster, remove it and call it out in the pull request. Do not rewrite git history unless the owner asks.
