# view = window.get_active_view()

from gi.repository import GObject, Gedit

class ScrollBeyondViewActivatable(GObject.Object, Gedit.ViewActivatable):
	view = GObject.property(type=Gedit.View)

	def __init__(self):
		# upper, value
		self.last = (0, 0)
		self.handler = None
		self.change_handler = None
		GObject.Object.__init__(self)

	def do_activate(self):
		adjustment = self.view.get_vadjustment()
		lineheight = 14 # too lazy to really calculate it, so just hardcode it for now

		def allocate(view, allocation):
			upper = adjustment.get_upper()
			pagesize = adjustment.get_page_size()
			# we have less lines than the viewport can hold
			if upper == pagesize:
				# actually figure out the y of the last line
				buf = view.get_buffer()
				iter = buf.get_iter_at_line(buf.get_line_count())
				y = view.get_line_yrange(iter)
				upper = y[0] + y[1]

			set_to = upper + pagesize - lineheight
			adjustment.set_upper(set_to)
			# scroll back to our old position, unless we actually scroll downward,
			# which means we just added a new line
			if adjustment.get_value() < self.last[1]:
				adjustment.set_value(self.last[1])
			self.last = (set_to, adjustment.get_value())

		self.handler = self.view.connect("size-allocate", allocate)

		# keep track of our scrolling position, so we can scroll back to it when
		# the allocation changes and the scroll position is reset
		def valuechange(adjustment):
			value = adjustment.get_value()
			if adjustment.get_upper() == self.last[0]:
				self.last = (self.last[0], value)

		self.change_handler = adjustment.connect("value_changed", valuechange)

	def do_deactivate(self):
		self.view.disconnect(self.handler)
		self.view.get_vadjustment().disconnect(self.change_handler)

