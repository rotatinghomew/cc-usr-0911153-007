中国—东盟跨境智慧物流走廊数字孪生

运行验收：
python3 -m corridor_twin run --fixture fixtures/acceptance.json --database /tmp/corridor_twin.sqlite3 --output /tmp/corridor_twin-output

核验：
python3 -m corridor_twin verify --database /tmp/corridor_twin.sqlite3 --output /tmp/corridor_twin-output

全量测试：
python3 -m unittest discover -s tests -v

按模块测试：
python3 -m unittest tests.events.test_logistics_event -v

构建检查：
python3 -m compileall -q corridor_twin tests
