#!/bin/bash
# ChromSploit Framework - Asciinema Management Tool

ASCIINEMA_DIR="/home/danii/github-projects/ChromSploit-Framework/asciinema"
cd "$ASCIINEMA_DIR"

show_help() {
    echo "🎬 ChromSploit Framework - Asciinema Management Tool"
    echo "===================================================="
    echo ""
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commands:"
    echo "  list       - List all available recordings"
    echo "  play       - Play a specific recording"
    echo "  info       - Show recording information"
    echo "  record     - Create new recordings"
    echo "  concat     - Concatenate recordings"
    echo "  upload     - Upload to asciinema.org"
    echo "  clean      - Clean up temporary files"
    echo "  validate   - Validate all recordings"
    echo "  help       - Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 list"
    echo "  $0 play chromsploit_complete_demo.cast"
    echo "  $0 info 01_framework_startup.cast"
    echo "  $0 record"
    echo ""
}

list_recordings() {
    echo "📁 Available ChromSploit Asciinema Recordings"
    echo "=============================================="
    echo ""
    
    if [ ! -f "chromsploit_complete_demo.cast" ]; then
        echo "⚠️  Main demo not found. Run: $0 record"
    else
        echo "🎯 Main Demo:"
        ls -lh chromsploit_complete_demo.cast 2>/dev/null
        echo ""
    fi
    
    echo "🔍 Individual Recordings:"
    if ls [0-9]*.cast >/dev/null 2>&1; then
        for file in $(ls [0-9]*.cast | sort); do
            size=$(ls -lh "$file" | awk '{print $5}')
            echo "  📹 $file ($size)"
        done
    else
        echo "  No individual recordings found"
    fi
    
    echo ""
    echo "📊 Statistics:"
    cast_count=$(ls *.cast 2>/dev/null | wc -l)
    total_size=$(du -sh *.cast 2>/dev/null | tail -1 | awk '{print $1}' 2>/dev/null || echo "0")
    echo "  - Total recordings: $cast_count"
    echo "  - Total size: $total_size"
    
    if [ -f "playlist.json" ]; then
        echo "  ✅ Playlist metadata available"
    fi
    
    if [ -f "asciinema_links.txt" ]; then
        echo "  ✅ Upload links available"
    fi
}

play_recording() {
    if [ -z "$1" ]; then
        echo "❌ No recording specified"
        echo "Available recordings:"
        ls *.cast 2>/dev/null || echo "No recordings found"
        return 1
    fi
    
    if [ ! -f "$1" ]; then
        echo "❌ Recording not found: $1"
        return 1
    fi
    
    echo "🎬 Playing: $1"
    echo "Press Ctrl+C to stop"
    echo ""
    
    asciinema play "$1"
}

