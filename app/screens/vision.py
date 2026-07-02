#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Vision Screen
=============================
Handles image processing, OCR, and image generation UI
"""

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty, NumericProperty
from kivy.metrics import dp
from kivy.core.window import Window
from kivymd.uix.screen import MDScreen
from kivymd.uix.boxlayout import MDBoxLayout
from kivymd.uix.scrollview import MDScrollView
from kivymd.uix.label import MDLabel
from kivymd.uix.textfield import MDTextField
from kivymd.uix.button import MDRaisedButton, MDIconButton, MDTextButton, MDFlatButton
from kivymd.uix.list import OneLineListItem, TwoLineListItem, ThreeLineListItem, MDList
from kivymd.uix.dialog import MDDialog
from kivymd.uix.snackbar import Snackbar
from kivymd.uix.progressbar import MDProgressBar
from kivymd.uix.card import MDCard
from kivymd.uix.filemanager import MDFileManager
from kivymd.uix.dropdown import MDDropDownItem
from typing import Optional, Dict, Any, List
import os
from pathlib import Path


class VisionFeatureCard(MDCard):
    """Card for a vision feature"""
    pass


class ImagePreview(MDBoxLayout):
    """Preview of an image"""
    pass


class VisionScreen(MDScreen):
    """Vision & Image AI screen"""
    
    image_preview = ObjectProperty(None)
    file_manager = ObjectProperty(None)
    progress_bar = ObjectProperty(None)
    status_label = ObjectProperty(None)
    
    # Vision components
    ocr_processor = None
    image_analyzer = None
    image_generator = None
    
    # Current image
    current_image_path = StringProperty('')
    current_image_info = DictProperty({})
    
    # Processing state
    is_processing = BooleanProperty(False)
    processing_progress = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_runtime()
    
    def _init_runtime(self):
        """Initialize vision components"""
        try:
            from vision.ocr import OCRProcessor
            from vision.image_analyzer import ImageAnalyzer
            from vision.image_generator import ImageGenerator
            
            self.ocr_processor = OCRProcessor()
            self.image_analyzer = ImageAnalyzer()
            self.image_generator = ImageGenerator()
            
            print("✅ Vision runtime initialized")
        except Exception as e:
            print(f"⚠️  Error initializing vision runtime: {e}")
            Snackbar(text=f"Error: {str(e)}").open()
    
    def on_pre_enter(self, *args):
        """Called before entering the screen"""
        self._update_feature_cards()
    
    def _update_feature_cards(self):
        """Update feature cards with current status"""
        pass  # Cards are defined in KV
    
    def open_file_manager(self, feature: str = "ocr"):
        """Open file manager to select an image"""
        self.current_feature = feature
        
        if not self.file_manager:
            self.file_manager = MDFileManager(
                exit_manager=self.exit_file_manager,
                select_path=self.select_image,
                preview=True
            )
            self.file_manager.show('/')
        else:
            self.file_manager.show('/')
    
    def exit_file_manager(self, *args):
        """Exit file manager"""
        self.file_manager.close()
    
    def select_image(self, path: str):
        """Handle image selection"""
        self.exit_file_manager()
        
        # Check if it's an image file
        supported_extensions = ['.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp']
        if not any(Path(path).suffix.lower() in supported_extensions):
            Snackbar(text="Please select an image file").open()
            return
        
        self.current_image_path = path
        self._load_image(path)
    
    def _load_image(self, image_path: str):
        """Load and display an image"""
        try:
            # Get image info
            info = self.image_analyzer.get_image_info(image_path)
            self.current_image_info = info
            
            # Update UI
            self.status_label.text = f"Loaded: {Path(image_path).name} ({info.get('width', 0)}x{info.get('height', 0)})"
            
            # In a real app, would display the image
            # For now, just show info
            Snackbar(text=f"Image loaded: {Path(image_path).name}").open()
            
        except Exception as e:
            Snackbar(text=f"Error loading image: {str(e)}").open()
    
    def run_ocr(self):
        """Run OCR on the current image"""
        if not self.current_image_path:
            Snackbar(text="Please select an image first").open()
            return
        
        if self.is_processing:
            Snackbar(text="Already processing").open()
            return
        
        self.is_processing = True
        self.progress_bar.value = 0
        self.status_label.text = "Running OCR..."
        
        Clock.schedule_once(lambda dt: self._run_ocr_background(), 0.1)
    
    def _run_ocr_background(self):
        """Run OCR in background"""
        try:
            result = self.ocr_processor.process_image(self.current_image_path, 'eng')
            
            if result:
                # Show OCR result
                self._show_ocr_result(result)
                self.status_label.text = f"OCR Complete (Confidence: {result.confidence:.0%})"
            else:
                self.status_label.text = "OCR Failed"
                Snackbar(text="OCR failed").open()
                
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"
            Snackbar(text=f"OCR Error: {str(e)}").open()
        finally:
            self.is_processing = False
            self.progress_bar.value = 100
    
    def _show_ocr_result(self, result):
        """Show OCR result in a dialog"""
        dialog = MDDialog(
            title="OCR Result",
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        
        scroll = MDScrollView()
        
        # Create content with extracted text
        content = MDBoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )
        
        text_label = MDLabel(
            text=result.text,
            size_hint_y=None,
            height=max(dp(400), len(result.text.split()) * dp(20)),
            text_size=(Window.width * 0.85, None),
            halign='left',
            valign='top'
        )
        
        content.add_widget(text_label)
        
        # Add metadata
        meta_label = MDLabel(
            text=f"Language: {result.language} | Confidence: {result.confidence:.0%} | Regions: {len(result.regions)}",
            font_style='Caption',
            theme_text_color='Secondary'
        )
        content.add_widget(meta_label)
        
        scroll.add_widget(content)
        dialog.add_widget(scroll)
        
        dialog.add_widget(MDFlatButton(
            text="CLOSE",
            on_press=dialog.dismiss
        ))
        
        dialog.open()
    
    def analyze_image(self):
        """Analyze the current image"""
        if not self.current_image_path:
            Snackbar(text="Please select an image first").open()
            return
        
        if self.is_processing:
            Snackbar(text="Already processing").open()
            return
        
        self.is_processing = True
        self.progress_bar.value = 0
        self.status_label.text = "Analyzing image..."
        
        Clock.schedule_once(lambda dt: self._analyze_image_background(), 0.1)
    
    def _analyze_image_background(self):
        """Analyze image in background"""
        try:
            analysis = self.image_analyzer.analyze(self.current_image_path)
            
            if analysis:
                self._show_analysis_result(analysis)
                self.status_label.text = "Analysis Complete"
            else:
                self.status_label.text = "Analysis Failed"
                Snackbar(text="Analysis failed").open()
                
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"
            Snackbar(text=f"Analysis Error: {str(e)}").open()
        finally:
            self.is_processing = False
            self.progress_bar.value = 100
    
    def _show_analysis_result(self, analysis):
        """Show image analysis result"""
        dialog = MDDialog(
            title="Image Analysis",
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        
        scroll = MDScrollView()
        content = MDBoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )
        
        # Scene description
        if analysis.scene_description:
            scene_label = MDLabel(
                text=f"📝 Scene: {analysis.scene_description}",
                font_style='H6'
            )
            content.add_widget(scene_label)
        
        # Objects
        if analysis.objects:
            objects_label = MDLabel(
                text="🎯 Detected Objects:",
                font_style='H6'
            )
            content.add_widget(objects_label)
            
            for obj in analysis.objects:
                obj_item = TwoLineListItem(
                    text=obj['label'],
                    secondary_text=f"Confidence: {obj['confidence']:.0%}"
                )
                content.add_widget(obj_item)
        
        # Colors
        if analysis.dominant_colors:
            colors_label = MDLabel(
                text="🎨 Dominant Colors:",
                font_style='H6'
            )
            content.add_widget(colors_label)
            
            for color in analysis.dominant_colors[:3]:
                color_item = TwoLineListItem(
                    text=color['hex'],
                    secondary_text=f"{color['percentage']:.0f}%"
                )
                content.add_widget(color_item)
        
        # Technical info
        tech_label = MDLabel(
            text="⚙️  Technical Info:",
            font_style='H6'
        )
        content.add_widget(tech_label)
        
        tech_info = MDLabel(
            text=f"Size: {analysis.width}x{analysis.height} | Brightness: {analysis.brightness:.0%} | Contrast: {analysis.contrast:.0%}",
            font_style='Body2'
        )
        content.add_widget(tech_info)
        
        scroll.add_widget(content)
        dialog.add_widget(scroll)
        
        dialog.add_widget(MDFlatButton(
            text="CLOSE",
            on_press=dialog.dismiss
        ))
        
        dialog.open()
    
    def generate_image(self):
        """Generate an image from a prompt"""
        # Show prompt dialog
        dialog = MDDialog(
            title="Generate Image",
            size_hint=(0.8, 0.5)
        )
        
        content = MDBoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )
        
        prompt_field = MDTextField(
            hint_text="Describe the image you want to generate...",
            mode="rectangle",
            multiline=True,
            max_height=dp(150)
        )
        
        content.add_widget(prompt_field)
        
        # Model selection
        model_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40)
        )
        
        model_label = MDLabel(
            text="Model:",
            font_style='Body1',
            size_hint_x=0.3
        )
        model_layout.add_widget(model_label)
        
        model_button = MDTextButton(
            text=self.image_generator.current_model,
            size_hint_x=0.7
        )
        model_button.bind(on_press=self._show_model_selector)
        model_layout.add_widget(model_button)
        
        content.add_widget(model_layout)
        
        # Generate button
        generate_button = MDRaisedButton(
            text="Generate Image",
            size_hint=(1, None),
            height=dp(48),
            on_press=lambda x: self._start_generation(prompt_field.text, dialog)
        )
        
        content.add_widget(generate_button)
        dialog.add_widget(content)
        dialog.open()
    
    def _show_model_selector(self, instance):
        """Show model selection dropdown"""
        models = self.image_generator.get_available_models()
        
        dropdown_items = []
        for model_name, model_info in models.items():
            item = MDDropDownItem(
                text=model_info['name'],
                on_release=lambda x, m=model_name: self._select_model(m)
            )
            dropdown_items.append(item)
        
        # In a real app, would use MDDropdown
        # For now, just show a dialog
        dialog = MDDialog(
            title="Select Model",
            size_hint=(0.6, 0.4)
        )
        
        list_view = MDList()
        for item in dropdown_items:
            list_view.add_widget(item)
        
        dialog.add_widget(list_view)
        dialog.open()
    
    def _select_model(self, model_name: str):
        """Select a model"""
        self.image_generator.set_model(model_name)
        Snackbar(text=f"Model selected: {model_name}").open()
    
    def _start_generation(self, prompt: str, dialog):
        """Start image generation"""
        dialog.dismiss()
        
        if not prompt or not prompt.strip():
            Snackbar(text="Please enter a prompt").open()
            return
        
        self.is_processing = True
        self.progress_bar.value = 0
        self.status_label.text = "Generating image..."
        
        Clock.schedule_once(lambda dt: self._generate_image_background(prompt), 0.1)
    
    def _generate_image_background(self, prompt: str):
        """Generate image in background"""
        try:
            from vision.generation_engine import GenerationConfig
            
            config = GenerationConfig(
                prompt=prompt,
                width=512,
                height=512,
                steps=50,
                guidance_scale=7.5
            )
            
            result = self.image_generator.generate(prompt, config)
            
            if result:
                self.current_image_path = result.image_path
                self._load_image(result.image_path)
                self.status_label.text = f"Generated in {result.generation_time:.1f}s"
                Snackbar(text=f"Image generated: {result.image_path}").open()
            else:
                self.status_label.text = "Generation Failed"
                Snackbar(text="Image generation failed").open()
                
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"
            Snackbar(text=f"Generation Error: {str(e)}").open()
        finally:
            self.is_processing = False
            self.progress_bar.value = 100
    
    def describe_image(self):
        """Describe the current image"""
        if not self.current_image_path:
            Snackbar(text="Please select an image first").open()
            return
        
        self.is_processing = True
        self.status_label.text = "Describing image..."
        
        Clock.schedule_once(lambda dt: self._describe_image_background(), 0.1)
    
    def _describe_image_background(self):
        """Describe image in background"""
        try:
            description = self.image_analyzer.describe_image(self.current_image_path)
            
            dialog = MDDialog(
                title="Image Description",
                size_hint=(0.8, 0.6)
            )
            
            scroll = MDScrollView()
            content = MDLabel(
                text=description['description'],
                size_hint_y=None,
                height=max(dp(300), len(description['description']) * dp(15)),
                text_size=(Window.width * 0.75, None),
                halign='left',
                valign='top'
            )
            
            scroll.add_widget(content)
            dialog.add_widget(scroll)
            
            dialog.add_widget(MDFlatButton(
                text="CLOSE",
                on_press=dialog.dismiss
            ))
            
            dialog.open()
            
        except Exception as e:
            Snackbar(text=f"Error: {str(e)}").open()
        finally:
            self.is_processing = False
            self.status_label.text = "Ready"
    
    def extract_colors(self):
        """Extract colors from the current image"""
        if not self.current_image_path:
            Snackbar(text="Please select an image first").open()
            return
        
        self.is_processing = True
        self.status_label.text = "Extracting colors..."
        
        Clock.schedule_once(lambda dt: self._extract_colors_background(), 0.1)
    
    def _extract_colors_background(self):
        """Extract colors in background"""
        try:
            colors = self.image_analyzer.extract_colors(self.current_image_path, count=5)
            
            dialog = MDDialog(
                title="Color Palette",
                size_hint=(0.8, 0.5)
            )
            
            content = MDBoxLayout(
                orientation='vertical',
                padding=dp(10),
                spacing=dp(10)
            )
            
            for color in colors:
                color_item = TwoLineListItem(
                    text=color['hex'],
                    secondary_text=f"{color['percentage']:.0f}% of image"
                )
                content.add_widget(color_item)
            
            dialog.add_widget(content)
            dialog.add_widget(MDFlatButton(
                text="CLOSE",
                on_press=dialog.dismiss
            ))
            
            dialog.open()
            
        except Exception as e:
            Snackbar(text=f"Error: {str(e)}").open()
        finally:
            self.is_processing = False
            self.status_label.text = "Ready"
    
    def clear_image(self):
        """Clear the current image"""
        self.current_image_path = ''
        self.current_image_info = {}
        self.status_label.text = "Ready"
        Snackbar(text="Image cleared").open()
    
    def on_back_button(self):
        """Handle back button press"""
        self.manager.current = 'home'


# Load KV language for vision screen
Builder.load_string('''
<VisionFeatureCard>:
    orientation: 'vertical'
    padding: dp(20)
    spacing: dp(15)
    radius: dp(32)
    elevation: 2
    md_bg_color: app.theme_cls.bg_normal
    size_hint: 0.45, None
    height: dp(180)
    
    MDBoxLayout:
        orientation: 'vertical'
        spacing: dp(10)
        
        MDIcon:
            icon: root.ids['feature_icon'].text if hasattr(root, 'ids') else "image"
            size: "48sp"
            halign: 'center'
            pos_hint: {'center_x': 0.5}
            theme_text_color: "Primary"
            font_size: "48sp"
        
        MDLabel:
            id: feature_title
            text: "Feature Title"
            halign: 'center'
            font_style: 'H6'
        
        MDLabel:
            id: feature_description
            text: "Feature description"
            halign: 'center'
            font_style: 'Caption'
            theme_text_color: "Secondary"
        
        MDRaisedButton:
            text: "Open"
            pos_hint: {'center_x': 0.5}
            size_hint: 0.8, None
            height: dp(40)
            on_press: root.open_feature()


<VisionScreen>:
    name: 'vision'
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        
        MDTopAppBar:
            title: "Vision Suite"
            subtitle: "Synthesize Reality. Locally."
            elevation: 4
            left_action_items: [["arrow-left", lambda x: root.on_back_button()]]
            
        # Status bar
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(40)
            
            MDLabel:
                id: status_label
                text: "Ready"
                halign: 'left'
                font_style: 'Caption'
                theme_text_color: "Secondary"
            
            MDProgressBar:
                id: progress_bar
                value: 0
                size_hint_x: 0.7
        
        # Feature cards
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(15)
            size_hint_y: None
            height: dp(200)
            
            VisionFeatureCard:
                id: ocr_card
                
                MDIcon:
                    icon: "ocr"
                
                MDLabel:
                    id: feature_title
                    text: "Image-to-Text"
                
                MDLabel:
                    id: feature_description
                    text: "OCR & Document Scanning"
                
                MDRaisedButton:
                    text: "Open"
                    on_press: root.open_file_manager("ocr")
            
            VisionFeatureCard:
                id: analyze_card
                
                MDIcon:
                    icon: "image-search"
                
                MDLabel:
                    id: feature_title
                    text: "Analyze"
                
                MDLabel:
                    id: feature_description
                    text: "Understand image content"
                
                MDRaisedButton:
                    text: "Open"
                    on_press: root.open_file_manager("analyze")
        
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(15)
            size_hint_y: None
            height: dp(200)
            
            VisionFeatureCard:
                id: generate_card
                
                MDIcon:
                    icon: "palette"
                
                MDLabel:
                    id: feature_title
                    text: "Text-to-Image"
                
                MDLabel:
                    id: feature_description
                    text: "Synthesis"
                
                MDRaisedButton:
                    text: "Open"
                    on_press: root.generate_image()
            
            VisionFeatureCard:
                id: describe_card
                
                MDIcon:
                    icon: "eye"
                
                MDLabel:
                    id: feature_title
                    text: "Describe"
                
                MDLabel:
                    id: feature_description
                    text: "Natural language description"
                
                MDRaisedButton:
                    text: "Open"
                    on_press: root.describe_image()
        
        # Neural Engine Status
        MDCard:
            orientation: 'vertical'
            padding: dp(15)
            spacing: dp(10)
            radius: dp(16)
            elevation: 1
            md_bg_color: app.theme_cls.bg_normal
            
            MDBoxLayout:
                orientation: 'horizontal'
                spacing: dp(10)
                
                MDIcon:
                    icon: "chip"
                    size: "24sp"
                    theme_text_color: "Primary"
                
                MDLabel:
                    text: "Neural Engine Status"
                    font_style: 'H6'
            
            MDLabel:
                text: "Stable Diffusion XL"
                font_style: 'Body1'
                halign: 'left'
            
            MDBoxLayout:
                orientation: 'horizontal'
                spacing: dp(20)
                
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(5)
                    
                    MDLabel:
                        text: "VRAM Usage"
                        font_style: 'Caption'
                        theme_text_color: "Secondary"
                    
                    MDLabel:
                        text: "8.2 / 16GB"
                        font_style: 'Body2'
                
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(5)
                    
                    MDLabel:
                        text: "CPU Load"
                        font_style: 'Caption'
                        theme_text_color: "Secondary"
                    
                    MDLabel:
                        text: "24%"
                        font_style: 'Body2'
            
            MDProgressBar:
                value: 48.5
                size_hint_y: None
                height: dp(4)
        
        # Recent Generations
        MDLabel:
            text: "Recent Generations"
            font_style: 'H6'
            halign: 'left'
            padding: dp(10), dp(0)
            size_hint_y: None
            height: dp(40)
        
        ScrollView:
            id: scroll_view
            bar_width: dp(5)
            
            MDBoxLayout:
                id: recent_images
                orientation: 'horizontal'
                padding: dp(10)
                spacing: dp(10)
                size_hint_y: None
                height: dp(120)
                adaptive_width: True
''')
