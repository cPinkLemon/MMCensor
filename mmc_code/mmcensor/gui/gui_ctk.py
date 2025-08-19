import tkinter as tk
from tkinter import ttk, filedialog
from mmcensor.rt import mmc_realtime
import os
import sys
import importlib
import mmcensor.const as mmc_const
from functools import partial
import threading
import json
import customtkinter as ctk
from CTkListbox import CTkListbox

class mmc_gui_ctk:
    def initialize( self ):
        self.current_decorator_index = -1


        ctk.set_appearance_mode("light")
        self.root = ctk.CTk()

        # windows size and position
        width = 650
        height = 580
        screen_width = self.root.winfo_screenwidth() 
        screen_height = self.root.winfo_screenheight()
        window_size = f'{width}x{height}+{round((screen_width-width)/2)}+{round((screen_height-height)/2)}'
        self.root.geometry(window_size)
        self.root.resizable(False,False)

        self.root.title("MMCensor")
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)


        self.decorator_types = []
        self.maintabview = ctk.CTkTabview(self.root)
        self.maintabview.grid(row=0, column=0, padx=5, pady=5, sticky='nsew')
        
        self.decorator_tab = self.maintabview.add("Decorator")
        self.decorator_tab.grid_columnconfigure(0, weight=0)
        self.decorator_tab.grid_columnconfigure(1, weight=1)
        self.decorator_tab.grid_rowconfigure(0, weight=1)
        self.decorator_tab.grid_rowconfigure(1, weight=0)

        self.runtime_tab = self.maintabview.add("Runtime")
        self.runtime_tab.columnconfigure(0, weight=1)
        self.runtime_tab.rowconfigure(0, weight=0)
        self.runtime_tab.rowconfigure(1, weight=1)
        
        ### decorator tab
        self.decorators_frame_left = ctk.CTkFrame(self.decorator_tab,width=200)
        self.decorators_frame_left.grid(row=0, column=0, padx=0, pady=0, sticky='nsew')
        self.decorators_frame_left.grid_rowconfigure(0, weight=0)
        self.decorators_frame_left.grid_rowconfigure(1, weight=1)
        self.decorators_frame_left.grid_columnconfigure(0, weight=1)

        self.decorators_frame_right = ctk.CTkFrame(self.decorator_tab)
        self.decorators_frame_right.grid(row=0, column=1, padx=0, pady=0, sticky='nsew')
        
        self.decorators_select_frame = ctk.CTkFrame(self.decorators_frame_left)
        self.decorators_list_frame = ctk.CTkScrollableFrame(self.decorators_frame_left)
        self.decorators_select_frame.grid(row=0, column=0, padx=1, pady=1, sticky='nsew')
        self.decorators_list_frame.grid(row=1, column=0, padx=1, pady=1, sticky='nsew')
        self.decorators_list_frame.grid_columnconfigure(0, weight=1)
        self.decorators_select_frame.grid_columnconfigure(0, weight=1)
        self.decorators_select_frame.grid_columnconfigure(1, weight=0)

        self.decorator_selector_menu = ctk.CTkOptionMenu(self.decorators_select_frame, values=self.get_known_decorators())
        self.decorator_add_button = ctk.CTkButton(self.decorators_select_frame, text="Add", command=self.add_selected_decorator, width=80)
        self.decorator_selector_menu.grid(row=0, column=0, padx=4, pady=4, sticky='nsew')
        self.decorator_add_button.grid(row=0, column=1, padx=4, pady=4, sticky='nsew')

        self.decorator_config_frame = ctk.CTkScrollableFrame(self.decorators_frame_right)
        self.decorator_config_frame.grid(row=0, column=0, padx=2, pady=2, sticky='nsew')
        self.apply_config_button = ctk.CTkButton(self.decorators_frame_right, text="Apply Config", command=partial(self.apply_decorator_config))
        self.apply_config_button.grid(row=1, column=0, padx=2, pady=2, sticky='nsew')
        self.decorators_frame_right.grid_rowconfigure(0, weight=1)
        self.decorators_frame_right.grid_rowconfigure(1, weight=0)
        self.decorators_frame_right.grid_columnconfigure(0, weight=1)

        self.decorators_gui = []

        # save and load frame
        self.save_config_frame = ctk.CTkFrame(self.decorator_tab)
        self.save_config_frame.grid(row=1, column=0, padx=0, pady=0, sticky='nsew', columnspan=2)
        
        self.save_config_frame.grid_columnconfigure([0,1,2,3], weight=1)
        self.save_config_frame.grid_rowconfigure(0, weight=1)
        self.save_button = ctk.CTkButton(self.save_config_frame, text="Save", command=self.save_pushed)
        self.load_button = ctk.CTkButton(self.save_config_frame, text="Load", command=self.load_pushed)
        self.save_button.grid(row=0, column=0, padx=2, pady=2, sticky='nsew')
        self.load_button.grid(row=0, column=1, padx=2, pady=2, sticky='nsew')
        self.save_as_button = ctk.CTkButton(self.save_config_frame, text="Save As...", command=self.save_as)
        self.load_from_button = ctk.CTkButton(self.save_config_frame, text="Load From...", command=self.load_from)
        self.save_as_button.grid(row=0, column=2, padx=2, pady=2, sticky='nsew')
        self.load_from_button.grid(row=0, column=3, padx=2, pady=2, sticky='nsew')

        ### runtime tab
        self.runtime_frame_upper = ctk.CTkFrame(self.runtime_tab)
        self.runtime_frame_upper.grid(row=0, column=0, padx=1, pady=1, sticky='nsew')
        self.runtime_frame_lower = ctk.CTkFrame(self.runtime_tab)
        self.runtime_frame_lower.grid(row=1, column=0, padx=1, pady=1, sticky='nsew')
        
        for i in range(5):
            self.runtime_frame_upper.grid_columnconfigure(i, weight=1)
        self.runtime_frame_lower.grid_rowconfigure(0, weight=1)
        self.ready_button = ctk.CTkButton(self.runtime_frame_upper, text="Make Ready", command=self.make_ready_pushed)
        self.start_button = ctk.CTkButton(self.runtime_frame_upper, text="Start", command=self.start_pushed, state='disabled')
        self.stop_button = ctk.CTkButton(self.runtime_frame_upper, text="Stop", command=self.stop_pushed, state='disabled')
        self.refresh_windows_button = ctk.CTkButton(self.runtime_frame_upper, text="Refresh Windows List", command=self.refresh_hwnds)
        self.screenshot_button = ctk.CTkButton(self.runtime_frame_upper, text="Screenshot", command=self.screenshot_pushed)

        self.ready_button.grid(row=0, column=0, padx=2, pady=2, sticky='nsew')
        self.start_button.grid(row=0, column=1, padx=2, pady=2, sticky='nsew')
        self.stop_button.grid(row=0, column=2, padx=2, pady=2, sticky='nsew')
        self.refresh_windows_button.grid(row=0, column=3, padx=2, pady=2, sticky='nsew')
        self.screenshot_button.grid(row=0, column=4, padx=2, pady=2, sticky='nsew')

        self.runtime_frame_lower.grid_columnconfigure([0,1,2,3], weight=1)
        self.runtime_frame_lower.grid_rowconfigure(0, weight=1)
        self.runtime_frame_lower.grid_rowconfigure(1, weight=0)
        self.window_list = CTkListbox(self.runtime_frame_lower, multiple_selection=True)
        self.window_list.bind('<<ListboxSelect>>', self.change_hwnds_selection)
        self.window_list.grid(row=0, column=0, padx=2, pady=2, sticky='nsew', columnspan=4)

        self.size_checks = []
        for i in range(len(mmc_const.supported_sizes ) ):
            iv = tk.IntVar( value=(i<2) )
            ctk.CTkCheckBox( self.runtime_frame_lower, text='net size %s'%(mmc_const.supported_sizes[i],),onvalue=1,offvalue=0,variable=iv,command=self.update_sizes).grid(row=1,column=i,padx=2,pady=5,sticky='sew')
            self.size_checks.append( iv )

        ### runtime object
        self.rt = mmc_realtime()
        self.rt.initialize()
        self.rt.on_gray_callback = self.up
        self.rt.off_gray_callback = self.down
        
        # placeholder for realtime threads
        self.t_ready = None
        self.t_decorate = None

        self.known_hwnds = []

        self.refresh_hwnds()
        self.load_pushed()
        self.update_sizes()
        self.root.mainloop()

    def up( self ):
        self.root.attributes( '-topmost', True )

    def down( self ):
        self.root.attributes( '-topmost', False )

    def update_sizes( self ):
        sizes = []
        for i in range(len(mmc_const.supported_sizes)):
            if self.size_checks[i].get():
                sizes.append( mmc_const.supported_sizes[i] )

        self.rt.update_sizes(sizes)

    def get_known_decorators( self ):
        paths = [ f.name for f in os.scandir('mmcensor/decorate') if f.is_dir() ]
        if '__pycache__' in paths:
            paths.remove( '__pycache__' )
        return( paths )

    def add_selected_decorator( self ):
        if len(self.decorator_selector_menu.get() ):
            self.add_decorator( self.decorator_selector_menu.get() )

    def add_decorator( self, decorator_type ):
        decorator = importlib.import_module( 'mmcensor.decorate.%s'%decorator_type ).decorator()
        decorator.initialize( mmc_const.nudenet_v3_classes )
        self.rt.decorators.append( decorator )
        self.decorator_types.append( decorator_type )

        decorator_gui = ctk.CTkFrame(self.decorators_list_frame,height=50)
        decorator_gui.grid(row=len(self.decorators_gui), column=0, padx=2, pady=2, sticky='ew')
        decorator_close_button  = ctk.CTkButton(decorator_gui, text='x', command=partial(self.delete_decorator, len(self.decorators_gui)),width=30)
        decorator_close_button.grid(row=0, column=0, padx=2, pady=2, sticky='nsew')
        decorator_config_button = ctk.CTkButton(decorator_gui, text=decorator_type, command=partial(self.configure_decorator, len(self.decorators_gui)), fg_color="transparent", text_color="black", hover_color="lightblue", width=100)
        decorator_config_button.grid(row=0, column=1, padx=2, pady=2, sticky='nsew')
        decorator_config_button.configure()
        decorator_gui.grid_rowconfigure(0, weight=1)
        decorator_gui.grid_columnconfigure(0, weight=0)
        decorator_gui.grid_columnconfigure(1, weight=1)

        self.decorators_gui.append(decorator_gui)
        if len(self.rt.decorators) == 1:
            self.current_decorator_index = 0
            self.configure_decorator(0)

    def redraw_decorators( self ):
        for i, decorator_gui in enumerate(self.decorators_gui):
            decorator_gui.grid(row=i, column=0, padx=2, pady=2, sticky='ew')
            decorator_gui.children["!ctkbutton"].configure(command=partial(self.delete_decorator, i))
            decorator_gui.children["!ctkbutton2"].configure(command=partial(self.configure_decorator, i))

    def delete_decorator( self, index ):
        if self.current_decorator_index == -1:
            self.close_decorator_config()
        elif self.current_decorator_index == index:
            self.close_decorator_config()
            self.current_decorator_index = -1
        elif self.current_decorator_index > index:
            self.current_decorator_index -= 1
        elif self.current_decorator_index < index:
            pass
        print("current index:", self.current_decorator_index)
        self.rt.decorators.pop(index)
        self.decorator_types.pop(index)
        decorator_gui = self.decorators_gui.pop(index)
        decorator_gui.destroy()
        self.redraw_decorators()


    def configure_decorator( self, index ):
        self.current_decorator_index = index
        self.close_decorator_config()
        self.rt.decorators[index].populate_config_frame( self.decorator_config_frame )
        for i, decorator_gui in enumerate(self.decorators_gui):
            if i == index:
                decorator_gui.children["!ctkbutton2"].configure(fg_color="lightblue", text_color="black")
            else:
                decorator_gui.children["!ctkbutton2"].configure(fg_color="transparent", text_color="black")
        self.decorator_config_frame.grid(row=0,column=0, sticky='nsew')
    
    def apply_decorator_config(self):
        self.rt.decorators[self.current_decorator_index].apply_config_from_config_frame()

    def close_decorator_config(self):
        if self.current_decorator_index == -1:
            return
        if self.decorator_config_frame is not None:
            for child in self.decorator_config_frame.winfo_children():
                child.destroy()
        self.redraw_decorators()
    
    def save_pushed( self ):
        save_data = []
        for i in range( len( self.rt.decorators ) ):
            save_data.append( [ self.decorator_types[i], self.rt.decorators[i].export_settings() ] )

        with open('saved_settings.json', 'w') as f:
            json.dump( save_data, f )

    def load_pushed( self ):
        if not os.path.isfile( 'saved_settings.json' ):
            return

        with open('saved_settings.json' ) as data_file:
            save_data = json.load( data_file )

        
        for elt in self.decorators_gui:
            elt.destroy()
        self.decorators_gui.clear()
        self.rt.decorators.clear()
        self.decorator_types.clear()
        self.current_decorator_index = -1
        
        for elt in save_data:
            self.add_decorator( elt[0] )
            self.rt.decorators[-1].import_settings( elt[1] )

        self.redraw_decorators()
        self.close_decorator_config()
        self.current_decorator_index = -1
        if len(self.rt.decorators) > 0:
            self.current_decorator_index = 0
            self.configure_decorator(0)

    def save_as(self):
        save_data = []
        for i in range( len( self.rt.decorators ) ):
            save_data.append( [ self.decorator_types[i], self.rt.decorators[i].export_settings() ] )

        file_path = filedialog.asksaveasfilename(defaultextension=".json",
                                                 filetypes=[("JSON files", "*.json")],
                                                 initialfile="saved_settings.json")
        if not file_path:
            return

        try:
            with open(file_path, 'w') as f:
                json.dump(save_data, f)
        except Exception as e:
            print(f"Error saving file: {e}")

    def load_from(self):
        file_path = filedialog.askopenfilename(defaultextension=".json",
                                                filetypes=[("JSON files", "*.json")])
        if not file_path:
            return

        try:
            with open(file_path, 'r') as f:
                save_data = json.load(f)
        except Exception as e:
            print(f"Error loading file: {e}")
            return

        self.close_decorator_config()
        self.current_decorator_index = -1
        for elt in self.decorators_gui:
            elt.destroy()
        self.rt.decorators.clear()
        self.decorator_types.clear()

        for elt in save_data:
            self.add_decorator(elt[0])
            self.rt.decorators[-1].import_settings(elt[1])

        self.redraw_decorators()
        self.close_decorator_config()
        self.current_decorator_index = -1
        if len(self.rt.decorators) > 0:
            self.current_decorator_index = 0
            self.configure_decorator(0)

    def make_ready_pushed( self ):
        self.ready_button.configure(state='disabled')
        self.t_ready = threading.Thread( target=self.make_ready_async )
        self.t_ready.daemon = True
        self.t_ready.start()

    def make_ready_async( self ):
        self.rt.make_ready()
        self.start_button.configure(state='normal')

    def start_pushed( self ):
        self.start_button.configure(state='disabled')
        self.t_decorate = threading.Thread( target=self.start_async )
        self.t_decorate.daemon = True
        self.t_decorate.start()
        self.screenshot_button.configure(state='normal')
        self.stop_button.configure(state='normal')

    def start_async( self ):
        self.rt.go_decorate()
        self.start_button.configure(state='normal')
        self.screenshot_button.configure(state='disabled')
        self.stop_button.configure(state='disabled')

    def screenshot_pushed( self ):
        self.rt.take_screenshot()

    def stop_pushed( self ):
        self.rt.running = False

    def refresh_hwnds( self ):
        print( 'refresh triggered' )
        self.known_hwnds = self.rt.sc.get_hwnds() # [ [ hwnd, description ] ]
        self.window_list.delete("all")
        self.window_list.unbind('<<ListboxSelect>>')
        for i in range(len(self.known_hwnds)):
            self.window_list.insert(self.window_list.size(), self.known_hwnds[i][1])
            if self.known_hwnds[i][0] in self.rt.hwnds:
                self.window_list.activate(i)
        self.window_list.bind('<<ListboxSelect>>', self.change_hwnds_selection)
        for hwnd in self.rt.hwnds:
            if hwnd not in (x[0] for x in self.known_hwnds):
                self.rt.hwnds.remove(hwnd)

    def change_hwnds_selection( self, evt ):
        print( 'change triggered' )
        chosen = self.window_list.curselection()
        self.rt.hwnds.clear()
        for i in chosen:
            self.rt.hwnds.append( self.known_hwnds[i][0] )

    def on_close( self ):
        self.rt.detector_async.shutdown()
        self.rt.running = False
        sys.exit()

