# Revenue CRUD — Flask + SQLite (No setup needed)

This project is **ready to run**. It uses SQLite (a file-based DB), so no server, passwords or extra installs are required.

## Run
```bash
pip install -r requirements.txt
python app.py
```
Open http://127.0.0.1:5000 in your browser.

## Endpoints
- `GET /api/revenues`
- `POST /api/revenues` — body: `{revenue_id, date(YYYY-MM-DD), source, amount, category}`
- `PUT /api/revenues/<id>` — same body fields
- `DELETE /api/revenues/<id>`
