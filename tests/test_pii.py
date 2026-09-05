from app.core.pii import mask_pii


def test_mask_pii_redacts_email():
    text = "Contact me at jane.doe@example.com for details."

    masked = mask_pii(text)

    assert "jane.doe@example.com" not in masked
    assert "<EMAIL_ADDRESS>" in masked


def test_mask_pii_redacts_name():
    text = "The report was submitted by John Smith on Tuesday."

    masked = mask_pii(text)

    assert "John Smith" not in masked


def test_mask_pii_leaves_non_pii_text_unchanged():
    text = "The database migration completed without errors."

    masked = mask_pii(text)

    assert masked == text


def test_mask_pii_handles_empty_string():
    assert mask_pii("") == ""
