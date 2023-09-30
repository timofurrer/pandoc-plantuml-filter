from pandoc_plantuml_filter import plantuml


def test_call_plantuml_create_para_object(mocker):
    mocker.patch("os.path.isfile", return_value=False)
    mock = mocker.patch("subprocess.check_call")

    ret = plantuml(key="CodeBlock", value=[["", ["plantuml"], []], ""], format_=None, meta={})

    assert isinstance(ret, dict)
    assert "t" in ret.keys()
    assert ret["t"] == "Para"

    mock.assert_called_once()
