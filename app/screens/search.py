#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Search Screen
=============================
Handles search functionality UI
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
from kivymd.uix.card import MDCard
from kivymd.uix.progressbar import MDProgressBar
from typing import Optional, Dict, Any, List


class SearchScreen(MDScreen):
    search_field = ObjectProperty(None)
    results_list = ObjectProperty(None)
    status_label = ObjectProperty(None)
    progress_bar = ObjectProperty(None)
    search_index = None
    is_searching = BooleanProperty(False)
    current_query = StringProperty('')
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_runtime()
    
    def _init_runtime(self):
        try:
            from search.search_index import SearchIndex
            self.search_index = SearchIndex()
            self._add_demo_documents()
            print(" Search runtime initialized")
        except Exception as e:
            print(f" Error initializing search: {e}")
            Snackbar(text=f"Error: {str(e)}").open()
    
    def _add_demo_documents(self):
        if not self.search_index:
            return
        demo_docs = [
            {'id': 'doc1', 'title': 'Introduction to AI', 'content': 'Artificial Intelligence (AI) is the simulation of human intelligence processes by machines, especially computer systems. These processes include learning, reasoning, and self-correction.', 'metadata': {'category': 'AI'}},
            {'id': 'doc2', 'title': 'Machine Learning Basics', 'content': 'Machine Learning is a subset of AI that focuses on building systems that learn from data, identify patterns, and make decisions with minimal human intervention.', 'metadata': {'category': 'AI'}},
            {'id': 'doc3', 'title': 'Deep Learning Applications', 'content': 'Deep Learning uses neural networks with many layers to model and solve complex problems. Applications include image recognition, natural language processing, and autonomous vehicles.', 'metadata': {'category': 'AI'}},
            {'id': 'doc4', 'title': 'Python Programming', 'content': 'Python is a high-level, interpreted programming language known for its readability and extensive standard library. It supports multiple programming paradigms.', 'metadata': {'category': 'Programming'}},
            {'id': 'doc5', 'title': 'Kivy Framework', 'content': 'Kivy is an open-source Python framework for developing multitouch applications. It supports Android, iOS, Linux, macOS, and Windows.', 'metadata': {'category': 'Programming'}}
        ]
        for doc in demo_docs:
            self.search_index.add_document(doc['id'], doc['title'], doc['content'], doc['metadata'])
    
    def on_pre_enter(self, *args):
        self.search_field.focus = True
    
    def perform_search(self):
        if not self.search_field or not self.search_field.text:
            return
        query = self.search_field.text.strip()
        if not query:
            return
        self.current_query = query
        self.is_searching = True
        self.status_label.text = f"Searching for: {query}"
        self.progress_bar.value = 0
        Clock.schedule_once(lambda dt: self._perform_search_background(query), 0.1)
    
    def _perform_search_background(self, query: str):
        try:
            if not self.search_index:
                self.status_label.text = "Search engine not available"
                self.is_searching = False
                return
            for i in range(0, 101, 25):
                Clock.schedule_once(lambda dt, p=i: self._update_search_progress(p), 0.1)
                import time
                time.sleep(0.1)
            results = self.search_index.hybrid_search(query, top_k=10)
            self._display_results(results)
            self.status_label.text = f"Found {len(results)} results for: {query}"
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"
            Snackbar(text=f"Search error: {str(e)}").open()
        finally:
            self.is_searching = False
            self.progress_bar.value = 100
    
    def _update_search_progress(self, progress: int):
        self.progress_bar.value = progress
    
    def _display_results(self, results: List[Any]):
        self.results_list.clear_widgets()
        if not results:
            self.results_list.add_widget(MDLabel(text="No results found. Try a different query.", halign='center', theme_text_color='Secondary', padding=dp(20)))
            return
        for i, result in enumerate(results, 1):
            card = self._create_result_card(result, i)
            self.results_list.add_widget(card)
    
    def _create_result_card(self, result: Any, rank: int):
        card = MDCard(orientation='vertical', padding=dp(15), spacing=dp(10), radius=dp(16), elevation=1, md_bg_color=(0.15, 0.15, 0.15, 0.4), size_hint_y=None, height=dp(120))
        header = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(30))
        rank_label = MDLabel(text=f"#{rank}", font_style='H6', theme_text_color='Primary', size_hint_x=None, width=dp(40))
        header.add_widget(rank_label)
        title_label = MDLabel(text=result.document_title, font_style='H6', halign='left')
        header.add_widget(title_label)
        card.add_widget(header)
        content_preview = result.content[:200] + "..." if len(result.content) > 200 else result.content
        card.add_widget(MDLabel(text=content_preview, font_style='Body2', theme_text_color='Secondary', halign='left'))
        footer = MDBoxLayout(orientation='horizontal', spacing=dp(20), size_hint_y=None, height=dp(25))
        score_label = MDLabel(text=f"Score: {result.combined_score:.2f}", font_style='Caption', theme_text_color='Secondary')
        footer.add_widget(score_label)
        category = result.metadata.get('category', 'General')
        category_label = MDLabel(text=f"Category: {category}", font_style='Caption', theme_text_color='Secondary')
        footer.add_widget(category_label)
        card.add_widget(footer)
        return card
    
    def perform_semantic_search(self):
        if not self.search_field or not self.search_field.text:
            return
        query = self.search_field.text.strip()
        if not query:
            return
        self.is_searching = True
        self.status_label.text = f"Semantic search: {query}"
        Clock.schedule_once(lambda dt: self._perform_semantic_search_background(query), 0.1)
    
    def _perform_semantic_search_background(self, query: str):
        try:
            if not self.search_index:
                return
            results = self.search_index.semantic_search(query, top_k=10)
            self._display_results(results)
            self.status_label.text = f"Semantic: Found {len(results)} results"
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"
        finally:
            self.is_searching = False
    
    def perform_keyword_search(self):
        if not self.search_field or not self.search_field.text:
            return
        query = self.search_field.text.strip()
        if not query:
            return
        self.is_searching = True
        self.status_label.text = f"Keyword search: {query}"
        Clock.schedule_once(lambda dt: self._perform_keyword_search_background(query), 0.1)
    
    def _perform_keyword_search_background(self, query: str):
        try:
            if not self.search_index:
                return
            results = self.search_index.keyword_search(query, top_k=10)
            self._display_results(results)
            self.status_label.text = f"Keyword: Found {len(results)} results"
        except Exception as e:
            self.status_label.text = f"Error: {str(e)}"
        finally:
            self.is_searching = False
    
    def show_search_options(self):
        dialog = MDDialog(title="Search Options", size_hint=(0.8, 0.4))
        content = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(MDTextButton(text="Hybrid Search (Default)", on_press=lambda x: self._select_search_type('hybrid', dialog)))
        content.add_widget(MDTextButton(text="Semantic Search", on_press=lambda x: self._select_search_type('semantic', dialog)))
        content.add_widget(MDTextButton(text="Keyword Search", on_press=lambda x: self._select_search_type('keyword', dialog)))
        dialog.add_widget(content)
        dialog.add_widget(MDFlatButton(text="CLOSE", on_press=dialog.dismiss))
        dialog.open()
    
    def _select_search_type(self, search_type: str, dialog):
        dialog.dismiss()
        if search_type == 'hybrid':
            self.perform_search()
        elif search_type == 'semantic':
            self.perform_semantic_search()
        elif search_type == 'keyword':
            self.perform_keyword_search()
    
    def clear_results(self):
        self.results_list.clear_widgets()
        self.search_field.text = ""
        self.status_label.text = "Enter a search query"
        self.current_query = ""
        Snackbar(text="Search cleared").open()
    
    def show_index_stats(self):
        if not self.search_index:
            return
        stats = self.search_index.get_statistics()
        dialog = MDDialog(title="Index Statistics", size_hint=(0.8, 0.4))
        content = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        content.add_widget(TwoLineListItem(text="Total Documents", secondary_text=str(stats['total_documents'])))
        content.add_widget(TwoLineListItem(text="Semantic Index", secondary_text=f"{stats['semantic_documents']} documents"))
        content.add_widget(TwoLineListItem(text="Keyword Index", secondary_text=f"{stats['keyword_documents']} documents"))
        dialog.add_widget(content)
        dialog.add_widget(MDFlatButton(text="CLOSE", on_press=dialog.dismiss))
        dialog.open()
    
    def on_back_button(self):
        self.manager.current = 'home'


