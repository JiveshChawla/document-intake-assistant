from app.models.state import PersonalWishesState, ExecutorInfo, GiftItem
from app.services.document_generator import DocumentGenerator

def test_document_includes_mandatory_disclaimer():
    """Verify that both markdown and HTML outputs strictly contain the fictional legal disclaimer."""
    state = PersonalWishesState()
    md, html = DocumentGenerator.generate(state)
    assert "FICTIONAL DRAFT" in md
    assert "NOT LEGAL ADVICE" in md
    assert "FICTIONAL DOCUMENT NOTICE" in html
    assert "NOT LEGAL ADVICE" in html

def test_pending_placeholders_for_unconfirmed_state():
    """Verify that incomplete states clearly show pending badges rather than empty or hallucinated text."""
    state = PersonalWishesState()
    md, html = DocumentGenerator.generate(state)
    assert "[PENDING: FULL LEGAL NAME]" in md
    assert "[PENDING: RESIDENTIAL ADDRESS]" in md
    assert "[PENDING: Appointment of Executor" in md
    assert "pending-field" in html

def test_completed_document_renders_all_clauses():
    """Verify that a full state populates all formal clauses accurately."""
    state = PersonalWishesState(
        full_name="Eleanor Vance",
        home_address="Hill House, Massachusetts",
        covers_worldwide_assets=True,
        has_children=True,
        children=["Theo Vance", "Luke Sanderson"],
        executor=ExecutorInfo(name="Theodora Vance", relationship="sister"),
        specific_gifts=[GiftItem(item="Antique Emerald Necklace", recipient="Theo Vance")],
        additional_wishes=["Scatter ashes in the greenhouse garden."]
    )
    md, html = DocumentGenerator.generate(state)

    assert "Eleanor Vance" in md
    assert "Hill House, Massachusetts" in md
    assert "Worldwide Assets Included" in md
    assert "Theo Vance" in md
    assert "Theodora Vance" in md
    assert "Antique Emerald Necklace" in md
    assert "greenhouse garden" in md
    assert "WITNESS ATTESTATION" in md
    assert "Witness 1" in md
    assert "Witness 2" in md

    # Check HTML tags
    assert "doc-table" in html
    assert "witness-grid" in html
