#!/usr/bin/env python3 
LAB Product Validation Workflow - Domain Model Generator 
Generates complete domain model with all entities and associations 
 
import yaml 
import xml.etree.ElementTree as ET 
from pathlib import Path 
import argparse 
import sys 
from datetime import datetime 
 
def load_config(config_path): 
    """Load configuration from YAML file""" 
    try: 
        with open(config_path, 'r') as file: 
            return yaml.safe_load(file) 
    except Exception as e: 
        print(f"Error loading config: {e}") 
        sys.exit(1) 
 
def generate_entity(entity_config): 
    """Generate XML for a single entity""" 
    entity = ET.Element("entity") 
    entity.set("name", entity_config['name']) 
ECHO ist ausgeschaltet (OFF).
    if 'generalization' in entity_config: 
        generalization = ET.SubElement(entity, "generalization") 
        generalization.set("type", entity_config['generalization']) 
ECHO ist ausgeschaltet (OFF).
    # Add attributes 
    if 'attributes' in entity_config: 
        attributes_elem = ET.SubElement(entity, "attributes") 
ECHO ist ausgeschaltet (OFF).
        for attr in entity_config['attributes']: 
            attr_elem = ET.SubElement(attributes_elem, "attribute") 
            attr_elem.set("name", attr['name']) 
            attr_elem.set("type", attr['type']) 
ECHO ist ausgeschaltet (OFF).
            if 'length' in attr: 
                attr_elem.set("length", str(attr['length'])) 
            if 'enumeration' in attr: 
                attr_elem.set("enumeration", attr['enumeration']) 
ECHO ist ausgeschaltet (OFF).
    return entity 
 
def main(): 
    parser = argparse.ArgumentParser(description='Generate LAB workflow domain model') 
    parser.add_argument('--config', default='config/domain-model-config.yaml', help='Configuration file path') 
    parser.add_argument('--output', default='output/domain-model', help='Output directory') 
    parser.add_argument('--debug', action='store_true', help='Enable debug output') 
ECHO ist ausgeschaltet (OFF).
    args = parser.parse_args() 
ECHO ist ausgeschaltet (OFF).
    print("🏗️ Generating LAB Workflow Domain Model...") 
    print(f"📋 Configuration: {args.config}") 
    print(f"📁 Output: {args.output}") 
ECHO ist ausgeschaltet (OFF).
    # Create output directory 
    Path(args.output).mkdir(parents=True, exist_ok=True) 
ECHO ist ausgeschaltet (OFF).
    # Load configuration 
    try: 
        config = load_config(args.config) 
    except Exception as e: 
        print(f"❌ Error loading configuration: {e}") 
        return 
ECHO ist ausgeschaltet (OFF).
    # Generate entities from configuration 
    if 'entities' in config: 
        for entity_config in config['entities']: 
            try: 
                entity_xml = generate_entity(entity_config) 
                entity_file = Path(args.output) / f"{entity_config['name']}.xml" 
ECHO ist ausgeschaltet (OFF).
                with open(entity_file, 'w', encoding='utf-8') as f: 
                    f.write(ET.tostring(entity_xml, encoding='unicode')) 
ECHO ist ausgeschaltet (OFF).
                print(f"✅ Generated: {entity_config['name']}.xml") 
            except Exception as e: 
                print(f"❌ Error generating {entity_config.get('name', 'unknown')}: {e}") 
    else: 
        print("⚠️ No entities found in configuration") 
ECHO ist ausgeschaltet (OFF).
    print("🎉 Domain model generation completed!") 
 
if __name__ == "__main__": 
    main() 
