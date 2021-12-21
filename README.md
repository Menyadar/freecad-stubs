# freecad-stubs
[![PyPI version](https://img.shields.io/pypi/v/freecad-stubs)](https://pypi.org/project/freecad-stubs/)
[![GitHub license](https://img.shields.io/github/license/ostr00000/freecad-stubs)](https://github.com/ostr00000/freecad-stubs/blob/main/LICENSE)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/freecad-stubs)](https://pypi.python.org/pypi/freecad-stubs/)


Python stubs generated from FreeCAD source code.

### Stub source
Stubs are generated based on several available info:
- `*Py.xml` files - mainly docstrings, argument names, properties.
- corresponding `*PyImp.cpp` file - argument types are extracted from C code.
- other `*.cpp` files - functions or modules.

Unfortunately not all typing information may be generated. 
For example some objects are added dynamically. 
There are also many special cases 
therefore not all object are correctly mapped.
Moreover, some of C function has errors - invalid types, missing arguments 
(you can see more these errors if you change logger flag in configuration file `freecad-stubs/lib/freecad_stub_gen/config.py`) 

### Install stubs
You can install all stubs for freeCAD packages by running:
```bash
python -m pip install freecad-stubs 
```

### Adding stubs to python path
There are a lot of possible methods. This is only example: 

1. Copy stubs from a desired branch from this repository.  
Checkout to desired branch and copy folder `/freecad_stubs`.
   
2. (Optional) Or [generate](#Stub-Generation) stubs manually.
   Copy/move generated stubs to location of your choice. For example:
   ```shell
   cp -r ./freecad_stubs "$HOME/.local/lib/python3.9/freecad_stubs" 
   ```

3. Add location with stubs to python search path.
   For example:
   ```shell
   echo "$HOME/.local/lib/python3.9/freecad_stubs" > "$HOME/.local/lib/python3.9/site-packages/freecad_stubs.pth" 
   ```

### Stub Generation

1. Clone [freecad repository](https://github.com/FreeCAD/FreeCAD).
    ```shell
    git clone https://github.com/FreeCAD/FreeCAD.git
    ```
   #### Warning: FreeCAD repository has over `1.29 GB`
   You may download only these required folders:
    - /src/App
    - /src/Base
    - /src/Gui
    - /src/Main
    - /src/Mod


2. Clone this repository
    ```shell
    git clone https://github.com/ostr00000/freecad-stubs
    ```

3. Configure paths  
   In the file `freecad-stubs/lib/freecad_stub_gen/config.py`
   set desired configuration:
    - `SOURCE_DIR` - `src` folder from FreeCAD repository,
    - `TARGET_DIR` - target folder where stubs should be generated.
      #### Warning: `TARGET_DIR` folder and its content may be removed when generating stubs.

4. Run the main file from this project in Python
    ```shell
    pytohn freecad-stubs/lib/freecad_stub_gen/__main__.py
    ```
   Required python version: `>=3.10`.


### Progress

#### Stub source
- [x] generate class stub (xml files):
  - [x] property in xml,
  - [x] dynamic property added in cpp,
  - [x] method (+ static/class method),
  - [x] rich comparison (ex. `__eq__` method),
  - [x] number protocol (ex. `__add__` method),
- [x] generate class stub (cpp files):
  - [x] dynamically added in `init_type()`,
- [x] generate functions stub (cpp files):
  - [x] declared in `PyMethodDef` array,
  - [x] dynamically added in module constructor (subclass `Py::ExtensionModule`),

#### Stub quality
- [x] found class/function/method name,
- [x] copy docstring (+ generate property docstring),
- [x] guess argument names from docstrings,
- [x] found function/method argument types based on [c-api](https://docs.python.org/3/c-api/arg.html),
- [x] function/method return type,
- [x] raised exception in docstrings,
- [x] property getter type,
- [x] property setter type,
- [x] add comment "This class can be imported" for importable classes,
- [x] exceptions,
