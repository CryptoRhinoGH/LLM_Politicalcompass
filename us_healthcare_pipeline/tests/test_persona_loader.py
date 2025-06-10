from us_healthcare_pipeline.services.persona_loader import PersonaLoader

def test_load_left_persona():
    persona = PersonaLoader.load_persona("left")
    assert persona.label == "left"
    assert isinstance(persona.search_queries, list)
    assert isinstance(persona.news_sites, list)
    assert len(persona.search_queries) > 0
    assert len(persona.news_sites) > 0

def test_invalid_persona_raises():
    try:
        PersonaLoader.load_persona("unknown")
        assert False, "Should raise ValueError"
    except ValueError as e:
        assert "No queries found for persona" in str(e) or "No news sites found" in str(e)