from ddgs import DDGS

from src.retrieval.web_models import WebResult



class WebRetriever:
    def __init__(
            self,max_results : int = 5
    )->None:
        self.max_results = max_results

    def search(
            self,
            query:str
    )->list[WebResult]:
        if not query.strip():
            raise ValueError("Query cannot be empty.")
        results : list[WebResult] = []
        with DDGS() as ddgs:
            for item in ddgs.text(
                query,
                max_results = self.max_results,

            ):
                title = item.get("title", "").strip()
                url = item.get("href", "").strip()
                snippet = item.get("body", "").strip()

                if not url or not snippet:
                    continue

                results.append(
                    WebResult(
                        title=title,
                        url=url,
                        snippet=snippet,
                    )
                )

        return results
                


