"""Tests for invoice.payments.

DEMO ROLE: deliberately THIN, same as test_reminders.py. Two shallow tests
across five new modules keeps Coverage on New Code far below the 80% gate
threshold, which is the realistic state of a rushed feature branch.
"""

from invoice.payments import apply_fx, capture_payment


def test_capture_payment_returns_idempotency_key():
    result = capture_payment("INV-2001", 100.00, "tok_test_abc")
    assert result["invoice_id"] == "INV-2001"
    assert len(result["idempotency_key"]) == 32


def test_apply_fx_multiplies_by_rate():
    assert apply_fx(100.0, 1.35, "CAD") == 135.0
