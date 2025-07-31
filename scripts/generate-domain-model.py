#!/usr/bin/env python3
"""
LAB Product Validation Workflow - Domain Model Generator
Generates complete domain model with all entities and associations
"""

import yaml
import xml.etree.ElementTree as ET
from pathlib import Path
import argparse
import sys
from datetime import datetime

def load_config(config_path):
    """Load configuration from YAML file with fallback"""
    try:
        # Try the specified path first
        if Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as file:
                return yaml.safe_load(file)
        
        # Try alternative paths
        alternative_paths = [
            Path("config/domain-model-config.yaml"),
            Path("config/lab-workflow-config.yaml"),
            Path("../config/domain-model-config.yaml")
        ]
        
        for alt_path in alternative_paths:
            if alt_path.exists():
                print(f"📁 Using configuration from: {alt_path}")
                with open(alt_path, 'r', encoding='utf-8') as file:
                    return yaml.safe_load(file)
        
        # If no config found, provide default configuration
        print("⚠️ No configuration file found, using default entities")
        return {
            'entities': [
                {
                    'name': 'ProductValidation',
                    'generalization': 'System.WorkflowContext',
                    'attributes': [
                        {'name': 'ProductID', 'type': 'String', 'length': 50},
                        {'name': 'WorkflowOutcome', 'type': 'Boolean'},
                        {'name': 'ValidationStage', 'type': 'Enumeration', 'enumeration': 'WorkflowStage'},
                        {'name': 'CreatedDate', 'type': 'DateTime'},
                        {'name': 'CompletedDate', 'type': 'DateTime'}
                    ]
                },
                {
                    'name': 'ImageAcquisition',
                    'attributes': [
                        {'name': 'ImageFile', 'type': 'System.Image'},
                        {'name': 'IsQualityApproved', 'type': 'Boolean'},
                        {'name': 'TechnicianID', 'type': 'String', 'length': 50},
                        {'name': 'AcquisitionDate', 'type': 'DateTime'},
                        {'name': 'QualityScore', 'type': 'Decimal', 'length': 8}
                    ]
                },
                {
                    'name': 'DetailedImageAcquisition',
                    'attributes': [
                        {'name': 'EnhancedImageFile', 'type': 'System.Image'},
                        {'name': 'ProcessingStatus', 'type': 'Enumeration', 'enumeration': 'ProcessingStatus'},
                        {'name': 'ProcessedBy', 'type': 'String', 'length': 50},
                        {'name': 'ProcessingDate', 'type': 'DateTime'}
                    ]
                },
                {
                    'name': 'ValidationResult',
                    'attributes': [
                        {'name': 'Result', 'type': 'Enumeration', 'enumeration': 'ValidationOutcome'},
                        {'name': 'ValidatedBy', 'type': 'String', 'length': 50},
                        {'name': 'ValidationDate', 'type': 'DateTime'},
                        {'name': 'Comments', 'type': 'String', 'length': 1000}
                    ]
                }
            ]
        }
        
    except Exception as e:
        print(f"❌ Error loading configuration: {e}")
        return None

def generate_entity_xml(entity_config):
    """Generate XML for a single entity with proper Mendix structure"""
    try:
        # Create root entity element
        entity = ET.Element("entity")
        entity.set("name", entity_config.get('name', 'UnknownEntity'))
        
        # Add documentation if provided
        if 'description' in entity_config:
            documentation = ET.SubElement(entity, "documentation")
            documentation.text = entity_config['description']
        
        # Add generalization if specified
        if 'generalization' in entity_config:
            generalization = ET.SubElement(entity, "generalization")
            generalization.set("type", entity_config['generalization'])
        
        # Add attributes
        if 'attributes' in entity_config and entity_config['attributes']:
            attributes_elem = ET.SubElement(entity, "attributes")
            
            for attr in entity_config['attributes']:
                attr_elem = ET.SubElement(attributes_elem, "attribute")
                attr_elem.set("name", attr.get('name', 'UnknownAttribute'))
                attr_elem.set("type", attr.get('type', 'String'))
                
                # Add length for string and decimal attributes
                if attr.get('type') in ['String', 'Decimal'] and 'length' in attr:
                    attr_elem.set("length", str(attr['length']))
                
                # Add enumeration reference
                if 'enumeration' in attr:
                    attr_elem.set("enumeration", attr['enumeration'])
                
                # Add default value if specified
                if 'default' in attr:
                    attr_elem.set("default", str(attr['default']))
        
        return entity
        
    except Exception as e:
        print(f"❌ Error creating entity XML for {entity_config.get('name', 'unknown')}: {e}")
        return None

def create_mendix_xml_header():
    """Create proper Mendix XML header"""
    return '<?xml version="1.0" encoding="UTF-8"?>\n'

def format_xml_output(element):
    """Format XML with proper indentation"""
    from xml.dom import minidom
    rough_string = ET.tostring(element, encoding='unicode')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ").split('\n', 1)[1]  # Remove first line (XML declaration)

def main():
    """Main function to generate domain model"""
    parser = argparse.ArgumentParser(description='Generate LAB Workflow Domain Model')
    parser.add_argument('--config', default='config/domain-model-config.yaml', 
                       help='Path to configuration file')
    parser.add_argument('--output', default='output/domain-model', 
                       help='Output directory for generated files')
    parser.add_argument('--debug', action='store_true', 
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    print("🏗️ Generating LAB Workflow Domain Model...")
    print(f"📋 Configuration: {args.config}")
    print(f"📁 Output: {args.output}")
    
    if args.debug:
        print(f"🐛 Debug mode enabled")
        print(f"🐛 Python path: {sys.executable}")
        print(f"🐛 Working directory: {Path.cwd()}")
    
    # Create output directory
    output_path = Path(args.output)
    output_path.mkdir(parents=True, exist_ok=True)
    print(f"📁 Created output directory: {output_path.absolute()}")
    
    # Load configuration
    config = load_config(args.config)
    if config is None:
        print("❌ Failed to load configuration")
        return 1
    
    if args.debug:
        print(f"🐛 Loaded configuration: {config}")
    
    # Generate entities
    if 'entities' in config and config['entities']:
        print(f"📊 Found {len(config['entities'])} entities to generate")
        
        generated_count = 0
        for entity_config in config['entities']:
            try:
                entity_name = entity_config.get('name', 'Unknown')
                print(f"🔨 Generating: {entity_name}")
                
                # Create entity XML
                entity_xml = generate_entity_xml(entity_config)
                if entity_xml is not None:
                    # Save to file with proper formatting
                    entity_file = output_path / f"{entity_name}.xml"
                    
                    with open(entity_file, 'w', encoding='utf-8') as f:
                        f.write(create_mendix_xml_header())
                        f.write(format_xml_output(entity_xml))
                    
                    print(f"✅ Generated: {entity_name}.xml")
                    generated_count += 1
                else:
                    print(f"❌ Failed to generate XML for {entity_name}")
                    
            except Exception as e:
                print(f"❌ Error generating {entity_config.get('name', 'unknown')}: {e}")
                if args.debug:
                    import traceback
                    traceback.print_exc()
        
        print(f"📈 Successfully generated {generated_count} entities")
    else:
        print("⚠️ No entities found in configuration")
    
    print("🎉 Domain model generation completed!")
    print(f"📁 Files saved to: {output_path.absolute()}")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n⚠️ Generation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)