show_info() {
    if [ -z "$1" ]; then
        echo "❌ No recording specified"
        return 1
    fi
    
    if [ ! -f "$1" ]; then
        echo "❌ Recording not found: $1"
        return 1
    fi
    
    echo "ℹ️  Recording Information: $1"
    echo "==============================="
    
    # Parse header
    header=$(head -1 "$1")
    echo "📊 Technical Details:"
    echo "$header" | python3 -c "
import json, sys
data = json.load(sys.stdin)
print(f\"  - Version: {data.get('version', 'Unknown')}\")
print(f\"  - Width: {data.get('width', 'Unknown')}\")
print(f\"  - Height: {data.get('height', 'Unknown')}\")
print(f\"  - Duration: {data.get('duration', 'Unknown')} seconds\")
print(f\"  - Title: {data.get('title', 'No title')}\")
print(f\"  - Command: {data.get('command', 'Unknown')}\")
if 'env' in data:
    print(f\"  - Terminal: {data['env'].get('TERM', 'Unknown')}\")
"
    
    # File details
    echo ""
    echo "📁 File Details:"
    ls -lh "$1"
    
    # Event count
    event_count=$(($(wc -l < "$1") - 1))
    echo "  - Events: $event_count"
    
    echo ""
    echo "🎬 Preview (first 10 events):"
    tail -n +2 "$1" | head -10 | while read line; do
        echo "    $line"
    done
}

record_new() {
    echo "🎬 ChromSploit Framework - New Recording"
    echo "========================================"
    echo ""
    echo "Choose recording type:"
    echo "1) Complete framework demo (re-record all)"
    echo "2) Single module demo"
    echo "3) Custom recording"
    echo ""
    read -p "Selection [1-3]: " choice
    
    case $choice in
        1)
            echo "🔄 Re-recording complete framework demo..."
            ./record_intro.sh
            ;;
        2)
            echo "📋 Available modules:"
            echo "1) Framework startup"
            echo "2) CVE exploits"
            echo "3) Advanced features"
            echo "4) CVE-2025-2783"
            echo "5) WebAssembly JIT"
            echo "6) Tomcat RCE"
            echo "7) Git RCE"
            echo "8) Framework overview"
            read -p "Module [1-8]: " module
            
            filename="0${module}_module_$(date +%s).cast"
            echo "Recording to: $filename"
            asciinema rec "$filename" -t "ChromSploit Module $module"
            ;;
        3)
            read -p "Recording filename: " filename
            read -p "Recording title: " title
            echo "Starting custom recording..."
            asciinema rec "$filename" -t "$title"
            ;;
        *)
            echo "❌ Invalid selection"
            ;;
    esac
}

concatenate_recordings() {
    echo "🔄 Concatenating recordings..."
    if [ ! -f "concat_recordings.py" ]; then
        echo "❌ Concatenation script not found"
        return 1
    fi
    
    python3 concat_recordings.py
}

upload_recordings() {
    echo "📤 Uploading to asciinema.org..."
    if [ ! -f "upload_to_asciinema.sh" ]; then
        echo "❌ Upload script not found"
        return 1
    fi
    
    ./upload_to_asciinema.sh
}

clean_temp() {
    echo "🧹 Cleaning temporary files..."
    
    # Remove backup files
    rm -f *.cast.bak
    rm -f *.tmp
    
    # Remove old recordings (optional)
    read -p "Remove recordings older than 7 days? [y/N]: " confirm
    if [[ $confirm =~ ^[Yy]$ ]]; then
        find . -name "*.cast" -mtime +7 -not -name "chromsploit_complete_demo.cast" -not -name "[0-9][0-9]_*.cast"
        echo "Files to be removed (add -delete to actually remove)"
    fi
    
    echo "✅ Cleanup completed"
}

validate_recordings() {
    echo "✅ Validating recordings..."
    echo "=========================="
    
    error_count=0
    
    for cast_file in *.cast; do
        if [ ! -f "$cast_file" ]; then
            continue
        fi
        
        echo -n "Checking $cast_file... "
        
        # Check if file is valid JSON on first line
        if ! head -1 "$cast_file" | python3 -c "import json, sys; json.load(sys.stdin)" >/dev/null 2>&1; then
            echo "❌ Invalid header"
            ((error_count++))
            continue
        fi
        
        # Check if file has events
        if [ $(wc -l < "$cast_file") -lt 2 ]; then
            echo "❌ No events"
            ((error_count++))
            continue
        fi
        
        # Check file size
        if [ ! -s "$cast_file" ]; then
            echo "❌ Empty file"
            ((error_count++))
            continue
        fi
        
        echo "✅ Valid"
    done
    
    echo ""
    if [ $error_count -eq 0 ]; then
        echo "🎉 All recordings are valid!"
    else
        echo "⚠️  Found $error_count invalid recordings"
    fi
}

# Main command handling
case "$1" in
    "list"|"ls")
        list_recordings
        ;;
    "play")
        play_recording "$2"
        ;;
    "info")
        show_info "$2"
        ;;
    "record"|"rec")
        record_new
        ;;
    "concat"|"merge")
        concatenate_recordings
        ;;
    "upload")
        upload_recordings
        ;;
    "clean")
        clean_temp
        ;;
    "validate"|"check")
        validate_recordings
        ;;
    "help"|"-h"|"--help"|"")
        show_help
        ;;
    *)
        echo "❌ Unknown command: $1"
        echo ""
        show_help
        exit 1
        ;;
esac