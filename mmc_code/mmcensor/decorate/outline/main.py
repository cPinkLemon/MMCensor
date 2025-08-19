import importlib
import tkinter as tk
import customtkinter as ctk
import cv2
from mmcensor.decorate.decorator_utils import feature_selector_ctk, rgb_slider, text_slider
import mmcensor.geo as geo

class decorator:

    def initialize( self, known_classes ):
        self.known_classes = known_classes
        self.classes = []
        self.color = (255,100,150)
        self.expand = 0
        self.circular = False
        return

    def decorate( self, img, boxes ):
        boxes = geo.expand_boxes_bounded( boxes, self.expand, img)
        condensed = geo.condense_boxes_single( boxes )

        for feature in condensed:
            if self.known_classes[feature] in self.classes:
                for box in condensed[feature]:
                    wr = (box[4] - box[2])>>1 # Width radius (half of diameter)
                    hr = (box[5] - box[3])>>1
                    if self.circular:
                        img = cv2.ellipse( img, (box[2] + wr, box[3] + hr), (wr, hr), 0, 0, 360, tuple(reversed(self.color)), 3)
                    else:
                        img = cv2.rectangle( img, (box[2],box[3]),(box[4],box[5]), tuple(reversed(self.color)), 3 )

        return img

    def export_settings( self ):
        return( { 'classes': self.classes, 'color': self.color, 'circular': self.circular, 'expand': self.expand } )

    def import_settings( self, settings ):
        self.classes = settings['classes']
        self.color = settings['color']
        self.circular = settings['circular']
        self.expand = settings['expand']

    def short_name( self ):
        return 'outline'

    def short_desc( self ):
        return '%d classes, color (%d,%d,%d)'%(len(self.classes),self.color[0], self.color[1], self.color[2] )

    def populate_config_frame( self, frame ):
        self.rgb_slider = rgb_slider(frame, *self.color)
        self.rgb_slider.grid(row=0, column=0, sticky="ew")

        self.expand_var = tk.IntVar()
        self.expand_var.set(self.expand)
        self.expand_slider = text_slider(frame, "Expand", self.expand_var, 0, 30)
        self.expand_slider.grid(row=1, column=0, padx=2, pady=2, sticky="ew")

        self.circular_var = tk.BooleanVar()
        self.circular_var.set(self.circular)
        self.circle_entry = ctk.CTkSwitch(frame, text="Circular", variable=self.circular_var)
        self.circle_entry.grid(row=2, column=0, padx=2, pady=2, sticky="ew")

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
        self.color = self.rgb_slider.get()
        self.circular = self.circular_var.get()
        self.expand = self.expand_var.get()

    def destroy_config_frame( self ):
        return 0

