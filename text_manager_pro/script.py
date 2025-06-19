import os
import json
import gradio as gr
from datetime import datetime
import difflib
from pathlib import Path
import re
from modules import chat, shared
from modules.text_generation import encode

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

# Global variables
displayed_text = ""
extension_dir = ""
text_history = []
current_file = None
file_contents = {}
bookmarks = {}
last_modified = {}

def setup():
    """Initialize the extension and load default files."""
    global displayed_text, extension_dir, file_contents, bookmarks
    
    extension_dir = os.path.dirname(__file__)
    
    # Create necessary directories
    os.makedirs(os.path.join(extension_dir, "files"), exist_ok=True)
    os.makedirs(os.path.join(extension_dir, "backups"), exist_ok=True)
    
    # Load default files
    for filename in params["default_files"]:
        file_path = os.path.join(extension_dir, "files", filename)
        if not os.path.exists(file_path):
            # Create default files if they don't exist
            with open(file_path, "w", encoding="utf-8") as f:
                if filename == "info.txt":
                    f.write("# Text Manager Pro\n\nWelcome to the enhanced text management extension!")
                elif filename == "notes.txt":
                    f.write("# Notes\n\nYour notes go here...")
                elif filename == "prompts.txt":
                    f.write("# Prompt Templates\n\n## Translation\nTranslate the following to [LANGUAGE]:\n\n## Summary\nSummarize this text in 3 bullet points:")
        
        load_file_content(file_path)
    
    # Load bookmarks if exists
    bookmarks_path = os.path.join(extension_dir, "bookmarks.json")
    if os.path.exists(bookmarks_path):
        with open(bookmarks_path, "r") as f:
            bookmarks = json.load(f)
    
    # Set default displayed text
    default_file = os.path.join(extension_dir, "files", params["default_files"][0])
    if os.path.exists(default_file):
        with open(default_file, "r", encoding="utf-8") as f:
            displayed_text = f.read()

def load_file_content(file_path):
    """Load file content and track modification time."""
    global file_contents, last_modified
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            file_contents[file_path] = content
            last_modified[file_path] = os.path.getmtime(file_path)
            return content
    except Exception as e:
        return f"Error loading file: {e}"

def save_to_history(content, filename):
    """Save content to history for undo functionality."""
    global text_history
    text_history.append({
        "content": content,
        "filename": filename,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    })
    if len(text_history) > params["max_history"]:
        text_history.pop(0)

def save_text(content, filename, create_backup=True):
    """Save text to file with optional backup."""
    try:
        file_path = os.path.join(extension_dir, "files", filename)
        
        # Create backup if requested
        if create_backup and os.path.exists(file_path):
            backup_dir = os.path.join(extension_dir, "backups")
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = os.path.join(backup_dir, f"{filename}.{timestamp}.bak")
            with open(file_path, "r", encoding="utf-8") as f:
                backup_content = f.read()
            with open(backup_path, "w", encoding="utf-8") as f:
                f.write(backup_content)
        
        # Save new content
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        save_to_history(content, filename)
        file_contents[file_path] = content
        last_modified[file_path] = os.path.getmtime(file_path)
        
        return f"✅ Saved to {filename} successfully!", content
    except Exception as e:
        return f"❌ Error saving file: {e}", content

def load_file(filename):
    """Load a file from the files directory."""
    global current_file, displayed_text
    try:
        if filename:
            file_path = os.path.join(extension_dir, "files", filename)
            content = load_file_content(file_path)
            current_file = filename
            displayed_text = content
            return content, f"📄 Loaded: {filename}"
        return displayed_text, "No file selected"
    except Exception as e:
        return f"Error: {e}", f"❌ Failed to load {filename}"

def search_text(content, search_term, case_sensitive):
    """Search and highlight text."""
    if not search_term:
        return content
    
    flags = 0 if case_sensitive else re.IGNORECASE
    pattern = re.escape(search_term)
    highlighted = re.sub(f"({pattern})", r"**\1**", content, flags=flags)
    
    # Count occurrences
    matches = len(re.findall(pattern, content, flags=flags))
    return highlighted + f"\n\n---\n*Found {matches} occurrence(s)*"

