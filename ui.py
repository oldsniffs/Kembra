import tkinter as tk


class GameScreen(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.parent = parent

        self.create_widgets()

    def create_widgets(self):

        # Container Frames
        self.text_frame = tk.Frame(self, height=760, width=850, bg='black')
        self.visual_frame = tk.Frame(self, height=760, width=575, bg='thistle3')

        self.text_frame.grid(row=1, column=1, sticky='nsew')
        self.visual_frame.grid(row=1, column=3)

        # Text Panels

        self.output_display = OutputText(self.text_frame, width=105, bg='black', foreground='#CCCCFF', wrap='word', relief='sunken', state='disabled')
        self.player_input = tk.Text(self.text_frame, height=2, width=105, bg='black', foreground='white',
                                    relief="sunken")
        self.output_display.pack(expand=True, fill='y')
        self.player_input.pack()


class OutputText(tk.Text):
    def __init__(self, *args, **kwargs):
        tk.Text.__init__(self, *args, **kwargs)

        self.configure(state='disabled')
        # TODO: see if this can be overloaded

        # self.output_font = tkfont.Font('system', 8)
        # self.configure(font=self.output_font)

        # ---- Tags ----

        self.tag_configure('red', foreground='#ff0000')
        self.tag_configure('orange-red', foreground='#FF4500')
        self.tag_configure('dark-turquoise', foreground='#2C7B80')
        self.tag_configure('light-turquoise', foreground='#3FB1B7')
        self.tag_configure('salmon', foreground='#D76565')
        self.tag_configure('light-salmon', foreground='#6B3232')
        self.tag_configure('teal', foreground='#01B8AA')
        self.tag_configure('mudfish', foreground='#2E3A22')
        self.tag_configure('light-mudfish', foreground='#12170D')
        self.tag_configure('light-lavender', foreground='#9797FF')
        self.tag_configure('vanilla', foreground='#fff68f')
        self.tag_configure('overcast', foreground='#939FAB')
        self.tag_configure('cocoa', foreground='#3E2323')
        self.tag_configure('blood', foreground='#6D0F0F')
        self.tag_configure('lavender-blue', foreground='#CCCCFF')
        self.tag_configure('light-brown', foreground='#AB9481')
        self.tag_configure('muted-purple', foreground='#6F404B')

    def display_text(self, text):
        # Tagging, custom formatting should be worked out at higher level

        self.configure(state='normal')
        self.insert('end', text)
        self.configure(state='disabled')
        self.see('end')

    def apply_tag_to_pattern(self, pattern, tag, start='1.0', end='end', regexp=False):

        start = self.index(start)
        end = self.index(end)

        self.mark_set('matchStart', start)
        self.mark_set('matchEnd', start)
        self.mark_set('searchLimit', end)

        count = tk.IntVar()  # initiates at 0
        while True:
            index = self.search(pattern, 'matchEnd', 'searchLimit', count=count, regexp=regexp)
            if index == '':
                break
            if count.get() == 0:
                break
            self.mark_set('matchStart', index)
            self.mark_set('matchEnd', '%s+%sc' % (index, count.get()))
            self.tag_add(tag, 'matchStart', 'matchEnd')
