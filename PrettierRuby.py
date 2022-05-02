from subprocess import Popen, PIPE
import imp
import os
import sys
import inspect

import sublime
import sublime_plugin

# Reload sub-packages
package_name = "PrettierRuby"
print(
    "Performing custom full reload of {package_name}".format(package_name=package_name)
)
for module in sys.modules:
    if module.startswith(package_name) and module != package_name:
        imp.reload(sys.modules[package_name])
# end sub-package reloading

from .prettier_ruby.utils import (
    decode_bytes,
    format_error_message,
    get_proc_env,
    is_windows,
    normalize_line_endings,
    resolve_path,
)


class PrettierRubyCommand(sublime_plugin.TextCommand):
    def run(self, edit):
        view = self.view
        source_file_path = view.file_name()

        region = sublime.Region(0, view.size())
        source_text = view.substr(region)

        prettified_text = self.format_code(source_text)
        view.replace(edit, region, prettified_text)

    def format_code(self, source_text):
        source_file_path = self.view.file_name()
        working_directory = os.path.dirname(source_file_path)

        rbprettier_cli_path = resolve_path(
            "rbprettier",
            working_directory,
            default="/home/marlen/.asdf/shims/rbprettier",
        )
        cmd = [
            rbprettier_cli_path,
            source_file_path,
        ]

        node_cmd = "node.exe" if is_windows() else "node"
        node_binary_path = resolve_path(
            node_cmd, working_directory, default="/home/marlen/.asdf/shims/node"
        )
        node_path = os.path.dirname(node_binary_path)
        env = get_proc_env(additional_paths=[working_directory, node_path])

        try:
            proc = Popen(
                cmd,
                stdin=PIPE,
                stderr=PIPE,
                stdout=PIPE,
                env=env,
                shell=is_windows(),
            )
            stdout, stderr = proc.communicate(input=source_text.encode("utf-8"))

            if stderr:
                stderr_output = normalize_line_endings(decode_bytes(stderr))
                if stderr_output:
                    print(format_error_message(stderr_output, str(proc.returncode)))
                    return source_text

            return normalize_line_endings(decode_bytes(stdout))
        except OSError as ex:
            sublime.error_message(
                "{plugin_name} - {error}".format(plugin_name="PrettierRuby", error=ex)
            )
            raise


class CommandOnSave(sublime_plugin.ViewEventListener):
    def on_pre_save(self):
        view = self.view
        source_file_path = view.file_name()
        _, source_file_name = os.path.split(source_file_path)
        root, extension = os.path.splitext(source_file_name)
        extension = root if extension == "" else extension

        if extension not in [".rb", ".gemspec", "Gemfile"]:
            return

        self.view.run_command("prettier_ruby")
