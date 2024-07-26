def separate_data_url_from_base64(base64_with_data_url: str) -> tuple[str, str]:
    data_url, base64_data = base64_with_data_url.split(",")
    return data_url, base64_data
