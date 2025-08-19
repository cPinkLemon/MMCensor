import importlib
import tkinter as tk
import customtkinter as ctk
import cv2
import math
from mmcensor.decorate.decorator_utils import feature_selector_ctk, rgb_slider, text_slider
import mmcensor.geo as geo

class decorator:

    def initialize( self, known_classes ):
        self.known_classes = known_classes
        self.classes = []
        self.color = (0,0,0)
        self.expand = 0
        return

    def decorate( self, img, boxes ):
        boxes = geo.expand_boxes( boxes, self.expand)
        for box in boxes:
            if self.known_classes[box[1]] in self.classes:
                img = cv2.rectangle( img, (box[2],box[3]),(box[4],box[5]), tuple(reversed(self.color)), cv2.FILLED )
        return img

    def export_settings( self ):
        return( { 'classes': self.classes, 'color': self.color, 'expand': self.expand } )

    def import_settings( self, settings ):
        self.classes = settings['classes']
        self.color = settings['color']
        self.expand = settings['expand']

    def short_name( self ):
        return 'bar'

    def short_desc( self ):
        return '%d classes, color (%d,%d,%d)'%(len(self.classes),self.color[0], self.color[1], self.color[2] )

    def populate_config_frame( self, frame ):
        self.rgb_slider = rgb_slider(frame, *self.color)
        self.rgb_slider.grid(row=0, column=0, sticky="ew")

        self.expand_var = tk.IntVar()
        self.expand_var.set(self.expand)
        self.expand_slider = text_slider(frame, "Expand", self.expand_var, 0, 30)
        self.expand_slider.grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        
        self.feature_selector = feature_selector_ctk()
        class_frame = ctk.CTkFrame(frame)
        self.feature_selector.populate_frame(class_frame, self.known_classes, self.classes)
        class_frame.grid(row=2,column=0, padx=2, pady=2)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_rowconfigure(3, weight=0)

    def apply_config_from_config_frame( self ):
        self.classes = self.feature_selector.get_selected_classes()
        self.color = self.rgb_slider.get()
        self.expand = self.expand_slider.get()

    def destroy_config_frame( self ):
        return 0

