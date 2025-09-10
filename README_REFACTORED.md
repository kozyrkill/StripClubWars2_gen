# SCW Character Image Pack Generator - Refactored Architecture

## 🏗️ New Architecture Overview

The codebase has been refactored into a modular, maintainable structure:

```
src/
├── __init__.py              # Package initialization
├── config.py                # Configuration settings and templates
├── models.py                # Data models and classes
├── prompt_generator.py      # Stable Diffusion prompt generation
├── sd_client.py            # Stable Diffusion WebUI API client
├── image_processor.py       # Image processing utilities
├── generator.py            # Main character image generator
└── character_loader.py     # Character configuration loading

main.py                     # CLI interface (entry point)
```

## 🎯 Key Improvements

### ✅ **Separation of Concerns**
- **Configuration**: All settings centralized in `config.py`
- **Data Models**: Clean dataclasses in `models.py`
- **API Client**: Dedicated SD WebUI client in `sd_client.py`
- **Image Processing**: Background removal and resizing in `image_processor.py`
- **Prompt Generation**: Complex prompt logic isolated in `prompt_generator.py`

### ✅ **Maintainability**
- **Modular Design**: Each module has a single responsibility
- **Type Safety**: Full type hints throughout
- **Error Handling**: Comprehensive error handling and logging
- **Configuration**: Easily configurable without code changes

### ✅ **Extensibility**
- **Plugin Architecture**: Easy to add new pose types or clothing styles
- **Configurable Prompts**: Templates can be modified without code changes
- **API Abstraction**: SD client can be easily swapped or extended

## 📁 Module Details

### `config.py` - Configuration Management
- **`Config`**: Main configuration class with all settings
- **`PromptTemplates`**: Prompt templates and mappings
- **`PoseConfig`**: Pose configurations and aliases
- Environment variable support for API URLs

### `models.py` - Data Models
- **`CharacterAttributes`**: Character definition with validation
- **`GenerationSettings`**: Image generation parameters
- **`GenerationResult`**: Result tracking with success/error states

### `prompt_generator.py` - Prompt Engineering
- **Smart Prompt Building**: Context-aware prompt construction
- **Gender-Aware**: Different prompts for male/female characters
- **Pose-Specific**: Detailed clothing descriptions per pose/reveal level
- **Anti-Cropping**: Advanced negative prompts for full-body generation

### `sd_client.py` - API Integration
- **Connection Management**: Robust connection handling
- **Timeout Handling**: Prevents hanging on slow generations
- **Error Recovery**: Graceful handling of API failures
- **Session Management**: Efficient HTTP session reuse

### `image_processor.py` - Image Operations
- **Background Removal**: Using rembg for clean backgrounds
- **Smart Resizing**: Maintains aspect ratio with proper centering
- **Format Optimization**: Ensures proper RGBA format for game use
- **Quality Processing**: Optimized for game integration

### `generator.py` - Core Generator
- **Session Management**: Organized output with timestamp-based sessions
- **Character ID Generation**: Time-based unique IDs following SCW conventions
- **Seed Management**: Consistent character appearance across poses
- **Progress Tracking**: Detailed progress reporting and error handling

### `character_loader.py` - Configuration Loading
- **Flexible Loading**: Supports multiple config formats and locations
- **Validation**: Ensures character data integrity
- **Fallback Support**: Built-in sample characters for testing
- **Error Recovery**: Graceful handling of malformed configs

## 🚀 Usage Examples

### Basic Usage
```bash
# Quick test
python main.py --test

# Generate from config
python main.py --config configs/character_config.json

# List available configs
python main.py --list-configs
```

### Advanced Usage
```bash
# Custom output directory
python main.py --config configs/character_config.json --output-dir my_characters

# Custom modkey
python main.py --config configs/character_config.json --modkey mymod

# Different test types
python main.py --test --test-type diverse
```

## 🔧 Configuration Options

### Environment Variables
```bash
export WEBUI_URL="http://localhost:7860"  # SD WebUI URL
```

### Config File Structure
All configuration templates are in `src/config.py`:
- Prompt templates
- Pose configurations
- Image generation settings
- Quality settings

## 🎨 Extending the Generator

### Adding New Poses
1. Add pose configuration to `PoseConfig.POSES_CONFIG`
2. Add pose prompts to `PoseConfig.POSE_PROMPTS`
3. Add clothing descriptions to `PromptGenerator._get_clothing_map()`

### Adding New Character Attributes
1. Update `CharacterAttributes` dataclass in `models.py`
2. Add prompt templates to `PromptTemplates` in `config.py`
3. Update `PromptGenerator.build_base_prompt()`

### Custom Image Processing
1. Extend `ImageProcessor` class
2. Override processing methods
3. Update `Generator` to use custom processor

## 🧪 Testing

The refactored code maintains full compatibility with existing functionality:

```bash
# Test basic functionality
python main.py --test --test-type simple

# Test with existing configs
python main.py --config configs/character_config.mini.json

# Verify all poses work
python main.py --config configs/character_config.players.json
```

## 📈 Performance Benefits

- **Faster Startup**: Modular loading reduces initialization time
- **Memory Efficiency**: Only load needed components
- **Better Error Handling**: Isolated failures don't crash entire generation
- **Concurrent Safe**: Better separation enables future concurrency improvements

## 🔄 Migration from Old Code

The new architecture is **fully backward compatible**:
- Same CLI interface (`main.py`)
- Same configuration files (in `configs/` folder)
- Same output format and naming conventions
- Same functionality and features

Old script users can simply:
```bash
# Old way (still works)
python scw_image_generator.py --config configs/character_config.json

# New way (recommended)  
python main.py --config configs/character_config.json
```

## 🏆 Code Quality

- **Type Safety**: 100% type hinted
- **Documentation**: Comprehensive docstrings
- **Error Handling**: Robust error management
- **Logging**: Detailed progress and error reporting
- **Modularity**: Clean separation of concerns
- **Testability**: Each module can be tested independently
