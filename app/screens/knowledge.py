#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Knowledge Base Screen
===================================
Handles knowledge management UI
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
from kivymd.uix.progressbar import MDProgressBar, MDCircularProgressBar
from kivymd.uix.card import MDCard
from kivymd.uix.filemanager import MDFileManager
from kivy.graphics import Color, Ellipse, Line
from kivy.core.image import Image as CoreImage
from typing import Optional, Dict, Any, List
import os
from pathlib import Path


class KnowledgeSiloCard(MDCard):
    """Card representing a knowledge silo"""
    pass


class KnowledgeGraphVisualization(MDBoxLayout):
    """Visualization of the knowledge graph"""
    pass


class KnowledgeScreen(MDScreen):
    """Knowledge Base screen"""
    
    silo_list = ObjectProperty(None)
    graph_container = ObjectProperty(None)
    file_manager = ObjectProperty(None)
    progress_bar = ObjectProperty(None)
    status_label = ObjectProperty(None)
    indexing_progress = ObjectProperty(None)
    
    # Knowledge base instance
    knowledge_base = None
    indexer = None
    graph = None
    
    # Processing state
    is_processing = BooleanProperty(False)
    is_indexing = BooleanProperty(False)
    indexing_progress_value = NumericProperty(0)
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_runtime()
    
    def _init_runtime(self):
        """Initialize knowledge base components"""
        try:
            from knowledge.knowledge_base import KnowledgeBase
            from knowledge.indexer import FileIndexer
            from knowledge.graph import KnowledgeGraph
            
            self.knowledge_base = KnowledgeBase()
            self.indexer = FileIndexer(self.knowledge_base)
            self.graph = KnowledgeGraph()
            
            print("✅ Knowledge Base runtime initialized")
            self._update_ui()
        except Exception as e:
            print(f"⚠️  Error initializing knowledge base: {e}")
            Snackbar(text=f"Error: {str(e)}").open()
    
    def on_pre_enter(self, *args):
        """Called before entering the screen"""
        self._update_ui()
    
    def _update_ui(self):
        """Update UI with current knowledge base state"""
        if not self.knowledge_base:
            return
        
        # Update stats
        stats = self.knowledge_base.get_stats()
        self.status_label.text = f"{stats['total_items']} items • {stats['total_silos']} silos"
        
        # Update silo list
        self._update_silo_list()
        
        # Update indexing progress
        if self.is_indexing:
            self.indexing_progress.value = self.indexing_progress_value
    
    def _update_silo_list(self):
        """Update the silo list"""
        if not self.knowledge_base:
            return
        
        self.silo_list.clear_widgets()
        
        silos = self.knowledge_base.get_all_silos()
        
        if not silos:
            # Add "no silos" message
            self.silo_list.add_widget(MDLabel(
                text="No knowledge silos yet. Tap + to create one.",
                halign='center',
                theme_text_color='Secondary'
            ))
            return
        
        for silo in silos:
            card = self._create_silo_card(silo)
            self.silo_list.add_widget(card)
    
    def _create_silo_card(self, silo):
        """Create a card for a knowledge silo"""
        card = KnowledgeSiloCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            radius=dp(16),
            elevation=2
        )
        
        # Header with color indicator
        header = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40)
        )
        
        # Color indicator
        color_box = MDBoxLayout(
            size_hint_x=None,
            width=dp(10),
            height=dp(10),
            radius=dp(5),
            md_bg_color=self._hex_to_rgba(silo.color)
        )
        header.add_widget(color_box)
        
        # Silo name and item count
        header.add_widget(MDLabel(
            text=silo.name,
            font_style='H6',
            halign='left'
        ))
        
        header.add_widget(MDBoxLayout(
            size_hint_x=0.5
        ))
        
        header.add_widget(MDLabel(
            text=f"{silo.item_count} items",
            font_style='Caption',
            halign='right',
            theme_text_color='Secondary'
        ))
        
        card.add_widget(header)
        
        # Description
        if silo.description:
            card.add_widget(MDLabel(
                text=silo.description,
                font_style='Body2',
                theme_text_color='Secondary',
                halign='left'
            ))
        
        # Size
        size_mb = silo.size_bytes / (1024 * 1024)
        card.add_widget(MDLabel(
            text=f"{size_mb:.2f} MB • {silo.updated_at}",
            font_style='Caption',
            theme_text_color='Secondary',
            halign='left'
        ))
        
        # Action buttons
        actions = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(35)
        )
        
        actions.add_widget(MDTextButton(
            text="View",
            size_hint_x=0.4,
            on_press=lambda x, s=silo: self.view_silo(s)
        ))
        
        actions.add_widget(MDTextButton(
            text="Add Files",
            size_hint_x=0.6,
            on_press=lambda x, s=silo: self.add_files_to_silo(s)
        ))
        
        card.add_widget(actions)
        
        return card
    
    def _hex_to_rgba(self, hex_color: str) -> Tuple[float, float, float, float]:
        """Convert hex color to RGBA tuple"""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) == 6:
            r = int(hex_color[0:2], 16) / 255.0
            g = int(hex_color[2:4], 16) / 255.0
            b = int(hex_color[4:6], 16) / 255.0
            return (r, g, b, 1.0)
        return (0.5, 0.5, 0.5, 1.0)
    
    def create_silo(self):
        """Create a new knowledge silo"""
        dialog = MDDialog(
            title="Create New Silo",
            size_hint=(0.8, 0.5)
        )
        
        content = MDBoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )
        
        name_field = MDTextField(
            hint_text="Silo Name",
            mode="rectangle"
        )
        
        desc_field = MDTextField(
            hint_text="Description (optional)",
            mode="rectangle",
            multiline=True
        )
        
        content.add_widget(name_field)
        content.add_widget(desc_field)
        
        dialog.add_widget(content)
        
        dialog.add_widget(MDRaisedButton(
            text="CREATE",
            size_hint=(1, None),
            height=dp(48),
            on_press=lambda x: self._create_silo_confirm(name_field.text, desc_field.text, dialog)
        ))
        
        dialog.open()
    
    def _create_silo_confirm(self, name: str, description: str, dialog):
        """Confirm and create silo"""
        if not name or not name.strip():
            Snackbar(text="Please enter a silo name").open()
            return
        
        dialog.dismiss()
        
        # Create silo
        silo = self.knowledge_base.create_silo(
            name=name.strip(),
            description=description.strip()
        )
        
        # Update UI
        self._update_silo_list()
        self._update_ui()
        
        Snackbar(text=f"Silo created: {name}").open()
    
    def view_silo(self, silo):
        """View items in a silo"""
        dialog = MDDialog(
            title=f"{silo.name}",
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        
        scroll = MDScrollView()
        list_view = MDList()
        
        # Get items in silo
        items = self.knowledge_base.get_items_in_silo(silo.id)
        
        if not items:
            list_view.add_widget(OneLineListItem(
                text="No items in this silo yet.",
                theme_text_color='Secondary'
            ))
        else:
            for item in items:
                list_view.add_widget(ThreeLineListItem(
                    text=item.title[:50] + "..." if len(item.title) > 50 else item.title,
                    secondary_text=item.content[:70] + "..." if len(item.content) > 70 else item.content,
                    tertiary_text=f"{item.source_type} • {len(item.content)} chars"
                ))
        
        scroll.add_widget(list_view)
        dialog.add_widget(scroll)
        
        dialog.add_widget(MDFlatButton(
            text="CLOSE",
            on_press=dialog.dismiss
        ))
        
        dialog.open()
    
    def add_files_to_silo(self, silo):
        """Add files to a silo"""
        self.current_silo = silo
        
        if not self.file_manager:
            self.file_manager = MDFileManager(
                exit_manager=self.exit_file_manager,
                select_path=self.select_file_for_silo,
                preview=True,
                multiselect=True
            )
            self.file_manager.show('/')
        else:
            self.file_manager.show('/')
    
    def exit_file_manager(self, *args):
        """Exit file manager"""
        self.file_manager.close()
    
    def select_file_for_silo(self, path: str):
        """Handle file selection for silo"""
        # In a real app, would handle multiple files
        # For now, just process the first file
        self.exit_file_manager()
        
        # Index the file
        self._index_file(path, self.current_silo.id)
    
    def _index_file(self, file_path: str, silo_id: str):
        """Index a file and add to silo"""
        self.is_processing = True
        self.status_label.text = f"Indexing: {Path(file_path).name}..."
        
        Clock.schedule_once(lambda dt: self._index_file_background(file_path, silo_id), 0.1)
    
    def _index_file_background(self, file_path: str, silo_id: str):
        """Index file in background"""
        try:
            # Index the file
            indexed = self.indexer.index_file(file_path, silo_id)
            
            if indexed:
                self.status_label.text = f"✅ Indexed: {Path(file_path).name}"
                Snackbar(text=f"File indexed: {Path(file_path).name}").open()
                
                # Update UI
                self._update_silo_list()
                self._update_ui()
            else:
                self.status_label.text = f"❌ Failed to index: {Path(file_path).name}"
                Snackbar(text=f"Failed to index file").open()
                
        except Exception as e:
            self.status_label.text = f"❌ Error: {str(e)}"
            Snackbar(text=f"Error: {str(e)}").open()
        finally:
            self.is_processing = False
    
    def index_folder(self):
        """Index an entire folder"""
        if not self.file_manager:
            self.file_manager = MDFileManager(
                exit_manager=self.exit_file_manager,
                select_path=self.select_folder_for_indexing,
                preview=False,
                dirselect=True
            )
            self.file_manager.show('/')
        else:
            self.file_manager.show('/')
    
    def select_folder_for_indexing(self, path: str):
        """Handle folder selection for indexing"""
        self.exit_file_manager()
        
        # Start indexing
        self._start_indexing(path)
    
    def _start_indexing(self, directory_path: str):
        """Start indexing a directory"""
        self.is_indexing = True
        self.is_processing = True
        self.indexing_progress_value = 0
        self.status_label.text = "Indexing files..."
        
        # Start indexing in background
        Clock.schedule_once(lambda dt: self._index_directory_background(directory_path), 0.1)
    
    def _index_directory_background(self, directory_path: str):
        """Index directory in background"""
        try:
            # Get all files in directory
            directory_path_obj = Path(directory_path)
            all_files = list(directory_path_obj.glob('**/*'))
            supported_extensions = self.indexer.get_supported_extensions()
            files_to_index = [
                f for f in all_files if f.is_file() and f.suffix.lower() in supported_extensions
            ]
            
            total_files = len(files_to_index)
            if total_files == 0:
                self.status_label.text = "No supported files found"
                self.is_indexing = False
                self.is_processing = False
                return
            
            # Index files one by one
            for i, file_path in enumerate(files_to_index):
                self.indexing_progress_value = (i + 1) / total_files * 100
                self.status_label.text = f"Indexing: {Path(file_path).name} ({i+1}/{total_files})"
                
                try:
                    self.indexer.index_file(str(file_path))
                except Exception as e:
                    print(f"⚠️  Error indexing {file_path}: {e}")
                
                # Update progress
                Clock.schedule_once(lambda dt: self._update_indexing_progress(), 0.1)
            
            self.status_label.text = f"✅ Indexed {total_files} files"
            Snackbar(text=f"Indexed {total_files} files").open()
            
            # Update UI
            self._update_silo_list()
            self._update_ui()
            
        except Exception as e:
            self.status_label.text = f"❌ Error: {str(e)}"
            Snackbar(text=f"Indexing error: {str(e)}").open()
        finally:
            self.is_indexing = False
            self.is_processing = False
            self.indexing_progress_value = 0
    
    def _update_indexing_progress(self):
        """Update indexing progress in UI"""
        self.indexing_progress.value = self.indexing_progress_value
    
    def search_knowledge(self):
        """Search the knowledge base"""
        dialog = MDDialog(
            title="Search Knowledge",
            size_hint=(0.8, 0.4)
        )
        
        content = MDBoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )
        
        search_field = MDTextField(
            hint_text="Enter search query...",
            mode="rectangle",
            multiline=False
        )
        
        content.add_widget(search_field)
        
        search_button = MDRaisedButton(
            text="Search",
            size_hint=(1, None),
            height=dp(48),
            on_press=lambda x: self._perform_search(search_field.text, dialog)
        )
        
        content.add_widget(search_button)
        dialog.add_widget(content)
        dialog.open()
    
    def _perform_search(self, query: str, dialog):
        """Perform knowledge search"""
        dialog.dismiss()
        
        if not query or not query.strip():
            Snackbar(text="Please enter a search query").open()
            return
        
        self.is_processing = True
        self.status_label.text = "Searching..."
        
        Clock.schedule_once(lambda dt: self._perform_search_background(query), 0.1)
    
    def _perform_search_background(self, query: str):
        """Perform search in background"""
        try:
            # Search knowledge base
            results = self.knowledge_base.semantic_search(query, limit=20)
            
            if not results:
                self.status_label.text = "No results found"
                Snackbar(text="No results found").open()
                return
            
            # Show results
            dialog = MDDialog(
                title=f"Search Results ({len(results)} found)",
                size_hint=(0.9, 0.8),
                auto_dismiss=False
            )
            
            scroll = MDScrollView()
            list_view = MDList()
            
            for result in results:
                list_view.add_widget(ThreeLineListItem(
                    text=result.title[:50] + "..." if len(result.title) > 50 else result.title,
                    secondary_text=result.content[:70] + "..." if len(result.content) > 70 else result.content,
                    tertiary_text=f"{result.source_type} • {result.metadata.get('file_name', '')}"
                ))
            
            scroll.add_widget(list_view)
            dialog.add_widget(scroll)
            
            dialog.add_widget(MDFlatButton(
                text="CLOSE",
                on_press=dialog.dismiss
            ))
            
            dialog.open()
            
            self.status_label.text = f"Found {len(results)} results"
            
        except Exception as e:
            self.status_label.text = f"❌ Error: {str(e)}"
            Snackbar(text=f"Search error: {str(e)}").open()
        finally:
            self.is_processing = False
    
    def view_graph(self):
        """View the knowledge graph"""
        if not self.graph:
            Snackbar(text="Graph not available").open()
            return
        
        # Generate layout
        layout = self.graph.generate_layout("circular")
        
        # Show graph visualization
        dialog = MDDialog(
            title="Knowledge Graph",
            size_hint=(0.95, 0.9),
            auto_dismiss=False
        )
        
        # Create visualization
        vis = KnowledgeGraphVisualization(
            size_hint=(1, 1),
            md_bg_color=(0.1, 0.1, 0.1, 0.8)
        )
        
        # Draw graph (simplified for demo)
        with vis.canvas:
            # Draw background
            Color(0.1, 0.1, 0.1, 0.8)
            
            # Draw nodes
            for node_id, node in self.graph.nodes.items():
                if node_id in layout.nodes:
                    x, y = layout.nodes[node_id]
                    
                    # Draw node
                    Color(*self._hex_to_rgba(node.color))
                    Ellipse(
                        pos=(x * vis.width - 15, y * vis.height - 15),
                        size=(30, 30)
                    )
                    
                    # Draw label
                    Color(1, 1, 1, 1)
                    # In a real app, would draw text
            
            # Draw edges
            Color(0.5, 0.5, 0.5, 0.5)
            for edge in self.graph.edges.values():
                if edge.source in layout.nodes and edge.target in layout.nodes:
                    sx, sy = layout.nodes[edge.source]
                    tx, ty = layout.nodes[edge.target]
                    
                    Line(
                        points=[
                            sx * vis.width, sy * vis.height,
                            tx * vis.width, ty * vis.height
                        ],
                        width=1
                    )
        
        dialog.add_widget(vis)
        dialog.add_widget(MDFlatButton(
            text="CLOSE",
            on_press=dialog.dismiss
        ))
        
        dialog.open()
    
    def get_stats(self):
        """Show knowledge base statistics"""
        if not self.knowledge_base:
            return
        
        stats = self.knowledge_base.get_stats()
        
        dialog = MDDialog(
            title="Knowledge Base Stats",
            size_hint=(0.7, 0.6)
        )
        
        content = MDBoxLayout(
            orientation='vertical',
            padding=dp(10),
            spacing=dp(10)
        )
        
        content.add_widget(MDLabel(
            text=f"Total Items: {stats['total_items']}",
            font_style='H6'
        ))
        
        content.add_widget(MDLabel(
            text=f"Total Silos: {stats['total_silos']}",
            font_style='H6'
        ))
        
        content.add_widget(MDLabel(
            text=f"Total Size: {stats['total_size'] / (1024 * 1024):.2f} MB",
            font_style='H6'
        ))
        
        content.add_widget(MDLabel(
            text=f"Last Updated: {time.ctime(stats['last_updated'])}",
            font_style='Caption'
        ))
        
        # Silo stats
        if stats.get('silo_stats'):
            content.add_widget(MDLabel(
                text="Silo Statistics:",
                font_style='H6',
                halign='left'
            ))
            
            for silo_id, silo_stat in stats['silo_stats'].items():
                content.add_widget(TwoLineListItem(
                    text=silo_stat['name'],
                    secondary_text=f"{silo_stat['item_count']} items • {silo_stat['size_mb']:.2f} MB"
                ))
        
        dialog.add_widget(content)
        dialog.add_widget(MDFlatButton(
            text="CLOSE",
            on_press=dialog.dismiss
        ))
        
        dialog.open()
    
    def clear_knowledge_base(self):
        """Clear the entire knowledge base"""
        if self.knowledge_base:
            self.knowledge_base.clear()
        if self.indexer:
            self.indexer.clear_index()
        if self.graph:
            self.graph.clear()
        
        self._update_ui()
        Snackbar(text="Knowledge base cleared").open()
    
    def on_back_button(self):
        """Handle back button press"""
        self.manager.current = 'home'


