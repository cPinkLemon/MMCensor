import tkinter as tk
import customtkinter as ctk

class feature_selector_ctk:
    def populate_frame( self, frame, classes, selected_classes ):
        for w in frame.winfo_children():
            w.destroy()
        self.checkboxframe = ctk.CTkFrame(frame)
        self.checkboxframe.grid(row=0, column=0, sticky="nsew")
        self.classes = classes
        self.intvars = []
        self.checkboxes = []
        # maxrow = (len(classes) // 2) + 1
        self.checkboxframe.grid_columnconfigure(0, weight=1)
        self.checkboxframe.grid_columnconfigure(1, weight=1)
        for i in range(len(classes)):
            iv = ctk.IntVar(value=classes[i] in selected_classes)
            cb = ctk.CTkCheckBox(self.checkboxframe, text=self.classes[i],onvalue=1,offvalue=0,variable=iv,height=20)
            cb.grid(row=i//2,column=i%2, sticky="nsew")
            self.checkboxframe.grid_rowconfigure(i//2, weight=0)
            self.intvars.append(iv)
            self.checkboxes.append(cb)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_columnconfigure(0, weight=1)

    def get_selected_classes( self ):
        out = []
        for i in range(len(self.classes)):
            if( self.intvars[i].get() ):
                out.append( self.classes[i] )
        return out


class text_slider:
    def __init__(self, frame, text, variable, from_, to_):
        self.text = text
        self.mainframe = ctk.CTkFrame(frame)
        self.mainframe.grid(row=0, column=0, sticky="nsew")
        self.mainframe.grid_columnconfigure(0, weight=0)
        self.mainframe.grid_columnconfigure(1, weight=1)

        self.label = ctk.CTkLabel(self.mainframe, text=text,width=100)
        self.label.grid(row=0, column=0, sticky="w", padx=2, pady=2)
        self.slider = ctk.CTkSlider(self.mainframe, variable=variable, from_=from_, to=to_)
        self.slider.grid(row=0, column=1, sticky="ew", padx=2, pady=2)
        self.slider.bind("<Motion>", self.on_slider_change)

        value_text = str(self.get())
        show_text = self.text + "("+ value_text +")"
        self.label.configure(text=show_text)
    
    def get(self):
        return int(self.slider.get())

    def set(self, value):
        self.slider.set(value)

    def grid(self, **args):
        self.mainframe.grid(**args)

    def on_slider_change(self, event):
        value_text = str(self.get())
        show_text = self.text + "("+ value_text +")"
        self.label.configure(text=show_text)


class rgb_slider:
    def __init__(self, frame, r=0, g=0, b=0):
        self.mainframe = ctk.CTkFrame(frame)
        self.label = ctk.CTkLabel(self.mainframe, text="Color (0-255)")
        self.r = tk.IntVar(value=r)
        self.g = tk.IntVar(value=g)
        self.b = tk.IntVar(value=b)
        self.r_slider = text_slider(self.mainframe, "R", self.r, 0, 255)
        self.g_slider = text_slider(self.mainframe, "G", self.g, 0, 255)
        self.b_slider = text_slider(self.mainframe, "B", self.b, 0, 255)
        self.mainframe.grid_columnconfigure(0, weight=1)
        self.mainframe.grid_rowconfigure([0,1,2,3], weight=1)
        self.mainframe.grid(row=0, column=0, sticky="nsew")
        self.label.grid(row=0, column=0, sticky="ew")
        self.r_slider.grid(row=1, column=0, sticky="ew", padx=2, pady=2)
        self.g_slider.grid(row=2, column=0, sticky="ew", padx=2, pady=2)
        self.b_slider.grid(row=3, column=0, sticky="ew", padx=2, pady=2)

    def get(self):
        return (self.r_slider.get(), self.g_slider.get(), self.b_slider.get())
    
    def set(self, r, g, b):
        self.r_slider.set(r)
        self.g_slider.set(g)
        self.b_slider.set(b)
    
    def grid(self, **args):
        self.mainframe.grid(**args)
