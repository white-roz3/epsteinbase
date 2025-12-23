#!/bin/bash
# Monitor git push progress

echo "🔍 Monitoring Git Push..."
echo ""

while true; do
    clear
    echo "=== Git Push Monitor ==="
    echo ""
    echo "Time: $(date +%H:%M:%S)"
    echo ""
    
    cd /Users/white_roze/epsteinbase
    
    echo "--- Git Status ---"
    git status 2>&1 | grep -A2 "Your branch" | head -3
    echo ""
    
    echo "--- Commits Ahead ---"
    AHEAD=$(git rev-list --count origin/main..HEAD 2>/dev/null || echo "0")
    if [ "$AHEAD" -gt 0 ]; then
        echo "⚠️  $AHEAD commits ahead (still pushing...)"
        git log origin/main..HEAD --oneline 2>&1 | head -5
    else
        echo "✅ All commits pushed!"
    fi
    echo ""
    
    echo "--- Push Process ---"
    if ps aux | grep -q "[g]it push"; then
        echo "🔄 Push process is running..."
    else
        echo "⏸️  No push process active"
    fi
    echo ""
    
    if [ "$AHEAD" -eq 0 ]; then
        echo "✅ Push completed! Your branch is up to date."
        break
    fi
    
    echo "Press Ctrl+C to stop monitoring"
    sleep 3
done

