# Repository Folder Structure

This document outlines the folder structure of the Emergence Art repository and explains the purpose of each directory.

[Prototype, actual contents COMING SOON]

## Root Level

```
emergence-art/
├── LICENSE.md               # CC4 license file
├── README.md                # Project overview and quickstart
├── CODE_OF_CONDUCT.md       # Community guidelines
├── CONTRIBUTING.md          # How to contribute
├── docs/                    # Documentation
├── pipelines/               # DCC integration tools
└── examples/                # Example projects and showcases
```

## Documentation (`/docs/`)

```
docs/
├── getting-started.md       # Setup guide
├── world-guide.md           # Emergence universe overview
├── asset-catalog.md         # Available assets reference
├── folder-structure.md      # This file - repo organization
├── faq.md                   # Frequently asked questions
└── images/                  # Images used in documentation
```

## Pipelines (`/pipelines/`)

This directory contains tools and scripts for integrating Emergence assets with various Digital Content Creation (DCC) tools.

```
pipelines/
├── blender/                 # Blender tools and scripts
│   ├── README.md            # Blender-specific instructions
│   ├── scripts/             # Python scripts for Blender
│   └── addons/              # Blender addons
│
├── maya/                    # Maya tools and scripts
│   ├── README.md            # Maya-specific instructions
│   ├── scripts/             # MEL/Python scripts for Maya
│   └── plugins/             # Maya plugins
│
├── godot/                   # Godot tools and scripts
│   ├── README.md            # Godot-specific instructions
│   ├── addons/              # Godot addons
│   └── scripts/             # GDScript utilities
│
└── unreal/                  # Unreal Engine tools and scripts
    ├── README.md            # Unreal-specific instructions
    ├── plugins/             # Unreal plugins
    └── blueprints/          # Blueprint libraries
```

## Examples (`/examples/`)

This directory contains example projects demonstrating how to use Emergence assets in different DCCs.

```
examples/
├── blender/                 # Blender examples
│   ├── README.md            # Example descriptions
│   └── projects/            # Sample Blender projects
│
├── maya/                    # Maya examples
│   ├── README.md            # Example descriptions
│   └── projects/            # Sample Maya projects
│
├── godot/                   # Godot examples
│   ├── README.md            # Example descriptions
│   └── projects/            # Sample Godot projects
│
└── unreal/                  # Unreal Engine examples
    ├── README.md            # Example descriptions
    └── projects/            # Sample Unreal projects
```

## Asset References

Assets are stored on AWS and referenced via URLs in the repository. The structure of these references follows a consistent pattern:

```
aws://emergence-assets/
├── characters/              # Character models and animations
├── environments/            # Environment assets
├── props/                   # Props and objects
├── vfx/                     # Visual effects
├── textures/                # Materials and textures
└── audio/                   # Sound effects and music
```

Each pipeline includes tools for automatically downloading and setting up these assets in the appropriate format for its respective DCC.

## Future Directories

As the project evolves, additional directories may be added:

```
community/                   # Community showcase and resources
tutorials/                   # Step-by-step tutorials
releases/                    # Release notes and version history
```