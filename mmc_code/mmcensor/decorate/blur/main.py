import importlib
import tkinter as tk
import customtkinter as ctk
import cv2
from mmcensor.decorate.decorator_utils import feature_selector_ctk, text_slider
import mmcensor.geo as geo
import math
import numpy as np

class decorator:


    def initialize( self, known_classes ):
        self.known_classes = known_classes
        self.classes = []
        self.strength=10
        self.color = (1, 1, 1)
        self.circular = False
        self.expand = 0

    def decorate( self, img, boxes ):
        boxes = geo.expand_boxes( boxes, self.expand)
        condensed = geo.condense_boxes_single( boxes )

        for feature in condensed:
            if self.known_classes[feature] in self.classes:
                for box in condensed[feature]:
                    w = box[4]-box[2]
                    h = box[5]-box[3]
                    wr = w>>1
                    hr = h>>1
                    factor = 2 * math.ceil( self.strength * min( w,h ) / 100 /2 ) + 1
                    region = img[box[3]:box[5],box[2]:box[4]]
                    blur = cv2.blur( region, (factor,factor), cv2.BORDER_DEFAULT )
                    if self.circular:
                        mask = np.zeros(region.shape, np.uint8)
                        mask = cv2.ellipse(mask, (wr, hr), (wr, hr), 
                            0, 0, 360, self.color, -1)
                        img[box[3]:box[5],box[2]:box[4]] = region + blur*mask - region*mask
                    else:
                        img[box[3]:box[5],box[2]:box[4]] = blur

        return img

    def export_settings( self ):
        return( { 'classes': self.classes, 'strength': self.strength, 'circular': self.circular, 'expand': self.expand } )

    def import_settings( self, settings ):
        self.classes = settings['classes']
        self.strength = settings['strength']
        self.circular = settings['circular']
        self.expand = settings['expand']
        

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

        self.circular_var = tk.BooleanVar()
        self.circular_switch = ctk.CTkSwitch(frame, text="Circular", variable=self.circular_var)
        self.circular_switch.grid(row=2, column=0, padx=20, pady=2, sticky="ew")

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
        self.circular = self.circular_var.get()
        self.expand = self.expand_var.get()

    def destroy_config_frame( self ):
        return 0

