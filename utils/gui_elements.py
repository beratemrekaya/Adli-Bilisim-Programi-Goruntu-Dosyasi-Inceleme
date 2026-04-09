import tkinter as tk
from tkinter import ttk

class ScrollableFrame(ttk.Frame):
    """
    İçeriği kaydırılabilir bir Tkinter Frame'i.
    Büyük miktarda içeriği görüntülemek için kullanışlıdır.
    """
    def __init__(self, container, *args, **kwargs):
        super().__init__(container, *args, **kwargs)
        self.canvas = tk.Canvas(self, borderwidth=0, background="#2b2b2b", highlightthickness=0)
        self.viewport = ttk.Frame(self.canvas, background="#2b2b2b")
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.hsb = ttk.Scrollbar(self, orient="horizontal", command=self.canvas.xview)

        self.canvas.configure(yscrollcommand=self.vsb.set, xscrollcommand=self.hsb.set)

        self.vsb.pack(side="right", fill="y")
        self.hsb.pack(side="bottom", fill="x")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((4, 4), window=self.viewport, anchor="nw",
                                                      tags="self.viewport")

        self.viewport.bind("<Configure>", self._on_frame_configure)
        self.canvas.bind("<Configure>", self._on_canvas_configure)

        self.viewport_height = 0
        self.viewport_width = 0

    def _on_frame_configure(self, event):
        """Viewport boyut değiştiğinde canvas'ın scroll bölgesini güncelle."""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        if self.viewport.winfo_width() != self.viewport_width or \
           self.viewport.winfo_height() != self.viewport_height:
            self.viewport_width = self.viewport.winfo_width()
            self.viewport_height = self.viewport.winfo_height()
            self.canvas.itemconfig(self.canvas_window, width=self.viewport_width, height=self.viewport_height)


    def _on_canvas_configure(self, event):
        """Canvas boyut değiştiğinde viewport'un genişliğini ayarla."""
        canvas_width = event.width
        self.canvas.itemconfig(self.canvas_window, width=canvas_width)

def create_tooltip(widget, text):
    """Bir widget üzerine fare geldiğinde ipucu (tooltip) gösterir."""
    tooltip = None
    def enter(event):
        nonlocal tooltip
        x = y = 0
        x, y, cx, cy = widget.bbox("insert")
        x += widget.winfo_rootx() + 25
        y += widget.winfo_rooty() + 20
        # creates a toplevel window
        tooltip = tk.Toplevel(widget)
        tooltip.wm_overrideredirect(True) # Removes window decorations
        tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(tooltip, text=text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "8", "normal"))
        label.pack(ipadx=1)
    def leave(event):
        nonlocal tooltip
        if tooltip:
            tooltip.destroy()
        tooltip = None
    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)