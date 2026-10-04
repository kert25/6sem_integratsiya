"""End-to-end checks for the Express API and PostgreSQL persistence layer."""

import allure

from conftest import API_URL


@allure.feature("Schools API")
@allure.story("Schema initialization")
def test_setup_endpoint_created_schools_table(api_session, db_connection):
    with allure.step("Verify the table created by GET /setup"):
        with db_connection.cursor() as cursor:
            cursor.execute("SELECT to_regclass('public.schools')")
            assert cursor.fetchone()[0] == "schools"


@allure.feature("Schools API")
@allure.story("Read schools")
def test_get_returns_empty_list_for_clean_database(api_session, db_connection):
    response = api_session.get(API_URL, timeout=5)

    assert response.status_code == 200
    assert response.json() == []
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT COUNT(*) FROM schools")
        assert cursor.fetchone()[0] == 0


@allure.feature("Schools API")
@allure.story("Create school")
def test_post_persists_school_in_postgresql(create_school, db_connection):
    response = create_school("School No. 9", "Tula")

    assert response.status_code == 200
    assert response.json() == {"message": "Successfully added child"}
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT name, address FROM schools")
        assert cursor.fetchone() == ("School No. 9", "Tula")


@allure.feature("Schools API")
@allure.story("Read after create")
def test_created_school_is_returned_by_get(create_school, api_session, db_connection):
    create_school("Gymnasium", "Lenina 10")

    response = api_session.get(API_URL, timeout=5)

    assert response.status_code == 200
    assert response.json() == [{"id": 1, "name": "Gymnasium", "address": "Lenina 10"}]
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT id, name, address FROM schools")
        assert cursor.fetchone() == (1, "Gymnasium", "Lenina 10")


@allure.feature("Schools API")
@allure.story("Multiple writes")
def test_multiple_api_requests_persist_all_rows(create_school, api_session, db_connection):
    assert create_school("Lyceum", "Sovetskaya 1").status_code == 200
    assert create_school("College", "Mira 2").status_code == 200

    response = api_session.get(API_URL, timeout=5)

    assert [school["name"] for school in response.json()] == ["Lyceum", "College"]
    with db_connection.cursor() as cursor:
        cursor.execute("SELECT name, address FROM schools ORDER BY id")
        assert cursor.fetchall() == [
            ("Lyceum", "Sovetskaya 1"),
            ("College", "Mira 2"),
        ]
