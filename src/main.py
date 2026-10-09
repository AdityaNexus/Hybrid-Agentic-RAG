import logging

from src.application import (
    RAGApplication,
    create_application as build_application,
)


def create_application():
    return build_application()


def main():
    logging.basicConfig(
        level=logging.INFO,
        format="%(levelname)s %(name)s: %(message)s",
    )

    app = create_application()

    print("Hybrid Agentic RAG")
    print("Type 'exit' to quit.")

    while True:

        query = input("\nYou: ").strip()

        if query.lower() == "exit":
            break

        if not query:
            continue

        try:
            result = app.ask(query)
        except Exception as error:
            print(f"\nRequest failed: {error}")
            continue

        print("\nAssistant:")
        print(result["answer"])

        print("\nCache hit:", result.get("cache_hit"))


if __name__ == "__main__":
    main()