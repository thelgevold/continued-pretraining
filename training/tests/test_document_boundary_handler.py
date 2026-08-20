from training.handlers.data.document_boundary_handler import (
    DocumentBoundaryHandler,
)


def test_appends_exactly_one_end_of_document_token_to_each_document() -> None:
    handler = DocumentBoundaryHandler()
    records = [
        {"section": "routes", "text": "First document."},
        {"section": "history", "text": "Second document.\n<|im_end|>"},
    ]

    bounded_records = handler.append_end_of_document_token(
        records,
        "<|im_end|>",
    )

    assert bounded_records == [
        {"section": "routes", "text": "First document.\n<|im_end|>"},
        {"section": "history", "text": "Second document.\n<|im_end|>"},
    ]


def test_requires_tokenizer_end_of_document_token() -> None:
    handler = DocumentBoundaryHandler()

    try:
        handler.append_end_of_document_token([], "")
    except RuntimeError as error:
        assert str(error) == "The tokenizer must define an EOS token."
    else:
        raise AssertionError("Expected a missing-token error.")


def test_city_context_uses_the_supported_training_window() -> None:
    from city_training.pre_training_config import PreTrainingConfig

    assert PreTrainingConfig().max_seq_length == 1024
