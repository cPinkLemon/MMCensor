import importlib
import tkinter as tk
import customtkinter as ctk
import cv2
from mmcensor.decorate.decorator_utils import feature_selector_ctk, text_slider
import mmcensor.geo as geo
import math

class decorator:

    def initialize( self, known_classes ):
        self.known_classes = known_classes
        self.classes = []
        self.strength = 10
        self.expand = 0
        self.soft = True

    def decorate( self, img, boxes ):
        boxes = geo.expand_boxes_bounded( boxes, self.expand, img)
        condensed = geo.condense_boxes_single( boxes )

        for feature in condensed:
            if self.known_classes[feature] in self.classes:
                for box_or in condensed[feature]:
                    box = box_or.copy()
                    w = box[4]-box[2]
                    h = box[5]-box[3]
                    factor = self.strength * min( w,h ) / 100
                    new_w = math.ceil( w/factor )
                    new_h = math.ceil( h/factor )
                    if self.soft:
                        inter = cv2.INTER_AREA
                    else:
                        inter = cv2.BORDER_DEFAULT
                    img[box[3]:box[5],box[2]:box[4]]=cv2.resize( cv2.resize( img[box[3]:box[5],box[2]:box[4]], (new_w,new_h), interpolation=inter ), (w,h), interpolation = cv2.INTER_NEAREST )

        return img

    def export_settings( self ):
        return( { 'classes': self.classes, 'strength': self.strength, 'harshness': self.expand, 'soft': self.soft } )

    def import_settings( self, settings ):
        self.classes = settings['classes']
        self.strength = settings['strength']
        self.expand = settings['harshness']
        self.soft = settings['soft']

    def short_name( self ):
        return 'pixel'

    def short_desc( self ):
        return '%d classes, strength %d'%(len(self.classes),self.strength)

    def populate_config_frame( self, frame ):
        self.strength_var = tk.IntVar()
        self.strength_var.set(self.strength)
        self.strength_slider = text_slider(frame, "Strength", self.strength_var, 1, 50)
        self.strength_slider.grid(row=0, column=0, padx=2, pady=2, sticky="ew")

        self.expand_var = tk.IntVar()
        self.expand_var.set(self.expand)
        self.expand_slider = text_slider(frame, "Expand", self.expand_var, 0, 30)
        self.expand_slider.grid(row=1, column=0, padx=2, pady=2, sticky="ew")
        
        self.soft_var = tk.BooleanVar()
        self.soft_var.set(self.soft)
        self.soft_switch = ctk.CTkSwitch(frame, text="Soft", variable=self.soft_var)
        self.soft_switch.grid(row=2, column=0, padx=20, pady=2, sticky="ew")

        self.feature_selector = feature_selector_ctk()
        class_frame = ctk.CTkFrame(frame)
        self.feature_selector.populate_frame(class_frame, self.known_classes, self.classes)
        class_frame.grid(row=3,column=0, padx=2, pady=2)

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_rowconfigure(0, weight=0)
        frame.grid_rowconfigure(1, weight=0)
        frame.grid_rowconfigure(2, weight=1)
        frame.grid_rowconfigure(3, weight=1)

    def apply_config_from_config_frame( self ):
        self.classes = self.feature_selector.get_selected_classes()
        self.strength = self.strength_var.get()
        self.expand = self.expand_var.get()
        self.soft = self.soft_var.get()

    def destroy_config_frame( self ):
        return 0

