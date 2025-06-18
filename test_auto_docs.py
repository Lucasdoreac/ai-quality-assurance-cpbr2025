#!/usr/bin/env python3
"""
Simple test script for the auto-documentation system.
Tests the documentation generation functionality.
"""

import asyncio
import sys
from pathlib import Path

# Add current directory to path
sys.path.insert(0, str(Path(__file__).parent))

async def test_documentation_generation():
    """Test the documentation generation system."""
    try:
        # Import the documentation generator directly
        import sys
        sys.path.insert(0, 'src')
        from automation.doc_generator import DocumentationGenerator
        
        print("🚀 Testing Auto-Documentation System")
        print("=" * 50)
        
        # Initialize generator
        generator = DocumentationGenerator(Path('.'))
        print("✅ Documentation generator initialized")
        
        # Test README generation
        print("\n📝 Generating README.md...")
        readme_success = await generator.update_readme()
        print(f"README.md: {'✅ Success' if readme_success else '❌ Failed'}")
        
        # Test CHANGELOG generation
        print("\n📝 Generating CHANGELOG.md...")
        changelog_success = await generator.update_changelog()
        print(f"CHANGELOG.md: {'✅ Success' if changelog_success else '❌ Failed'}")
        
        # Test API docs generation
        print("\n📝 Generating API_DOCS.md...")
        api_success = await generator.update_api_docs()
        print(f"API_DOCS.md: {'✅ Success' if api_success else '❌ Failed'}")
        
        # Test architecture docs generation
        print("\n📝 Generating ARCHITECTURE.md...")
        arch_success = await generator.update_architecture_docs()
        print(f"ARCHITECTURE.md: {'✅ Success' if arch_success else '❌ Failed'}")
        
        # Summary
        total_tests = 4
        successful_tests = sum([readme_success, changelog_success, api_success, arch_success])
        
        print("\n" + "=" * 50)
        print(f"📊 Test Results: {successful_tests}/{total_tests} successful")
        
        if successful_tests == total_tests:
            print("🎉 All documentation generated successfully!")
            print("\n🔍 Generated files:")
            
            doc_files = ['README.md', 'CHANGELOG.md', 'API_DOCS.md', 'ARCHITECTURE.md']
            for doc_file in doc_files:
                file_path = Path(doc_file)
                if file_path.exists():
                    size = file_path.stat().st_size
                    print(f"  ✅ {doc_file} ({size:,} bytes)")
                else:
                    print(f"  ❌ {doc_file} (not found)")
            
            print("\n🚀 Auto-Documentation System is working perfectly!")
            print("Ready for Campus Party Brasil 2025 demonstration!")
            return True
        else:
            print(f"⚠️ Some documentation generation failed ({successful_tests}/{total_tests})")
            return False
            
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure you're running this from the project root directory.")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Main test function."""
    print("🧪 AI Quality Assurance Auto-Documentation Test")
    print("=" * 60)
    
    result = asyncio.run(test_documentation_generation())
    
    if result:
        print("\n✅ Auto-documentation system test PASSED!")
        return 0
    else:
        print("\n❌ Auto-documentation system test FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())