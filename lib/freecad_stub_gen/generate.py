import logging
import shutil
from pathlib import Path

from freecad_stub_gen.config import SOURCE_DIR, TARGET_DIR
from freecad_stub_gen.generators.from_methods import FreecadStubGeneratorFromMethods
from freecad_stub_gen.generators.from_xml import FreecadStubGeneratorFromXML
from freecad_stub_gen.module_map import genXmlFiles, genPyCppFiles
from freecad_stub_gen.stub_container import StubContainer

logger = logging.getLogger(__name__)


def _genModule(moduleName: str, modulePath: Path, sourcePath=SOURCE_DIR):
    moduleStub = StubContainer(name=moduleName)

    for xmlPath in genXmlFiles(modulePath):
        if not (tg := FreecadStubGeneratorFromXML.safeCreate(xmlPath, sourcePath)):
            continue
        moduleStub += tg.getStub()

    for cppPath in genPyCppFiles(modulePath):
        if not (mg := FreecadStubGeneratorFromMethods.safeCreate(cppPath, sourcePath)):
            continue

        if stub := mg.getStub():
            moduleStub += stub

    return moduleStub


def generateFreeCadStubs(sourcePath=SOURCE_DIR, targetPath=TARGET_DIR):
    shutil.rmtree(targetPath, ignore_errors=True)
    targetPath.mkdir(parents=True, exist_ok=True)
    (targetPath / '__init__.pyi').touch(exist_ok=True)

    freeCADStub = StubContainer('class PyObjectBase(object): ...\n\n')
    freeCADStub += _genModule('FreeCAD', sourcePath / 'Base', sourcePath)
    freeCADStub += _genModule('FreeCAD', sourcePath / 'App', sourcePath)
    freeCADStub += StubContainer('GuiUp: typing.Literal[0, 1]', {'typing'})
    freeCADStub += StubContainer('Gui = FreeCADGui', {'FreeCADGui'})
    freeCADStub.save(targetPath)

    freeCADGuiStub = _genModule('FreeCADGui', sourcePath / 'Gui')
    freeCADGuiStub += StubContainer('Workbench: FreeCADGui.Workbench')
    freeCADGuiStub += StubContainer('ActiveDocument: Document')
    freeCADGuiStub.save(targetPath)

    for mod in (sourcePath / 'Mod').iterdir():
        ms = _genModule(mod.name, mod / 'App', sourcePath)
        ms += _genModule(mod.name, mod / 'Gui', sourcePath)
        ms.save(targetPath)

# TODO P4 preprocess and remove macros
# https://www.tutorialspoint.com/cplusplus/cpp_preprocessor.htm
