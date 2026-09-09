from app.utils.tool_detection import detect_tool, detect_all_tools, get_platform_info, get_available_qemu_binaries


def test_detect_tool_for_nonexistent_binary():
    result = detect_tool("this_tool_definitely_does_not_exist_xyz")
    assert result.available is False
    assert result.path == ""


def test_detect_tool_for_python3():
    result = detect_tool("python3")
    assert result.available is True
    assert result.path != ""


def test_detect_all_tools_returns_expected_keys():
    results = detect_all_tools()
    assert "binwalk" in results
    assert "qemu-system-arm" in results
    assert "tcpdump" in results


def test_get_platform_info_returns_required_fields():
    info = get_platform_info()
    assert "system" in info
    assert "machine" in info
    assert "python_version" in info


def test_get_available_qemu_binaries_returns_list():
    binaries = get_available_qemu_binaries()
    assert isinstance(binaries, list)
