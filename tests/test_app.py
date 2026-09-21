from pathlib import Path
from streamlit.testing.v1 import AppTest

ROOT = Path(__file__).parents[1]

def test_dashboard_workflow():
    app = AppTest.from_file(str(ROOT / "streamlit_app.py"), default_timeout=30).run()
    assert not app.exception
    assert app.title[0].value == "WindCtrl Validator"
    assert app.metric[0].value == "360"
    initial_failed = int(app.metric[2].value)
    app.slider[0].set_value(0.0).run()
    assert not app.exception
    assert int(app.metric[2].value) >= initial_failed
    app.button[0].click().run()
    app.selectbox[0].select("FAIL").run()
    assert not app.exception
    assert app.dataframe[-1].value.status.eq("FAIL").all()
