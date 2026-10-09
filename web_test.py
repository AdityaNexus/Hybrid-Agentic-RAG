from src.retrieval.web_retriever import WebRetriever

retriever = WebRetriever() 
resuts = retriever.search(
    "latest python releases"
)

for result in resuts:
    print(f"Title: {result.title}")
    print(f"URL: {result.url}")
    print(f"Snippet: {result.snippet}")
    print("-" * 40)

    