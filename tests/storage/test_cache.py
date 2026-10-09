from src.storage.cache import AnswerCache


def test_cache(tmp_path):

    cache = AnswerCache(
        tmp_path / "answers.db"
    )

    cache.put(
        query="What is the leave policy?",
        answer="Employees receive 20 days.",
        knowledge_version="version1",
    )

    result = cache.get(
        query="What is the leave policy?",
        knowledge_version="version1",
    )

    assert result is not None
    assert result.answer == "Employees receive 20 days."

    cache.close()


def test_stale_cache(tmp_path):

    cache = AnswerCache(
        tmp_path / "answers.db"
    )

    cache.put(
        query="What is the leave policy?",
        answer="Old answer",
        knowledge_version="version1",
    )

    result = cache.get(
        query="What is the leave policy?",
        knowledge_version="version2",
    )

    assert result is None

    cache.close()