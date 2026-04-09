Build me a small FastAPI app for saving and organizing bookmarks. I want it to feel like a real starter app, not a toy. It should let me create, edit, delete, archive, tag, search, and list bookmarks, and listing should support pagination and sorting. Please keep the code clean, reasonably modular, and follow best practices. If there are a couple of sensible design choices, pick them and keep moving.

Writable files:

- `src/bookmarks_api/main.py`
- `src/bookmarks_api/models.py`
- `src/bookmarks_api/store.py`

Target command:

`python -m pytest -q tests/test_bookmarks_api.py`
