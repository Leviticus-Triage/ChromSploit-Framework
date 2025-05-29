#!/bin/bash
# ChromSploit Framework - Asciinema Upload Script
# Uploads recordings to asciinema.org for GitHub embedding

cd /home/danii/github-projects/ChromSploit-Framework/asciinema

echo "🚀 ChromSploit Framework - Asciinema Upload Tool"
echo "================================================="
echo ""

# Check if asciinema auth is configured
if ! asciinema auth >/dev/null 2>&1; then
    echo "⚠️  Asciinema authentication required!"
    echo "Run: asciinema auth"
    echo "Then retry this script."
    exit 1
fi

echo "📋 Available recordings:"
ls -la *.cast

echo ""
echo "🔄 Starting upload process..."
echo ""

# Upload main demo
echo "📤 Uploading main demo..."
MAIN_URL=$(asciinema upload chromsploit_complete_demo.cast 2>&1 | grep -o 'https://asciinema.org/a/[A-Za-z0-9]*')
if [ ! -z "$MAIN_URL" ]; then
    echo "✅ Main demo uploaded: $MAIN_URL"
    MAIN_ID=$(echo $MAIN_URL | grep -o '[A-Za-z0-9]*$')
else
    echo "❌ Main demo upload failed"
    MAIN_ID=""
fi

echo ""
echo "📤 Uploading individual recordings..."

# Upload individual recordings
declare -a UPLOAD_URLS=()
declare -a UPLOAD_IDS=()

for cast_file in $(ls [0-9]*.cast | sort); do
    echo "  Uploading $cast_file..."
    URL=$(asciinema upload "$cast_file" 2>&1 | grep -o 'https://asciinema.org/a/[A-Za-z0-9]*')
    if [ ! -z "$URL" ]; then
        echo "  ✅ $cast_file -> $URL"
        UPLOAD_URLS+=("$URL")
        ID=$(echo $URL | grep -o '[A-Za-z0-9]*$')
        UPLOAD_IDS+=("$ID")
    else
        echo "  ❌ $cast_file upload failed"
        UPLOAD_URLS+=("")
        UPLOAD_IDS+=("")
    fi
done

echo ""
echo "📝 Generating GitHub README snippets..."

# Create README snippets
cat > github_embed_snippets.md << EOF
# ChromSploit Framework - GitHub README Snippets

## Main Demo (Complete)
\`\`\`markdown
[![ChromSploit Framework Demo](https://asciinema.org/a/${MAIN_ID}.svg)](https://asciinema.org/a/${MAIN_ID})
\`\`\`

## Individual Modules

### Framework Startup
\`\`\`markdown
[![Framework Startup](https://asciinema.org/a/${UPLOAD_IDS[0]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[0]})
\`\`\`

### CVE Exploits Overview
\`\`\`markdown
[![CVE Exploits](https://asciinema.org/a/${UPLOAD_IDS[1]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[1]})
\`\`\`

### Advanced Features
\`\`\`markdown
[![Advanced Features](https://asciinema.org/a/${UPLOAD_IDS[2]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[2]})
\`\`\`

### CVE-2025-2783 Exploit Demo
\`\`\`markdown
[![CVE-2025-2783](https://asciinema.org/a/${UPLOAD_IDS[3]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[3]})
\`\`\`

### WebAssembly JIT Exploit
\`\`\`markdown
[![WebAssembly JIT](https://asciinema.org/a/${UPLOAD_IDS[4]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[4]})
\`\`\`

### Apache Tomcat RCE
\`\`\`markdown
[![Tomcat RCE](https://asciinema.org/a/${UPLOAD_IDS[5]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[5]})
\`\`\`

### Git RCE Demo
\`\`\`markdown
[![Git RCE](https://asciinema.org/a/${UPLOAD_IDS[6]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[6]})
\`\`\`

### Framework Overview
\`\`\`markdown
[![Framework Overview](https://asciinema.org/a/${UPLOAD_IDS[7]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[7]})
\`\`\`

## For README.md Main Section

\`\`\`markdown
## 🎬 Live Demo

See ChromSploit Framework in action:

[![ChromSploit Framework Complete Demo](https://asciinema.org/a/${MAIN_ID}.svg)](https://asciinema.org/a/${MAIN_ID})

### Quick Feature Demos

| Feature | Demo | Description |
|---------|------|-------------|
| 🚀 Framework | [![Startup](https://asciinema.org/a/${UPLOAD_IDS[0]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[0]}) | Framework startup and basics |
| 🔍 CVE Exploits | [![CVE Exploits](https://asciinema.org/a/${UPLOAD_IDS[1]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[1]}) | Available exploit modules |
| ⚡ Mojo IPC | [![CVE-2025-2783](https://asciinema.org/a/${UPLOAD_IDS[3]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[3]}) | Chrome sandbox escape |
| 🧠 WebAssembly | [![WASM JIT](https://asciinema.org/a/${UPLOAD_IDS[4]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[4]}) | Edge JIT type confusion |
| 🐱 Tomcat RCE | [![Tomcat](https://asciinema.org/a/${UPLOAD_IDS[5]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[5]}) | Apache Tomcat exploitation |
| 📚 Git RCE | [![Git RCE](https://asciinema.org/a/${UPLOAD_IDS[6]}.svg)](https://asciinema.org/a/${UPLOAD_IDS[6]}) | Git repository attacks |

\`\`\`
EOF

# Create links file
cat > asciinema_links.txt << EOF
ChromSploit Framework - Asciinema Links
=======================================

Main Demo: $MAIN_URL

Individual Recordings:
- Framework Startup: ${UPLOAD_URLS[0]}
- CVE Exploits: ${UPLOAD_URLS[1]}
- Advanced Features: ${UPLOAD_URLS[2]}
- CVE-2025-2783: ${UPLOAD_URLS[3]}
- WebAssembly JIT: ${UPLOAD_URLS[4]}
- Tomcat RCE: ${UPLOAD_URLS[5]}
- Git RCE: ${UPLOAD_URLS[6]}
- Framework Overview: ${UPLOAD_URLS[7]}

Upload completed: $(date)
EOF

echo ""
echo "✅ Upload process completed!"
echo ""
echo "📋 Summary:"
echo "  - Main demo: $MAIN_URL"
echo "  - Individual recordings: ${#UPLOAD_URLS[@]} uploaded"
echo ""
echo "📁 Generated files:"
echo "  - github_embed_snippets.md (for README.md)"
echo "  - asciinema_links.txt (all links)"
echo ""
echo "🔗 Next steps:"
echo "  1. Copy snippets from github_embed_snippets.md"
echo "  2. Update main README.md with demo links"
echo "  3. Test embedded players in GitHub"
echo ""
echo "🎬 ChromSploit Framework demos now available online!"