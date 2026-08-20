class DocumentBoundaryHandler:
    def append_end_of_document_token(
        self,
        records: list[dict[str, str]],
        end_of_document_token: str,
    ) -> list[dict[str, str]]:
        if not end_of_document_token:
            raise RuntimeError("The tokenizer must define an EOS token.")
        return [
            self._append_end_of_document_token(record, end_of_document_token)
            for record in records
        ]

    def _append_end_of_document_token(
        self,
        record: dict[str, str],
        end_of_document_token: str,
    ) -> dict[str, str]:
        text = record["text"]
        if text.endswith(end_of_document_token):
            return record.copy()
        return {
            **record,
            "text": f"{text}\n{end_of_document_token}",
        }
