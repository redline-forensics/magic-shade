
<h1 align="center">
  <br>
    <img src="https://cdn.rawgit.com/redline-forensics/magic-shade/master/resources/logo.svg" alt="Magic Shade" width="200">
  <br>
    Magic Shade
  <br>
</h1>

<h4 align="center">A simple shader replacement script for Maya.</h4>
<br>

![screenshot](https://github.com/redline-forensics/magic-shade/raw/master/resources/magic_shade.gif)

## Key Features

* Quickly apply custom shaders to an entire scene
  - Search for objects based on name or current shader
* Save shader replacement lists to files for reuse and distribution
* Reorder shader replacements for replacement chaining
* Included utility script for bulk processing of Hum3D.com vehicles

## Installation

1. Clone or download repository
   * Clone: ```git clone https://github.com/redline-forensics/magic-shade.git```
   * Download: <a href="https://github.com/redline-forensics/magic-shade/archive/master.zip">master.zip</a> and unzip
2. In ```\Documents\maya\scripts``` create a new folder ```magic-shade```
3. Place repository contents (```\resources```, ```magic_shade.py```, etc.) inside newly-created ```magic-shade``` folder
4. In Maya, open the Script Editor (Windows - General Editors - Script Editor)
5. Open ```\Documents\maya\scripts\magic-shade\magic_shade.py``` in the Script Editor (File - Open Script...)
6. Save the script to the shelf (File - Save Script to Shelf...)
7. Name the script (e.g. "Magic Shade")
8. (Optional) To install bulk Hum3D utility script, repeat steps 5-7 for ```\Documents\maya\scripts\vehicular.py```

## Usage

1. Start Magic Shade from your shelf button
2. Add a shader replacement ("spell") by clicking the green "+" button on the right
3. Select the shader to replace from the drop-down box on the left
   * You can select objects from this box by choosing "Object" from the Type drop-down box
4. Select the shader to apply from the drop-down box on the right
   * Both drop-down boxes can be edited manually. Add a "*" as a wildcard
5. Apply all spells by clicking Cast - Cast All Spells
6. Save your spells to a spellbook file for future use by clicking the save button
7. If new shaders are added to your scene, click File - Refresh Shaders to make them show up in the drop-down boxes

---


#### Contributors

Jake Cheek - [@jgchk](https://github.com/jgchk)

#### License

GPL
