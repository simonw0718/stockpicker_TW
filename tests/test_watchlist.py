# tests/test_watchlist.py
def test_watchlist_crud(client):
    # Create：混中文/舊格式/空白/None
    payload = {
        "name": "  我的追蹤   清單  ",
        "symbols": ["2330", " 台積電 ", "2330.TW", "", "國泰金", None, "  "],
    }
    r = client.post("/api/v1/watchlist", json=payload)
    assert r.status_code == 201, r.text
    data = r.json()

    # name 會被清洗：多空白折疊
    assert data["name"] == "我的追蹤 清單"
    # items 以正規化後的順序+去重，position 0..n
    assert [i["symbol"] for i in data["items"]] == ["2330", "2882"]
    assert [i["position"] for i in data["items"]] == [0, 1]

    list_id = data["id"]

    # GET 單筆
    r = client.get(f"/api/v1/watchlist/{list_id}")
    assert r.status_code == 200
    data = r.json()
    assert [i["symbol"] for i in data["items"]] == ["2330", "2882"]

    # PATCH：只改 name
    r = client.patch(f"/api/v1/watchlist/{list_id}", json={"name": "清單2"})
    assert r.status_code == 200
    assert r.json()["name"] == "清單2"

    # PATCH：改 symbols（會全刪重建，並依順序給 position）
    r = client.patch(
        f"/api/v1/watchlist/{list_id}",
        json={"symbols": ["2882", "2330", "2330", " 台積 "]},
    )
    assert r.status_code == 200
    data = r.json()
    assert [i["symbol"] for i in data["items"]] == ["2882", "2330"]
    assert [i["position"] for i in data["items"]] == [0, 1]

    # GET all
    r = client.get("/api/v1/watchlist")
    assert r.status_code == 200
    all_lists = r.json()
    assert any(wl["id"] == list_id for wl in all_lists)

    # DELETE
    r = client.delete(f"/api/v1/watchlist/{list_id}")
    assert r.status_code == 204