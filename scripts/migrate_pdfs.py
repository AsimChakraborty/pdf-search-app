"""
Migration Script
Index existing PDFs to ChromaDB for semantic search
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.semantic_search import rebuild_chroma_index


def main():
    print("=" * 50)
    print("PDF to ChromaDB Migration Script")
    print("=" * 50)
    print()
    
    print("This script will index all PDFs in the SQLite database to ChromaDB.")
    print("Existing ChromaDB data will be cleared and rebuilt.")
    print()
    
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() != 'yes':
        print("Cancelled.")
        return
    
    print("\nStarting migration...")
    print()
    
    try:
        count = rebuild_chroma_index()
        print()
        print("=" * 50)
        print(f"SUCCESS! Indexed {count} pages to ChromaDB.")
        print("=" * 50)
    except Exception as e:
        print(f"\nERROR: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()