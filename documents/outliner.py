#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TurboMind AI - Outliner
======================
Generates outlines and structures from documents
"""

from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
import re


@dataclass
class OutlineItem:
    """Represents an item in an outline"""
    title: str
    level: int = 1
    content: str = ""
    children: List['OutlineItem'] = field(default_factory=list)
    section_id: str = ""
    page: int = 0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'level': self.level,
            'content': self.content,
            'section_id': self.section_id,
            'page': self.page,
            'children': [child.to_dict() for child in self.children]
        }


@dataclass
class Outline:
    """Represents a complete outline"""
    title: str
    items: List[OutlineItem]
    document_id: str = ""
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'title': self.title,
            'document_id': self.document_id,
            'items': [item.to_dict() for item in self.items]
        }


class Outliner:
    """
    Generates outlines from documents.
    Extracts headings, sections, and creates hierarchical structures.
    """
    
    def __init__(self):
        """Initialize the outliner"""
        print("📑 Outliner initialized")
    
    def generate_outline(self, text: str, title: str = "Outline", document_id: str = "") -> Outline:
        """
        Generate an outline from text.
        
        Args:
            text: Text to generate outline from
            title: Title for the outline
            document_id: Optional document ID
            
        Returns:
            Outline object
        """
        # Detect if it's Markdown
        if self._is_markdown(text):
            return self._generate_markdown_outline(text, title, document_id)
        
        # For plain text, try to detect structure
        return self._generate_text_outline(text, title, document_id)
    
    def _is_markdown(self, text: str) -> bool:
        """Check if text appears to be Markdown"""
        # Check for Markdown headings
        return bool(re.search(r'^#{1,6}\s', text, re.MULTILINE))
    
    def _generate_markdown_outline(self, text: str, title: str, document_id: str) -> Outline:
        """Generate outline from Markdown text"""
        lines = text.split('\n')
        items = []
        stack = []  # Stack of parent items
        current_level = 0
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Check for heading
            heading_match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if heading_match:
                level = len(heading_match.group(1))
                heading_text = heading_match.group(2)
                
                # Create new item
                item = OutlineItem(
                    title=heading_text,
                    level=level,
                    section_id=f"section_{i}"
                )
                
                # Find parent level
                while stack and stack[-1][0] >= level:
                    stack.pop()
                
                # Add to parent or root
                if stack:
                    parent_level, parent_item = stack[-1]
                    parent_item.children.append(item)
                else:
                    items.append(item)
                
                # Push to stack
                stack.append((level, item))
                current_level = level
            elif line and stack:
                # Add to current item's content
                current_item = stack[-1][1]
                current_item.content += line + "\n"
        
        return Outline(
            title=title or items[0].title if items else "Outline",
            items=items,
            document_id=document_id
        )
    
    def _generate_text_outline(self, text: str, title: str, document_id: str) -> Outline:
        """Generate outline from plain text"""
        # Try to detect structure from text
        lines = text.split('\n')
        items = []
        current_item = None
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            if not line:
                continue
            
            # Check for potential headings (lines that are short and end with punctuation)
            if self._is_heading_line(line):
                # Save previous item
                if current_item:
                    items.append(current_item)
                
                current_item = OutlineItem(
                    title=line,
                    level=1,
                    section_id=f"section_{i}"
                )
            elif current_item:
                # Add to current item's content
                current_item.content += line + "\n"
        
        # Add last item
        if current_item:
            items.append(current_item)
        
        return Outline(
            title=title,
            items=items,
            document_id=document_id
        )
    
    def _is_heading_line(self, line: str) -> bool:
        """Check if a line looks like a heading"""
        # Short lines that end with punctuation
        if len(line.split()) < 5 and line.endswith(('.', ':', '!', '?')):
            return True
        
        # All caps
        if line.isupper():
            return True
        
        # Numbered items
        if re.match(r'^\d+\.', line) or re.match(r'^\d+\)', line):
            return True
        
        return False
    
    def outline_from_document(self, document: 'ProcessedDocument') -> Outline:
        """
        Generate outline from a processed document.
        
        Args:
            document: ProcessedDocument to outline
            
        Returns:
            Outline object
        """
        return self.generate_outline(
            text=document.content,
            title=document.metadata.title or document.metadata.file_name,
            document_id=document.metadata.id
        )
    
    def outline_from_chunks(self, chunks: List[str]) -> Outline:
        """
        Generate outline from text chunks.
        
        Args:
            chunks: List of text chunks
            
        Returns:
            Outline object
        """
        full_text = '\n\n'.join(chunks)
        return self.generate_outline(full_text)
    
    def get_table_of_contents(self, outline: Outline) -> List[Dict[str, Any]]:
        """
        Generate a table of contents from an outline.
        
        Args:
            outline: Outline to convert
            
        Returns:
            List of TOC items with indentation
        """
        toc = []
        
        def process_items(items: List[OutlineItem], level: int = 0):
            for item in items:
                toc.append({
                    'title': item.title,
                    'level': item.level,
                    'indent': '  ' * (item.level - 1),
                    'section_id': item.section_id,
                    'page': item.page
                })
                process_items(item.children, item.level)
        
        process_items(outline.items)
        return toc
    
    def get_flat_outline(self, outline: Outline) -> List[Dict[str, Any]]:
        """
        Get a flat list of outline items.
        
        Args:
            outline: Outline to flatten
            
        Returns:
            Flat list of items
        """
        flat = []
        
        def flatten(items: List[OutlineItem], path: str = ""):
            for i, item in enumerate(items):
                current_path = f"{path}.{i+1}" if path else str(i+1)
                flat.append({
                    'path': current_path,
                    'title': item.title,
                    'level': item.level,
                    'content': item.content,
                    'section_id': item.section_id
                })
                flatten(item.children, current_path)
        
        flatten(outline.items)
        return flat
    
    def create_study_guide(self, outline: Outline) -> Dict[str, Any]:
        """
        Create a study guide from an outline.
        
        Args:
            outline: Outline to convert to study guide
            
        Returns:
            Study guide dictionary
        """
        study_guide = {
            'title': outline.title,
            'sections': []
        }
        
        def process_section(item: OutlineItem, path: str = ""):
            section = {
                'title': item.title,
                'path': path,
                'content': item.content.strip(),
                'subsections': []
            }
            
            for child in item.children:
                child_path = f"{path}.{len(section['subsections']) + 1}"
                section['subsections'].append(process_section(child, child_path))
            
            return section
        
        for item in outline.items:
            study_guide['sections'].append(process_section(item, str(len(study_guide['sections']) + 1)))
        
        return study_guide
    
    def generate_flashcards(self, outline: Outline, max_length: int = 200) -> List[Dict[str, Any]]:
        """
        Generate flashcards from an outline.
        
        Args:
            outline: Outline to generate flashcards from
            max_length: Maximum length for flashcard content
            
        Returns:
            List of flashcard dictionaries
        """
        flashcards = []
        
        def process_item(item: OutlineItem):
            # Create flashcard from item
            if item.title and item.content:
                # Split content into chunks
                content_chunks = [
                    item.content[i:i+max_length]
                    for i in range(0, len(item.content), max_length)
                ]
                
                for chunk in content_chunks:
                    flashcards.append({
                        'front': item.title,
                        'back': chunk.strip(),
                        'section': item.section_id
                    })
            
            # Process children
            for child in item.children:
                process_item(child)
        
        for item in outline.items:
            process_item(item)
        
        return flashcards
    
    def generate_questions(self, outline: Outline, count: int = 5) -> List[str]:
        """
        Generate potential questions from an outline.
        
        Args:
            outline: Outline to generate questions from
            count: Number of questions to generate
            
        Returns:
            List of question strings
        """
        questions = []
        
        def process_item(item: OutlineItem):
            if item.title:
                # Generate questions from title
                questions.append(f"What is {item.title}?")
                questions.append(f"Explain {item.title}.")
                questions.append(f"Describe {item.title}.")
            
            for child in item.children:
                process_item(child)
        
        for item in outline.items:
            process_item(item)
        
        return questions[:count]
    
    def save_outline(self, outline: Outline, file_path: str) -> bool:
        """
        Save outline to file.
        
        Args:
            outline: Outline to save
            file_path: Path to save to
            
        Returns:
            True if successful
        """
        try:
            import json
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(outline.to_dict(), f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"❌ Error saving outline: {e}")
            return False
    
    def load_outline(self, file_path: str) -> Optional[Outline]:
        """
        Load outline from file.
        
        Args:
            file_path: Path to load from
            
        Returns:
            Outline object or None
        """
        try:
            import json
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Reconstruct outline
            def reconstruct_items(items_data: List[Dict[str, Any]]) -> List[OutlineItem]:
                items = []
                for item_data in items_data:
                    item = OutlineItem(
                        title=item_data['title'],
                        level=item_data.get('level', 1),
                        content=item_data.get('content', ''),
                        section_id=item_data.get('section_id', ''),
                        page=item_data.get('page', 0)
                    )
                    item.children = reconstruct_items(item_data.get('children', []))
                    items.append(item)
                return items
            
            return Outline(
                title=data.get('title', 'Outline'),
                items=reconstruct_items(data.get('items', [])),
                document_id=data.get('document_id', '')
            )
        except Exception as e:
            print(f"❌ Error loading outline: {e}")
            return None
