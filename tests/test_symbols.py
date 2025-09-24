def test_search_code(client):
    r = client.get("/api/v1/symbols/search", params={"q": "2330"})
    assert r.status_code == 200
    data = r.json()
    assert any(x["code"] == "2330" for x in data)

def test_search_name(client):
    r = client.get("/api/v1/symbols/search", params={"q": "台積"})
    assert r.status_code == 200
    data = r.json()
    assert any(x["code"] == "2330" for x in data)

def test_search_alias_new(client):
    r = client.get("/api/v1/symbols/search", params={"q": "國泰金"})
    assert r.status_code == 200
    assert r.json()[0]["code"] == "2882"

def test_search_suffix(client):
    r = client.get("/api/v1/symbols/search", params={"q": "2330.TW"})
    assert r.status_code == 200
    assert r.json()[0]["code"] == "2330"