Builder.load_string('''
<SearchScreen>:
    name: 'search'
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        MDTopAppBar:
            title: "Search"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: root.on_back_button()]]
            right_action_items: [["tune", lambda x: root.show_search_options()]]
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(60)
            MDTextField:
                id: search_field
                hint_text: "Search..."
                mode: "rectangle"
                size_hint_x: 0.85
                on_text_validate: root.perform_search()
            MDRaisedButton:
                text: "Search"
                icon: "magnify"
                on_press: root.perform_search()
                size_hint_x: 0.15
                elevation: 2
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(30)
            MDLabel:
                id: status_label
                text: "Enter a search query"
                halign: 'left'
                font_style: 'Caption'
                theme_text_color: "Secondary"
            MDProgressBar:
                id: progress_bar
                value: 0
                size_hint_x: 0.7
        ScrollView:
            bar_width: dp(5)
            bar_color: 33/255, 150/255, 243/255, 0.5
            bar_inactive_color: 33/255, 150/255, 243/255, 0.2
            scroll_type: ['bars', 'content']
            MDBoxLayout:
                id: results_list
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(10)
                size_hint_y: None
                height: max(self.minimum_height, root.height - dp(300))
                adaptive_height: True
        MDBoxLayout:
            orientation: 'horizontal'
            padding: dp(10)
            spacing: dp(10)
            size_hint_y: None
            height: dp(60)
            MDRaisedButton:
                text: "Clear"
                icon: "delete"
                on_press: root.clear_results()
                size_hint_x: 0.48
                elevation: 2
            MDRaisedButton:
                text: "Stats"
                icon: "chart-bar"
                on_press: root.show_index_stats()
                size_hint_x: 0.48
                elevation: 2
''')
