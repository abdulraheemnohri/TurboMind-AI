#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Models Screen
=============================
Handles model management UI
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
from typing import Optional, Dict, Any, List
import os
from pathlib import Path
import time


class ModelCard(MDCard):
    """Card representing a model"""
    pass


class ModelDownloadCard(MDCard):
    """Card for downloading a model"""
    pass


class ModelsScreen(MDScreen):
    """Models screen for managing AI models"""
    
    model_list = ObjectProperty(None)
    download_list = ObjectProperty(None)
    file_manager = ObjectProperty(None)
    progress_bar = ObjectProperty(None)
    status_label = ObjectProperty(None)
    
    # Model manager instance
    model_manager = None
    model_downloader = None
    benchmark_tool = None
    
    # Current state
    current_model_id = StringProperty('')
    is_processing = BooleanProperty(False)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_runtime()
    
    def _init_runtime(self):
        """Initialize model management components"""
        try:
            from models.model_manager import ModelManager
            from models.model_downloader import ModelDownloader
            from models.benchmark import ModelBenchmark
            
            self.model_manager = ModelManager()
            self.model_downloader = ModelDownloader()
            self.benchmark_tool = ModelBenchmark()
            
            print("✅ Models runtime initialized")
            self._update_ui()
        except Exception as e:
            print(f"⚠️  Error initializing models runtime: {e}")
            Snackbar(text=f"Error: {str(e)}").open()
    
    def on_pre_enter(self, *args):
        """Called before entering the screen"""
        self._update_ui()
    
    def _update_ui(self):
        """Update UI with current state"""
        if not self.model_manager:
            return
        
        # Update stats
        stats = self.model_manager.get_stats()
        self.status_label.text = f"{stats['downloaded_models']} Installed • {stats['total_storage_mb']:.2f} MB"
        
        # Update model lists
        self._update_installed_models()
        self._update_available_models()
    
    def _update_installed_models(self):
        """Update the installed models list"""
        if not self.model_manager:
            return
        
        self.model_list.clear_widgets()
        
        installed_models = self.model_manager.get_downloaded_models()
        
        if not installed_models:
            self.model_list.add_widget(MDLabel(
                text="No models installed. Download from the list below.",
                halign='center',
                theme_text_color='Secondary'
            ))
            return
        
        for model in installed_models:
            card = self._create_model_card(model)
            self.model_list.add_widget(card)
    
    def _update_available_models(self):
        """Update the available models list"""
        if not self.model_downloader:
            return
        
        self.download_list.clear_widgets()
        
        available_models = self.model_downloader.get_available_models()
        
        for model in available_models[:5]:  # Show top 5
            card = self._create_download_card(model)
            self.download_list.add_widget(card)
    
    def _create_model_card(self, model):
        """Create a card for an installed model"""
        card = ModelCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            radius=dp(16),
            elevation=2
        )
        
        # Header
        header = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40)
        )
        
        # Status indicator
        status_color = (0, 1, 0, 1) if model.is_loaded else (1, 1, 0, 1)
        status_box = MDBoxLayout(
            size_hint_x=None,
            width=dp(10),
            height=dp(10),
            radius=dp(5),
            md_bg_color=status_color
        )
        header.add_widget(status_box)
        
        # Model name
        header.add_widget(MDLabel(
            text=model.name,
            font_style='H6',
            halign='left'
        ))
        
        # Model type badge
        type_badge = MDLabel(
            text=model.model_type,
            font_style='Caption',
            halign='right',
            theme_text_color='Secondary'
        )
        header.add_widget(type_badge)
        
        card.add_widget(header)
        
        # Description
        if model.description:
            card.add_widget(MDLabel(
                text=model.description[:100] + "..." if len(model.description) > 100 else model.description,
                font_style='Body2',
                theme_text_color='Secondary',
                halign='left'
            ))
        
        # Stats
        stats_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(30)
        )
        
        stats_layout.add_widget(MDLabel(
            text=f"💾 {model.get_size_mb():.2f} MB",
            font_style='Caption'
        ))
        
        stats_layout.add_widget(MDLabel(
            text=f"🧠 {model.context_length / 1024:.1f}K Context",
            font_style='Caption'
        ))
        
        card.add_widget(stats_layout)
        
        # Action buttons
        actions = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(35)
        )
        
        if model.is_loaded:
            actions.add_widget(MDTextButton(
                text="Unload",
                size_hint_x=0.3,
                on_press=lambda x, m=model: self.unload_model(m)
            ))
        else:
            actions.add_widget(MDTextButton(
                text="Load",
                size_hint_x=0.3,
                on_press=lambda x, m=model: self.load_model(m)
            ))
        
        actions.add_widget(MDTextButton(
            text="Benchmark",
            size_hint_x=0.35,
            on_press=lambda x, m=model: self.benchmark_model(m)
        ))
        
        actions.add_widget(MDTextButton(
            text="Delete",
            size_hint_x=0.35,
            theme_text_color="Error",
            on_press=lambda x, m=model: self.delete_model(m)
        ))
        
        card.add_widget(actions)
        
        return card
    
    def _create_download_card(self, model):
        """Create a card for downloading a model"""
        card = ModelDownloadCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            radius=dp(16),
            elevation=1
        )
        
        # Header
        header = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40)
        )
        
        header.add_widget(MDLabel(
            text=model['name'],
            font_style='H6',
            halign='left'
        ))
        
        # Downloads and likes
        header.add_widget(MDBoxLayout(
            size_hint_x=0.5
        ))
        
        header.add_widget(MDLabel(
            text=f"⬇️ {model.get('downloads', '0')}",
            font_style='Caption',
            halign='right'
        ))
        
        card.add_widget(header)
        
        # Description
        if model.get('description'):
            card.add_widget(MDLabel(
                text=model['description'][:80] + "..." if len(model['description']) > 80 else model['description'],
                font_style='Body2',
                theme_text_color='Secondary',
                halign='left'
            ))
        
        # Tags
        tags = model.get('tags', [])
        if tags:
            tags_layout = MDBoxLayout(
                orientation='horizontal',
                spacing=dp(5),
                size_hint_y=None,
                height=dp(25)
            )
            
            for tag in tags[:3]:
                tags_layout.add_widget(MDLabel(
                    text=f"#{tag}",
                    font_style='Caption',
                    theme_text_color='Secondary'
                ))
            
            card.add_widget(tags_layout)
        
        # Stats
        stats_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(30)
        )
        
        stats_layout.add_widget(MDLabel(
            text=f"💾 {model.get('size', '0')}",
            font_style='Caption'
        ))
        
        stats_layout.add_widget(MDLabel(
            text=f"❤️ {model.get('likes', '0')}",
            font_style='Caption'
        ))
        
        card.add_widget(stats_layout)
        
        # Download button
        download_btn = MDRaisedButton(
            text="Download",
            size_hint=(1, None),
            height=dp(40),
            on_press=lambda x, m=model: self.download_model(m)
        )
        
        card.add_widget(download_btn)
        
        return card
    
    def load_model(self, model):
        """Load a model"""
        if not self.model_manager:
            return
        
        self.is_processing = True
        self.status_label.text = f"Loading {model.name}..."
        
        Clock.schedule_once(lambda dt: self._load_model_background(model), 0.1)
    
    def _load_model_background(self, model):
        """Load model in background"""
        try:
            success = self.model_manager.load_model(model.id)
            
            if success:
                self.status_label.text = f"✅ Loaded: {model.name}"
                Snackbar(text=f"Model loaded: {model.name}").open()
                self.model_manager.set_current_model(model.id)
            else:
                self.status_label.text = f"❌ Failed to load: {model.name}"
                Snackbar(text=f"Failed to load model").open()
                
            self._update_ui()
            
        except Exception as e:
            self.status_label.text = f"❌ Error: {str(e)}"
            Snackbar(text=f"Error: {str(e)}").open()
        finally:
            self.is_processing = False
    
    def unload_model(self, model):
        """Unload a model"""
        if not self.model_manager:
            return
        
        self.is_processing = True
        self.status_label.text = f"Unloading {model.name}..."
        
        Clock.schedule_once(lambda dt: self._unload_model_background(model), 0.1)
    
    def _unload_model_background(self, model):
        """Unload model in background"""
        try:
            success = self.model_manager.unload_model(model.id)
            
            if success:
                self.status_label.text = f"✅ Unloaded: {model.name}"
                Snackbar(text=f"Model unloaded: {model.name}").open()
            else:
                self.status_label.text = f"❌ Failed to unload: {model.name}"
                Snackbar(text=f"Failed to unload model").open()
                
            self._update_ui()
            
        except Exception as e:
            self.status_label.text = f"❌ Error: {str(e)}"
            Snackbar(text=f"Error: {str(e)}").open()
        finally:
            self.is_processing = False
    
    def download_model(self, model_data):
        """Download a model"""
        if not self.model_downloader:
            return
        
        model_id = model_data['id']
        model_name = model_data['name']
        
        # Get download URL
        url = self.model_downloader.get_model_url(model_id)
        if not url:
            Snackbar(text="Download URL not available").open()
            return
        
        # Start download
        self.is_processing = True
        self.status_label.text = f"Downloading {model_name}..."
        
        Clock.schedule_once(lambda dt: self._download_model_background(model_id, model_name, url), 0.1)
    
    def _download_model_background(self, model_id: str, model_name: str, url: str):
        """Download model in background"""
        try:
            # For demo, simulate download
            output_path = str(Path("models") / f"{model_id}.gguf")
            
            # Simulate download progress
            for i in range(0, 101, 10):
                Clock.schedule_once(lambda dt, p=i: self._update_download_progress(p), 0.1)
                time.sleep(0.1)
            
            # Add to model manager
            self.model_manager.add_custom_model({
                'id': model_id,
                'name': model_name,
                'description': f"Downloaded from {url}",
                'model_type': 'GGUF',
                'file_path': output_path,
                'file_size': 4 * 1024 * 1024 * 1024,  # 4 GB
                'context_length': 8192,
                'is_downloaded': True,
                'downloaded_at': time.time()
            })
            
            self.status_label.text = f"✅ Downloaded: {model_name}"
            Snackbar(text=f"Model downloaded: {model_name}").open()
            
            self._update_ui()
            
        except Exception as e:
            self.status_label.text = f"❌ Download failed: {str(e)}"
            Snackbar(text=f"Download error: {str(e)}").open()
        finally:
            self.is_processing = False
    
    def _update_download_progress(self, progress: int):
        """Update download progress"""
        self.progress_bar.value = progress
        self.status_label.text = f"Downloading... {progress}%"
    
    def benchmark_model(self, model):
        """Benchmark a model"""
        if not self.benchmark_tool:
            return
        
        self.is_processing = True
        self.status_label.text = f"Benchmarking {model.name}..."
        
        Clock.schedule_once(lambda dt: self._benchmark_model_background(model), 0.1)
    
    def _benchmark_model_background(self, model):
        """Benchmark model in background"""
        try:
            results = self.benchmark_tool.run_benchmark(
                model_id=model.id,
                model_name=model.name
            )
            
            overall_score = self.benchmark_tool.calculate_overall_score(model.id)
            
            # Show results
            dialog = MDDialog(
                title=f"Benchmark Results: {model.name}",
                size_hint=(0.8, 0.6)
            )
            
            content = MDBoxLayout(
                orientation='vertical',
                padding=dp(10),
                spacing=dp(10)
            )
            
            content.add_widget(MDLabel(
                text=f"Overall Score: {overall_score:.2f}/100",
                font_style='H6',
                halign='center'
            ))
            
            for result in results:
                content.add_widget(TwoLineListItem(
                    text=result.test_name,
                    secondary_text=f"Score: {result.score:.2f} • Time: {result.time_elapsed:.2f}s"
                ))
            
            dialog.add_widget(content)
            dialog.add_widget(MDFlatButton(
                text="CLOSE",
                on_press=dialog.dismiss
            ))
            
            dialog.open()
            
            self.status_label.text = f"✅ Benchmarked: {model.name}"
            
        except Exception as e:
            self.status_label.text = f"❌ Error: {str(e)}"
            Snackbar(text=f"Benchmark error: {str(e)}").open()
        finally:
            self.is_processing = False
    
    def delete_model(self, model):
        """Delete a model"""
        if not self.model_manager:
            return
        
        # Confirm deletion
        dialog = MDDialog(
            title=f"Delete {model.name}",
            text=f"Are you sure you want to delete {model.name}? This cannot be undone.",
            size_hint=(0.8, 0.4)
        )
        
        dialog.add_widget(MDFlatButton(
            text="CANCEL",
            on_press=dialog.dismiss
        ))
        
        dialog.add_widget(MDRaisedButton(
            text="DELETE",
            theme_text_color="Error",
            on_press=lambda x: self._delete_model_confirm(model, dialog)
        ))
        
        dialog.open()
    
    def _delete_model_confirm(self, model, dialog):
        """Confirm and delete model"""
        dialog.dismiss()
        
        self.is_processing = True
        self.status_label.text = f"Deleting {model.name}..."
        
        Clock.schedule_once(lambda dt: self._delete_model_background(model), 0.1)
    
    def _delete_model_background(self, model):
        """Delete model in background"""
        try:
            success = self.model_manager.delete_model(model.id)
            
            if success:
                self.status_label.text = f"✅ Deleted: {model.name}"
                Snackbar(text=f"Model deleted: {model.name}").open()
            else:
                self.status_label.text = f"❌ Failed to delete: {model.name}"
                Snackbar(text=f"Failed to delete model").open()
                
            self._update_ui()
            
        except Exception as e:
            self.status_label.text = f"❌ Error: {str(e)}"
            Snackbar(text=f"Error: {str(e)}").open()
        finally:
            self.is_processing = False
    
    def import_model(self):
        """Import a model from file"""
        if not self.file_manager:
            self.file_manager = MDFileManager(
                exit_manager=self.exit_file_manager,
                select_path=self.select_model_file,
                preview=False
            )
            self.file_manager.show('/')
        else:
            self.file_manager.show('/')
    
    def exit_file_manager(self, *args):
        """Exit file manager"""
        self.file_manager.close()
    
    def select_model_file(self, path: str):
        """Handle model file selection"""
        self.exit_file_manager()
        
        # Check if it's a model file
        supported_extensions = ['.gguf', '.onnx', '.pt', '.pth', '.safetensors']
        if not any(Path(path).suffix.lower() in supported_extensions):
            Snackbar(text="Please select a model file (GGUF, ONNX, PT, etc.)").open()
            return
        
        # Import the model
        self._import_model_file(path)
    
    def _import_model_file(self, file_path: str):
        """Import a model file"""
        self.is_processing = True
        self.status_label.text = f"Importing {Path(file_path).name}..."
        
        Clock.schedule_once(lambda dt: self._import_model_file_background(file_path), 0.1)
    
    def _import_model_file_background(self, file_path: str):
        """Import model file in background"""
        try:
            # For demo, just add to model manager
            model_name = Path(file_path).stem.replace('-', ' ').title()
            model_id = Path(file_path).stem.lower().replace('-', '_')
            
            self.model_manager.add_custom_model({
                'id': model_id,
                'name': model_name,
                'description': f"Imported from {file_path}",
                'model_type': Path(file_path).suffix.upper().replace('.', ''),
                'file_path': file_path,
                'file_size': Path(file_path).stat().st_size,
                'is_downloaded': True,
                'downloaded_at': time.time()
            })
            
            self.status_label.text = f"✅ Imported: {model_name}"
            Snackbar(text=f"Model imported: {model_name}").open()
            
            self._update_ui()
            
        except Exception as e:
            self.status_label.text = f"❌ Error: {str(e)}"
            Snackbar(text=f"Import error: {str(e)}").open()
        finally:
            self.is_processing = False
    
    def view_leaderboard(self):
        """View benchmark leaderboard"""
        if not self.benchmark_tool:
            Snackbar(text="Benchmark tool not available").open()
            return
        
        leaderboard = self.benchmark_tool.get_leaderboard()
        
        if not leaderboard:
            Snackbar(text="No benchmark results yet").open()
            return
        
        dialog = MDDialog(
            title="Benchmark Leaderboard",
            size_hint=(0.8, 0.6)
        )
        
        scroll = MDScrollView()
        list_view = MDList()
        
        for i, entry in enumerate(leaderboard, 1):
            list_view.add_widget(ThreeLineListItem(
                text=f"{i}. {entry['model_name']}",
                secondary_text=f"Score: {entry['overall_score']:.2f}/100",
                tertiary_text=f"Tests: {entry['test_count']}"
            ))
        
        scroll.add_widget(list_view)
        dialog.add_widget(scroll)
        
        dialog.add_widget(MDFlatButton(
            text="CLOSE",
            on_press=dialog.dismiss
        ))
        
        dialog.open()
    
    def get_recommendations(self):
        """Get model recommendations"""
        if not self.benchmark_tool:
            Snackbar(text="Benchmark tool not available").open()
            return
        
        dialog = MDDialog(
            title="Model Recommendations",
            size_hint=(0.8, 0.5)
        )
        
        content = MDBoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )
        
        use_cases = ['general', 'speed', 'quality', 'memory']
        
        for use_case in use_cases:
            recommendations = self.benchmark_tool.get_recommendations(use_case)
            
            if recommendations:
                content.add_widget(MDLabel(
                    text=f"{use_case.upper()}:",
                    font_style='H6'
                ))
                
                for rec in recommendations:
                    content.add_widget(TwoLineListItem(
                        text=rec['model_name'],
                        secondary_text=f"Score: {rec['overall_score']:.2f}"
                    ))
        
        dialog.add_widget(content)
        dialog.add_widget(MDFlatButton(
            text="CLOSE",
            on_press=dialog.dismiss
        ))
        
        dialog.open()
    
    def on_back_button(self):
        """Handle back button press"""
        self.manager.current = 'home'


