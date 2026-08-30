import pytest
from app.tools.sql_tool import enforce_row_limit, validate_sql

def test_select_allowed(): assert validate_sql("SELECT supplier_id FROM suppliers").startswith("SELECT")
@pytest.mark.parametrize("query",["DELETE FROM suppliers","DROP TABLE suppliers","UPDATE suppliers SET rating=5"])
def test_destructive_blocked(query):
    with pytest.raises(ValueError): validate_sql(query)
def test_unknown_table_blocked():
    with pytest.raises(ValueError): validate_sql("SELECT * FROM payroll")
def test_multiple_statements_blocked():
    with pytest.raises(ValueError): validate_sql("SELECT * FROM suppliers; DROP TABLE suppliers")
def test_row_limit_added(): assert "LIMIT 25" in enforce_row_limit("SELECT * FROM suppliers",25)

def test_large_row_limit_is_clamped():
    assert "LIMIT 100" in enforce_row_limit("SELECT * FROM suppliers LIMIT 1000", 100)