def process_text(content, operation):
    """Process text with various operations."""
    if operation == "Trim Whitespace":
        return "\n".join(line.strip() for line in content.split("\n"))
    elif operation == "Count Tokens":
        try:
            tokens = encode(content)[0]
            token_count = len(tokens)
            return content + f"\n\n---\n*Token count: {token_count}*"
        except:
            return content + "\n\n---\n*Token counting not available*"
    elif operation == "Count Words":
        word_count = len(content.split())
        char_count = len(content)
        line_count = len(content.split("\n"))
        return content + f"\n\n---\n*Words: {word_count} | Characters: {char_count} | Lines: {line_count}*"
    elif operation == "Convert to Uppercase":
        return content.upper()
    elif operation == "Convert to Lowercase":
        return content.lower()
    elif operation == "Remove Empty Lines":
        return "\n".join(line for line in content.split("\n") if line.strip())
    elif operation == "Sort Lines":
        lines = [line for line in content.split("\n") if line.strip()]
        return "\n".join(sorted(lines))
    elif operation == "Reverse Lines":
        lines = content.split("\n")
        return "\n".join(reversed(lines))
    elif operation == "Extract URLs":
        url_pattern = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
        urls = re.findall(url_pattern, content)
        if urls:
            return "# Extracted URLs:\n\n" + "\n".join(urls)
        else:
            return "No URLs found in the text."
    elif operation == "Format as Markdown List":
        lines = [line.strip() for line in content.split("\n") if line.strip()]
        return "\n".join(f"- {line}" for line in lines)
    return content

