#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Settings Screen
===============================
Handles application settings UI
"""

from kivy.lang import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, StringProperty, BooleanProperty, NumericProperty
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
from kivymd.uix.switch import MDSwitch
from kivymd.uix.slider import MDSlider
from typing import Optional, Dict, Any, List


class SettingsScreen(MDScreen):
    settings_list = ObjectProperty(None)
    app_settings = None
    privacy_settings = None
    theme_settings = None
    model_settings = None
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._init_runtime()
    
    def _init_runtime(self):
        try:
            from settings.app_settings import AppSettings
            from settings.privacy_settings import PrivacySettings
            from settings.theme_settings import ThemeSettings
            from settings.model_settings import ModelSettings
            self.app_settings = AppSettings()
            self.privacy_settings = PrivacySettings()
            self.theme_settings = ThemeSettings()
            self.model_settings = ModelSettings()
            print(" Settings runtime initialized")
            self._update_ui()
        except Exception as e:
            print(f" Error initializing settings: {e}")
            Snackbar(text=f"Error: {str(e)}").open()
    
    def on_pre_enter(self, *args):
        self._update_ui()
    
    def _update_ui(self):
        if not self.app_settings:
            return
        self.settings_list.clear_widgets()
        self._add_section_header("General Settings")
        self._add_setting_item("translate", "Language", self.app_settings.get_setting('language', 'en').upper(), self.show_language_dialog)
        self._add_setting_item("palette", "Theme", self.theme_settings.get_theme_config().theme_style, self.show_theme_dialog)
        self._add_section_header("Privacy & Security")
        self._add_switch_setting("database", "Data Collection", self.privacy_settings.is_data_collection_enabled(), self.toggle_data_collection)
        self._add_switch_setting("lock", "Local Data Encryption", self.privacy_settings.get_setting('encrypt_local_data', True), self.toggle_encryption)
        self._add_switch_setting("microphone", "Microphone Access", self.privacy_settings.get_permission('microphone'), lambda x: self.toggle_permission('microphone'))
        self._add_section_header("AI Model Settings")
        default_model = self.model_settings.get_default_model()
        model_name = default_model.get('name', 'Unknown')
        self._add_setting_item("robot", "Default Model", model_name, self.show_model_dialog)
        self._add_slider_setting("thermostat", "Creativity", self.app_settings.get_setting('temperature', 0.7), 0.0, 2.0, 0.1, self.set_temperature)
        self._add_section_header("About")
        self._add_setting_item("information", "Version", self.app_settings.get_setting('app_version', '1.0.0'), None)
        self.settings_list.add_widget(MDBoxLayout(orientation='horizontal', padding=dp(15), spacing=dp(10), size_hint_y=None, height=dp(60)))
        reset_btn = MDRaisedButton(text="Reset All Settings", icon="restart", on_press=self.show_reset_confirmation, size_hint_x=0.6, md_bg_color=(1, 0, 0, 0.2))
        self.settings_list.add_widget(reset_btn)
    
    def _add_section_header(self, title: str):
        self.settings_list.add_widget(MDLabel(text=title, font_style='H6', halign='left', padding=dp(15), dp(0)))
    
    def _add_setting_item(self, icon: str, title: str, value: str, on_press):
        item = TwoLineListItem(text=title, secondary_text=str(value), on_press=on_press)
        icon_box = MDBoxLayout(size_hint_x=None, width=dp(48), padding=dp(10))
        icon_box.add_widget(MDIcon(icon=icon))
        container = MDBoxLayout(orientation='horizontal', spacing=dp(10), padding=dp(10), size_hint_y=None, height=dp(60))
        container.add_widget(icon_box)
        container.add_widget(item)
        self.settings_list.add_widget(container)
    
    def _add_switch_setting(self, icon: str, title: str, value: bool, on_change):
        switch = MDSwitch(value=value, on_active=on_change)
        container = MDBoxLayout(orientation='horizontal', spacing=dp(10), padding=dp(10), size_hint_y=None, height=dp(60))
        icon_box = MDBoxLayout(size_hint_x=None, width=dp(48), padding=dp(10))
        icon_box.add_widget(MDIcon(icon=icon))
        container.add_widget(icon_box)
        title_label = MDLabel(text=title, halign='left', size_hint_x=0.7)
        container.add_widget(title_label)
        switch_box = MDBoxLayout(size_hint_x=None, width=dp(48), padding=dp(10))
        switch_box.add_widget(switch)
        container.add_widget(switch_box)
        self.settings_list.add_widget(container)
    
    def _add_slider_setting(self, icon: str, title: str, value: float, min_value: float, max_value: float, step: float, on_change):
        slider = MDSlider(value=value, min=min_value, max=max_value, step=step, on_value_change=on_change)
        container = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(5), size_hint_y=None, height=dp(80))
        top_row = MDBoxLayout(orientation='horizontal', spacing=dp(10), size_hint_y=None, height=dp(40))
        icon_box = MDBoxLayout(size_hint_x=None, width=dp(48), padding=dp(10))
        icon_box.add_widget(MDIcon(icon=icon))
        top_row.add_widget(icon_box)
        title_label = MDLabel(text=title, halign='left')
        top_row.add_widget(title_label)
        value_label = MDLabel(text=str(round(value, 2)), halign='right')
        top_row.add_widget(value_label)
        container.add_widget(top_row)
        container.add_widget(slider)
        self.settings_list.add_widget(container)
    
    def show_language_dialog(self):
        if not self.app_settings:
            return
        languages = self.app_settings.get_supported_languages()
        current_language = self.app_settings.get_setting('language', 'en')
        dialog = MDDialog(title="Select Language", size_hint=(0.8, 0.6))
        scroll = MDScrollView()
        list_view = MDList()
        for lang_code, lang_name in languages.items():
            item = OneLineListItem(text=f"{lang_name} ({lang_code})", on_press=lambda x, code=lang_code: self.set_language(code, dialog))
            if lang_code == current_language:
                item.bg_color = (0.21, 0.58, 0.94, 0.2)
            list_view.add_widget(item)
        scroll.add_widget(list_view)
        dialog.add_widget(scroll)
        dialog.add_widget(MDFlatButton(text="CANCEL", on_press=dialog.dismiss))
        dialog.open()
    
    def set_language(self, language_code: str, dialog):
        dialog.dismiss()
        if self.app_settings:
            if self.app_settings.set_language(language_code):
                Snackbar(text=f"Language set to: {language_code}").open()
                self._update_ui()
    
    def show_theme_dialog(self):
        if not self.theme_settings:
            return
        theme_styles = ['Dark', 'Light']
        current_style = self.theme_settings.get_theme_config().theme_style
        dialog = MDDialog(title="Select Theme", size_hint=(0.8, 0.5))
        content = MDBoxLayout(orientation='vertical', padding=dp(10), spacing=dp(10))
        for style in theme_styles:
            item = OneLineListItem(text=style, on_press=lambda x, s=style: self.set_theme_style(s, dialog))
            if style == current_style:
                item.bg_color = (0.21, 0.58, 0.94, 0.2)
            content.add_widget(item)
        dialog.add_widget(content)
        dialog.add_widget(MDFlatButton(text="CANCEL", on_press=dialog.dismiss))
        dialog.open()
    
    def set_theme_style(self, style: str, dialog):
        dialog.dismiss()
        if self.theme_settings:
            if self.theme_settings.set_theme_style(style):
                Snackbar(text=f"Theme set to: {style}").open()
                self._update_ui()
    
    def show_model_dialog(self):
        if not self.model_settings:
            return
        models = self.model_settings.get_available_models()
        current_model = self.model_settings.get_default_model().get('id', '')
        dialog = MDDialog(title="Select Default Model", size_hint=(0.8, 0.6))
        scroll = MDScrollView()
        list_view = MDList()
        for model_id, model_info in models.items():
            item = TwoLineListItem(text=model_info['name'], secondary_text=model_info['description'], on_press=lambda x, mid=model_id: self.set_default_model(mid, dialog))
            if model_id == current_model:
                item.bg_color = (0.21, 0.58, 0.94, 0.2)
            list_view.add_widget(item)
        scroll.add_widget(list_view)
        dialog.add_widget(scroll)
        dialog.add_widget(MDFlatButton(text="CANCEL", on_press=dialog.dismiss))
        dialog.open()
    
    def set_default_model(self, model_id: str, dialog):
        dialog.dismiss()
        if self.model_settings:
            if self.model_settings.set_default_model(model_id):
                Snackbar(text="Default model set").open()
                self._update_ui()
    
    def toggle_data_collection(self, switch, value):
        if self.privacy_settings:
            self.privacy_settings.set_data_collection(collect_usage=value, collect_errors=value, collect_analytics=value)
            Snackbar(text=f"Data collection: {'ON' if value else 'OFF'}").open()
    
    def toggle_encryption(self, switch, value):
        if self.privacy_settings:
            self.privacy_settings.set_encryption(value)
            Snackbar(text=f"Encryption: {'ON' if value else 'OFF'}").open()
    
    def toggle_permission(self, permission_name: str):
        if self.privacy_settings:
            current = self.privacy_settings.get_permission(permission_name)
            self.privacy_settings.set_permission(permission_name, not current)
            Snackbar(text=f"{permission_name.capitalize()} access: {'ON' if not current else 'OFF'}").open()
            self._update_ui()
    
    def set_temperature(self, slider, value):
        if self.app_settings:
            self.app_settings.set_setting('temperature', value)
            Snackbar(text=f"Temperature: {value:.2f}").open()
    
    def show_reset_confirmation(self):
        dialog = MDDialog(title="Reset All Settings", text="Are you sure you want to reset all settings to defaults?", size_hint=(0.8, 0.4))
        dialog.add_widget(MDFlatButton(text="CANCEL", on_press=dialog.dismiss))
        dialog.add_widget(MDRaisedButton(text="RESET", theme_text_color="Error", on_press=lambda x: self.reset_all_settings(dialog)))
        dialog.open()
    
    def reset_all_settings(self, dialog):
        dialog.dismiss()
        try:
            if self.app_settings:
                self.app_settings.reset_to_defaults()
            if self.privacy_settings:
                self.privacy_settings.reset_to_defaults()
            if self.theme_settings:
                self.theme_settings.reset_to_defaults()
            if self.model_settings:
                self.model_settings.__init__()
            Snackbar(text="All settings reset to defaults").open()
            self._update_ui()
        except Exception as e:
            Snackbar(text=f"Error: {str(e)}").open()
    
    def on_back_button(self):
        self.manager.current = 'home'


Builder.load_string('''
<SettingsScreen>:
    name: 'settings'
    MDBoxLayout:
        orientation: 'vertical'
        padding: dp(10)
        spacing: dp(10)
        MDTopAppBar:
            title: "Settings"
            elevation: 4
            left_action_items: [["arrow-left", lambda x: root.on_back_button()]]
        ScrollView:
            bar_width: dp(5)
            bar_color: 33/255, 150/255, 243/255, 0.5
            bar_inactive_color: 33/255, 150/255, 243/255, 0.2
            scroll_type: ['bars', 'content']
            MDBoxLayout:
                id: settings_list
                orientation: 'vertical'
                padding: dp(10)
                spacing: dp(5)
                size_hint_y: None
                height: max(self.minimum_height, root.height - dp(150))
                adaptive_height: True
''')
