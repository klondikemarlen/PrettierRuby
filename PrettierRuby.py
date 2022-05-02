import sublime
import sublime_plugin


class PrettierRubyCommand(sublime_plugin.ViewEventListener):
	# on_post_save_async(view)
	def on_pre_save(self):
		print("self.view.file_name()", self.view.file_name())
		file_name = self.view.file_name()

