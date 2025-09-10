#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SCW Character Image Pack Generator - Main CLI Interface

Generates character image packs for Strip Club Wars 2 using Stable Diffusion WebUI API.
"""

import argparse
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.generator import CharacterImageGenerator
from src.character_loader import CharacterLoader
from src.config import Config

def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Generate SCW character image packs",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --test                              # Generate sample characters
  %(prog)s --config configs/character_config.json  # Generate from config
  %(prog)s --config configs/character_config.mini.json  # Quick test
        """
    )
    
    parser.add_argument(
        "--config", 
        type=str, 
        help="Path to character configuration file"
    )
    parser.add_argument(
        "--test", 
        action="store_true",
        help="Generate test characters"
    )
    parser.add_argument(
        "--test-type",
        type=str,
        default="simple",
        choices=["simple", "diverse"],
        help="Type of test characters to generate"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        help="Output directory for generated images"
    )
    parser.add_argument(
        "--modkey",
        type=str,
        help="Mod key for file naming"
    )
    parser.add_argument(
        "--list-configs",
        action="store_true",
        help="List available configuration files"
    )
    
    args = parser.parse_args()
    
    # Initialize components
    config = Config()
    character_loader = CharacterLoader()
    
    # List configs if requested
    if args.list_configs:
        print("Available configuration files:")
        configs = character_loader.list_available_configs()
        if configs:
            for config_file in configs:
                print(f"  - configs/{config_file}")
        else:
            print("  No configuration files found in configs/ directory")
        return
    
    # Create generator
    generator = CharacterImageGenerator(
        output_dir=args.output_dir,
        modkey=args.modkey
    )
    
    # Check WebUI connection
    if not generator.check_webui_connection():
        return
    
    # Load characters
    characters = []
    
    if args.config:
        characters = character_loader.load_from_config(args.config)
    elif args.test:
        print(f"🧪 Test mode: {args.test_type} characters")
        characters = character_loader.load_test_characters(args.test_type)
    else:
        print("Use one of the options:")
        print("  --test                          - generate sample characters")
        print("  --config configs/character_config.json  - load characters from file")
        print("  --list-configs                  - show available configs")
        return
    
    if not characters:
        print("❌ No characters to generate")
        return
    
    print(f"Starting generation for {len(characters)} characters...")
    
    # Generate images for all characters
    successful = 0
    total_images = 0
    
    for i, character in enumerate(characters, 1):
        print(f"\nGenerating character {i}/{len(characters)}")
        
        try:
            results = generator.generate_character_images(character)
            
            # Count successful results
            char_images = 0
            for pose_results in results.values():
                char_images += len([r for r in pose_results if r.success])
            
            if char_images > 0:
                successful += 1
                total_images += char_images
            
        except KeyboardInterrupt:
            print("\n⚠️ Generation interrupted by user")
            break
        except Exception as e:
            print(f"❌ Error generating character {character.name}: {e}")
    
    print(f"\nGeneration completed. Successfully created: {successful}/{len(characters)} characters")
    print(f"Total images generated: {total_images}")

if __name__ == "__main__":
    main()