# Load KV language for models screen
Builder.load_string('''
<ModelCard>:
    orientation: 'vertical'
    padding: dp(15)
    spacing: dp(10)
    radius: dp(16)
    elevation: 2
    md_bg_color: 0.1, 0.1, 0.1, 0.6
    size_hint_y: None
    height: dp(160)


<ModelDownloadCard>:
    orientation: 'vertical'
    padding: dp(15)
    spacing: dp(10)
    radius: dp(16)
    elevation: 1
    md_bg_color: 0.15, 0.15, 0.15, 0.4
    size_hint_y: None
    height: dp(170)


<ModelsScreen>:
    name: 'models'
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        
        MDTopAppBar:
            title: "Model Manager"
            subtitle: "Local & Encrypted"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: root.on_back_button()]]
            right_action_items: [["trophy", lambda x: root.view_leaderboard()], ["lightbulb", lambda x: root.get_recommendations()]]
            
        # Neural Engine Status
        MDCard:
            orientation: 'vertical'
            padding: dp(15)
            spacing: dp(10)
            radius: dp(16)
            elevation: 1
            md_bg_color: 0.1, 0.1, 0.1, 0.6
            size_hint_y: None
            height: dp(120)
            
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
                text: "Llama 3 8B"
                font_style: 'Body1'
                halign: 'left'
            
            MDLabel:
                text: "(Quantized)"
                font_style: 'Caption'
                theme_text_color: "Secondary"
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
                        text: "6.4 / 16GB"
                        font_style: 'Body2'
                
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(5)
                    
                    MDLabel:
                        text: "Context Size"
                        font_style: 'Caption'
                        theme_text_color: "Secondary"
                    
                    MDLabel:
                        text: "8192 Tokens"
                        font_style: 'Body2'
            
            MDRaisedButton:
                text: "Benchmark"
                size_hint: 0.4, None
                height: dp(35)
                on_press: root.benchmark_model(root.model_manager.get_current_model()) if root.model_manager and root.model_manager.get_current_model() else None
                elevation: 2
        
        # Installed Models Section
        MDLabel:
            text: "Installed Models"
            font_style: 'H6'
            halign: 'left'
            padding: dp(10), dp(0)
            size_hint_y: None
            height: dp(40)
        
        ScrollView:
            id: scroll_view_installed
            bar_width: dp(5)
            bar_color: 33/255, 150/255, 243/255, 0.5
            bar_inactive_color: 33/255, 150/255, 243/255, 0.2
            scroll_type: ['bars', 'content']
            
            MDBoxLayout:
                id: model_list
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(10)
                size_hint_y: None
                height: max(self.minimum_height, root.height - dp(500))
                adaptive_height: True
        
        # Available for Download Section
        MDLabel:
            text: "Available for Download"
            font_style: 'H6'
            halign: 'left'
            padding: dp(10), dp(0)
            size_hint_y: None
            height: dp(40)
        
        ScrollView:
            id: scroll_view_available
            bar_width: dp(5)
            bar_color: 33/255, 150/255, 243/255, 0.5
            bar_inactive_color: 33/255, 150/255, 243/255, 0.2
            scroll_type: ['bars', 'content']
            
            MDBoxLayout:
                id: download_list
                orientation: 'horizontal'
                padding: dp(10)
                spacing: dp(10)
                size_hint_y: None
                height: dp(180)
                adaptive_width: True
        
        # Status bar
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(40)
            
            MDLabel:
                id: status_label
                text: "0 Installed • 0 MB"
                halign: 'left'
                font_style: 'Caption'
                theme_text_color: "Secondary"
            
            MDProgressBar:
                id: progress_bar
                value: 0
                size_hint_x: 0.7
        
        # Action buttons
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(60)
            
            MDRaisedButton:
                text: "Import Model"
                icon: "upload"
                on_press: root.import_model()
                size_hint_x: 0.48
                elevation: 2
                
            MDRaisedButton:
                text: "Refresh"
                icon: "refresh"
                on_press: root._update_ui()
                size_hint_x: 0.48
                elevation: 2
''')
