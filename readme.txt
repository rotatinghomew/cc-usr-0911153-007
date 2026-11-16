中国—东盟跨境智慧物流走廊数字孪生

transport_book 提供手工路段容量和运输承诺。capacity 按路段与时间窗登记容量及版本，
reserve 在一个事务内校验连续路径、货票状态、各路段版本和合计占用；同一货票不能重复预订。
transition 使承诺进入 dispatched、completed 或尚未发运时 cancelled，完成或取消释放占用，
已发运承诺不可撤销。发运前货票资料改变需重新确认。inspect 可查看各时窗剩余容量及历史承诺。

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
