"""Test configuration helpers: save_env_key, .env loading, CLI flag defaults."""

import os, sys


class TestSaveEnvKey:
    """save_env_key() updates .env without mangling other keys or comments."""

    def test_add_key(self, tmp_env):
        from lib.conf import save_env_key

        save_env_key("ABS_SERVER_URL", "http://localhost:13378")
        with open(os.path.join(tmp_env, ".env")) as f:
            content = f.read()
        assert "ABS_SERVER_URL=http://localhost:13378" in content

    def test_add_multiple_keys(self, tmp_env):
        from lib.conf import save_env_key

        save_env_key("ABS_SERVER_URL", "http://abs:13378")
        save_env_key("ABS_API_TOKEN", "tok_abc123")
        with open(os.path.join(tmp_env, ".env")) as f:
            content = f.read()
        assert "ABS_SERVER_URL=http://abs:13378" in content
        assert "ABS_API_TOKEN=tok_abc123" in content

    def test_update_existing_key(self, tmp_env):
        from lib.conf import save_env_key

        save_env_key("ABS_SERVER_URL", "http://old:13378")
        save_env_key("ABS_SERVER_URL", "http://new:13378")
        with open(os.path.join(tmp_env, ".env")) as f:
            content = f.read()
        # Only one line should exist, with the new value
        assert content.count("ABS_SERVER_URL") == 1
        assert "http://new:13378" in content

    def test_preserves_other_content(self, tmp_env):
        from lib.conf import save_env_key

        env_path = os.path.join(tmp_env, ".env")
        with open(env_path, "w") as f:
            f.write("# This is a comment\nEXISTING_KEY=old_value\n")

        save_env_key("ABS_ENABLED", "true")
        with open(env_path) as f:
            content = f.read()
        assert "# This is a comment" in content
        assert "EXISTING_KEY=old_value" in content
        assert "ABS_ENABLED=true" in content

    def test_empty_value(self, tmp_env):
        from lib.conf import save_env_key

        save_env_key("ABS_API_TOKEN", "")
        with open(os.path.join(tmp_env, ".env")) as f:
            content = f.read()
        assert "ABS_API_TOKEN=" in content


class TestDefaults:
    """Verify module-level defaults are correct types."""

    def test_default_chapter_mode(self):
        from lib.conf import default_output_chapter_mode

        assert default_output_chapter_mode is False

    def test_default_overwrite(self):
        from lib.conf import default_output_overwrite

        assert default_output_overwrite is False

    def test_default_abs_enabled(self):
        from lib.conf import default_abs_enabled

        assert isinstance(default_abs_enabled, bool)

    def test_default_server_url_is_string(self):
        from lib.conf import default_abs_server_url

        assert isinstance(default_abs_server_url, str)

    def test_cli_options_list(self):
        from lib.conf import cli_options

        assert "--chapter_mode" in cli_options
        assert "--output_overwrite" in cli_options
        assert "--abs_enabled" in cli_options
        assert "--abs_server_url" in cli_options
        assert "--abs_api_token" in cli_options
        assert "--abs_library_id" in cli_options