# Load KV language for knowledge screen
Builder.load_string('''
<KnowledgeSiloCard>:
    orientation: 'vertical'
    padding: dp(15)
    spacing: dp(10)
    radius: dp(16)
    elevation: 2
    md_bg_color: 0.1, 0.1, 0.1, 0.6


<KnowledgeGraphVisualization>:
    orientation: 'vertical'
    padding: dp(10)
    spacing: dp(10)


<KnowledgeScreen>:
    name: 'knowledge'
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        
        MDTopAppBar:
            title: "Knowledge Base"
            subtitle: "Manage your private intelligence"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: root.on_back_button()]]
            right_action_items: [["magnify", lambda x: root.search_knowledge()], ["chart-bar", lambda x: root.get_stats()]]
            
        # Local Knowledge Graph Section
        MDCard:
            orientation: 'vertical'
            padding: dp(15)
            spacing: dp(10)
            radius: dp(16)
            elevation: 1
            md_bg_color: 0.1, 0.1, 0.1, 0.6
            size_hint_y: None
            height: dp(200)
            
            MDBoxLayout:
                orientation: 'horizontal'
                spacing: dp(10)
                
                MDIcon:
                    icon: "graphql"
                    size: "32sp"
                    theme_text_color: "Primary"
                
                MDLabel:
                    text: "Local Knowledge Graph"
                    font_style: 'H6'
            
            MDLabel:
                text: "All data remains indexed locally on your device, ensuring total privacy and offline accessibility."
                font_style: 'Caption'
                theme_text_color: "Secondary"
                halign: 'left'
            
            MDBoxLayout:
                orientation: 'horizontal'
                spacing: dp(20)
                size_hint_y: None
                height: dp(60)
                
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(5)
                    
                    MDLabel:
                        text: "Indexed Files"
                        font_style: 'Caption'
                        theme_text_color: "Secondary"
                    
                    MDLabel:
                        id: indexed_files_label
                        text: "0"
                        font_style: 'H4'
                
                MDBoxLayout:
                    orientation: 'vertical'
                    spacing: dp(5)
                    
                    MDLabel:
                        text: "Auto-Indexing"
                        font_style: 'Caption'
                        theme_text_color: "Secondary"
                    
                    MDBoxLayout:
                        orientation: 'horizontal'
                        spacing: dp(5)
                        size_hint_y: None
                        height: dp(20)
                        
                        MDCircularProgressBar:
                            id: auto_indexing_progress
                            value: 82
                            size: dp(20)
                            size_hint: None, None
                            width: dp(20)
                            height: dp(20)
                        
                        MDLabel:
                            text: "82%"
                            font_style: 'Caption'
            
            MDLabel:
                text: "Processing 'Deep_Learning_ML_2.pdf'"
                font_style: 'Caption'
                theme_text_color: "Secondary"
                halign: 'left'
            
            MDRaisedButton:
                text: "View Graph"
                size_hint: 0.4, None
                height: dp(40)
                on_press: root.view_graph()
                pos_hint: {'center_x': 0.5}
        
        # Active Knowledge Silos Section
        MDLabel:
            text: "Active Knowledge Silos"
            font_style: 'H6'
            halign: 'left'
            padding: dp(10), dp(0)
            size_hint_y: None
            height: dp(40)
        
        ScrollView:
            id: scroll_view
            bar_width: dp(5)
            bar_color: 33/255, 150/255, 243/255, 0.5
            bar_inactive_color: 33/255, 150/255, 243/255, 0.2
            scroll_type: ['bars', 'content']
            
            MDBoxLayout:
                id: silo_list
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(10)
                size_hint_y: None
                height: max(self.minimum_height, root.height - dp(450))
                adaptive_height: True
        
        # Import Source Section
        MDLabel:
            text: "Import Source"
            font_style: 'H6'
            halign: 'left'
            padding: dp(10), dp(0)
            size_hint_y: None
            height: dp(40)
        
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(80)
            
            MDCard:
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(5)
                radius: dp(12)
                elevation: 1
                md_bg_color: 0.15, 0.15, 0.15, 0.6
                size_hint_x: 0.45
                
                MDIcon:
                    icon: "folder"
                    size: "24sp"
                    theme_text_color: "Primary"
                    halign: 'center'
                    pos_hint: {'center_x': 0.5}
                
                MDLabel:
                    text: "Local Folder"
                    font_style: 'Caption'
                    halign: 'center'
                
                MDLabel:
                    text: "PDF Docs"
                    font_style: 'Caption'
                    theme_text_color: "Secondary"
                    halign: 'center'
                
                MDRaisedButton:
                    text: "Browse"
                    size_hint: 0.8, None
                    height: dp(30)
                    on_press: root.index_folder()
                    pos_hint: {'center_x': 0.5}
            
            MDCard:
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(5)
                radius: dp(12)
                elevation: 1
                md_bg_color: 0.15, 0.15, 0.15, 0.6
                size_hint_x: 0.45
                
                MDIcon:
                    icon: "markdown"
                    size: "24sp"
                    theme_text_color: "Primary"
                    halign: 'center'
                    pos_hint: {'center_x': 0.5}
                
                MDLabel:
                    text: "Markdown"
                    font_style: 'Caption'
                    halign: 'center'
                
                MDLabel:
                    text: "UPL/HTS"
                    font_style: 'Caption'
                    theme_text_color: "Secondary"
                    halign: 'center'
                
                MDRaisedButton:
                    text: "Import"
                    size_hint: 0.8, None
                    height: dp(30)
                    on_press: root.import_markdown()
                    pos_hint: {'center_x': 0.5}
        
        # Auto-Indexing Toggle
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(40)
            
            MDLabel:
                text: "Auto-Indexing"
                font_style: 'Body1'
                halign: 'left'
            
            # In a real app, would have a toggle switch
            MDIconButton:
                icon: "toggle-switch"
                theme_text_color: "Primary"
                on_press: root.toggle_auto_indexing()
        
        # Status bar
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(40)
            
            MDLabel:
                id: status_label
                text: "0 items • 0 silos"
                halign: 'left'
                font_style: 'Caption'
                theme_text_color: "Secondary"
            
            MDProgressBar:
                id: indexing_progress
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
                text: "New Silo"
                icon: "plus"
                on_press: root.create_silo()
                size_hint_x: 0.48
                elevation: 2
                
            MDRaisedButton:
                text: "Clear All"
                icon: "delete"
                on_press: root.clear_knowledge_base()
                size_hint_x: 0.48
                elevation: 2
''')
