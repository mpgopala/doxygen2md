#!/usr/bin/env python3
"""
Enhanced Markdown Documentation Generator

This script generates comprehensive markdown documentation directly from XML files,
including detailed descriptions, parameter information, visual indicators, and Table of Contents.
"""

import xml.etree.ElementTree as ET
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
import re
import html

class MarkdownGenerator:
    """Generates enhanced markdown documentation directly from XML files"""
    
    def __init__(self, xml_dir: str = "xml", output_dir: str = "markdown_docs"):
        self.xml_dir = Path(xml_dir)
        self.output_dir = Path(output_dir)
        
        # Create output directory
        self.output_dir.mkdir(exist_ok=True)
        
        # Data structures
        self.classes = []
        self.namespaces = []
        self.structs = []
        self.functions = []
        self.enums = []
        self.variables = []
        self.typedefs = []
        self.friends = []
        
        # Statistics
        self.stats = {
            'total_files': 0,
            'classes': 0,
            'namespaces': 0,
            'structs': 0,
            'functions': 0,
            'enums': 0,
            'variables': 0,
            'typedefs': 0,
            'friends': 0
        }
    
    def clean_text(self, text: str) -> str:
        """Clean and format text content"""
        if not text:
            return ""
        
        # Decode HTML entities
        text = html.unescape(text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        return text
    
    def extract_text_content(self, element) -> str:
        """Extract text content from XML element, handling nested elements"""
        if element is None:
            return ""
        
        text_parts = []
        
        # Get direct text
        if element.text:
            text_parts.append(element.text)
        
        # Get text from child elements
        for child in element:
            if child.text:
                text_parts.append(child.text)
            if child.tail:
                text_parts.append(child.tail)
        
        return self.clean_text(''.join(text_parts))
    
    def extract_parameters(self, memberdef) -> List[Dict[str, str]]:
        """Extract parameter information from memberdef"""
        parameters = []
        
        for param in memberdef.findall('param'):
            param_type = param.find('type')
            param_name = param.find('declname')
            
            param_info = {
                'type': self.extract_text_content(param_type) if param_type is not None else '',
                'name': self.extract_text_content(param_name) if param_name is not None else '',
                'description': ''
            }
            
            # Look for parameter description
            param_desc = param.find('defval')
            if param_desc is not None:
                param_info['default'] = self.extract_text_content(param_desc)
            
            parameters.append(param_info)
        
        return parameters
    
    def extract_member_data(self, memberdef) -> Optional[Dict[str, Any]]:
        """Extract detailed member data from memberdef element"""
        if memberdef is None:
            return None
        
        # Basic information
        member_id = memberdef.get('id', '')
        kind = memberdef.get('kind', '')
        protection = memberdef.get('prot', '')
        static = memberdef.get('static', 'no') == 'yes'
        const = memberdef.get('const', 'no') == 'yes'
        virtual = memberdef.get('virt', '') == 'virtual'
        
        # Name
        name_elem = memberdef.find('name')
        name = self.extract_text_content(name_elem) if name_elem is not None else ''
        
        # Type
        type_elem = memberdef.find('type')
        return_type = self.extract_text_content(type_elem) if type_elem is not None else ''
        
        # Brief description
        brief_elem = memberdef.find('briefdescription')
        brief_description = self.extract_text_content(brief_elem) if brief_elem is not None else ''
        
        # Detailed description
        detailed_elem = memberdef.find('detaileddescription')
        detailed_description = self.extract_text_content(detailed_elem) if detailed_elem is not None else ''
        
        # Parameters
        parameters = self.extract_parameters(memberdef)
        
        # Args string (function signature)
        argsstring_elem = memberdef.find('argsstring')
        argsstring = self.extract_text_content(argsstring_elem) if argsstring_elem is not None else ''
        
        # Definition
        definition_elem = memberdef.find('definition')
        definition = self.extract_text_content(definition_elem) if definition_elem is not None else ''
        
        return {
            'id': member_id,
            'kind': kind,
            'name': name,
            'type': return_type,
            'protection': protection,
            'static': static,
            'const': const,
            'virtual': virtual,
            'brief_description': brief_description,
            'detailed_description': detailed_description,
            'parameters': parameters,
            'argsstring': argsstring,
            'definition': definition
        }
    
    def extract_compound_data(self, compounddef) -> Optional[Dict[str, Any]]:
        """Extract detailed compound data from compounddef element"""
        if compounddef is None:
            return None
        
        # Basic information
        compound_id = compounddef.get('id', '')
        kind = compounddef.get('kind', '')
        language = compounddef.get('language', '')
        protection = compounddef.get('prot', '')
        
        # Name
        compoundname_elem = compounddef.find('compoundname')
        name = self.extract_text_content(compoundname_elem) if compoundname_elem is not None else ''
        
        # Brief description
        brief_elem = compounddef.find('briefdescription')
        brief_description = self.extract_text_content(brief_elem) if brief_elem is not None else ''
        
        # Detailed description
        detailed_elem = compounddef.find('detaileddescription')
        detailed_description = self.extract_text_content(detailed_elem) if detailed_elem is not None else ''
        
        # Base classes
        base_classes = []
        for base in compounddef.findall('basecompoundref'):
            base_classes.append({
                'name': self.extract_text_content(base),
                'protection': base.get('prot', ''),
                'virtual': base.get('virt', '') == 'virtual'
            })
        
        # Inner classes
        inner_classes = []
        for inner in compounddef.findall('innerclass'):
            inner_classes.append({
                'name': self.extract_text_content(inner),
                'refid': inner.get('refid', ''),
                'protection': inner.get('prot', '')
            })
        
        return {
            'id': compound_id,
            'kind': kind,
            'name': name,
            'language': language,
            'protection': protection,
            'brief_description': brief_description,
            'detailed_description': detailed_description,
            'base_classes': base_classes,
            'inner_classes': inner_classes
        }
    
    def parse_xml_file(self, xml_file: Path):
        """Parse a single XML file and extract data"""
        try:
            tree = ET.parse(xml_file)
            root = tree.getroot()
            
            # Check if this is a Doxygen file
            if root.tag != 'doxygen':
                return
            
            self.stats['total_files'] += 1
            
            # Extract compound definitions (classes, structs, namespaces)
            for compounddef in root.findall('.//compounddef'):
                compound_data = self.extract_compound_data(compounddef)
                if compound_data:
                    kind = compound_data['kind']
                    if kind == 'class':
                        self.classes.append(compound_data)
                        self.stats['classes'] += 1
                    elif kind == 'namespace':
                        self.namespaces.append(compound_data)
                        self.stats['namespaces'] += 1
                    elif kind == 'struct':
                        self.structs.append(compound_data)
                        self.stats['structs'] += 1
            
            # Extract member definitions (functions, variables, etc.)
            for memberdef in root.findall('.//memberdef'):
                member_data = self.extract_member_data(memberdef)
                if member_data:
                    kind = member_data['kind']
                    if kind == 'function':
                        self.functions.append(member_data)
                        self.stats['functions'] += 1
                    elif kind == 'enum':
                        self.enums.append(member_data)
                        self.stats['enums'] += 1
                    elif kind == 'variable':
                        self.variables.append(member_data)
                        self.stats['variables'] += 1
                    elif kind == 'typedef':
                        self.typedefs.append(member_data)
                        self.stats['typedefs'] += 1
                    elif kind == 'friend':
                        self.friends.append(member_data)
                        self.stats['friends'] += 1
                        
        except Exception as e:
            print(f"Error parsing {xml_file}: {e}")
    
    def parse_all_xml_files(self):
        """Parse all XML files in the directory"""
        print("Parsing XML files...")
        
        xml_files = list(self.xml_dir.glob("*.xml"))
        print(f"Found {len(xml_files)} XML files")
        
        for xml_file in xml_files:
            self.parse_xml_file(xml_file)
        
        print("Parsing complete!")
        print(f"Statistics: {self.stats}")
    
    def extract_namespace(self, full_name: str) -> str:
        """Extract namespace from full class/function name"""
        if '::' in full_name:
            return full_name.rsplit('::', 1)[0]
        return "Global"
    
    def format_parameters(self, parameters: List[Dict[str, str]]) -> str:
        """Format parameters for markdown"""
        if not parameters:
            return ""
        
        content = "\n**Parameters:**\n\n"
        for param in parameters:
            param_type = param.get('type', '')
            param_name = param.get('name', '')
            param_desc = param.get('description', '')
            param_default = param.get('default', '')
            
            content += f"- **`{param_name}`** (`{param_type}`)"
            if param_default:
                content += f" = `{param_default}`"
            if param_desc:
                content += f" - {param_desc}"
            content += "\n"
        
        return content
    
    def format_detailed_description(self, description: str) -> str:
        """Format detailed description for markdown"""
        if not description:
            return ""
        
        # Convert HTML-like tags to markdown
        description = re.sub(r'<para>(.*?)</para>', r'\1\n\n', description, flags=re.DOTALL)
        description = re.sub(r'<emphasis>(.*?)</emphasis>', r'**\1**', description)
        description = re.sub(r'<ulink url="([^"]*)">(.*?)</ulink>', r'[\2](\1)', description)
        description = re.sub(r'<ref refid="([^"]*)" kindref="member">(.*?)</ref>', r'`\2`', description)
        
        # Clean up extra whitespace
        description = re.sub(r'\n\s*\n', '\n\n', description)
        description = description.strip()
        
        return description
    
    def generate_table_of_contents(self, related_functions: List[Dict], related_enums: List[Dict], related_variables: List[Dict]) -> str:
        """Generate a table of contents for a class"""
        toc = "## Table of Contents\n\n"
        
        if related_functions:
            toc += "### Member Functions\n\n"
            for func in related_functions:
                name = func.get('name', 'Unknown')
                # Create anchor-friendly name
                anchor = name.lower().replace(' ', '-').replace('::', '-').replace('(', '').replace(')', '').replace('&', '').replace('<', '').replace('>', '').replace(',', '').replace('=', '').replace('~', '').replace('*', '').replace('[', '').replace(']', '')
                toc += f"- [{name}](#{anchor})\n"
            toc += "\n"
        
        if related_enums:
            toc += "### Types\n\n"
            for enum in related_enums:
                name = enum.get('name', 'Unknown')
                anchor = name.lower().replace(' ', '-').replace('::', '-').replace('(', '').replace(')', '').replace('&', '').replace('<', '').replace('>', '').replace(',', '').replace('=', '').replace('~', '').replace('*', '').replace('[', '').replace(']', '')
                toc += f"- [{name}](#{anchor})\n"
            toc += "\n"
        
        if related_variables:
            toc += "### Attributes\n\n"
            for var in related_variables:
                name = var.get('name', 'Unknown')
                anchor = name.lower().replace(' ', '-').replace('::', '-').replace('(', '').replace(')', '').replace('&', '').replace('<', '').replace('>', '').replace(',', '').replace('=', '').replace('~', '').replace('*', '').replace('[', '').replace(']', '')
                toc += f"- [{name}](#{anchor})\n"
            toc += "\n"
        
        return toc
    
    def generate_function_entry(self, func: Dict[str, Any]) -> str:
        """Generate a function entry with detailed information"""
        # Create full signature
        return_type = func.get('type', '')
        name = func.get('name', 'Unknown')
        argsstring = func.get('argsstring', '')
        
        # Clean up the argsstring to remove extra spaces and formatting
        argsstring = argsstring.strip()
        
        # Handle constructors and destructors (no return type)
        if name.startswith('~') or (not return_type and name and not name.startswith('operator')):
            # Destructor or constructor
            if not argsstring:
                signature = f"{name}()"
            elif argsstring.startswith('('):
                signature = f"{name}{argsstring}"
            elif argsstring and not argsstring.startswith('('):
                signature = f"{name}({argsstring})"
            else:
                signature = f"{name}()"
        else:
            # Regular function with return type
            if not return_type:
                return_type = 'void'
            
            if not argsstring:
                signature = f"{return_type} {name}()"
            elif argsstring.startswith('('):
                signature = f"{return_type} {name}{argsstring}"
            elif argsstring and not argsstring.startswith('('):
                signature = f"{return_type} {name}({argsstring})"
            else:
                signature = f"{return_type} {name}()"
        
        content = f"### {name}\n\n"
        content += f"`{signature}`\n\n"
        
        if func.get('brief_description'):
            content += f"**Brief:** {func['brief_description']}\n\n"
        
        if func.get('detailed_description'):
            detailed = self.format_detailed_description(func['detailed_description'])
            content += f"**Description:** {detailed}\n\n"
        
        # Parameters
        if func.get('parameters'):
            content += self.format_parameters(func['parameters'])
        
        # Visual indicators for function qualifiers
        qualifiers = []
        protection = func.get('protection', '')
        if protection == 'public':
            qualifiers.append("🟢 **public**")
        elif protection == 'private':
            qualifiers.append("🔴 **private**")
        elif protection == 'protected':
            qualifiers.append("🟡 **protected**")
        
        if func.get('static', False):
            qualifiers.append("⚡ **static**")
        
        if func.get('const', False):
            qualifiers.append("🔒 **const**")
        
        if func.get('virtual', False):
            qualifiers.append("👻 **virtual**")
        
        if qualifiers:
            content += f"**Qualifiers:** {' '.join(qualifiers)}\n\n"
        
        return content
    
    def generate_enum_entry(self, enum: Dict[str, Any]) -> str:
        """Generate an enum entry"""
        name = enum.get('name', 'Unknown')
        content = f"### {name}\n\n"
        content += f"`enum {name}`\n\n"
        
        if enum.get('brief_description'):
            content += f"**Brief:** {enum['brief_description']}\n\n"
        
        if enum.get('detailed_description'):
            detailed = self.format_detailed_description(enum['detailed_description'])
            content += f"**Description:** {detailed}\n\n"
        
        # Visual indicators for enum qualifiers
        qualifiers = []
        protection = enum.get('protection', '')
        if protection == 'public':
            qualifiers.append("🟢 **public**")
        elif protection == 'private':
            qualifiers.append("🔴 **private**")
        elif protection == 'protected':
            qualifiers.append("🟡 **protected**")
        
        if qualifiers:
            content += f"**Qualifiers:** {' '.join(qualifiers)}\n\n"
        
        return content
    
    def generate_variable_entry(self, var: Dict[str, Any]) -> str:
        """Generate a variable entry"""
        name = var.get('name', 'Unknown')
        var_type = var.get('type', 'auto')
        content = f"### {name}\n\n"
        content += f"`{var_type} {name}`\n\n"
        
        if var.get('brief_description'):
            content += f"**Brief:** {var['brief_description']}\n\n"
        
        if var.get('detailed_description'):
            detailed = self.format_detailed_description(var['detailed_description'])
            content += f"**Description:** {detailed}\n\n"
        
        # Visual indicators for variable qualifiers
        qualifiers = []
        protection = var.get('protection', '')
        if protection == 'public':
            qualifiers.append("🟢 **public**")
        elif protection == 'private':
            qualifiers.append("🔴 **private**")
        elif protection == 'protected':
            qualifiers.append("🟡 **protected**")
        
        if qualifiers:
            content += f"**Qualifiers:** {' '.join(qualifiers)}\n\n"
        
        return content
    
    def generate_detailed_class_page(self, cls: Dict[str, Any]):
        """Generate a detailed page for a single class"""
        class_id = cls['id']
        filename = f"class_{class_id}.md"
        
        content = f"# {cls.get('name', 'Unknown')}\n\n"
        
        if cls.get('brief_description'):
            content += f"**Brief:** {cls['brief_description']}\n\n"
        
        if cls.get('detailed_description'):
            detailed = self.format_detailed_description(cls['detailed_description'])
            content += f"**Description:** {detailed}\n\n"
        
        content += f"**Language:** {cls.get('language', 'Unknown')}\n\n"
        
        # Base classes
        if cls.get('base_classes'):
            content += "## Base Classes\n\n"
            for base in cls['base_classes']:
                content += f"- **{base['name']}**"
                if base['virtual']:
                    content += " (virtual)"
                content += f" - {base['protection']}\n"
            content += "\n"
        
        # Inner classes
        if cls.get('inner_classes'):
            content += "## Inner Classes\n\n"
            for inner in cls['inner_classes']:
                content += f"- **{inner['name']}** - {inner['protection']}\n"
            content += "\n"
        
        # Find related members
        related_functions = [f for f in self.functions if class_id in f['id']]
        related_variables = [v for v in self.variables if class_id in v['id']]
        related_enums = [e for e in self.enums if class_id in e['id']]
        
        # Generate Table of Contents
        toc = self.generate_table_of_contents(related_functions, related_enums, related_variables)
        content += toc
        
        if related_functions:
            content += "## Member Functions\n\n"
            for func in related_functions:
                content += self.generate_function_entry(func)
                content += "\n"
        
        if related_enums:
            content += "## Types\n\n"
            for enum in related_enums:
                content += self.generate_enum_entry(enum)
                content += "\n"
        
        if related_variables:
            content += "## Attributes\n\n"
            for var in related_variables:
                content += self.generate_variable_entry(var)
                content += "\n"
        
        content += "\n---\n\n"
        content += "[Back to Classes](classes.md) | [Back to Index](index.md)\n"
        
        with open(self.output_dir / filename, 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_documentation(self):
        """Generate complete markdown documentation"""
        print("Generating enhanced markdown documentation...")
        
        # Parse all XML files
        self.parse_all_xml_files()
        
        # Generate main index
        self.generate_index()
        
        # Generate category pages
        self.generate_classes_documentation()
        self.generate_namespaces_documentation()
        self.generate_structs_documentation()
        self.generate_functions_documentation()
        self.generate_enums_documentation()
        self.generate_files_list()
        
        # Generate detailed class pages
        self.generate_detailed_class_pages()
        
        print(f"Enhanced documentation generated in: {self.output_dir}")
    
    def generate_index(self):
        """Generate main index page"""
        content = f"""# Shared Asset Model C++ Client Library (SAM.cpp)

**Version:** 14.3.0  
**Description:** Reusable ACPL Shared Asset Model (SAM) and its test applications (Mac, Win, and iOS)

## Overview

This documentation covers the Shared Asset Model C++ Client Library, providing comprehensive API reference for managing Adobe assets in Creative Cloud applications.

## Documentation Statistics

- **Total Classes:** {self.stats['classes']}
- **Total Namespaces:** {self.stats['namespaces']}
- **Total Structs:** {self.stats['structs']}
- **Total Functions:** {self.stats['functions']}
- **Total Enums:** {self.stats['enums']}
- **Total Variables:** {self.stats['variables']}
- **Total Typedefs:** {self.stats['typedefs']}

## Quick Navigation

### [Classes](classes.md)
Complete list of all classes with their methods and properties.

### [Namespaces](namespaces.md)
Namespace organization and hierarchy.

### [Structs](structs.md)
Data structures and utility classes.

### [Functions](functions.md)
Standalone functions and utilities.

### [Enums](enums.md)
Enumerations and constants.

### [Files](files.md)
Source file organization and structure.

## Main Components

### Core Classes
- **AdobeAsset** - Base class for Adobe assets
- **AssetContext** - Context management for assets
- **AssetCollection** - Collection of assets
- **Space** - Creative Cloud space management

### Namespaces
- **ccx::assets_v2** - Main asset management namespace
- **ccx::util** - Utility functions and classes
- **ccx::presence** - Presence and collaboration features
- **ccx::analytics** - Analytics and logging

---

*Generated directly from Doxygen XML documentation*
"""
        
        with open(self.output_dir / "index.md", 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_classes_documentation(self):
        """Generate classes documentation"""
        content = "# Classes\n\n"
        content += f"Total Classes: {self.stats['classes']}\n\n"
        
        # Group classes by namespace
        classes_by_namespace = defaultdict(list)
        for cls in self.classes:
            if cls.get('name'):
                namespace = self.extract_namespace(cls['name'])
                classes_by_namespace[namespace].append(cls)
        
        for namespace, classes in sorted(classes_by_namespace.items()):
            content += f"## {namespace}\n\n"
            
            for cls in sorted(classes, key=lambda x: x.get('name', '')):
                content += self.generate_class_entry(cls)
                content += "\n"
        
        with open(self.output_dir / "classes.md", 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_class_entry(self, cls: Dict[str, Any]) -> str:
        """Generate a single class entry"""
        content = f"### {cls.get('name', 'Unknown')}\n\n"
        
        if cls.get('brief_description'):
            content += f"**Brief:** {cls['brief_description']}\n\n"
        
        if cls.get('detailed_description'):
            detailed = self.format_detailed_description(cls['detailed_description'])
            content += f"**Description:** {detailed}\n\n"
        
        content += f"- **Language:** {cls.get('language', 'Unknown')}\n\n"
        
        # Add base classes if any
        if cls.get('base_classes'):
            content += "**Base Classes:**\n"
            for base in cls['base_classes']:
                content += f"- {base['name']}\n"
            content += "\n"
        
        # Add link to detailed class page
        class_filename = f"class_{cls.get('id', 'unknown')}.md"
        content += f"[Detailed Documentation]({class_filename})\n\n"
        
        return content
    
    def generate_namespaces_documentation(self):
        """Generate namespaces documentation"""
        content = "# Namespaces\n\n"
        content += f"Total Namespaces: {self.stats['namespaces']}\n\n"
        
        for ns in sorted(self.namespaces, key=lambda x: x.get('name', '')):
            content += f"## {ns.get('name', 'Unknown')}\n\n"
            
            if ns.get('brief_description'):
                content += f"**Brief:** {ns['brief_description']}\n\n"
            
            if ns.get('detailed_description'):
                detailed = self.format_detailed_description(ns['detailed_description'])
                content += f"**Description:** {detailed}\n\n"
            
            content += f"- **Language:** {ns.get('language', 'Unknown')}\n\n"
        
        with open(self.output_dir / "namespaces.md", 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_structs_documentation(self):
        """Generate structs documentation"""
        content = "# Structs\n\n"
        content += f"Total Structs: {self.stats['structs']}\n\n"
        
        # Group structs by namespace
        structs_by_namespace = defaultdict(list)
        for struct in self.structs:
            if struct.get('name'):
                namespace = self.extract_namespace(struct['name'])
                structs_by_namespace[namespace].append(struct)
        
        for namespace, structs in sorted(structs_by_namespace.items()):
            content += f"## {namespace}\n\n"
            
            for struct in sorted(structs, key=lambda x: x.get('name', '')):
                content += f"### {struct.get('name', 'Unknown')}\n\n"
                
                if struct.get('brief_description'):
                    content += f"**Brief:** {struct['brief_description']}\n\n"
                
                if struct.get('detailed_description'):
                    detailed = self.format_detailed_description(struct['detailed_description'])
                    content += f"**Description:** {detailed}\n\n"
                
                content += f"- **Language:** {struct.get('language', 'Unknown')}\n\n"
        
        with open(self.output_dir / "structs.md", 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_functions_documentation(self):
        """Generate functions documentation"""
        content = "# Functions\n\n"
        content += f"Total Functions: {self.stats['functions']}\n\n"
        
        # Group functions by namespace
        functions_by_namespace = defaultdict(list)
        for func in self.functions:
            if func.get('name'):
                namespace = self.extract_namespace(func['name'])
                functions_by_namespace[namespace].append(func)
        
        for namespace, functions in sorted(functions_by_namespace.items()):
            content += f"## {namespace}\n\n"
            
            for func in sorted(functions, key=lambda x: x.get('name', '')):
                content += self.generate_function_entry(func)
        
        with open(self.output_dir / "functions.md", 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_enums_documentation(self):
        """Generate enums documentation"""
        content = "# Enums\n\n"
        content += f"Total Enums: {self.stats['enums']}\n\n"
        
        # Group enums by namespace
        enums_by_namespace = defaultdict(list)
        for enum in self.enums:
            if enum.get('name'):
                namespace = self.extract_namespace(enum['name'])
                enums_by_namespace[namespace].append(enum)
        
        for namespace, enums in sorted(enums_by_namespace.items()):
            content += f"## {namespace}\n\n"
            
            for enum in sorted(enums, key=lambda x: x.get('name', '')):
                content += self.generate_enum_entry(enum)
        
        with open(self.output_dir / "enums.md", 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_files_list(self):
        """Generate files list documentation"""
        content = "# Files\n\n"
        content += "Source file organization and structure.\n\n"
        
        # Get file information from XML directory
        xml_files = list(self.xml_dir.glob("*.xml"))
        
        # Group files by type
        class_files = []
        namespace_files = []
        struct_files = []
        other_files = []
        
        for xml_file in xml_files:
            filename = xml_file.name
            if filename.startswith('class'):
                class_files.append(filename)
            elif filename.startswith('namespace'):
                namespace_files.append(filename)
            elif filename.startswith('struct'):
                struct_files.append(filename)
            else:
                other_files.append(filename)
        
        content += f"## Class Files ({len(class_files)})\n\n"
        for filename in sorted(class_files):
            content += f"- `{filename}`\n"
        
        content += f"\n## Namespace Files ({len(namespace_files)})\n\n"
        for filename in sorted(namespace_files):
            content += f"- `{filename}`\n"
        
        content += f"\n## Struct Files ({len(struct_files)})\n\n"
        for filename in sorted(struct_files):
            content += f"- `{filename}`\n"
        
        content += f"\n## Other Files ({len(other_files)})\n\n"
        for filename in sorted(other_files):
            content += f"- `{filename}`\n"
        
        with open(self.output_dir / "files.md", 'w', encoding='utf-8') as f:
            f.write(content)
    
    def generate_detailed_class_pages(self):
        """Generate detailed pages for each class"""
        print("Generating detailed class pages...")
        
        for cls in self.classes:
            self.generate_detailed_class_page(cls)


def main():
    """Main function to generate enhanced markdown documentation"""
    generator = MarkdownGenerator()
    generator.generate_documentation()
    
    print("Enhanced markdown documentation generation complete!")


if __name__ == "__main__":
    main() 