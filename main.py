"""Start the simplified AI logistics web app.

This keeps the project easy to run for a demo or a class presentation.
"""

import uvicorn


def main() -> None:
    uvicorn.run("app.api.main:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