def export_text(content, format_type, filename):
    """Export text in various formats."""
    try:
        export_dir = os.path.join(extension_dir, "exports")
        os.makedirs(export_dir, exist_ok=True)
        
        base_name = os.path.splitext(filename)[0] if filename else "export"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if format_type == "Text (.txt)":
            export_path = os.path.join(export_dir, f"{base_name}_{timestamp}.txt")
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(content)
        elif format_type == "Markdown (.md)":
            export_path = os.path.join(export_dir, f"{base_name}_{timestamp}.md")
            with open(export_path, "w", encoding="utf-8") as f:
                f.write(content)
        elif format_type == "JSON (.json)":
            export_path = os.path.join(export_dir, f"{base_name}_{timestamp}.json")
            data = {
                "filename": filename,
                "content": content,
                "exported_at": datetime.now().isoformat(),
                "lines": content.split("\n")
            }
            with open(export_path, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        
        return f"✅ Exported to: {export_path}"
    except Exception as e:
        return f"❌ Export failed: {e}"

def get_file_list():
    """Get list of available files."""
    files_dir = os.path.join(extension_dir, "files")
    if os.path.exists(files_dir):
        return [f for f in os.listdir(files_dir) if f.endswith(('.txt', '.md'))]
    return []

def create_new_file(filename):
    """Create a new file."""
    if not filename:
        return "Please enter a filename", get_file_list()
    
    if not filename.endswith(('.txt', '.md')):
        filename += '.txt'
    
    file_path = os.path.join(extension_dir, "files", filename)
    if os.path.exists(file_path):
        return f"File {filename} already exists", get_file_list()
    
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(f"# {filename}\n\nNew file created on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        return f"✅ Created: {filename}", get_file_list()
    except Exception as e:
        return f"❌ Error: {e}", get_file_list()

def delete_file(filename):
    """Delete a file (moves to trash folder)."""
    if not filename:
        return "No file selected", get_file_list()
    
    try:
        file_path = os.path.join(extension_dir, "files", filename)
        trash_dir = os.path.join(extension_dir, "trash")
        os.makedirs(trash_dir, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        trash_path = os.path.join(trash_dir, f"{filename}.{timestamp}")
        
        os.rename(file_path, trash_path)
        return f"🗑️ Moved {filename} to trash", get_file_list()
    except Exception as e:
        return f"❌ Error: {e}", get_file_list()

def add_bookmark(content, line_number, bookmark_name):
    """Add a bookmark to the current file."""
    global bookmarks, current_file
    
    if not current_file:
        return "No file loaded"
    
    if not bookmark_name:
        bookmark_name = f"Bookmark at line {line_number}"
    
    if current_file not in bookmarks:
        bookmarks[current_file] = []
    
    bookmarks[current_file].append({
        "name": bookmark_name,
        "line": line_number,
        "preview": content.split('\n')[line_number-1] if line_number <= len(content.split('\n')) else "",
        "created": datetime.now().isoformat()
    })
    
    # Save bookmarks
    bookmarks_path = os.path.join(extension_dir, "bookmarks.json")
    with open(bookmarks_path, "w") as f:
        json.dump(bookmarks, f, indent=2)
    
    return f"✅ Bookmark added: {bookmark_name}"

def get_diff(old_content, new_content):
    """Get diff between two versions of content."""
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    diff = difflib.unified_diff(old_lines, new_lines, fromfile='Previous', tofile='Current', lineterm='')
    diff_text = ''.join(diff)
    
    if diff_text:
        return f"```diff\n{diff_text}\n```"
    else:
        return "No changes detected"

def format_for_prompt(content, template_type):
    """Format text for various prompt templates."""
    templates = {
        "Translation": f"Translate the following text to [TARGET_LANGUAGE]:\n\n{content}",
        "Summary": f"Please summarize the following text in 3-5 bullet points:\n\n{content}",
        "Rewrite": f"Please rewrite the following text to be more clear and concise:\n\n{content}",
        "Explain": f"Please explain the following text in simple terms:\n\n{content}",
        "Questions": f"Generate 5 questions about the following text:\n\n{content}",
        "Keywords": f"Extract the main keywords and concepts from this text:\n\n{content}",
        "Sentiment": f"Analyze the sentiment and tone of this text:\n\n{content}",
        "Fact Check": f"Please fact-check and verify the claims in this text:\n\n{content}",
        "SD Prompt": f"Positive prompt: {content}\n\nNegative prompt: [ADD_NEGATIVE_TERMS]",
        "Custom": content
    }
    
    return templates.get(template_type, content)

def send_to_chat(content):
    """Send content to the chat interface."""
    # This function would integrate with the chat interface
    # For now, we'll return a formatted version
    return f"📤 Ready to send to chat:\n\n{content[:200]}..."

def ui():
    """Create the UI components."""
    with gr.Tabs():
        # Main Editor Tab
        with gr.Tab("Editor"):
            with gr.Row():
                with gr.Column(scale=3):
                    # File selector
                    file_dropdown = gr.Dropdown(
                        choices=get_file_list(),
                        label="📁 Select File",
                        value=params["default_files"][0] if get_file_list() else None
                    )
                    
                    # Main text editor
                    text_editor = gr.Textbox(
                        value=displayed_text,
                        label="✏️ Text Editor",
                        lines=20,
                        max_lines=50,
                        elem_classes="text-editor"
                    )
                    
                    # Editor controls
                    with gr.Row():
                        save_btn = gr.Button("💾 Save", variant="primary")
                        save_as_input = gr.Textbox(label="Save as:", placeholder="filename.txt", scale=2)
                        save_as_btn = gr.Button("💾 Save As")
                    
                    save_status = gr.Markdown()
                
                with gr.Column(scale=1):
                    # File management
                    gr.Markdown("### 📂 File Management")
                    new_file_input = gr.Textbox(label="New file name:", placeholder="my_file.txt")
                    with gr.Row():
                        create_btn = gr.Button("➕ Create", size="sm")
                        delete_btn = gr.Button("🗑️ Delete", size="sm", variant="stop")
                    
                    file_status = gr.Markdown()
                    
                    # Search
                    gr.Markdown("### 🔍 Search")
                    search_input = gr.Textbox(label="Search term:", placeholder="Enter text to search")
                    case_sensitive = gr.Checkbox(label="Case sensitive", value=False)
                    search_btn = gr.Button("🔍 Search")
                    
                    # Bookmarks
                    gr.Markdown("### 📌 Bookmarks")
                    bookmark_line = gr.Number(label="Line number:", value=1, precision=0)
                    bookmark_name = gr.Textbox(label="Bookmark name:", placeholder="Important section")
                    add_bookmark_btn = gr.Button("📌 Add Bookmark")
                    bookmark_status = gr.Markdown()
        
        # Text Processing Tab
        with gr.Tab("Processing"):
            with gr.Row():
                with gr.Column():
                    process_input = gr.Textbox(
                        value=displayed_text,
                        label="Input Text",
                        lines=15
                    )
                    
                    operation_dropdown = gr.Dropdown(
                        choices=[
                            "Trim Whitespace",
                            "Count Tokens",
                            "Count Words",
                            "Convert to Uppercase",
                            "Convert to Lowercase",
                            "Remove Empty Lines",
                            "Sort Lines",
                            "Reverse Lines",
                            "Extract URLs",
                            "Format as Markdown List"
                        ],
                        label="Select Operation",
                        value="Count Words"
                    )
                    
                    process_btn = gr.Button("⚡ Process Text", variant="primary")
                
                with gr.Column():
                    process_output = gr.Textbox(
                        label="Processed Output",
                        lines=15
                    )
                    
                    # Export options
                    gr.Markdown("### 📤 Export Options")
                    export_format = gr.Dropdown(
                        choices=["Text (.txt)", "Markdown (.md)", "JSON (.json)"],
                        label="Export Format",
                        value="Text (.txt)"
                    )
                    export_btn = gr.Button("📥 Export")
                    export_status = gr.Markdown()
        
        # Templates Tab
        with gr.Tab("Templates"):
            with gr.Row():
                with gr.Column():
                    template_input = gr.Textbox(
                        value=displayed_text,
                        label="Input Text",
                        lines=10
                    )
                    
                    template_type = gr.Dropdown(
                        choices=[
                            "Translation",
                            "Summary",
                            "Rewrite",
                            "Explain",
                            "Questions",
                            "Keywords",
                            "Sentiment",
                            "Fact Check",
                            "SD Prompt",
                            "Custom"
                        ],
                        label="Template Type",
                        value="Summary"
                    )
                    
                    format_btn = gr.Button("📝 Format for Prompt", variant="primary")
                
                with gr.Column():
                    template_output = gr.Textbox(
                        label="Formatted Prompt",
                        lines=10
                    )
                    
                    send_chat_btn = gr.Button("📤 Send to Chat", variant="primary")
                    chat_status = gr.Markdown()
        
        # History Tab
        with gr.Tab("History"):
            history_display = gr.Markdown("### 📜 File History\n\nNo history available yet.")
            refresh_history_btn = gr.Button("🔄 Refresh History")
            
            with gr.Row():
                history_file_select = gr.Dropdown(
                    choices=[],
                    label="Select Version"
                )
                restore_btn = gr.Button("♻️ Restore Version")
            
            diff_display = gr.Markdown()
    
    # Event handlers
    file_dropdown.change(
        fn=load_file,
        inputs=[file_dropdown],
        outputs=[text_editor, save_status]
    )
    
    save_btn.click(
        fn=lambda content: save_text(content, current_file if current_file else "untitled.txt"),
        inputs=[text_editor],
        outputs=[save_status, text_editor]
    )
    
    save_as_btn.click(
        fn=lambda content, filename: save_text(content, filename if filename else "untitled.txt"),
        inputs=[text_editor, save_as_input],
        outputs=[save_status, text_editor]
    )
    
    create_btn.click(
        fn=create_new_file,
        inputs=[new_file_input],
        outputs=[file_status, file_dropdown]
    )
    
    delete_btn.click(
        fn=lambda filename: delete_file(filename),
        inputs=[file_dropdown],
        outputs=[file_status, file_dropdown]
    )
    
    search_btn.click(
        fn=search_text,
        inputs=[text_editor, search_input, case_sensitive],
        outputs=[text_editor]
    )
    
    add_bookmark_btn.click(
        fn=lambda content, line, name: add_bookmark(content, int(line), name),
        inputs=[text_editor, bookmark_line, bookmark_name],
        outputs=[bookmark_status]
    )
    
    process_btn.click(
        fn=process_text,
        inputs=[process_input, operation_dropdown],
        outputs=[process_output]
    )
    
    export_btn.click(
        fn=lambda content, format: export_text(content, format, current_file),
        inputs=[process_output, export_format],
        outputs=[export_status]
    )
    
    format_btn.click(
        fn=format_for_prompt,
        inputs=[template_input, template_type],
        outputs=[template_output]
    )
    
    send_chat_btn.click(
        fn=send_to_chat,
        inputs=[template_output],
        outputs=[chat_status]
    )
    
    # Update process input when main editor changes
    text_editor.change(
        fn=lambda x: (x, x),
        inputs=[text_editor],
        outputs=[process_input, template_input]
    )

def custom_css():
    """Custom CSS for better styling."""
    return """
    .text-editor textarea {
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 14px;
        line-height: 1.5;
    }
    
    .gr-button-primary {
        background-color: #2563eb !important;
    }
    
    .gr-button-primary:hover {
        background-color: #1d4ed8 !important;
    }
    
    .gr-button-stop {
        background-color: #dc2626 !important;
    }
    
    .gr-button-stop:hover {
        background-color: #b91c1c !important;
    }
    
    .dark .text-editor textarea {
        background-color: #1a1a1a;
        color: #e0e0e0;
    }
    
    .markdown-text h1, .markdown-text h2, .markdown-text h3 {
        color: #3b82f6;
    }
    
    .diff-display {
        font-family: monospace;
        white-space: pre-wrap;
    }
    
    .diff-display .added {
        background-color: #22c55e20;
        color: #22c55e;
    }
    
    .diff-display .removed {
        background-color: #ef444420;
        color: #ef4444;
    }
    """

def custom_js():
    """Custom JavaScript for enhanced functionality."""
    return """
    // Add line numbers functionality
    function addLineNumbers(textarea) {
        // This would add line numbers to the textarea
        // Implementation depends on the specific requirements
    }
    
    // Auto-save functionality
    let autoSaveTimer;
    function setupAutoSave() {
        const textareas = document.querySelectorAll('.text-editor textarea');
        textareas.forEach(textarea => {
            textarea.addEventListener('input', () => {
                clearTimeout(autoSaveTimer);
                autoSaveTimer = setTimeout(() => {
                    // Trigger auto-save after 3 seconds of inactivity
                    console.log('Auto-saving...');
                }, 3000);
            });
        });
    }
    
    // Keyboard shortcuts
    document.addEventListener('keydown', (e) => {
        // Ctrl/Cmd + S to save
        if ((e.ctrlKey || e.metaKey) && e.key === 's') {
            e.preventDefault();
            const saveBtn = document.querySelector('[value="💾 Save"]');
            if (saveBtn) saveBtn.click();
        }
        
        // Ctrl/Cmd + F for search
        if ((e.ctrlKey || e.metaKey) && e.key === 'f') {
            e.preventDefault();
            const searchInput = document.querySelector('[placeholder="Enter text to search"]');
            if (searchInput) searchInput.focus();
        }
    });
    
    // Initialize when page loads
    setTimeout(setupAutoSave, 1000);
    """

# Optional modifier functions (not used in this extension)
def input_modifier(string, state, is_chat=False):
    return string

def output_modifier(string, state, is_chat=False):
    return string

def bot_prefix_modifier(string, state):
    return string

def state_modifier(state):
    return state

def history_modifier(history):
    return history

def chat_input_modifier(text, visible_text, state):
    return text, visible_text
