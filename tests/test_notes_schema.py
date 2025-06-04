# tests/test_notes_schema.py
"""
pytest tests for validating the Notes schema
"""

import pytest
from pydantic import ValidationError
from scripts.generate_notes import Note, NotesResponse

def test_valid_note():
    """Test that a valid note passes validation."""
    note = Note(
        id=1,
        heading="Mean Value Theorem",
        summary="States that for a continuous function on [a,b], there exists a point c where f'(c) equals the average rate of change.",
        page_ref=42
    )
    
    assert note.id == 1
    assert note.heading == "Mean Value Theorem"
    assert len(note.summary) <= 150
    assert note.page_ref == 42

def test_note_without_page_ref():
    """Test that a note without page reference is valid."""
    note = Note(
        id=5,
        heading="Derivative Definition",
        summary="The derivative is the limit of the difference quotient as h approaches zero."
    )
    
    assert note.page_ref is None

def test_invalid_note_id_too_high():
    """Test that note ID > 10 fails validation."""
    with pytest.raises(ValidationError):
        Note(
            id=15,
            heading="Invalid Note",
            summary="This should fail"
        )

def test_invalid_note_id_too_low():
    """Test that note ID < 1 fails validation."""
    with pytest.raises(ValidationError):
        Note(
            id=0,
            heading="Invalid Note",
            summary="This should fail"
        )

def test_invalid_summary_too_long():
    """Test that summary > 150 chars fails validation."""
    with pytest.raises(ValidationError):
        Note(
            id=1,
            heading="Valid Heading",
            summary="x" * 151  # 151 characters
        )

def test_empty_heading():
    """Test that empty heading fails validation."""
    with pytest.raises(ValidationError):
        Note(
            id=1,
            heading="",
            summary="Valid summary"
        )

def test_valid_notes_response():
    """Test that a valid NotesResponse with 10 notes passes."""
    notes = [
        Note(id=i, heading=f"Topic {i}", summary=f"Summary for topic {i}")
        for i in range(1, 11)
    ]
    
    response = NotesResponse(notes=notes)
    assert len(response.notes) == 10

def test_invalid_notes_response_too_few():
    """Test that NotesResponse with < 10 notes fails."""
    notes = [
        Note(id=i, heading=f"Topic {i}", summary=f"Summary for topic {i}")
        for i in range(1, 5)  # Only 4 notes
    ]
    
    with pytest.raises(ValidationError):
        NotesResponse(notes=notes)

def test_invalid_notes_response_too_many():
    """Test that NotesResponse with > 10 notes fails."""
    notes = [
        Note(id=i, heading=f"Topic {i}", summary=f"Summary for topic {i}")
        for i in range(1, 15)  # 14 notes
    ]
    
    with pytest.raises(ValidationError):
        NotesResponse(notes=notes)

def test_note_serialization():
    """Test that notes can be serialized to dict."""
    note = Note(
        id=3,
        heading="Integration by Parts",
        summary="Formula: ∫u dv = uv - ∫v du",
        page_ref=78
    )
    
    note_dict = note.model_dump()
    
    assert note_dict['id'] == 3
    assert note_dict['heading'] == "Integration by Parts"
    assert note_dict['summary'] == "Formula: ∫u dv = uv - ∫v du"
    assert note_dict['page_ref'] == 78

if __name__ == "__main__":
    # Run tests manually if not using pytest
    print("🧪 Running schema validation tests...")
    
    try:
        test_valid_note()
        print("✅ Valid note test passed")
        
        test_note_without_page_ref()
        print("✅ Note without page ref test passed")
        
        test_note_serialization()
        print("✅ Note serialization test passed")
        
        # Test invalid cases
        try:
            test_invalid_note_id_too_high()
            print("❌ Should have failed for ID > 10")
        except AssertionError:
            print("✅ Correctly rejected ID > 10")
        
        try:
            test_invalid_summary_too_long()
            print("❌ Should have failed for long summary")
        except AssertionError:
            print("✅ Correctly rejected long summary")
        
        print("\n🎉 All tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")