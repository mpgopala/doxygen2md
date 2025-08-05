# Doxygen to Markdown Documentation Generator

A comprehensive Python tool for converting Doxygen XML documentation into enhanced markdown format with visual indicators, Table of Contents, and complete function signatures.

## 🚀 Features

### **Enhanced Documentation Generation**
- **Direct XML Parsing** - Generates markdown directly from Doxygen XML files
- **Complete Function Signatures** - Full parameter lists and qualifiers included
- **Visual Indicators** - Color-coded qualifiers with emoji indicators
- **Table of Contents** - Comprehensive navigation for each class
- **H3 Headers** - Individual headers for each member function, variable, and enum
- **Detailed Descriptions** - Complete parameter information and descriptions
- **Cross-References** - Anchor links for direct navigation

### **Visual Indicators**
- 🟢 **public** - Public members
- 🔴 **private** - Private members  
- 🟡 **protected** - Protected members
- ⚡ **static** - Static members
- 🔒 **const** - Const qualifiers
- 👻 **virtual** - Virtual functions

### **Complete Function Signatures**
```markdown
### commitFileChanges

`util::Promise< FileCommitResult > commitFileChanges(const std::string &localPath, const std::string &localETag, bool moveIn) noexcept`
```

### **Table of Contents**
Each class documentation includes a comprehensive TOC:
```markdown
## Table of Contents

### Member Functions
- [AdobeAssetWithError](#adobeassetwitherror)
- [getAdobeAsset](#getadobeasset)
- [commitFileChanges](#commitfilechanges)
- [createComposite](#createcomposite)
```

## 📋 Requirements

- Python 3.6+
- XML files from Doxygen documentation

## 🛠️ Installation

1. **Clone or download the project**
2. **Install dependencies** (if needed):
   ```bash
   pip install -r requirements.txt
   ```

## 🚀 Usage

### **Basic Usage**
```bash
python markdown_generator.py
```

Place the generated xmls from Doxygen in `xml` directory next to `markdown_generator.py`.

### **Custom Directories**
```python
from markdown_generator import MarkdownGenerator

# Custom XML and output directories
generator = MarkdownGenerator(xml_dir="path/to/xml", output_dir="path/to/output")
generator.generate_documentation()
```

## 📁 Project Structure

```
xml2md/
├── markdown_generator.py         # Main generator script
├── requirements.txt              # Python dependencies
└── README.md                    # This file
```

## 📊 Generated Documentation

The generator creates comprehensive markdown documentation including:

### **Main Pages**
- `index.md` - Main landing page with statistics and navigation
- `classes.md` - Complete list of all classes
- `namespaces.md` - Namespace organization
- `structs.md` - Data structures
- `functions.md` - Standalone functions
- `enums.md` - Enumerations
- `files.md` - Source file organization

### **Detailed Class Pages**
- Individual `class_*.md` files for each class
- Complete member documentation
- Table of Contents with anchor links
- Base class and inheritance information
- Parameter details and qualifiers

## 🔧 Technical Details

### **Signature Generation**
The generator handles various function types:
- **Regular Functions:** `ReturnType functionName(parameters) qualifiers`
- **Constructors:** `ClassName(parameters) qualifiers`
- **Destructors:** `~ClassName() qualifiers`
- **Operators:** `ReturnType operator=(parameters) qualifiers`

### **Parameter Extraction**
- Extracts parameter types, names, and default values
- Handles complex C++ types with templates
- Preserves const, noexcept, and other qualifiers

### **Anchor Generation**
- Creates URL-safe anchor links for navigation
- Handles special characters in function names
- Supports cross-referencing between documentation sections

## 🛠️ Customization

### **Adding New Visual Indicators**
```python
# In generate_function_entry method
if func.get('new_qualifier', False):
    qualifiers.append("🔮 **new_qualifier**")
```

### **Customizing Output Format**
```python
# Modify signature generation
signature = f"{return_type} {name}{argsstring}"
```

### **Extending Parameter Extraction**
```python
# Add new parameter types
def extract_parameters(self, memberdef):
    # Custom parameter extraction logic
    pass
```

## 🐛 Troubleshooting

### **Common Issues**

1. **Missing Parameters in Signatures**
   - Ensure XML files contain complete argsstring elements
   - Check for proper Doxygen configuration

2. **Anchor Link Issues**
   - Verify special character handling in anchor generation
   - Check for duplicate anchor names

3. **Visual Indicators Not Showing**
   - Confirm protection levels are correctly extracted
   - Check for proper qualifier detection

### **Debug Mode**
```python
# Add debug output to specific functions
if name == 'target_function':
    print(f"DEBUG: {argsstring}")
```

## 📚 API Reference

### **MarkdownGenerator Class**

#### **Methods**
- `__init__(xml_dir, output_dir)` - Initialize generator
- `parse_all_xml_files()` - Parse all XML files
- `generate_documentation()` - Generate complete documentation
- `generate_function_entry(func)` - Generate function documentation
- `generate_table_of_contents()` - Generate TOC for class

#### **Properties**
- `classes` - List of extracted class data
- `functions` - List of extracted function data
- `stats` - Statistics about extracted data

## 🤝 Contributing

### **Adding New Features**
1. Fork the repository
2. Create a feature branch
3. Implement your changes
4. Add tests if applicable
5. Submit a pull request

### **Reporting Issues**
- Include XML file examples
- Describe expected vs actual output
- Provide system information

## 📄 License

This project is open source and available under the MIT License.

## 🙏 Acknowledgments

- **Doxygen** - For generating the XML documentation
- **Python Standard Library** - For XML parsing and file operations
- **Markdown Community** - For documentation standards

---

**Generated with ❤️ using the Doxygen to Markdown Documentation Generator** 
