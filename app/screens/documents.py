#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Documents Screen
================================
Handles document processing, analysis, and management UI
"""

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, ListProperty, BooleanProperty
from kivy.metrics import dp
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
from kivy.core.window import Window
from typing import Optional, Dict, Any, List
import os
from pathlib import Path


class DocumentItem(MDBoxLayout):
    """Represents a document in the list"""
    pass


class DocumentActionButton(MDIconButton):
    """Action button for documents"""
    pass


class DocumentsScreen(MDScreen):
    """Documents AI screen for processing and analyzing documents"""
    
    document_list = ObjectProperty(None)
    file_manager = ObjectProperty(None)
    progress_bar = ObjectProperty(None)
    status_label = ObjectProperty(None)
    
    # Document processor instance
    document_processor = None
    summarizer = None
    translator = None
    search_engine = None
    
    # Current document
    current_document = None
    current_document_path = StringProperty('')
    
    # Processing state
    is_processing = BooleanProperty(False)
    processing_progress = 0
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.documents = []  # List of loaded documents
        self._init_runtime()
    
    def _init_runtime(self):
        """Initialize document processing components"""
        try:
            from documents.document_processor import DocumentProcessor
            from documents.summarizer import Summarizer
            from documents.translator import Translator
            from documents.search_engine import DocumentSearchEngine
            
            self.document_processor = DocumentProcessor()
            self.summarizer = Summarizer()
            self.translator = Translator()
            self.search_engine = DocumentSearchEngine()
            
            print("✅ Documents runtime initialized")
        except Exception as e:
            print(f"⚠️  Error initializing documents runtime: {e}")
            Snackbar(text=f"Error: {str(e)}").open()
    
    def on_pre_enter(self, *args):
        """Called before entering the screen"""
        self.refresh_document_list()
    
    def on_enter(self, *args):
        """Called when entering the screen"""
        pass
    
    def open_file_manager(self):
        """Open file manager to select a document"""
        if not self.file_manager:
            self.file_manager = MDFileManager(
                exit_manager=self.exit_file_manager,
                select_path=self.select_document,
                preview=True
            )
            self.file_manager.show('/')
        else:
            self.file_manager.show('/')
    
    def exit_file_manager(self, *args):
        """Exit file manager"""
        self.file_manager.close()
    
    def select_document(self, path: str):
        """Handle document selection"""
        self.exit_file_manager()
        
        # Check if file is supported
        supported_extensions = self.document_processor.get_supported_extensions()
        if not any(Path(path).suffix.lower() == ext for ext in supported_extensions):
            Snackbar(text=f"Unsupported file type: {Path(path).suffix}").open()
            return
        
        self.current_document_path = path
        self.process_document(path)
    
    def process_document(self, file_path: str):
        """Process a selected document"""
        if self.is_processing:
            Snackbar(text="Already processing a document").open()
            return
        
        self.is_processing = True
        self.progress_bar.value = 0
        self.status_label.text = f"Processing: {Path(file_path).name}..."
        
        # Process in background
        Clock.schedule_once(lambda dt: self._process_document_background(file_path), 0.1)
    
    def _process_document_background(self, file_path: str):
        """Process document in background"""
        try:
            # Process document
            processed = self.document_processor.process(file_path)
            
            if processed:
                # Add to search engine
                self.search_engine.add_document(
                    document_id=processed.metadata.file_path,
                    content=processed.content,
                    metadata={
                        'name': processed.metadata.file_name,
                        'type': processed.metadata.file_type.value,
                        'size': processed.metadata.file_size,
                        'path': processed.metadata.file_path
                    }
                )
                
                # Store document
                self.current_document = processed
                self.documents.append(processed)
                
                # Update UI
                self._update_document_ui(processed)
                
                self.status_label.text = f"✅ Processed: {processed.metadata.file_name}"
                Snackbar(text=f"Document processed: {processed.metadata.file_name}").open()
            else:
                self.status_label.text = "❌ Failed to process document"
                Snackbar(text="Failed to process document").open()
                
        except Exception as e:
            self.status_label.text = f"❌ Error: {str(e)}"
            Snackbar(text=f"Error: {str(e)}").open()
        finally:
            self.is_processing = False
            self.progress_bar.value = 100
    
    def _update_document_ui(self, document):
        """Update UI with document information"""
        # Clear existing items
        self.document_list.clear_widgets()
        
        # Add document card
        doc_card = self._create_document_card(document)
        self.document_list.add_widget(doc_card)
        
        # Extract and display sections
        sections = self.document_processor.extract_sections(document)
        for section in sections:
            section_item = TwoLineListItem(
                text=section.get('title', 'Untitled'),
                secondary_text=f"{len(section.get('content', '').split())} words"
            )
            section_item.bind(on_press=lambda instance, s=section: self.show_section_content(s))
            self.document_list.add_widget(section_item)
    
    def _create_document_card(self, document):
        """Create a card for the document"""
        card = MDCard(
            orientation='vertical',
            padding=dp(15),
            spacing=dp(10),
            radius=dp(15),
            elevation=5
        )
        
        # Title and metadata
        title_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40)
        )
        
        title_layout.add_widget(MDLabel(
            text=document.metadata.file_name,
            font_style='H6',
            halign='left'
        ))
        
        title_layout.add_widget(MDLabel(
            text=f"{document.metadata.file_type.value.upper()} • {document.metadata.file_size // 1024} KB",
            font_style='Caption',
            halign='right',
            theme_text_color='Secondary'
        ))
        
        card.add_widget(title_layout)
        
        # Stats
        stats_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(20),
            size_hint_y=None,
            height=dp(30)
        )
        
        stats_layout.add_widget(MDLabel(
            text=f"📄 {document.metadata.page_count} pages",
            font_style='Caption'
        ))
        
        stats_layout.add_widget(MDLabel(
            text=f"📝 {document.metadata.word_count} words",
            font_style='Caption'
        ))
        
        stats_layout.add_widget(MDLabel(
            text=f"🔤 {document.metadata.char_count} chars",
            font_style='Caption'
        ))
        
        card.add_widget(stats_layout)
        
        # Action buttons
        actions_layout = MDBoxLayout(
            orientation='horizontal',
            spacing=dp(10),
            size_hint_y=None,
            height=dp(40)
        )
        
        actions_layout.add_widget(MDTextButton(
            text="Summarize",
            on_press=lambda x: self.summarize_document(document)
        ))
        
        actions_layout.add_widget(MDTextButton(
            text="Translate",
            on_press=lambda x: self.translate_document(document)
        ))
        
        actions_layout.add_widget(MDTextButton(
            text="Search",
            on_press=lambda x: self.search_document(document)
        ))
        
        actions_layout.add_widget(MDTextButton(
            text="Outline",
            on_press=lambda x: self.show_outline(document)
        ))
        
        card.add_widget(actions_layout)
        
        return card
    
    def show_section_content(self, section: Dict[str, Any]):
        """Show content of a section"""
        content = section.get('content', '')
        
        dialog = MDDialog(
            title=section.get('title', 'Section'),
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        
        scroll = MDScrollView()
        content_label = MDLabel(
            text=content,
            size_hint_y=None,
            height=max(dp(400), len(content.split()) * dp(20)),
            text_size=(Window.width * 0.85, None),
            halign='left',
            valign='top'
        )
        
        scroll.add_widget(content_label)
        dialog.add_widget(scroll)
        
        dialog.add_widget(MDFlatButton(
            text="CLOSE",
            on_press=dialog.dismiss
        ))
        
        dialog.open()
    
    def summarize_document(self, document):
        """Summarize the current document"""
        if not document:
            Snackbar(text="No document selected").open()
            return
        
        self.is_processing = True
        self.status_label.text = "Generating summary..."
        
        Clock.schedule_once(lambda dt: self._summarize_background(document), 0.1)
    
    def _summarize_background(self, document):
        """Generate summary in background"""
        try:
            summary = self.summarizer.summarize(document.content)
            
            # Show summary dialog
            dialog = MDDialog(
                title=f"Summary of {document.metadata.file_name}",
                size_hint=(0.9, 0.8),
                auto_dismiss=False
            )
            
            scroll = MDScrollView()
            
            # Summary text
            summary_label = MDLabel(
                text=summary.text,
                size_hint_y=None,
                height=max(dp(400), len(summary.text.split()) * dp(20)),
                text_size=(Window.width * 0.85, None),
                halign='left',
                valign='top'
            )
            
            scroll.add_widget(summary_label)
            dialog.add_widget(scroll)
            
            # Stats
            stats = MDLabel(
                text=f"Original: {summary.original_length} words • Summary: {summary.summary_length} words • Ratio: {summary.ratio:.2f}x",
                font_style='Caption',
                halign='center'
            )
            dialog.add_widget(stats)
            
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
    
    def translate_document(self, document):
        """Translate the current document"""
        if not document:
            Snackbar(text="No document selected").open()
            return
        
        # Show language selection dialog
        dialog = MDDialog(
            title="Select Target Language",
            size_hint=(0.8, 0.6)
        )
        
        scroll = MDScrollView()
        list_view = MDList()
        
        for code, name in self.translator.get_supported_languages().items():
            item = TwoLineListItem(
                text=name,
                secondary_text=code,
                on_press=lambda x, c=code: self._translate_to_language(document, c, dialog)
            )
            list_view.add_widget(item)
        
        scroll.add_widget(list_view)
        dialog.add_widget(scroll)
        dialog.open()
    
    def _translate_to_language(self, document, language_code: str, dialog):
        """Translate document to selected language"""
        dialog.dismiss()
        
        self.is_processing = True
        self.status_label.text = f"Translating to {language_code}..."
        
        Clock.schedule_once(lambda dt: self._translate_background(document, language_code), 0.1)
    
    def _translate_background(self, document, language_code: str):
        """Translate in background"""
        try:
            translation = self.translator.translate(
                document.content,
                target_language=language_code
            )
            
            # Show translation dialog
            dialog = MDDialog(
                title=f"Translation to {self.translator.get_language_name(language_code)}",
                size_hint=(0.9, 0.8),
                auto_dismiss=False
            )
            
            scroll = MDScrollView()
            
            translation_label = MDLabel(
                text=translation.text,
                size_hint_y=None,
                height=max(dp(400), len(translation.text.split()) * dp(20)),
                text_size=(Window.width * 0.85, None),
                halign='left',
                valign='top'
            )
            
            scroll.add_widget(translation_label)
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
    
    def search_document(self, document):
        """Search within the current document"""
        if not document:
            Snackbar(text="No document selected").open()
            return
        
        # Show search dialog
        dialog = MDDialog(
            title="Search Document",
            size_hint=(0.8, 0.4)
        )
        
        content = MDBoxLayout(orientation='vertical', spacing=dp(10), padding=dp(10))
        
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
            on_press=lambda x: self._perform_search(document, search_field.text, dialog)
        )
        
        content.add_widget(search_button)
        dialog.add_widget(content)
        dialog.open()
    
    def _perform_search(self, document, query: str, dialog):
        """Perform search in document"""
        dialog.dismiss()
        
        if not query or not query.strip():
            Snackbar(text="Please enter a search query").open()
            return
        
        # Search in document content
        results = []
        content_lower = document.content.lower()
        query_lower = query.lower()
        
        # Find all occurrences
        start = 0
        while True:
            pos = content_lower.find(query_lower, start)
            if pos == -1:
                break
            
            # Get context around the match
            context_start = max(0, pos - 50)
            context_end = min(len(document.content), pos + len(query) + 50)
            context = document.content[context_start:context_end]
            
            results.append({
                'position': pos,
                'context': context,
                'snippet': f"...{context}..."
            })
            
            start = pos + len(query)
        
        if not results:
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
        
        for i, result in enumerate(results, 1):
            item = ThreeLineListItem(
                text=f"Result {i}",
                secondary_text=result['snippet'][:100] + "...",
                tertiary_text=f"Position: {result['position']}"
            )
            list_view.add_widget(item)
        
        scroll.add_widget(list_view)
        dialog.add_widget(scroll)
        
        dialog.add_widget(MDFlatButton(
            text="CLOSE",
            on_press=dialog.dismiss
        ))
        
        dialog.open()
    
    def show_outline(self, document):
        """Show document outline"""
        if not document:
            Snackbar(text="No document selected").open()
            return
        
        from documents.outliner import Outliner
        outliner = Outliner()
        outline = outliner.generate_outline(
            document.content,
            title=document.metadata.file_name
        )
        
        # Show outline dialog
        dialog = MDDialog(
            title=f"Outline: {outline.title}",
            size_hint=(0.9, 0.8),
            auto_dismiss=False
        )
        
        scroll = MDScrollView()
        list_view = MDList()
        
        def add_outline_items(items: list, level: int = 0):
            for item in items:
                indent = "  " * level
                list_view.add_widget(OneLineListItem(
                    text=f"{indent}{item.title}",
                    theme_text_color="Primary" if level == 0 else "Secondary"
                ))
                add_outline_items(item.children, level + 1)
        
        add_outline_items(outline.items)
        
        scroll.add_widget(list_view)
        dialog.add_widget(scroll)
        
        dialog.add_widget(MDFlatButton(
            text="CLOSE",
            on_press=dialog.dismiss
        ))
        
        dialog.open()
    
    def refresh_document_list(self):
        """Refresh the document list"""
        pass
    
    def clear_documents(self):
        """Clear all loaded documents"""
        self.documents.clear()
        self.current_document = None
        self.current_document_path = ''
        self.document_list.clear_widgets()
        self.search_engine.clear_index()
        
        Snackbar(text="All documents cleared").open()
    
    def on_back_button(self):
        """Handle back button press"""
        self.manager.current = 'home'


# Load KV language for documents screen
Builder.load_string('''
<DocumentItem>:
    orientation: 'horizontal'
    padding: dp(10)
    spacing: dp(10)
    size_hint_y: None
    height: dp(60)
    
    MDLabel:
        text: ''
        halign: 'left'
        font_style: 'Body1'
        size_hint_x: 0.7
    
    MDBoxLayout:
        orientation: 'horizontal'
        spacing: dp(5)
        size_hint_x: 0.3
        
        DocumentActionButton:
            icon: "file-document-outline"
            theme_text_color: "Primary"
            on_press: 
        
        DocumentActionButton:
            icon: "delete"
            theme_text_color: "Error"


<DocumentsScreen>:
    name: 'documents'
    
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        
        MDTopAppBar:
            title: "Documents AI"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: root.on_back_button()]]
            right_action_items: [["magnify", lambda x: root.search_document(root.current_document)], ["delete", lambda x: root.clear_documents()]]
            
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
        
        # Document list area
        ScrollView:
            id: scroll_view
            
            MDBoxLayout:
                id: document_list
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(10)
                size_hint_y: None
                height: max(self.minimum_height, root.height - dp(200))
                
        # Action buttons
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(60)
            
            MDRaisedButton:
                text: "Import Document"
                icon: "upload"
                on_press: root.open_file_manager()
                size_hint_x: 0.5
                
            MDRaisedButton:
                text: "New Scan"
                icon: "camera"
                on_press: root.scan_document()
                size_hint_x: 0.5
''')
