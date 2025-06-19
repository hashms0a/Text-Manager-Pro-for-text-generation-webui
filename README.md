# Text Manager Pro for text-generation-webui

A powerful text management extension for [oobabooga/text-generation-webui](https://github.com/oobabooga/text-generation-webui) that provides a comprehensive suite of tools for editing, organizing, and processing text files directly within the web UI.

## 🌟 Features

### 📁 Advanced File Management
- **Multi-file support** - Work with multiple text files simultaneously
- **File operations** - Create, delete, rename, and organize files
- **Auto-backup system** - Automatic versioning with timestamped backups
- **Soft delete** - Files are moved to trash instead of permanent deletion

### ✏️ Professional Text Editor
- **Full-featured editor** - Syntax-aware text editing with adjustable size
- **Auto-save** - Automatic saving with configurable intervals
- **Keyboard shortcuts** - Ctrl+S (save), Ctrl+F (search), and more
- **Real-time sync** - Content synchronization across all tabs

### 🔍 Search & Navigation
- **Advanced search** - Case-sensitive/insensitive text search with highlighting
- **Bookmarks** - Mark and quickly navigate to important sections
- **Line references** - Jump to specific line numbers
- **Match counting** - See total occurrences of search terms

### ⚡ Text Processing Tools
- **Token counting** - Integrated with text-generation-webui's tokenizer
- **Text statistics** - Word count, character count, line count
- **Text transformation** - Case conversion, whitespace trimming, line sorting
- **Content extraction** - Extract URLs, format as lists, and more
- **Batch operations** - Process multiple files at once

### 📝 Prompt Templates
Pre-built templates for common LLM tasks:
- Translation prompts
- Summarization requests
- Text rewriting
- Explanation generation
- Question extraction
- Keyword analysis
- Sentiment analysis
- Stable Diffusion prompt formatting

### 📤 Export & Import
- **Multiple formats** - Export to .txt, .md, .json
- **Metadata preservation** - Timestamps and file information
- **Bulk export** - Export multiple files at once
- **Import from URL** - Load text from web sources

### 📜 Version Control
- **Change history** - Track all modifications with timestamps
- **Diff viewer** - Visual comparison between versions
- **Version restore** - Revert to any previous version
- **Change annotations** - Add notes to specific versions

## 📦 Installation

1. Navigate to your text-generation-webui extensions folder:
```bash
cd text-generation-webui/extensions/
```

2. Create the extension directory:
```bash
mkdir text_manager_pro
cd text_manager_pro
```

3. Download the extension file:
```bash
wget https://raw.githubusercontent.com/hashms0a/text-manager-pro/main/script.py
```

Or clone the repository:
```bash
git clone https://github.com/hashms0a/text_manager_pro.git
```

4. Launch text-generation-webui with the extension:
```bash
python server.py --extensions text_manager_pro
```

## 🚀 Usage

### First Launch
On first launch, the extension will:
1. Create necessary directories (`files/`, `backups/`, `trash/`, `exports/`)
2. Generate default files (`info.txt`, `notes.txt`, `prompts.txt`)
3. Initialize the bookmark system

### Basic Operations

#### Creating a New File
1. Navigate to the Editor tab
2. Enter a filename in the "New file name" field
3. Click "➕ Create"

#### Editing and Saving
1. Select a file from the dropdown
2. Edit content in the text editor
3. Press Ctrl+S or click "💾 Save" to save changes

#### Searching Text
1. Enter search term in the search box
2. Toggle "Case sensitive" if needed
3. Click "🔍 Search" to highlight matches

#### Using Templates
1. Go to the Templates tab
2. Paste or type your text
3. Select a template type
4. Click "📝 Format for Prompt"
5. Optionally send to chat with "📤 Send to Chat"

### Advanced Features

#### Bookmarks
- Add bookmarks by specifying line numbers and names
- Bookmarks are saved per file
- Quick navigation to bookmarked sections

#### Text Processing
- Select from various text operations
- Process text without modifying the original
- Export processed results in different formats

#### Version History
- View all previous versions in the History tab
- Compare versions with diff highlighting
- Restore any previous version

## 🗂️ File Structure

```
text_manager_pro/
├── script.py           # Main extension file
├── files/             # Your text files
│   ├── info.txt
│   ├── notes.txt
│   └── prompts.txt
├── backups/           # Automatic backups
├── trash/             # Deleted files
├── exports/           # Exported files
└── bookmarks.json     # Bookmark data
```

## ⚙️ Configuration

The extension can be configured by modifying the `params` dictionary in `script.py`:

```python
params = {
    "display_name": "Text Manager Pro",
    "is_tab": True,
    "auto_refresh": False,
    "refresh_interval": 2,
    "default_files": ["info.txt", "notes.txt", "prompts.txt"],
    "max_history": 10,
    "enable_syntax_highlight": True,
    "theme": "dark"
}
```

You can also add custom settings in `settings.yaml`:
```yaml
text_manager_pro-max_history: 20
text_manager_pro-theme: 'light'
```

## 🎨 Customization

### Custom CSS
The extension includes custom CSS for improved styling. You can modify the `custom_css()` function to change:
- Editor fonts and sizes
- Button colors and styles
- Dark/light theme adjustments
- Layout spacing

### Custom Templates
Add your own prompt templates by modifying the `format_for_prompt()` function:
```python
templates = {
    "Your Template": f"Your custom prompt format: {content}",
    # Add more templates here
}
```

## 🔧 Troubleshooting

### Extension fails to load
- Ensure the extension is in the correct directory
- Check that all required files have proper permissions
- Look for error messages in the console

### Files not saving
- Verify write permissions in the extension directory
- Check disk space availability
- Ensure filenames are valid for your operating system

### Search not working
- Clear any existing search terms
- Try toggling case sensitivity
- Refresh the page if issues persist
